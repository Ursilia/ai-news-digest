from openai import APIError, RateLimitError, APITimeoutError
from tenacity import (
    retry,
    retry_if_exception_type,
    wait_exponential_jitter,
    stop_after_attempt,
)

from app.llm.client import client
from app.llm.prompts import load_prompt_with_vars

TIMEOUT_SECONDS = 30

def format_context(chunks: list[str]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        parts.append(f"[Source {i}]\n{chunk}")
    return "\n\n---\n\n".join(parts)

@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((APITimeoutError, RateLimitError, APIError)),
    wait=wait_exponential_jitter(initial=1, max=10, jitter=1),
    reraise=True,
)
async def answer_with_context(question: str, chunks: list[str]) -> str:
    context = format_context(chunks)
    system_prompt = load_prompt_with_vars(
        "rag",
        context=context,
        question=question,
    )
    response = await client.chat.completions.create(
        model = "gpt-4o-mini",
        timeout=TIMEOUT_SECONDS,
        temperature=0.2,
        messages=[{"role": "user", "content": system_prompt}],
    )
    return response.choices[0].message.content