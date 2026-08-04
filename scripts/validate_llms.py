#!/usr/bin/env python3
"""Validate that the configured real-LLM adapters can generate a response."""

import os

from eads.core.adapters import AnthropicLLM, OllamaLLM, OpenAILLM

PROMPT = "What is 2 + 2? Answer with only the number."


def _validate_openai() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        print("[OpenAI] OPENAI_API_KEY not set; skipping.")
        return
    try:
        response = OpenAILLM().generate(PROMPT)
        print(f"[OpenAI] {response}")
    except Exception as exc:
        print(f"[OpenAI] error: {exc}")


def _validate_anthropic() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("[Anthropic] ANTHROPIC_API_KEY not set; skipping.")
        return
    try:
        response = AnthropicLLM().generate(PROMPT)
        print(f"[Anthropic] {response}")
    except Exception as exc:
        print(f"[Anthropic] error: {exc}")


def _validate_ollama() -> None:
    host = os.getenv("OLLAMA_HOST")
    try:
        response = OllamaLLM(host=host).generate(PROMPT)
        print(f"[Ollama] {response}")
    except Exception as exc:
        print(f"[Ollama] error: {exc}")


def main() -> None:
    print("Validating real-LLM adapters...")
    _validate_openai()
    _validate_anthropic()
    _validate_ollama()


if __name__ == "__main__":
    main()
