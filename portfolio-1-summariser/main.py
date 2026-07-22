# TODO 1: A FastAPI app with one endpoint: POST /summarize
#   - Accepts a Pydantic model with a single field: text (str)
#   - Calls Claude (reuse your ask() function from Module 5, or inline it)
#     with a system prompt instructing it to summarize concisely
#   - Returns a Pydantic response model with a single field: summary (str)

# TODO 2: Add basic validation - if `text` is empty or under ~20 characters,
# raise an HTTPException (400) rather than wasting an API call

# TODO 3: Test it via curl, REST Client, or /docs with a real paragraph of text

import io
from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import TextBlock
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from pypdf import PdfReader

MAX_BYTES = 20 * 1024 * 1024
MIN_BYTES = 100

MAX_TEXT_CHARS = 15_000

app = FastAPI()

load_dotenv()
client = Anthropic()


class SummaryRequest(BaseModel):
    text: str = Field(min_length=20)


class SummaryResponse(BaseModel):
    summary: str


def validate_content_size(size: int):
    if size > MAX_BYTES:
        raise HTTPException(413, "File too large")
    if size < MIN_BYTES:
        raise HTTPException(400, "File too small")


def validate_prompt_length(text: str):
    if len(text) < MIN_BYTES:
        raise HTTPException(400, "Extracted text too short")
    if len(text) > MAX_TEXT_CHARS:
        raise HTTPException(413, "Extracted text too long")


def ask(prompt: str, system: str | None = None) -> str:
    validate_prompt_length(prompt)
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

    summary = ask(
        prompt=text,
        system="Summarize the following text concisely, in 2-3 sentences.",
    )

    return SummaryResponse(summary=summary)
