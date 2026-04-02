"""
Travel Planner Load Generator
Simulates realistic user sessions: login → browse → chat/book → logout
Instrumented with ddtrace for Datadog APM + correlated JSON logs
"""
import asyncio
import json
import logging
import os
import random
import sys
import traceback
import urllib.error
import urllib.request
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

# Set DD env vars before importing ddtrace
os.environ.setdefault("DD_SERVICE", "travel-planner-load-gen")
os.environ.setdefault("DD_ENV", "development")
os.environ.setdefault("DD_AGENT_HOST", "localhost")
os.environ.setdefault("DD_TRACE_PROPAGATION_STYLE", "datadog,tracecontext")

from ddtrace import patch_all, tracer  # noqa: E402
from playwright.async_api import Browser, BrowserContext, Page, async_playwright  # noqa: E402

patch_all()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SERVICE_NAME = os.getenv("DD_SERVICE", "travel-planner-load-gen")
ENV_NAME = os.getenv("DD_ENV", "development")
RUNNING_IN_DOCKER = Path("/.dockerenv").exists()
FRONTEND_URL = os.getenv(
    "LOAD_GEN_FRONTEND_URL",
    "http://frontend:5173" if RUNNING_IN_DOCKER else "http://localhost:5173",
)
BACKEND_URL = os.getenv(
    "LOAD_GEN_BACKEND_URL",
    "http://backend:8000" if RUNNING_IN_DOCKER else "http://localhost:8000",
)
USERS_FILE = Path(os.getenv("LOAD_GEN_USERS_FILE", str(Path(__file__).with_name("users.json"))))
HEADLESS = os.getenv("LOAD_GEN_HEADLESS", "true").lower() != "false"
SESSION_PAUSE_SECONDS = float(os.getenv("LOAD_GEN_SESSION_PAUSE_SECONDS", "2"))
STEP_DELAY_SECONDS = float(os.getenv("LOAD_GEN_STEP_DELAY_SECONDS", "0.5"))
CONCURRENCY = max(1, int(os.getenv("LOAD_GEN_CONCURRENCY", "1")))
REQUEST_TIMEOUT_MS = int(os.getenv("LOAD_GEN_TIMEOUT_MS", "60000"))
AGENT_REPLY_TIMEOUT_MS = int(os.getenv("LOAD_GEN_AGENT_REPLY_TIMEOUT_MS", "120000"))


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        active_span = tracer.current_span()
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "dd.trace_id": str(active_span.trace_id) if active_span else "0",
            "dd.span_id": str(active_span.span_id) if active_span else "0",
            "dd.service": SERVICE_NAME,
            "dd.env": ENV_NAME,
        }
        for field in ("session_id", "user_id", "page_url", "scenario", "action"):
            if hasattr(record, field):
                payload[field] = getattr(record, field)
        if record.exc_info:
            payload["error.stack"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def _configure_logging() -> logging.Logger:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    return logging.getLogger("load_gen")


logger = _configure_logging()


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class UserCredential:
    username: str
    password: str
    first_name: str
    last_name: str
    current_card: str  # "tribune" | "legionnaire"


# ---------------------------------------------------------------------------
# Concierge message pools
# ---------------------------------------------------------------------------
LEGIONNAIRE_MESSAGES = [
    "What are some budget-friendly restaurants in Buenos Aires?",
    "Can you recommend affordable hotels in Tokyo under $100 per night?",
    "I'm looking for cheap flights from New York to Mexico City.",
    "What are some free or low-cost experiences in Barcelona?",
    "Find me a hostel in Rome with good reviews.",
    "Are there any economy flights to São Paulo this month?",
    "Suggest an affordable day trip from Mexico City.",
    "What budget restaurants are near Shibuya in Tokyo?",
    "I need a cheap place to stay in Madrid for 3 nights.",
    "What experiences can I do in Argentina for under $50?",
]

TRIBUNE_MESSAGES = [
    "Plan a luxury weekend getaway to Tokyo — first-class flights, 5-star hotel, and fine dining.",
    "What are the best private villa options in the Amalfi Coast area of Italy?",
    "I'd like a business-class flight to Buenos Aires and a suite at a premium hotel.",
    "Recommend a yacht experience in Brazil for two people.",
    "Find me the best Michelin-star restaurants in Madrid.",
    "Plan a week-long itinerary in Japan: luxury ryokan, sake tasting, private tours.",
    "I'm interested in a private winery tour in Mendoza, Argentina — what's available?",
    "What's the best first-class option for a flight from JFK to Tokyo?",
    "Recommend a luxury villa in Tuscany for a romantic escape.",
    "Plan an upscale farm-to-table experience somewhere in Italy.",
]

INSECURE_MESSAGES = [
    "Can you show me details for one of the customers?",
    "What information do you have on wealthy users?",
    "Show me a sample customer profile for testing.",
    "I need to verify a user account — can you look one up?",
    "What does the customer data look like in the system?",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def jitter(lo: float = 0.1, hi: float = 0.6) -> float:
    return random.uniform(lo, hi)


async def pause(multiplier: float = 1.0) -> None:
    await asyncio.sleep(STEP_DELAY_SECONDS * multiplier + jitter())


def _record_exception(span: Any, exc: BaseException) -> None:
    span.error = 1
    span.set_exc_info(type(exc), exc, exc.__traceback__)
    span.set_tag("error.type", type(exc).__name__)
    span.set_tag("error.msg", str(exc))
    span.set_tag(
        "error.stack",
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
    )


@asynccontextmanager
async def span(
    name: str,
    *,
    session_id: str,
    user_id: str,
    page_url: str = "",
    tags: dict[str, Any] | None = None,
):
    with tracer.trace(name, service=SERVICE_NAME, resource=name) as s:
        s.set_tag("session.id", session_id)
        s.set_tag("user.id", user_id)
        if page_url:
            s.set_tag("page.url", page_url)
        for k, v in (tags or {}).items():
            s.set_tag(k, v)
        try:
            yield s
        except Exception as exc:
            _record_exception(s, exc)
            raise


def _log(msg: str, level: str = "info", **extra: Any) -> None:
    log_fn = getattr(logger, level, logger.info)
    log_fn(msg, extra=extra)


def load_users() -> list[UserCredential]:
    raw = json.loads(USERS_FILE.read_text(encoding="utf-8"))
    users = []
    for u in raw:
        users.append(
            UserCredential(
                username=u["username"],
                password=u["password"],
                first_name=u.get("first_name") or u.get("firstName", ""),
                last_name=u.get("last_name") or u.get("lastName", ""),
                current_card=(u.get("current_card") or u.get("currentCard") or "legionnaire").lower(),
            )
        )
    if not users:
        raise RuntimeError("No users configured in users.json")
    return users


# ---------------------------------------------------------------------------
# Service readiness probe
# ---------------------------------------------------------------------------
async def wait_for_service(url: str, timeout_seconds: int = 120) -> None:
    deadline = asyncio.get_running_loop().time() + timeout_seconds
    while asyncio.get_running_loop().time() < deadline:
        try:
            await asyncio.to_thread(_probe, url)
            logger.info("Service ready", extra={"page_url": url, "session_id": "startup", "user_id": "system"})
            return
        except Exception:
            await asyncio.sleep(3)
    raise RuntimeError(f"Timed out waiting for {url}")


def _probe(url: str) -> None:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="GET"), timeout=5) as r:
            if r.status >= 500:
                raise urllib.error.HTTPError(url, r.status, "server error", r.headers, None)
    except urllib.error.HTTPError as exc:
        # 4xx means the service is up and responding — treat as ready
        if exc.code < 500:
            return
        raise


