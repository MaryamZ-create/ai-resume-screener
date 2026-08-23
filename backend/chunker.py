def chunk_text(text, max_words=300):
    paragraphs = text.split("\n")

    chunks = []
    current_chunk = []
    word_count = 0

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        if not paragraph:
            continue

        paragraph_words = paragraph.split()

        if word_count + len(paragraph_words) > max_words and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            word_count = 0

        current_chunk.append(paragraph)
        word_count += len(paragraph_words)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


if __name__ == "__main__":
    text = """TCP is a reliable, connection-oriented protocol.

UDP is a connectionless protocol.

TCP uses acknowledgements to provide reliable delivery."""

    chunks = chunk_text(text)

    for i, chunk in enumerate(chunks, 1):
        print(f"Chunk {i}:")
        print(chunk)
        print()
