from backend.chunker import chunk_text
from backend.embeddings import generate_embedding
from backend.qdrant_db import create_collection, store_chunks


with open("test_notes.txt", "r", encoding="utf-8") as file:
    text = file.read()


chunks = chunk_text(text)

embeddings = [
    generate_embedding(chunk)
    for chunk in chunks
]

create_collection()
store_chunks(chunks, embeddings)

print(f"Stored {len(chunks)} chunk(s) in Qdrant.")
print(f"Embedding dimension: {len(embeddings[0])}")