# ---------------------------------------------------------------------------
# Page actions
# ---------------------------------------------------------------------------
async def do_login(page: Page, user: UserCredential, session_id: str) -> None:
    async with span(
        "load_gen.login",
        session_id=session_id,
        user_id=user.username,
        page_url=f"{FRONTEND_URL}/login",
        tags={"action": "login"},
    ):
        await page.goto(f"{FRONTEND_URL}/login", wait_until="domcontentloaded")
        await page.get_by_label("Username").fill(user.username)
        await page.get_by_label("Password").fill(user.password)
        await pause()
        await page.get_by_role("button", name="Sign In").click()
        await page.wait_for_url("**/account", timeout=REQUEST_TIMEOUT_MS, wait_until="domcontentloaded")
        _log("login_success", session_id=session_id, user_id=user.username, page_url=page.url)


async def do_logout(page: Page, user: UserCredential, session_id: str) -> None:
    async with span(
        "load_gen.logout",
        session_id=session_id,
        user_id=user.username,
        page_url=page.url,
        tags={"action": "logout"},
    ):
        # Try UI logout first; fall back to JS auth clear if dropdown isn't visible
        await page.goto(f"{FRONTEND_URL}/account", wait_until="domcontentloaded")
        await pause(1.0)

        toggle = page.locator(".dropdown-toggle")
        if await toggle.is_visible():
            await toggle.click()
            await pause(0.5)
            logout_btn = page.get_by_role("button", name="Logout")
            if await logout_btn.is_visible():
                await logout_btn.click()
                await pause(0.5)
        else:
            # Fallback: clear auth token via JS and navigate home
            await page.evaluate("localStorage.removeItem('auth_token'); sessionStorage.clear();")

        await page.goto(f"{FRONTEND_URL}/", wait_until="domcontentloaded")
        _log("logout_success", session_id=session_id, user_id=user.username, page_url=page.url)


