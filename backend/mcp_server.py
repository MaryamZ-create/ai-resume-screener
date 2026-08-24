import sys
from pathlib import Path

# Make the project root available when FastMCP loads this file directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastmcp import FastMCP

from backend.embeddings import generate_embedding
from backend.qdrant_db import (
    search_chunks,
    list_chunks,
    get_chunk,
)

# Create MCP server
mcp = FastMCP("Personal Knowledge Base")


@mcp.tool
def search_knowledge(query: str) -> list:
    """
    Search the personal knowledge base using semantic search.

    Returns ranked results with similarity scores and source citations.
    """

    query_embedding = generate_embedding(query)

    results = search_chunks(
        query_embedding,
        limit=5,
        score_threshold=0.45,
    )

    if not results:
        return [
            {
                "message": "No confident match found.",
                "query": query,
            }
        ]

    return results


@mcp.tool
def list_documents() -> list:
    """
    List all documents stored in the personal knowledge base.
    """

    return list_chunks()


@mcp.tool
def get_document(chunk_id: int) -> dict:
    """
    Retrieve a specific knowledge-base chunk by its ID.
    """

    result = get_chunk(chunk_id)

    if result is None:
        return {
            "error": "Document not found",
            "chunk_id": chunk_id,
        }

    return result


if __name__ == "__main__":
    mcp.run()