from fastmcp import FastMCP

from backend.embeddings import generate_embedding
from backend.qdrant_db import search_chunks, client, COLLECTION_NAME


mcp = FastMCP("Personal Knowledge Base")


@mcp.tool
def search_knowledge(query: str) -> list:
    """
    Search the personal knowledge base using semantic search.

    Args:
        query: The question or topic to search for.

    Returns:
        Relevant documents ranked by similarity.
    """

    query_embedding = generate_embedding(query)

    results = search_chunks(
        query_embedding,
        limit=5
    )

    return results


@mcp.tool
def list_documents() -> list:
    """
    List documents currently stored in the personal knowledge base.

    Returns:
        A list of stored document chunks.
    """

    points, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=100,
        with_payload=True,
        with_vectors=False
    )

    return [
        {
            "chunk_id": point.payload.get("chunk_id"),
            "text": point.payload.get("text", "")
        }
        for point in points
    ]


@mcp.tool
def get_document(chunk_id: int) -> dict:
    """
    Retrieve a specific document chunk by its ID.

    Args:
        chunk_id: The ID of the document chunk.

    Returns:
        The requested document chunk.
    """

    result = client.retrieve(
        collection_name=COLLECTION_NAME,
        ids=[chunk_id],
        with_payload=True,
        with_vectors=False
    )

    if not result:
        return {
            "error": "Document not found",
            "chunk_id": chunk_id
        }

    payload = result[0].payload or {}

    return {
        "chunk_id": chunk_id,
        "text": payload.get("text", "")
    }


if __name__ == "__main__":
    mcp.run()
