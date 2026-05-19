from rag.ingest import ingest_documents


def test_ingest_function_exists():
    assert callable(ingest_documents)