from fastmcp import FastMCP

from backend.embeddings import generate_embedding
from backend.qdrant_db import search_chunks


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


if __name__ == "__main__":
    mcp.run()
