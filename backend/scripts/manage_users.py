#!/usr/bin/env python3
"""
Secure local CLI for managing users stored in Google Cloud Firestore.

This script ONLY runs locally with GCP Application Default Credentials (ADC).
It is NOT exposed via any HTTP endpoint.

Usage:
    # List all users (no passwords shown)
    python scripts/manage_users.py list

    # Change a user's username (checks for conflicts)
    python scripts/manage_users.py change-username --user-id <id> --new-username <name>
    python scripts/manage_users.py change-username --user-id <id> --new-username <name> --yes
    python scripts/manage_users.py change-username --user-id <id> --new-username <name> --dry-run

    # Change a user's password (prompted securely via getpass, never printed)
    python scripts/manage_users.py change-password --user-id <id>
    python scripts/manage_users.py change-password --user-id <id> --yes
    python scripts/manage_users.py change-password --user-id <id> --dry-run

Environment variables:
    GOOGLE_CLOUD_PROJECT  — GCP project ID (required)
    GOOGLE_APPLICATION_CREDENTIALS — optional; uses ADC otherwise

Security properties:
    - Passwords are NEVER printed, logged, or echoed to the terminal.
    - All writes require explicit --yes flag or interactive y/n confirmation.
    - --dry-run shows what would change without writing anything to Firestore.
    - No hardcoded credentials; relies on GCP ADC.
"""

import argparse
import getpass
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow running from repo root: add backend to sys.path
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from argon2 import PasswordHasher
from google.cloud import firestore

_ph = PasswordHasher()

USERS_COLLECTION = "users"

# Fields safe to display — password is intentionally excluded
SAFE_DISPLAY_FIELDS = ("id", "username", "email", "firstName", "lastName", "currentCard", "createdAt")


# ---------------------------------------------------------------------------
# Firestore helpers (no dependency on app service layer — intentional,
# so this script works standalone without the full backend env configured)
# ---------------------------------------------------------------------------

