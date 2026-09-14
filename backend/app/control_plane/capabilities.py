from dataclasses import dataclass, field

from app.contracts.enums import RiskLevel


@dataclass(frozen=True)
class Capability:
    name: str
    slug: str
    version: str = "1.0"
    description: str = ""
    required_models: tuple[str, ...] = ()
    required_tools: tuple[str, ...] = ()
    supported_file_types: tuple[str, ...] = ()
    risk_level: RiskLevel = RiskLevel.MEDIUM
    privacy_level: str = "STANDARD"
    enabled: bool = True
    validation_requirements: tuple[str, ...] = ()


class CapabilityRegistry:
    """Dynamic capability registry for mission execution."""

    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}
        
        # 1. Resume Intelligence
        self.register(Capability(
            name="Resume Intelligence",
            slug="resume_intelligence",
            description="Compare resume and job descriptions with deterministic matching.",
            required_models=("local-deterministic",),
            required_tools=("document_parse",),
            supported_file_types=("pdf", "docx", "txt", "md"),
            risk_level=RiskLevel.LOW,
            privacy_level="STANDARD",
            enabled=True,
            validation_requirements=("schema", "evidence"),
        ))
        
        # 2. Document Parse
        self.register(Capability(
            name="Document Parse",
            slug="document_parse",
            description="Parse uploaded text-based documents and extract structured content.",
            required_tools=("text_parser",),
            supported_file_types=("pdf", "docx", "txt", "md", "csv", "json", "xlsx"),
            risk_level=RiskLevel.LOW,
            privacy_level="STANDARD",
            enabled=True,
            validation_requirements=("schema",),
        ))
        
        # 3. Research & Evidence
        self.register(Capability(
            name="Research and Evidence",
            slug="research",
            description="Retrieve and validate evidence from external references and web searches.",
            required_tools=("web_search", "url_fetcher"),
            risk_level=RiskLevel.HIGH,
            privacy_level="STANDARD",
            enabled=True,
            validation_requirements=("source", "citation"),
        ))
        
        # 4. Data Analysis
        self.register(Capability(
            name="Data Analysis",
            slug="data_analysis",
            description="Profile, aggregate, and summarize tabular data.",
            required_tools=("csv_reader", "json_reader", "python_sandbox"),
            supported_file_types=("csv", "json", "xlsx"),
            risk_level=RiskLevel.MEDIUM,
            privacy_level="STANDARD",
            enabled=True,
            validation_requirements=("schema", "stats"),
        ))
        
        # 5. Code Analysis
        self.register(Capability(
            name="Coding Assistant",
            slug="code_analysis",
            description="Inspect code for safety, quality, and architectural issues.",
            required_tools=("code_parser", "github_client"),
            supported_file_types=("py", "js", "ts", "java", "sql", "html", "css"),
            risk_level=RiskLevel.HIGH,
            privacy_level="STANDARD",
            enabled=True,
            validation_requirements=("schema", "security"),
        ))
        
        # 6. Learning
        self.register(Capability(
            name="Learning and Study Planning",
            slug="learning",
            description="Generate personalized study plans, quizzes, and learning roadmaps.",
            risk_level=RiskLevel.LOW,
            enabled=True,
            validation_requirements=("schema",)
        ))
        
        # 7. Translation
        self.register(Capability(
            name="Translation",
            slug="translation",
            description="High-fidelity document and text translation.",
            supported_file_types=("pdf", "docx", "txt", "md"),
            risk_level=RiskLevel.LOW,
            enabled=True,
            validation_requirements=("schema",)
        ))
        
        # 8. Knowledge/RAG
        self.register(Capability(
            name="Knowledge Retrieval",
            slug="rag",
            description="Semantic search against private workspace memory and knowledge base.",
            required_tools=("vector_search",),
            risk_level=RiskLevel.LOW,
            privacy_level="STRICT",
            enabled=True,
            validation_requirements=("schema", "citation")
        ))
        
        # 9. Report Generation
        self.register(Capability(
            name="Report Generation",
            slug="report_generation",
            description="Generate complex structured reports from data and context.",
            required_tools=("pdf_writer", "docx_writer"),
            risk_level=RiskLevel.LOW,
            enabled=True,
            validation_requirements=("schema",)
        ))

    def register(self, capability: Capability) -> None:
        self._capabilities[capability.slug] = capability

    def get(self, slug: str) -> Capability:
        try:
            return self._capabilities[slug]
        except KeyError as exc:
            raise KeyError(f"CAPABILITY_NOT_FOUND:{slug}") from exc

    def list(self) -> tuple[Capability, ...]:
        return tuple(self._capabilities.values())

    def find_matching(self, required: list[str]) -> list[Capability]:
        matches: list[Capability] = []
        for slug in required:
            capability = self._capabilities.get(slug)
            if capability is not None and capability.enabled:
                matches.append(capability)
        return matches
