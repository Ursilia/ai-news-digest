import tiktoken


CHUNK_SIZE_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 100

_encoder = tiktoken.encoding_for_model("text-embedding-3-small")


def _count_tokens(text: str) -> int:
    return len(_encoder.encode(text))

def _split_into_sentences(text: str) -> list[str]:
    import re
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]

def chunk_text(text: str) -> list[str]:
    sentences = _split_into_sentences(text)

    chunks = []
    current_chunk_sentences = []
    current_chunk_tokens = 0

    for sentence in sentences:
        sentence_tokens = _count_tokens(sentence)

        if current_chunk_tokens + sentence_tokens > CHUNK_SIZE_TOKENS and current_chunk_sentences:
            chunks.append(" ".join(current_chunk_sentences))

            overlap_sentences = []
            overlap_tokens = 0
            for s in reversed(current_chunk_sentences):
                s_tokens = _count_tokens(s)
                if overlap_tokens + s_tokens > CHUNK_OVERLAP_TOKENS:
                    break
                overlap_sentences.insert(0, s)
                overlap_tokens += s_tokens

            current_chunk_sentences = overlap_sentences
            current_chunk_tokens = overlap_tokens

        current_chunk_sentences.append(sentence)
        current_chunk_tokens += sentence_tokens

    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))

    return chunks