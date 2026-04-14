#!/usr/bin/env python3
"""
Firestore seeder — loads travel catalog data from JSON files and upserts
into Firestore.  Safe to run multiple times (idempotent).

Collections seeded (wiped + reloaded on every run):
  accommodations, restaurants, flights, experiences

Collections never touched (stateful data):
  users, applications

Image paths are normalized to clean relative paths (no leading slash) so
the backend service layer can generate signed GCS URLs at read time.

Usage (from /app/backend inside the container, or repo root locally):
    python scripts/seed_firestore.py

Environment variables:
    GOOGLE_CLOUD_PROJECT  — GCP project ID (required)
    MEDIA_BUCKET_NAME     — used only for logging; URL resolution is done
                            at read time by the service layer
    GOOGLE_APPLICATION_CREDENTIALS — optional; uses ADC otherwise
"""

import json
import os
import sys
from pathlib import Path

# Allow running from repo root: add backend to sys.path
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from google.cloud import firestore

DATA_DIR = _BACKEND_DIR / "data"

CATALOG_COLLECTIONS = ["accommodations", "restaurants", "flights", "experiences"]


def normalize_image_url(path: str | None) -> str | None:
    """
    Normalize imageUrl for storage in Firestore:
    - Absolute URLs (http/https): keep as-is.
    - Paths that resolve to the img/ prefix in the media bucket (e.g. img/... or /img/...):
      stored as clean relative path (no leading slash) so the backend can generate signed URLs.
    - Any other relative path (e.g. /logo.png, logo.png): kept as-is.
      These resolve against the frontend SPA bucket and are not in the media bucket.
    - None / empty: return as-is.
    """
    if not path:
        return path
    if path.startswith("http://") or path.startswith("https://"):
        return path
    clean = path.lstrip("/")
    if clean.startswith("img/"):
        return clean
    # Path is not in the media bucket (e.g. /logo.png) — preserve original
    return path


def load_json(filename: str) -> list[dict]:
    filepath = DATA_DIR / filename
    if not filepath.exists():
        print(f"  [WARN] {filepath} not found, skipping.")
        return []
    with open(filepath) as f:
        data = json.load(f)
    # restaurants.json has a {"restaurants": [...]} wrapper
    if isinstance(data, dict):
        key = next(iter(data))
        data = data[key]
    return data


def seed_collection(db: firestore.Client, collection_name: str, records: list[dict]) -> None:
    col_ref = db.collection(collection_name)

    # Delete existing documents so removed records don't linger
    batch_size = 400
    existing = list(col_ref.stream())
    for i in range(0, len(existing), batch_size):
        batch = db.batch()
        for doc in existing[i : i + batch_size]:
            batch.delete(doc.reference)
        batch.commit()
    print(f"  Cleared {len(existing)} existing docs from '{collection_name}'")

    # Upsert new records in batches of 400
    for i in range(0, len(records), batch_size):
        batch = db.batch()
        for record in records[i : i + batch_size]:
            # Normalize imageUrl before storing
            if "imageUrl" in record:
                record["imageUrl"] = normalize_image_url(record["imageUrl"])
            doc_id = record.get("id")
            if not doc_id:
                print(f"  [WARN] Record missing 'id' in {collection_name}, skipping: {record}")
                continue
            batch.set(col_ref.document(doc_id), record)
        batch.commit()

    print(f"  Seeded {len(records)} docs into '{collection_name}'")


def main() -> None:
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        print("[ERROR] GOOGLE_CLOUD_PROJECT is not set.")
        sys.exit(1)

    media_bucket = os.environ.get("MEDIA_BUCKET_NAME", "(not set — images resolved at read time)")
    print(f"Seeding Firestore for project '{project}'")
    print(f"Media bucket: {media_bucket}")
    print()

    db = firestore.Client(project=project)

    data_map = {
        "accommodations": load_json("accommodations.json"),
        "restaurants": load_json("restaurants.json"),
        "flights": load_json("flights.json"),
        "experiences": load_json("experiences.json"),
    }

    for collection_name in CATALOG_COLLECTIONS:
        records = data_map[collection_name]
        if not records:
            print(f"  Skipping '{collection_name}' — no data.")
            continue
        print(f"Seeding '{collection_name}' ({len(records)} records)...")
        seed_collection(db, collection_name, records)

    print()
    print("Seeding complete.")


if __name__ == "__main__":
    main()
