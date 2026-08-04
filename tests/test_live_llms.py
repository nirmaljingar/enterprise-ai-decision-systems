"""Live LLM adapter checks.

These hit real providers, so each is skipped -- visibly, via pytest -- unless both the
optional dependency and the credential are present.
"""

import importlib.util
import os

import pytest


def _installed(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


@pytest.mark.skipif(
    not (_installed("openai") and os.getenv("OPENAI_API_KEY")),
    reason="requires the 'openai' extra and OPENAI_API_KEY",
)
def test_openai_adapter_if_key_present():
    from eads.core.adapters import OpenAILLM

    response = OpenAILLM().generate("What is 2+2? Answer with one digit.")
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.skipif(
    not (_installed("anthropic") and os.getenv("ANTHROPIC_API_KEY")),
    reason="requires the 'anthropic' extra and ANTHROPIC_API_KEY",
)
def test_anthropic_adapter_if_key_present():
    from eads.core.adapters import AnthropicLLM

    response = AnthropicLLM().generate("What is 2+2? Answer with one digit.")
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.skipif(not _installed("ollama"), reason="requires the 'ollama' extra")
def test_ollama_adapter_if_available():
    from eads.core.adapters import OllamaLLM

    try:
        response = OllamaLLM().generate("What is 2+2? Answer with one digit.")
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"local Ollama server unavailable: {exc}")
    assert isinstance(response, str)