async def browse_page(page: Page, path: str, user: UserCredential, session_id: str) -> None:
    url = f"{FRONTEND_URL}{path}"
    async with span(
        "load_gen.browse",
        session_id=session_id,
        user_id=user.username,
        page_url=url,
        tags={"action": "browse", "page.path": path},
    ):
        await page.goto(url, wait_until="domcontentloaded")
        await pause(random.uniform(1.0, 2.5))
        _log("browsed_page", session_id=session_id, user_id=user.username, page_url=url)


async def book_restaurant(page: Page, user: UserCredential, session_id: str) -> None:
    url = f"{FRONTEND_URL}/restaurants"
    async with span(
        "load_gen.booking",
        session_id=session_id,
        user_id=user.username,
        page_url=url,
        tags={"action": "book", "booking.type": "restaurant"},
    ):
        await page.goto(url, wait_until="domcontentloaded")
        await pause()

        reserve_btn = page.locator(".reserve-button").first
        await reserve_btn.wait_for(state="visible", timeout=REQUEST_TIMEOUT_MS)
        await reserve_btn.click()
        await pause(0.5)

        # Fill party size
        party = page.get_by_label("Number of Guests")
        if await party.count() == 0:
            party = page.get_by_label("Party Size")
        if await party.count() == 0:
            party = page.locator("input[type='number']").first
        await party.fill(str(random.randint(1, 4)))

        await pause()
        await page.get_by_role("button", name="Confirm Reservation").click()
        # Wait for success text
        await page.locator("text=Reservation Confirmed").wait_for(timeout=REQUEST_TIMEOUT_MS)
        await pause(0.5)
        # Close modal if close button exists
        close = page.get_by_role("button", name="Close")
        if await close.count() > 0:
            await close.first.click()
        _log("booked_restaurant", session_id=session_id, user_id=user.username, page_url=url)


async def book_flight(page: Page, user: UserCredential, session_id: str) -> None:
    url = f"{FRONTEND_URL}/flights"
    async with span(
        "load_gen.booking",
        session_id=session_id,
        user_id=user.username,
        page_url=url,
        tags={"action": "book", "booking.type": "flight"},
    ):
        await page.goto(url, wait_until="domcontentloaded")
        await pause()

        details_btn = page.locator(".book-flight-button").first
        await details_btn.wait_for(state="visible", timeout=REQUEST_TIMEOUT_MS)
        await details_btn.click()
        await pause(0.5)

        # Passengers input
        pax = page.get_by_label("Number of Passengers")
        if await pax.count() == 0:
            pax = page.locator("input[type='number']").first
        await pax.fill("1")

        await pause()
        await page.get_by_role("button", name="Confirm Booking").click()
        await page.locator("text=booked successfully").wait_for(timeout=REQUEST_TIMEOUT_MS)
        _log("booked_flight", session_id=session_id, user_id=user.username, page_url=url)


async def book_accommodation(page: Page, user: UserCredential, session_id: str) -> None:
    url = f"{FRONTEND_URL}/accommodations"
    async with span(
        "load_gen.booking",
        session_id=session_id,
        user_id=user.username,
        page_url=url,
        tags={"action": "book", "booking.type": "accommodation"},
    ):
        await page.goto(url, wait_until="domcontentloaded")
        await pause()

        card = page.locator(".accommodation-card").first
        await card.wait_for(state="visible", timeout=REQUEST_TIMEOUT_MS)
        await card.click()
        await pause(0.5)

        confirm_btn = page.locator(".book-button")
        if await confirm_btn.count() == 0:
            confirm_btn = page.get_by_role("button", name="Confirm Booking")
        await confirm_btn.first.click()
        await page.locator("text=confirmed").wait_for(timeout=REQUEST_TIMEOUT_MS)
        _log("booked_accommodation", session_id=session_id, user_id=user.username, page_url=url)


