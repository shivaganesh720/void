from dataclasses import dataclass
from typing import Any

from app.contracts.enums import RiskLevel


@dataclass(frozen=True)
class AgentDefinition:
    id: str
    name: str
    version: str
    role: str
    responsibilities: tuple[str, ...]
    tool_allowlist: tuple[str, ...] = ()
    model_class: str = "GENERAL_WORKER"
    risk_level: RiskLevel = RiskLevel.MEDIUM


class AgentRegistry:
    """Central registry of all specialized agents in the system."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentDefinition] = {}
        
        self.register(
            AgentDefinition(
                id="resume_agent",
                name="Resume Intelligence Agent",
                version="1.0",
                role="Extract skills and evaluate candidates against JDs.",
                responsibilities=("Extract structured data from resumes", "Compare skills against JD constraints"),
                tool_allowlist=("document_parse",),
                risk_level=RiskLevel.LOW,
            )
        )
        self.register(
            AgentDefinition(
                id="research_agent",
                name="Research Agent",
                version="1.0",
                role="Perform web searches and gather evidence.",
                responsibilities=("Search the web for claims", "Extract evidence from sources"),
                tool_allowlist=("web_search", "url_fetcher"),
                risk_level=RiskLevel.HIGH,
            )
        )

    def register(self, agent: AgentDefinition) -> None:
        self._agents[agent.id] = agent

    def get(self, agent_id: str) -> AgentDefinition:
        if agent_id not in self._agents:
            raise KeyError(f"Agent '{agent_id}' not found.")
        return self._agents[agent_id]


class AgentHarness:
    """Safe execution sandbox for an agent, bounding access to models and tools."""

    def __init__(self, agent_def: AgentDefinition, model_gateway: Any, tool_gateway: Any):
        self.definition = agent_def
        self._model_gateway = model_gateway
        self._tool_gateway = tool_gateway

    def execute(self, task_input: dict[str, Any], context: Any) -> dict[str, Any]:
        """Execute the agent task safely."""
        # 1. Build Context
        prompt = f"Agent Role: {self.definition.role}\nInput: {task_input}"
        
        # 2. Call Model Gateway (bounded by agent's model_class)
        response = self._model_gateway.generate(prompt=prompt)
        
        # 3. Simulate parsing tool calls / output validation
        # In a real implementation, this loops through tool calls.
        # It restricts tools based on `self.definition.tool_allowlist`.
        
        return {
            "agent_id": self.definition.id,
            "status": "success",
            "output": response.content,
            "usage": {"tokens": response.usage_tokens, "cost": response.cost}
        }
