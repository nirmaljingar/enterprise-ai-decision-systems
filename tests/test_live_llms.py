import importlib.util
import os


def test_openai_adapter_if_key_present():
    if not os.getenv("OPENAI_API_KEY") or not importlib.util.find_spec("openai"):
        return
    from eads.core.adapters import OpenAILLM

    response = OpenAILLM().generate("What is 2+2? Answer with one digit.")
    assert isinstance(response, str)
    assert len(response) > 0


def test_anthropic_adapter_if_key_present():
    if not os.getenv("ANTHROPIC_API_KEY") or not importlib.util.find_spec("anthropic"):
        return
    from eads.core.adapters import AnthropicLLM

    response = AnthropicLLM().generate("What is 2+2? Answer with one digit.")
    assert isinstance(response, str)
    assert len(response) > 0


def test_ollama_adapter_if_available():
    if not importlib.util.find_spec("ollama"):
        return
    from eads.core.adapters import OllamaLLM

    try:
        response = OllamaLLM().generate("What is 2+2? Answer with one digit.")
    except Exception:  # noqa: BLE001
        # Ollama server may not be running locally.
        return
    assert isinstance(response, str)