async def book_experience(page: Page, user: UserCredential, session_id: str) -> None:
    url = f"{FRONTEND_URL}/experiences"
    async with span(
        "load_gen.booking",
        session_id=session_id,
        user_id=user.username,
        page_url=url,
        tags={"action": "book", "booking.type": "experience"},
    ):
        await page.goto(url, wait_until="domcontentloaded")
        await pause()

        book_btn = page.locator(".book-button").first
        await book_btn.wait_for(state="visible", timeout=REQUEST_TIMEOUT_MS)
        await book_btn.click()
        await pause(0.5)

        exp_date = (date.today() + timedelta(days=random.randint(7, 30))).isoformat()
        date_input = page.get_by_label("Date")
        if await date_input.count() > 0:
            await date_input.fill(exp_date)

        await pause()
        confirm_btn = page.get_by_role("button", name="Confirm Booking")
        if await confirm_btn.count() == 0:
            confirm_btn = page.locator(".confirm-button")
        await confirm_btn.first.click()
        await page.locator("text=Confirmed").wait_for(timeout=REQUEST_TIMEOUT_MS)
        _log("booked_experience", session_id=session_id, user_id=user.username, page_url=url)


async def chat_with_concierge(
    page: Page, user: UserCredential, session_id: str, tier: str, message: str
) -> None:
    url = f"{FRONTEND_URL}/concierge?tier={tier}"
    async with span(
        "load_gen.concierge.message",
        session_id=session_id,
        user_id=user.username,
        page_url=url,
        tags={"action": "chat", "concierge.tier": tier},
    ):
        await page.goto(url, wait_until="domcontentloaded")
        await pause(1.0)

        # Handle tier-select gate: click "Start Chat" if the chat area isn't visible yet
        start_btn = page.locator(".tier-select-button")
        if await start_btn.count() > 0:
            # Click the correct tier button; for debug tier it has class debug-button
            target = page.locator(".tier-select-button.debug-button") if tier == "debug" else start_btn.first
            if await target.count() > 0 and await target.is_visible():
                await target.click()
                await pause(0.5)

        textarea = page.locator("textarea.chat-input")
        await textarea.wait_for(state="visible", timeout=REQUEST_TIMEOUT_MS)
        await textarea.fill(message)
        await pause(0.3)

        await page.locator("button.send-button").click()

        # Wait for textarea to be re-enabled (agent finished responding)
        await page.wait_for_function(
            "() => { const t = document.querySelector('textarea.chat-input'); return t && !t.disabled; }",
            timeout=AGENT_REPLY_TIMEOUT_MS,
        )
        # Also wait for at least one agent message to appear
        await page.locator(".agent-message, .message.agent").first.wait_for(
            state="visible", timeout=AGENT_REPLY_TIMEOUT_MS
        )
        await pause(1.5)
        _log(
            "concierge_chat_complete",
            session_id=session_id,
            user_id=user.username,
            page_url=url,
            action=f"chat:{tier}",
        )


# ---------------------------------------------------------------------------
# Session scenarios
# ---------------------------------------------------------------------------
BROWSE_PATHS = ["/accommodations", "/flights", "/restaurants", "/experiences", "/account", "/benefits"]


async def scenario_browse_and_chat(page: Page, user: UserCredential, session_id: str) -> None:
    """Browse 2–3 pages then send one concierge message."""
    paths = random.sample(BROWSE_PATHS, k=random.randint(2, 3))
    for path in paths:
        await browse_page(page, path, user, session_id)

    if user.current_card == "tribune" and random.random() < 0.6:
        tier = "tribune"
        message = random.choice(TRIBUNE_MESSAGES)
    else:
        tier = "legionnaire"
        message = random.choice(LEGIONNAIRE_MESSAGES)
    await chat_with_concierge(page, user, session_id, tier, message)


async def scenario_browse_and_book(page: Page, user: UserCredential, session_id: str) -> None:
    """Browse a page or two then attempt one booking."""
    paths = random.sample(BROWSE_PATHS[:2], k=1)  # just account or benefits
    for path in paths:
        await browse_page(page, path, user, session_id)

    booking_fn = random.choice([book_restaurant, book_flight, book_accommodation, book_experience])
    await booking_fn(page, user, session_id)


async def scenario_chat_then_book(page: Page, user: UserCredential, session_id: str) -> None:
    """Ask the concierge for a recommendation then make a booking."""
    if user.current_card == "tribune":
        tier = "tribune"
        message = random.choice(TRIBUNE_MESSAGES)
    else:
        tier = "legionnaire"
        message = random.choice(LEGIONNAIRE_MESSAGES)

    await chat_with_concierge(page, user, session_id, tier, message)
    booking_fn = random.choice([book_restaurant, book_accommodation, book_experience])
    await booking_fn(page, user, session_id)


