from unittest.mock import MagicMock

from rag import retriever


def test_retrieve_documents_returns_source_and_score(
    monkeypatch,
):
    document = MagicMock()
    document.page_content = "CrashLoopBackOff runbook"
    document.metadata = {
        "source": "rag/documents/crashloop_runbook.md"
    }

    vectorstore = MagicMock()
    vectorstore.similarity_search_with_relevance_scores.return_value = [
        (document, 0.91)
    ]

    monkeypatch.setattr(
        retriever,
        "get_vectorstore",
        lambda: vectorstore,
    )

    results = retriever.retrieve_documents(
        "CrashLoopBackOff",
        k=2,
    )

    assert len(results) == 1
    assert (
        results[0]["source"]
        == "crashloop_runbook.md"
    )
    assert results[0]["score"] == 0.91
