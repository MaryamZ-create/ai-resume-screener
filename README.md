# Personal Knowledge-Base MCP Server

A semantic-search MCP server built with FastMCP and Qdrant. It allows an MCP-compatible client to search a personal networking knowledge base by meaning and receive ranked results with source citations.

## Problem

Keyword search can miss relevant information when the query uses different wording from the original document.

This project solves that problem using semantic embeddings and vector search. Networking study notes are converted into embeddings and stored in Qdrant. An MCP server exposes the search functionality as reusable tools.

## Architecture

```text
MCP Client
    |
    v
FastMCP Server
    |
    +-------------------+
    |                   |
    v                   v
search_knowledge   list_documents
    |
    v
Query Embedding
    |
    v
Qdrant Vector Database
    |
    v
Semantic Search
    |
    v
Ranked Results + Source Citation