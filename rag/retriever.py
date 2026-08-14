from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


load_dotenv()


PERSIST_DIRECTORY = "rag/vector_store"
EMBEDDING_MODEL = "text-embedding-3-small"



def build_retrieval_query(
    incident_data: dict,
) -> str:
    """
    Build a retrieval query from diagnostically useful incident
    evidence.

    Status, Kubernetes events, and logs carry the strongest signals
    for selecting the correct operational runbook.
    """
    parts = []

    status = incident_data.get("status")
    if status:
        parts.append(str(status))

    events = incident_data.get("events", [])

    if isinstance(events, list):
        parts.extend(
            str(event)
            for event in events
            if event
        )

    logs = incident_data.get("logs")
    if logs:
        parts.append(str(logs)[:500])

    return " ".join(parts).strip()

def get_vectorstore() -> Chroma:
    """
    Load the persisted Chroma vector store using the same embedding
    model used during ingestion.
    """
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    return Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings,
    )


def retrieve_documents(
    query: str,
    k: int = 2,
) -> list[dict]:
    """
    Retrieve documents together with source metadata and relevance
    scores for evaluation and debugging.
    """
    vectorstore = get_vectorstore()

    results = vectorstore.similarity_search_with_relevance_scores(
        query,
        k=k,
    )

    retrieved = []

    for document, score in results:
        source = document.metadata.get(
            "source",
            "unknown",
        )

        retrieved.append(
            {
                "content": document.page_content,
                "source": Path(source).name,
                "score": round(float(score), 4),
            }
        )

    return retrieved


def retrieve_context(
    query: str,
    k: int = 2,
) -> str:
    """
    Retrieve relevant runbook context.

    This preserves the existing public interface used by the RCA
    agent while the structured retrieval function supports RAG
    evaluation.
    """
    documents = retrieve_documents(
        query,
        k=k,
    )

    if not documents:
        return "No relevant context found."

    return "\n\n".join(
        document["content"]
        for document in documents
    )


if __name__ == "__main__":
    query = "CrashLoopBackOff startup failure"

    documents = retrieve_documents(
        query,
        k=2,
    )

    print("=" * 80)
    print("RETRIEVED DOCUMENTS")
    print("=" * 80)

    for index, document in enumerate(
        documents,
        start=1,
    ):
        print(
            f"\n#{index} "
            f"source={document['source']} "
            f"score={document['score']}"
        )
        print(document["content"])
