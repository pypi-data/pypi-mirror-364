import tiktoken


def chunk_text_with_overlap(
        text: str,
        chunk_size: int = 800,
        chunk_overlap: int = 200,
        model_name: str = "text-embedding-3-large"
) -> list[str]:
    enc = tiktoken.encoding_for_model(model_name)
    tokens = enc.encode(text)
    token_count = len(tokens)

    chunk_size = chunk_size
    overlap_prev = chunk_overlap
    overlap_next = chunk_overlap

    chunks = []
    start = 0

    while start < token_count:
        current_start = start
        current_end = min(start + chunk_size, token_count)

        prev_start = max(current_start - overlap_prev, 0)
        prev_end = current_start

        next_start = current_end
        next_end = min(current_end + overlap_next, token_count)

        chunk_tokens = tokens[prev_start:prev_end] + tokens[current_start:current_end] + tokens[next_start:next_end]
        chunk_text = enc.decode(chunk_tokens)

        chunks.append(chunk_text)
        start += chunk_size

    return chunks
