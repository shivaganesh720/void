from dataclasses import dataclass
from typing import Any

from app.models.enums import RiskLevel


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
    identity: str = "VOID governed agent cell"
    objective: str = "Complete its assigned typed task within policy bounds."
    non_responsibilities: tuple[str, ...] = ("Authorize itself", "Call unallowlisted tools", "Override policy")
    prompt_version: str = "1.0"
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    budget_tokens: int = 8_000
    timeout_seconds: int = 300
    retry_limit: int = 2
    privacy_level: str = "STANDARD"
    enabled: bool = True


class AgentRegistry:
    """Central registry of all specialized agents in the system."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentDefinition] = {}
        
        self.register(
            AgentDefinition(
                id="manager_agent",
                name="Manager / Supervisor Agent",
                version="1.0",
                role="Coordinate child agents, aggregate results, and ensure overall task success.",
                responsibilities=("Orchestrate parallel workflows", "Validate combined agent outputs", "Handle task retries"),
                tool_allowlist=(),
                risk_level=RiskLevel.MEDIUM,
            )
        )
        # Every cell is registered centrally.  The manager coordinates work
        # through typed task state; these descriptors are not independently
        # executable endpoints.
        for agent in (
            AgentDefinition("planner_agent", "Planner Agent", "1.0", "Turn normalized intent into a bounded task graph.", ("Create execution blueprints", "Identify dependencies")),
            AgentDefinition("learning_agent", "Learning Agent", "1.0", "Build sequenced learning roadmaps.", ("Set milestones", "Recommend practice"), risk_level=RiskLevel.LOW),
            AgentDefinition("document_agent", "Document Agent", "1.0", "Parse and transform governed documents.", ("Extract structure", "Draft document content"), tool_allowlist=("document_parse",)),
            AgentDefinition("critic_agent", "Critic Agent", "1.0", "Challenge output quality before completion.", ("Find unsupported claims", "Identify missing constraints"), risk_level=RiskLevel.LOW),
            AgentDefinition("evidence_agent", "Evidence Agent", "1.0", "Trace claims to approved sources.", ("Collect citations", "Score evidence"), tool_allowlist=("web_search", "document_parse"), risk_level=RiskLevel.HIGH),
            AgentDefinition("export_agent", "Export Agent", "1.0", "Create governed output artifacts.", ("Generate export manifests", "Hash artifacts"), tool_allowlist=("pdf_writer", "docx_writer"), risk_level=RiskLevel.LOW),
        ):
            self.register(agent)
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
                responsibilities=("Search the web for claims", "Extract evidence from sources", "Ensure source freshness"),
                tool_allowlist=("web_search", "url_fetcher"),
                risk_level=RiskLevel.HIGH,
            )
        )
        self.register(
            AgentDefinition(
                id="data_analyst_agent",
                name="Data Analyst Agent",
                version="1.0",
                role="Profile data, execute aggregations, and detect outliers.",
                responsibilities=("Process CSV/JSON data", "Perform pandas aggregations", "Generate summary charts"),
                tool_allowlist=("csv_reader", "json_reader", "python_sandbox"),
                risk_level=RiskLevel.MEDIUM,
            )
        )
        self.register(
            AgentDefinition(
                id="coding_agent",
                name="Coding Agent",
                version="1.0",
                role="Review code, generate tests, and suggest refactors safely.",
                responsibilities=("Analyze repositories", "Suggest code diffs", "Generate unit tests"),
                tool_allowlist=("code_parser", "github_client"),
                risk_level=RiskLevel.HIGH,
            )
        )
        self.register(
            AgentDefinition(
                id="validator_agent",
                name="Validator Agent",
                version="1.0",
                role="Critique and validate other agents' output against requirements.",
                responsibilities=("Check for hallucinations", "Verify constraints", "Output quality scoring"),
                tool_allowlist=(),
                risk_level=RiskLevel.LOW,
            )
        )
        self.register(
            AgentDefinition(
                id="report_agent",
                name="Report Agent",
                version="1.0",
                role="Synthesize multiple artifacts into final professional reports.",
                responsibilities=("Format markdown", "Generate PDFs", "Generate Docx"),
                tool_allowlist=("pdf_writer", "docx_writer"),
                risk_level=RiskLevel.LOW,
            )
        )

    def register(self, agent: AgentDefinition) -> None:
        self._agents[agent.id] = agent

    def get(self, agent_id: str) -> AgentDefinition:
        if agent_id not in self._agents:
            raise KeyError(f"Agent '{agent_id}' not found.")
        return self._agents[agent_id]

    def list(self) -> tuple[AgentDefinition, ...]:
        return tuple(self._agents.values())


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
