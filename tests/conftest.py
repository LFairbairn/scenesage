import pytest
import chromadb


@pytest.fixture
def chroma_client():
    client = chromadb.EphemeralClient()
    yield client
    # EphemeralClient shares a global in-memory store, so we explicitly delete
    # the collection after each test to prevent data leaking into the next test.
    try:
        client.delete_collection("scripts")
    except Exception:
        pass
