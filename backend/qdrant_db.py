
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct


client = QdrantClient(
    url="http://localhost:6333"
)

COLLECTION_NAME = "study_documents"
VECTOR_SIZE = 384


def create_collection():
    collections = client.get_collections().collections

    if COLLECTION_NAME not in [c.name for c in collections]:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )


def store_chunks(chunks, embeddings, source):
    points = []

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):

        points.append(
            PointStruct(
                id=store_chunks.next_id,
                vector=embedding,
                payload={
                    "text": chunk,
                    "chunk_id": store_chunks.next_id,
                    "source": source
                }
            )
        )

        store_chunks.next_id += 1

    if points:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )


store_chunks.next_id = 0


def reset_collection():
    if COLLECTION_NAME in [
        c.name for c in client.get_collections().collections
    ]:
        client.delete_collection(
            collection_name=COLLECTION_NAME
        )

    create_collection()

    store_chunks.next_id = 0


def search_chunks(query_embedding, limit=3, score_threshold=0.40):

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit,
        score_threshold=score_threshold
    )

    return [
        {
            "score": result.score,
            "text": result.payload.get("text", ""),
            "chunk_id": result.payload.get("chunk_id"),
            "source": result.payload.get("source", "unknown")
        }
        for result in results.points
    ]


def list_chunks():

    response = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=100,
        with_payload=True,
        with_vectors=False
    )

    points = response[0]

    return [
        {
            "chunk_id": point.payload.get("chunk_id"),
            "source": point.payload.get("source", "unknown"),
            "text": point.payload.get("text", "")
        }
        for point in points
    ]


def get_chunk(chunk_id):

    results = client.retrieve(
        collection_name=COLLECTION_NAME,
        ids=[chunk_id],
        with_payload=True,
        with_vectors=False
    )

    if not results:
        return None

    payload = results[0].payload or {}

    return {
        "chunk_id": payload.get("chunk_id"),
        "source": payload.get("source", "unknown"),
        "text": payload.get("text", "")
    }

