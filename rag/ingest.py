from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from rag.retriever import EMBEDDING_MODEL


load_dotenv()


DOCUMENTS_PATH = Path("rag/documents")
PERSIST_DIRECTORY = "rag/vector_store"


def load_runbooks() -> list[Document]:
    """
    Load Markdown runbooks directly from disk.

    This avoids the deprecated langchain-community document loader
    while preserving source metadata required by retrieval evaluation.
    """
    documents = []

    for path in sorted(
        DOCUMENTS_PATH.rglob("*.md")
    ):
        content = path.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            continue

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": str(path),
                },
            )
        )

    if not documents:
        raise ValueError(
            "No documents found in rag/documents"
        )

    return documents


def ingest_documents() -> Chroma:
    """
    Load, chunk, embed, and persist operational runbooks.
    """
    documents = load_runbooks()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    chunks = splitter.split_documents(
        documents
    )

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY,
    )

    print(
        f"Loaded {len(documents)} runbooks."
    )

    print(
        f"Ingested {len(chunks)} chunks "
        f"into {PERSIST_DIRECTORY}"
    )

    return vectorstore


if __name__ == "__main__":
    ingest_documents()
