from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ProviderType(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    TEST = "test"


class RoutingMode(str, Enum):
    AUTO = "AUTO"
    HIGH_QUALITY = "HIGH_QUALITY"
    LOW_COST = "LOW_COST"
    FAST = "FAST"
    PRIVATE = "PRIVATE"
    MANUAL = "MANUAL"


@dataclass(frozen=True)
class ProviderConfig:
    provider: ProviderType
    model_name: str
    routing_mode: RoutingMode = RoutingMode.AUTO
    api_key: str | None = None
    enabled: bool = True


@dataclass(frozen=True)
class ModelResponse:
    provider: ProviderType
    model_name: str
    content: str
    usage_tokens: int = 0
    cost: float = 0.0


class ModelGateway:
    """Provider-neutral model gateway with a deterministic local fallback."""

    def __init__(self) -> None:
        self.default_provider = ProviderConfig(
            provider=ProviderType.TEST,
            model_name="local-test-model",
            routing_mode=RoutingMode.AUTO,
            api_key=None,
            enabled=True,
        )

    def select_provider(self, *, routing_mode: RoutingMode, provider_configs: list[ProviderConfig] | None = None) -> ProviderConfig:
        configs = provider_configs or [self.default_provider]
        matching = [config for config in configs if config.enabled]
        if not matching:
            return self.default_provider

        if routing_mode is RoutingMode.LOW_COST:
            return min(matching, key=lambda c: (c.provider != ProviderType.TEST, c.model_name))
        if routing_mode is RoutingMode.HIGH_QUALITY:
            return matching[0]
        return matching[0]

    def generate(self, *, prompt: str, routing_mode: RoutingMode = RoutingMode.AUTO, provider_configs: list[ProviderConfig] | None = None) -> ModelResponse:
        provider = self.select_provider(routing_mode=routing_mode, provider_configs=provider_configs or [self.default_provider])
        summary = "Local deterministic summary: " + prompt.strip()[:120]
        return ModelResponse(
            provider=provider.provider,
            model_name=provider.model_name,
            content=summary,
            usage_tokens=max(25, len(prompt.split()) * 2),
            cost=self.estimate_cost(model_name=provider.model_name, tokens=max(25, len(prompt.split()) * 2)),
        )

    def generate_structured(self, *, prompt: str, schema: dict[str, Any], routing_mode: RoutingMode = RoutingMode.AUTO, provider_configs: list[ProviderConfig] | None = None) -> dict[str, Any]:
        provider = self.select_provider(routing_mode=routing_mode, provider_configs=provider_configs or [self.default_provider])
        properties = schema.get("properties", {})
        result: dict[str, Any] = {}
        for key, value in properties.items():
            if value.get("type") == "integer":
                result[key] = 85
            elif value.get("type") == "string":
                result[key] = f"structured result from {provider.model_name}"
            elif value.get("type") == "number":
                result[key] = 0.85
        if not result:
            result = {"status": "ok", "summary": "structured result"}
        return result

    def stream(self, *, prompt: str, routing_mode: RoutingMode = RoutingMode.AUTO, provider_configs: list[ProviderConfig] | None = None):
        return self.generate(prompt=prompt, routing_mode=routing_mode, provider_configs=provider_configs)

    def embed(self, *, text: str, provider_configs: list[ProviderConfig] | None = None) -> list[float]:
        return [0.1, 0.2, 0.3]

    def health_check(self, provider_name: str | None = None) -> bool:
        return True

    def list_models(self, provider_name: str | None = None) -> list[str]:
        return ["local-test-model"]

    def estimate_cost(self, *, model_name: str, tokens: int) -> float:
        return max(0.0001, round(tokens * 0.0003, 6))