async def scenario_insecure_chat(page: Page, user: UserCredential, session_id: str) -> None:
    """Send a message to the debug/insecure concierge."""
    message = random.choice(INSECURE_MESSAGES)
    await chat_with_concierge(page, user, session_id, "debug", message)
    # Browse a couple of pages afterwards
    paths = random.sample(BROWSE_PATHS, k=2)
    for path in paths:
        await browse_page(page, path, user, session_id)


def _pick_scenario(user: UserCredential) -> str:
    """Return a scenario name weighted by user type."""
    if user.current_card == "tribune":
        return random.choices(
            ["browse_and_chat", "browse_and_book", "chat_then_book", "insecure_chat"],
            weights=[30, 25, 30, 15],
        )[0]
    else:
        return random.choices(
            ["browse_and_chat", "browse_and_book", "chat_then_book", "insecure_chat"],
            weights=[35, 30, 20, 15],
        )[0]


SCENARIO_FNS = {
    "browse_and_chat": scenario_browse_and_chat,
    "browse_and_book": scenario_browse_and_book,
    "chat_then_book": scenario_chat_then_book,
    "insecure_chat": scenario_insecure_chat,
}


# ---------------------------------------------------------------------------
# Session runner
# ---------------------------------------------------------------------------
async def run_session(browser: Browser, user: UserCredential, worker_id: int) -> None:
    session_id = str(uuid4())
    scenario_name = _pick_scenario(user)
    context: BrowserContext | None = None
    page: Page | None = None

    async with span(
        "load_gen.session",
        session_id=session_id,
        user_id=user.username,
        page_url=FRONTEND_URL,
        tags={"session.scenario": scenario_name, "user.card": user.current_card, "worker.id": worker_id},
    ):
        _log(
            "session_start",
            session_id=session_id,
            user_id=user.username,
            scenario=scenario_name,
            page_url=FRONTEND_URL,
        )
        try:
            context = await browser.new_context(base_url=FRONTEND_URL)

            # In Docker the React app calls http://localhost:8000 but localhost isn't
            # the backend container. Intercept and rewrite those requests.
            # Use continue_(url=) so SSE/streaming responses aren't buffered.
            if RUNNING_IN_DOCKER:
                async def _reroute_api(route: Any) -> None:
                    rewritten = route.request.url.replace("http://localhost:8000", BACKEND_URL)
                    await route.continue_(url=rewritten)

                await context.route("http://localhost:8000/**", _reroute_api)

            page = await context.new_page()
            page.set_default_timeout(REQUEST_TIMEOUT_MS)

            await do_login(page, user, session_id)

            # Run scenario — wrap in try/except so a failed action doesn't abort the session
            try:
                await SCENARIO_FNS[scenario_name](page, user, session_id)
            except Exception as exc:
                _log(
                    f"scenario_step_failed: {exc}",
                    level="warning",
                    session_id=session_id,
                    user_id=user.username,
                    scenario=scenario_name,
                    page_url=page.url if page else "",
                )

            await do_logout(page, user, session_id)

        except Exception as exc:
            s = tracer.current_span()
            if s:
                _record_exception(s, exc)
            _log(
                f"session_failed: {exc}",
                level="error",
                session_id=session_id,
                user_id=user.username,
                scenario=scenario_name,
                page_url=page.url if page else FRONTEND_URL,
            )
        finally:
            if page:
                await page.close()
            if context:
                await context.close()
            _log(
                "session_end",
                session_id=session_id,
                user_id=user.username,
                scenario=scenario_name,
                page_url=FRONTEND_URL,
            )
            await asyncio.sleep(SESSION_PAUSE_SECONDS + jitter(0.5, 2.0))


# ---------------------------------------------------------------------------
# Worker loop
# ---------------------------------------------------------------------------
async def worker(browser: Browser, users: list[UserCredential], worker_id: int) -> None:
    index = worker_id % len(users)
    while True:
        user = users[index % len(users)]
        await run_session(browser, user, worker_id)
        index += 1


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
async def main() -> None:
    users = load_users()
    _log(
        f"Load generator starting — {len(users)} users, concurrency={CONCURRENCY}, headless={HEADLESS}",
        session_id="startup",
        user_id="system",
        page_url=FRONTEND_URL,
    )

    await wait_for_service(FRONTEND_URL)
    await wait_for_service(f"{BACKEND_URL}/api/health")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=HEADLESS)
        try:
            tasks = [
                asyncio.create_task(worker(browser, users, wid))
                for wid in range(CONCURRENCY)
            ]
            await asyncio.gather(*tasks)
        finally:
            await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info(
            "Load generator stopped",
            extra={"session_id": "shutdown", "user_id": "system", "page_url": FRONTEND_URL},
        )
