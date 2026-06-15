import os
from google.cloud import firestore

_client: firestore.Client | None = None


def get_client() -> firestore.Client:
    global _client
    if _client is None:
        _client = firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT"))
    return _client
