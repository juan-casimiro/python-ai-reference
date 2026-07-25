# TODO 1: A FastAPI app with one endpoint: POST /summarize
#   - Accepts a Pydantic model with a single field: text (str)
#   - Calls Claude (reuse your ask() function from Module 5, or inline it)
#     with a system prompt instructing it to summarize concisely
#   - Returns a Pydantic response model with a single field: summary (str)

# TODO 2: Add basic validation - if `text` is empty or under ~20 characters,
# raise an HTTPException (400) rather than wasting an API call

# TODO 3: Test it via curl, REST Client, or /docs with a real paragraph of text

import asyncio
import io
from dotenv import load_dotenv
from anthropic.types import TextBlock
from anthropic import AsyncAnthropic
from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel, Field
from pypdf import PdfReader

MAX_BYTES = 10 * 1024 * 1024  # 10 MB
MIN_BYTES = 100

MIN_TEXT_CHARS = 100
MAX_TEXT_CHARS = 100_000  # ~100 pages

DEF_CHUNK_TEXT_SIZE = 8_000  # ~4-5 pages per chunk

app = FastAPI()

load_dotenv()
client = AsyncAnthropic()


class SummaryRequest(BaseModel):
    text: str = Field(min_length=MIN_TEXT_CHARS, max_length=MAX_TEXT_CHARS)


class SummaryResponse(BaseModel):
    summary: str


def validate_content_size(size: int):
    if size > MAX_BYTES:
        raise HTTPException(413, "File too large")
    if size < MIN_BYTES:
        raise HTTPException(400, "File too small")


def validate_content_text_size(size: int):
    if size > MAX_TEXT_CHARS:
        raise HTTPException(413, "Content too large")
    if size < MIN_TEXT_CHARS:
        raise HTTPException(400, "Content too small")


def chunk_text(text: str, chunk_size: int = DEF_CHUNK_TEXT_SIZE) -> list[str]:
    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        if len(para) > chunk_size:
            if current:
                chunks.append(current.strip())
                current = ""
            for i in range(0, len(para), chunk_size):
                chunks.append(para[i : i + chunk_size])
            continue

        if current and len(current) + len(para) > chunk_size:
            chunks.append(current.strip())
            current = para
        else:
            current += ("\n\n" if current else "") + para

    if current:
        chunks.append(current.strip())

    return chunks


async def ask_in_batches(prompt: str, system: str | None = None) -> str:
    chunks = chunk_text(prompt)

    print("number of chunks: " + str(len(chunks)))
    summaries_futures = []
    for chunk in chunks:
        summaries_futures.append(ask(chunk, system))

    summaries = await asyncio.gather(*summaries_futures)

    summary = " ".join(summaries)
    print(summary)
    return await ask(
        summary,
        "Combine these partial summaries into one concise, coherent summary.",
    )


async def ask(prompt: str, system: str | None = None) -> str:
    kwargs = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system is not None:
        kwargs["system"] = system

    response = await client.messages.create(**kwargs)

    match response.content[0]:
        case TextBlock(text=text):
            return text
        case _:
            raise ValueError(f"Unexpected block type: {response.content[0]}")


@app.post("/summarize")
async def post_summary(summary_request: SummaryRequest) -> SummaryResponse:

    summary = await ask_in_batches(
        prompt=summary_request.text,
        system="Summarize the following text concisely, in 2-3 sentences.",
    )

    return SummaryResponse(summary=summary)


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    if file.content_type not in {"application/pdf", "text/plain"}:
        raise HTTPException(415, "Unsupported file type")

    if file.size is not None:
        validate_content_size(file.size)

    contents = await file.read()
    validate_content_size(len(contents))

    if file.content_type == "application/pdf":
        reader = PdfReader(io.BytesIO(contents))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        text = contents.decode("utf-8")

    validate_content_text_size(len(text))

    summary = await ask_in_batches(
        prompt=text,
        system="Summarize the following text concisely, in 2-3 sentences.",
    )

    return SummaryResponse(summary=summary)
