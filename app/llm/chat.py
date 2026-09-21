from openai import APIError, RateLimitError, APITimeoutError
from tenacity import (retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type,)

from app.llm.client import client
from app.schemas import ChatMessage
from typing import AsyncGenerator
from app.llm.prompts import load_prompt



TIMEOUT_SECONDS = 30

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10, jitter=1),
    retry=retry_if_exception_type((RateLimitError, APITimeoutError, APIError)),
    reraise=True,
    )
async def ask_question(question: str, 
                       history: list[ChatMessage],) -> str:
    messages = [{"role": "system", "content": load_prompt("chat")}]

    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": question})

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        timeout=TIMEOUT_SECONDS,
    )
    return response.choices[0].message.content



@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10, jitter=1),
    retry=retry_if_exception_type((RateLimitError, APITimeoutError, APIError)),
    reraise=True,
)
async def ask_question_stream(question: str, history: list[ChatMessage],) -> AsyncGenerator[str, None]:
    messages = [{"role": "system", "content": load_prompt("chat")}]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": question})

    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        timeout=TIMEOUT_SECONDS,
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta is not None:
            yield delta