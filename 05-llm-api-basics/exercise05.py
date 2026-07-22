import os
from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import TextBlock

load_dotenv()
client = Anthropic()


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


if __name__ == "__main__":
    print(ask("Explain async/await in python in one paragraph"))

    review = ask(
        prompt="def add(a, b):\n    return a+b",
        system="You are a terse code reviewer. Respond in max 2 sentences.",
    )
    print(review)
