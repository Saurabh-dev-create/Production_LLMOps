from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from rag.retriever import EMBEDDING_MODEL
from langchain_chroma import Chroma

load_dotenv()


def ingest_documents():
    documents_path = Path("rag/documents")
    persist_directory = "rag/vector_store"

    # Load all Markdown documents
    loader = DirectoryLoader(
        str(documents_path),
        glob="**/*.md"
    )
    documents = loader.load()

    if not documents:
        raise ValueError("No documents found in rag/documents")

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)

    # Create embeddings
    embeddings = OpenAIEmbeddings(
           model=EMBEDDING_MODEL
            )

    # Store in Chroma
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    print(f"Ingested {len(chunks)} chunks into {persist_directory}")

    return vectorstore


if __name__ == "__main__":
    ingest_documents()
