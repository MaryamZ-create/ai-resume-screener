from backend.embeddings import generate_embedding
from backend.qdrant_db import search_chunks


TEST_QUERIES = [
    {
        "query": "Which protocol provides reliable and connection-oriented communication?",
        "expected_source": "tcp_udp.txt"
    },
    {
        "query": "Which protocol is connectionless and has lower overhead?",
        "expected_source": "tcp_udp.txt"
    },
    {
        "query": "What is the seven-layer model used to understand network communication?",
        "expected_source": "osi_model.txt"
    },
    {
        "query": "Which OSI layer provides end-to-end communication?",
        "expected_source": "osi_model.txt"
    },
    {
        "query": "What routing protocol uses the Shortest Path First algorithm?",
        "expected_source": "ospf.txt"
    },
    {
        "query": "What is Area 0 in OSPF?",
        "expected_source": "ospf.txt"
    },
    {
        "query": "What does a subnet mask determine?",
        "expected_source": "ip_addressing.txt"
    },
    {
        "query": "What are the private IPv4 address ranges?",
        "expected_source": "ip_addressing.txt"
    },
    {
        "query": "What is a VLAN used for?",
        "expected_source": "vlans.txt"
    },
    {
        "query": "What is an access port and what is a trunk port?",
        "expected_source": "vlans.txt"
    }
]


def evaluate():
    print("=" * 60)
    print("RETRIEVAL EVALUATION")
    print("=" * 60)

    correct = 0

    for i, item in enumerate(TEST_QUERIES, start=1):

        query = item["query"]
        expected_source = item["expected_source"]

        print(f"\nQuery {i}: {query}")
        print(f"Expected: {expected_source}")

        query_embedding = generate_embedding(query)

        results = search_chunks(
            query_embedding,
            limit=5,
            score_threshold=0.0
        )

        retrieved_sources = [
            result.get("source", "unknown")
            for result in results
        ]

        print(f"Retrieved: {retrieved_sources}")

        if expected_source in retrieved_sources:
            print("Result: PASS")
            correct += 1
        else:
            print("Result: FAIL")

    total = len(TEST_QUERIES)
    precision = (correct / total) * 100

    print("\n" + "=" * 60)
    print("EVALUATION RESULT")
    print("=" * 60)
    print(f"Correct queries: {correct}/{total}")
    print(f"Retrieval precision: {precision:.2f}%")


if __name__ == "__main__":
    evaluate()
