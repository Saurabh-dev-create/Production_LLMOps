from rag.retriever import retrieve_context

def test_retrieve_context():
    assert callable(retrieve_context)