from pathlib import Path

from backend.chunker import chunk_text
from backend.embeddings import generate_embedding
from backend.qdrant_db import reset_collection, store_chunks


KNOWLEDGE_BASE_DIR = Path("knowledge_base")


def ingest_documents():

    if not KNOWLEDGE_BASE_DIR.exists():
        print("knowledge_base folder not found.")
        return

    documents = sorted(
        KNOWLEDGE_BASE_DIR.glob("*.txt")
    )

    if not documents:
        print("No .txt documents found.")
        return

    reset_collection()

    total_chunks = 0

    for document_path in documents:

        print(f"\nProcessing: {document_path.name}")

        text = document_path.read_text(
            encoding="utf-8"
        )

        chunks = chunk_text(text)

        print(f"  Created {len(chunks)} chunk(s)")

        embeddings = [
            generate_embedding(chunk)
            for chunk in chunks
        ]

        store_chunks(
            chunks,
            embeddings,
            document_path.name
        )

        total_chunks += len(chunks)

        print(f"  Stored {len(chunks)} chunk(s)")

    print("\n--------------------------------")
    print("Knowledge base ingestion complete")
    print("--------------------------------")
    print(f"Documents: {len(documents)}")
    print(f"Total chunks: {total_chunks}")


if __name__ == "__main__":
    ingest_documents()