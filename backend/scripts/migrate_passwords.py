#!/usr/bin/env python3
"""
One-time migration: hash all plaintext passwords in the Firestore `users`
collection using argon2id.

Accounts whose password already starts with `$argon2` are skipped (idempotent).

Usage:
    python scripts/migrate_passwords.py [--dry-run] [--yes]

Environment variables:
    GOOGLE_CLOUD_PROJECT  — GCP project ID (required)
    GOOGLE_APPLICATION_CREDENTIALS — optional; uses ADC otherwise
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

import argparse
from argon2 import PasswordHasher
from google.cloud import firestore

USERS_COLLECTION = "users"
_ph = PasswordHasher()


def get_db() -> firestore.Client:
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        print("[ERROR] GOOGLE_CLOUD_PROJECT is not set.", file=sys.stderr)
        sys.exit(1)
    return firestore.Client(project=project)


def confirm(auto_yes: bool) -> bool:
    if auto_yes:
        print("Auto-confirmed via --yes.")
        return True
    answer = input("Proceed? [y/N] ").strip().lower()
    return answer in ("y", "yes")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing.")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt.")
    args = parser.parse_args()

    db = get_db()

    docs = list(db.collection(USERS_COLLECTION).stream())
    to_migrate = []
    already_hashed = 0

    for doc in docs:
        data = doc.to_dict()
        pw = data.get("password", "")
        if pw.startswith("$argon2"):
            already_hashed += 1
        else:
            to_migrate.append((doc.id, data.get("username", doc.id), pw))

    print(f"Users found       : {len(docs)}")
    print(f"Already hashed    : {already_hashed}")
    print(f"Need migration    : {len(to_migrate)}")

    if not to_migrate:
        print("Nothing to do.")
        return

    print()
    if args.dry_run:
        print("[DRY-RUN] Would hash passwords for:")
        for uid, uname, _ in to_migrate:
            print(f"  {uid}  ({uname})")
        return

    print("About to hash passwords for:")
    for uid, uname, _ in to_migrate:
        print(f"  {uid}  ({uname})")
    print()

    if not confirm(args.yes):
        print("Aborted.")
        return

    updated_at = datetime.now(timezone.utc).isoformat()
    batch_size = 400
    for i in range(0, len(to_migrate), batch_size):
        batch = db.batch()
        for uid, uname, plaintext in to_migrate[i:i + batch_size]:
            hashed = _ph.hash(plaintext)
            batch.update(
                db.collection(USERS_COLLECTION).document(uid),
                {"password": hashed, "updatedAt": updated_at},
            )
        batch.commit()

    print(f"Migrated {len(to_migrate)} user(s).")


if __name__ == "__main__":
    main()
