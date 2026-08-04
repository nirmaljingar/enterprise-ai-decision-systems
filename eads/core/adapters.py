import random
from abc import ABC, abstractmethod
from typing import Any


class LLMBackend(ABC):
    supports_seed: bool = True
    """Whether ``generate`` can honor ``seed``.

    Backends that cannot are still usable, but runs against them are not reproducible; the
    pipeline records this on the trace instead of implying determinism it cannot provide.
    """

    @abstractmethod
    def generate(self, prompt: str, seed: int | None = None) -> str:
        ...


class FakeLLM(LLMBackend):
    """Deterministic placeholder LLM for offline reproducibility."""

    def generate(self, prompt: str, seed: int | None = None) -> str:
        rng = random.Random(seed if seed is not None else 42)
        lower = prompt.lower()
        if "order" in lower:
            return f"order_quantity={rng.randint(100, 200)}"
        if "route" in lower:
            return f"route={rng.choice(['A', 'B', 'C'])}"
        if "disruption" in lower or "risk" in lower:
            return "mitigation=hold_order"
        return f"decision=approved-{rng.randint(1, 1000)}"


class OpenAILLM(LLMBackend):
    """OpenAI chat completion adapter (requires the 'openai' extra)."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self._client: Any | None = None

    def _get_client(self) -> Any:
        try:
            import openai
        except ImportError as exc:
            raise ImportError(
                "OpenAI extra not installed. Run `pip install -e '.[openai]'`."
            ) from exc
        if self._client is None:
            kwargs = {}
            if self.api_key:
                kwargs["api_key"] = self.api_key
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = openai.OpenAI(**kwargs)
        return self._client

    def generate(self, prompt: str, seed: int | None = None) -> str:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if seed is not None:
            kwargs["seed"] = seed
        response = self._get_client().chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""


class AnthropicLLM(LLMBackend):
    """Anthropic Messages API adapter (requires the 'anthropic' extra)."""

    supports_seed = False

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self._client: Any | None = None

    def _get_client(self) -> Any:
        try:
            import anthropic
        except ImportError as exc:
            raise ImportError(
                "Anthropic extra not installed. Run `pip install -e '.[anthropic]'`."
            ) from exc
        if self._client is None:
            kwargs = {}
            if self.api_key:
                kwargs["api_key"] = self.api_key
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = anthropic.Anthropic(**kwargs)
        return self._client

    def generate(self, prompt: str, seed: int | None = None) -> str:
        # Anthropic API does not expose a deterministic seed parameter.
        del seed
        response = self._get_client().messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text or ""


class OllamaLLM(LLMBackend):
    """Ollama local generation adapter (requires the 'ollama' extra)."""

    def __init__(self, model: str = "llama3", host: str | None = None):
        self.model = model
        self.host = host

    def generate(self, prompt: str, seed: int | None = None) -> str:
        try:
            import ollama
        except ImportError as exc:
            raise ImportError(
                "Ollama extra not installed. Run `pip install -e '.[ollama]'`."
            ) from exc
        if self.host:
            client = ollama.Client(host=self.host)
        else:
            client = ollama
        options = {}
        if seed is not None:
            options["seed"] = seed
        response = client.generate(
            model=self.model,
            prompt=prompt,
            options=options or None,
        )
        return response["response"] or ""
