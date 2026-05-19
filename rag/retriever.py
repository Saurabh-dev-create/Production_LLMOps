from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()


def retrieve_context(query: str, k: int = 2) -> str:
    """
    Retrieve the most relevant runbook chunks for a query.
    """
    persist_directory = "rag/vector_store"

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    docs = vectorstore.similarity_search(query, k=k)

    if not docs:
        return "No relevant context found."

    return "\n\n".join(doc.page_content for doc in docs)


if __name__ == "__main__":
    query = "CrashLoopBackOff startup failure"
    context = retrieve_context(query)

    print("=" * 80)
    print("RETRIEVED CONTEXT")
    print("=" * 80)
    print(context)