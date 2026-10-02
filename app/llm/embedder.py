from openai import APIError, RateLimitError, APITimeoutError
from tenacity import (
    retry,
    wait_exponential_jitter,
    stop_after_attempt,
    retry_if_exception_type,
)

from app.llm.client import client


EMBEDDING_MODEL = "text-embedding-3-small"
TIMEOUT_SECONDS = 30


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10, jitter=1),
    retry=retry_if_exception_type((APIError, RateLimitError, APITimeoutError)),
    reraise=True,
)
async def embed_texts(texts: list[str]) -> list[list[float]]:
    response = await client.embeddings.create(
        model=EMBEDDING_MODEL,
        timeout=TIMEOUT_SECONDS,
        input=texts,
    )
    return [item.embedding for item in response.data]