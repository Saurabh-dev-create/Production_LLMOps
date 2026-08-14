from langchain_core.documents import Document

from rag import ingest


def test_load_runbooks_returns_documents(
    tmp_path,
    monkeypatch,
):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    runbook = (
        documents_dir
        / "example_runbook.md"
    )

    runbook.write_text(
        "# Example Runbook\n\n"
        "Troubleshooting content.",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        ingest,
        "DOCUMENTS_PATH",
        documents_dir,
    )

    documents = ingest.load_runbooks()

    assert len(documents) == 1

    assert isinstance(
        documents[0],
        Document,
    )

    assert (
        "Troubleshooting content"
        in documents[0].page_content
    )

    assert (
        documents[0].metadata["source"]
        == str(runbook)
    )


def test_load_runbooks_rejects_empty_directory(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        ingest,
        "DOCUMENTS_PATH",
        tmp_path,
    )

    try:
        ingest.load_runbooks()
    except ValueError as exc:
        assert (
            "No documents found"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )
