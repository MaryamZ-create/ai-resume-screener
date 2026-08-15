## Week 3 - AI Study Companion

### Features

- Upload PDF/TXT study documents
- Split documents into meaningful chunks
- Generate free local embeddings using all-MiniLM-L6-v2
- Store 384-dimensional embeddings in Qdrant
- Retrieve relevant study chunks using semantic search
- Generate a basic study plan from retrieved content

### Qdrant Setup

Run Qdrant with Docker:

docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant

Qdrant dashboard:

http://localhost:6333/dashboard

### Run Backend

uvicorn backend.main:app --reload

API documentation:

http://localhost:8000/docs

### Week 3 Flow

Document Upload → Chunking → Embeddings → Qdrant → Retrieval → Study Plan
