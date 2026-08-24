from fastmcp import FastMCP

from backend.embeddings import generate_embedding
from backend.qdrant_db import (
    search_chunks,
    list_chunks,
    get_chunk
)


mcp = FastMCP("Personal Knowledge Base")


@mcp.tool
def search_knowledge(query: str) -> list:
    """
    Search the personal knowledge base using semantic search.

    Returns ranked results with similarity scores and source citations.
    If no result meets the confidence threshold, an empty list is returned.
    """

    query_embedding = generate_embedding(query)

    results = search_chunks(
        query_embedding,
        limit=5,
        score_threshold=0.45
    )

    if not results:
        return [
            {
                "message": "No confident match found.",
                "query": query
            }
        ]

    return results


@mcp.tool
def list_documents() -> list:
    """
    List all documents currently stored in the personal knowledge base.

    Each result includes the document source, chunk ID, and text.
    """

    return list_chunks()


@mcp.tool
def get_document(chunk_id: int) -> dict:
    """
    Retrieve a specific document chunk by its ID.

    Returns the chunk text and its original source file.
    """

    result = get_chunk(chunk_id)

    if result is None:
        return {
            "error": "Document not found",
            "chunk_id": chunk_id
        }

    return result


if __name__ == "__main__":
    mcp.run()