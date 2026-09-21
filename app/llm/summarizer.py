from app.llm.client import client
from app.llm.prompts import load_prompt

from openai import APIError, RateLimitError, APITimeoutError
from tenacity import (retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type,)


TIMEOUT_SECONDS = 30

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10, jitter=1),
    retry=retry_if_exception_type((RateLimitError, APITimeoutError, APIError)),
    reraise=True,
)
async def summarize_text(text: str) -> str:
    response = await client.chat.completions.create(
        model= "gpt-4o-mini",
        temperature=0.3,
        max_tokens=1000,
        timeout=TIMEOUT_SECONDS,
        messages=[
            {"role": "system", "content": load_prompt("summarize")},
            {"role": "user", "content": text},
        ]
    )
    return response.choices[0].message.content

