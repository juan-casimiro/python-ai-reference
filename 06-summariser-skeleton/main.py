# TODO 1: A FastAPI app with one endpoint: POST /summarize
#   - Accepts a Pydantic model with a single field: text (str)
#   - Calls Claude (reuse your ask() function from Module 5, or inline it)
#     with a system prompt instructing it to summarize concisely
#   - Returns a Pydantic response model with a single field: summary (str)

# TODO 2: Add basic validation - if `text` is empty or under ~20 characters,
# raise an HTTPException (400) rather than wasting an API call

# TODO 3: Test it via curl, REST Client, or /docs with a real paragraph of text

import os
from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import TextBlock
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

load_dotenv()
client = Anthropic()


class SummaryRequest(BaseModel):
    text: str = Field(min_length=20)


class SummaryResponse(BaseModel):
    summary: str


def ask(prompt: str, system: str | None = None) -> str:
    kwargs = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 200,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system is not None:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)

    match response.content[0]:
        case TextBlock(text=text):
            return text
        case _:
            raise ValueError(f"Unexpected block type: {response.content[0]}")


@app.post("/summarize")
def post_summary(summary_request: SummaryRequest) -> SummaryResponse:

    summary = ask(
        prompt=summary_request.text,
        system="Summarize the following text concisely, in 2-3 sentences.",
    )
    return SummaryResponse(summary=summary)
