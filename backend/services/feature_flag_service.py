"""
Feature Flag Service using Datadog Feature Flags via OpenFeature SDK.

Flag state is managed in the Datadog UI (Software Delivery > Feature Flags)
and delivered via the Datadog Agent's Remote Configuration.
"""
import logging
import threading
from openfeature import api
from openfeature.evaluation_context import EvaluationContext
from openfeature.event import ProviderEvent

try:
    from ddtrace.openfeature import DataDogProvider
except ImportError:
    DataDogProvider = None

logger = logging.getLogger("feature_flags")

_initialized = False
_client = None


def init_feature_flags():
    """Initialize the OpenFeature SDK with the Datadog provider.

    Must be called after ddtrace is configured (i.e., after ddtrace-run starts).
    The DataDogProvider uses the Datadog Agent's Remote Configuration channel
    to receive flag updates from Datadog's cloud.
    """
    global _initialized, _client

    if _initialized:
        return

    if DataDogProvider is None:
        logger.warning("ddtrace.openfeature.DataDogProvider not available — feature flags disabled")
        _initialized = True
        return

    try:
        ready_event = threading.Event()
        api.add_handler(ProviderEvent.PROVIDER_READY, lambda e: ready_event.set())
        api.add_handler(ProviderEvent.PROVIDER_ERROR, lambda e: logger.warning("Feature flag provider error: %s", e))

        provider = DataDogProvider()
        api.set_provider(provider)

        # Wait for the provider to be ready (flag configs downloaded)
        if not ready_event.wait(timeout=10):
            logger.warning("Feature flag provider not ready after 10s — evaluations will use defaults")

        _client = api.get_client()
        _initialized = True
        logger.info("Datadog Feature Flags initialized via OpenFeature SDK")
    except Exception:
        logger.exception("Failed to initialize Datadog Feature Flags")
        _initialized = True


def evaluate_flag(flag_name: str, default: bool = False, context: dict | None = None) -> bool:
    """Evaluate a boolean feature flag via the Datadog OpenFeature provider.

    Args:
        flag_name: The flag key as defined in Datadog Feature Management.
        default: Default value if flag is not found or provider is unavailable.
        context: Optional evaluation context attributes (flat primitives only).

    Returns:
        The flag's boolean value.
    """
    if not _initialized:
        init_feature_flags()

    if _client is None:
        return default

    eval_ctx = None
    if context:
        eval_ctx = EvaluationContext(
            targeting_key=context.get("targeting_key", "anonymous"),
            attributes={k: v for k, v in context.items() if k != "targeting_key"},
        )

    try:
        return _client.get_boolean_value(flag_name, default, eval_ctx)
    except Exception:
        logger.exception("Error evaluating flag %s", flag_name)
        return default