def get_db() -> firestore.Client:
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        print("[ERROR] GOOGLE_CLOUD_PROJECT environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return firestore.Client(project=project)


def fetch_user_by_id(db: firestore.Client, user_id: str) -> dict | None:
    doc = db.collection(USERS_COLLECTION).document(user_id).get()
    if not doc.exists:
        return None
    return doc.to_dict()


def fetch_user_by_username(db: firestore.Client, username: str) -> dict | None:
    docs = (
        db.collection(USERS_COLLECTION)
        .where("username", "==", username)
        .limit(1)
        .stream()
    )
    for doc in docs:
        return doc.to_dict()
    return None


def fetch_all_users(db: firestore.Client) -> list[dict]:
    return [doc.to_dict() for doc in db.collection(USERS_COLLECTION).stream()]


def write_user(db: firestore.Client, user_id: str, updates: dict, dry_run: bool) -> None:
    updates["updatedAt"] = datetime.now(timezone.utc).isoformat()
    if dry_run:
        # Never show password values even in dry-run output
        safe_updates = {k: v for k, v in updates.items() if k != "password"}
        if "password" in updates:
            safe_updates["password"] = "*** (hidden) ***"
        print(f"[DRY-RUN] Would update user '{user_id}' with: {safe_updates}")
    else:
        db.collection(USERS_COLLECTION).document(user_id).set(updates, merge=True)


# ---------------------------------------------------------------------------
# Confirmation gate
# ---------------------------------------------------------------------------

def confirm(prompt: str, auto_yes: bool) -> bool:
    if auto_yes:
        print(f"{prompt} [auto-confirmed via --yes]")
        return True
    answer = input(f"{prompt} [y/N] ").strip().lower()
    return answer in ("y", "yes")


# ---------------------------------------------------------------------------
# Subcommand: list
# ---------------------------------------------------------------------------

def cmd_list(args, db: firestore.Client) -> None:
    users = fetch_all_users(db)
    if not users:
        print("No users found.")
        return

    # Sort by username for readability
    users.sort(key=lambda u: u.get("username", "").lower())

    col_widths = {f: len(f) for f in SAFE_DISPLAY_FIELDS}
    for user in users:
        for field in SAFE_DISPLAY_FIELDS:
            col_widths[field] = max(col_widths[field], len(str(user.get(field, ""))))

    header = "  ".join(f.ljust(col_widths[f]) for f in SAFE_DISPLAY_FIELDS)
    separator = "  ".join("-" * col_widths[f] for f in SAFE_DISPLAY_FIELDS)
    print(header)
    print(separator)
    for user in users:
        row = "  ".join(str(user.get(f, "")).ljust(col_widths[f]) for f in SAFE_DISPLAY_FIELDS)
        print(row)

    print(f"\nTotal: {len(users)} user(s)")


# ---------------------------------------------------------------------------
# Subcommand: change-username
# ---------------------------------------------------------------------------

def cmd_change_username(args, db: firestore.Client) -> None:
    user_id: str = args.user_id
    new_username: str = args.new_username.strip()
    dry_run: bool = args.dry_run
    auto_yes: bool = args.yes

    if not new_username:
        print("[ERROR] --new-username cannot be blank.", file=sys.stderr)
        sys.exit(1)

    # Fetch target user
    user = fetch_user_by_id(db, user_id)
    if user is None:
        print(f"[ERROR] No user found with id '{user_id}'.", file=sys.stderr)
        sys.exit(1)

    old_username = user.get("username", "")

    if old_username == new_username:
        print(f"Username is already '{new_username}'. Nothing to do.")
        return

    # Conflict check
    if not dry_run:
        conflict = fetch_user_by_username(db, new_username)
        if conflict and conflict.get("id") != user_id:
            print(
                f"[ERROR] Username '{new_username}' is already taken by user id '{conflict.get('id')}'.",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        print(f"[DRY-RUN] Skipping conflict check for username '{new_username}'.")

    print(f"  User id   : {user_id}")
    print(f"  Old username: {old_username}")
    print(f"  New username: {new_username}")

    if not confirm("Apply username change?", auto_yes):
        print("Aborted.")
        return

    write_user(db, user_id, {"username": new_username}, dry_run)

    if not dry_run:
        print(f"Username updated: '{old_username}' -> '{new_username}'")


# ---------------------------------------------------------------------------
# Subcommand: change-password
# ---------------------------------------------------------------------------

def cmd_change_password(args, db: firestore.Client) -> None:
    user_id: str = args.user_id
    dry_run: bool = args.dry_run
    auto_yes: bool = args.yes

    # Fetch target user
    user = fetch_user_by_id(db, user_id)
    if user is None:
        print(f"[ERROR] No user found with id '{user_id}'.", file=sys.stderr)
        sys.exit(1)

    username = user.get("username", user_id)
    print(f"  User id  : {user_id}")
    print(f"  Username : {username}")
    print()

    if dry_run:
        print("[DRY-RUN] Would update password for this user (new value not shown).")
        if not confirm("Proceed with dry-run?", auto_yes):
            print("Aborted.")
        return

    # Prompt securely — password is never echoed or stored beyond this scope
    new_password = getpass.getpass(prompt="New password: ")
    if not new_password:
        print("[ERROR] Password cannot be blank.", file=sys.stderr)
        sys.exit(1)

    confirm_password = getpass.getpass(prompt="Confirm new password: ")
    if new_password != confirm_password:
        print("[ERROR] Passwords do not match.", file=sys.stderr)
        # Zero out before exiting — best-effort in CPython
        new_password = ""
        confirm_password = ""
        sys.exit(1)

    # Zero out the confirmation copy immediately
    confirm_password = ""

    print()
    print(f"  About to change password for user '{username}' (id: {user_id}).")

    if not confirm("Apply password change?", auto_yes):
        new_password = ""
        print("Aborted.")
        return

    hashed = _ph.hash(new_password)
    # Zero out plaintext immediately after hashing
    new_password = ""

    write_user(db, user_id, {"password": hashed}, dry_run=False)

    print("Password updated successfully.")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Secure local CLI for managing GCP Agentic Demo users in Firestore.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # -- list --
    subparsers.add_parser("list", help="List all users (no passwords shown).")

    # -- change-username --
    p_cu = subparsers.add_parser("change-username", help="Change a user's username.")
    p_cu.add_argument("--user-id", required=True, help="Firestore document ID of the user.")
    p_cu.add_argument("--new-username", required=True, help="The desired new username.")
    p_cu.add_argument(
        "--yes", action="store_true", help="Skip interactive confirmation prompt."
    )
    p_cu.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing to Firestore.",
    )

    # -- change-password --
    p_cp = subparsers.add_parser("change-password", help="Change a user's password.")
    p_cp.add_argument("--user-id", required=True, help="Firestore document ID of the user.")
    p_cp.add_argument(
        "--yes", action="store_true", help="Skip interactive confirmation prompt."
    )
    p_cp.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing to Firestore.",
    )

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    db = get_db()

    if args.command == "list":
        cmd_list(args, db)
    elif args.command == "change-username":
        cmd_change_username(args, db)
    elif args.command == "change-password":
        cmd_change_password(args, db)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
