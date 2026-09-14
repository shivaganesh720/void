from app.integrations.providers import ModelGateway, ProviderConfig, ProviderType, RoutingMode


def test_model_gateway_uses_local_fallback_when_unconfigured() -> None:
    gateway = ModelGateway()
    response = gateway.generate(prompt="Summarize the project status", routing_mode=RoutingMode.AUTO)
    assert response.provider == ProviderType.TEST
    assert "summary" in response.content.lower()


def test_model_gateway_handles_structured_output() -> None:
    gateway = ModelGateway()
    payload = gateway.generate_structured(
        prompt="Return a JSON object with keys score and summary",
        schema={"type": "object", "properties": {"score": {"type": "integer"}, "summary": {"type": "string"}}},
        routing_mode=RoutingMode.HIGH_QUALITY,
    )
    assert payload["score"] >= 0
    assert isinstance(payload["summary"], str)


def test_provider_health_and_cost_estimation() -> None:
    gateway = ModelGateway()
    assert gateway.health_check("local") is True
    estimate = gateway.estimate_cost(model_name="local-test-model", tokens=250)
    assert estimate > 0


def test_routing_mode_selection_prefers_fast_for_low_cost() -> None:
    config = ProviderConfig(provider=ProviderType.TEST, model_name="local-test-model", routing_mode=RoutingMode.LOW_COST)
    selected = ModelGateway().select_provider(routing_mode=RoutingMode.LOW_COST, provider_configs=[config])
    assert selected.provider is ProviderType.TEST
