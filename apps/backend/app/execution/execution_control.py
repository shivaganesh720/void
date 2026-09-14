import re
from dataclasses import dataclass

from app.models.enums import ExecutionMode, IntentType, RiskLevel, StrategyType
from app.schemas import MissionRequest


@dataclass(frozen=True)
class IntentAnalysis:
    intent_type: IntentType
    entities: tuple[str, ...]
    constraints: tuple[str, ...]
    required_capabilities: tuple[str, ...]
    risk_level: RiskLevel
    strategy: StrategyType
    needs_clarification: bool


class IntentGate:
    """Normalize raw user intent into a structured mission request."""

    def analyze(self, text: str, *, execution_mode: ExecutionMode = ExecutionMode.AUTO) -> MissionRequest:
        normalized = text.strip()
        if not normalized:
            raise ValueError("INTENT_EMPTY")

        lowered = normalized.casefold()
        intent_type = self._detect_intent(lowered)
        entities = self._extract_entities(normalized)
        constraints = self._extract_constraints(lowered)
        required_capabilities = self._detect_capabilities(intent_type)
        risk_level = self._detect_risk(intent_type, normalized)
        strategy = self._detect_strategy(intent_type)

        return MissionRequest(
            project_id=None,
            intent=normalized,
            intent_type=intent_type,
            execution_mode=execution_mode,
            strategy=strategy,
            entities=list(entities),
            constraints=list(constraints),
            required_capabilities=list(required_capabilities),
            approval_required=risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL},
            risk_level=risk_level,
            context={"source": "intent_gate"},
            input_files=[],
        )

    def _detect_intent(self, text: str) -> IntentType:
        if any(term in text for term in ("resume", "cv", "job description", "job posting", "jd")):
            return IntentType.RESUME_ANALYSIS
        if any(term in text for term in ("research", "find", "lookup", "sources", "evidence")):
            return IntentType.RESEARCH
        if any(term in text for term in ("analyze", "summarize", "compare", "document")) and "report" in text:
            return IntentType.REPORT_GENERATION
        if any(term in text for term in ("csv", "xlsx", "data", "chart", "statistics", "analyze data")):
            return IntentType.DATA_ANALYSIS
        if any(term in text for term in ("code", "python", "bug", "refactor", "typescript", "java")):
            return IntentType.CODE_ANALYSIS
        if any(term in text for term in ("learn", "study", "plan", "interview", "practice")):
            return IntentType.LEARNING
        if any(term in text for term in ("presentation", "slide", "deck")):
            return IntentType.PRESENTATION_GENERATION
        if any(term in text for term in ("email", "schedule", "workflow", "automation")):
            return IntentType.WORKFLOW_EXECUTION
        if any(term in text for term in ("document", "write", "draft", "generate")):
            return IntentType.DOCUMENT_GENERATION
        return IntentType.GENERAL_ASSISTANCE

    def _extract_entities(self, text: str) -> tuple[str, ...]:
        matches = re.findall(r"[A-Za-z][A-Za-z0-9_./#-]{2,}", text)
        return tuple(dict.fromkeys(matches))[:12]

    def _extract_constraints(self, text: str) -> tuple[str, ...]:
        constraints: list[str] = []
        if "fast" in text:
            constraints.append("FAST")
        if "cheap" in text or "low cost" in text:
            constraints.append("LOW_COST")
        if "private" in text or "confidential" in text:
            constraints.append("PRIVATE")
        if "approve" in text or "approval" in text:
            constraints.append("APPROVAL_REQUIRED")
        if "pdf" in text or "docx" in text or "csv" in text:
            constraints.append("FILE_INPUT")
        return tuple(constraints)

    def _detect_capabilities(self, intent_type: IntentType) -> tuple[str, ...]:
        mapping = {
            IntentType.RESUME_ANALYSIS: ("resume_intelligence", "document_parse", "evidence_validation"),
            IntentType.RESEARCH: ("research", "source_validation", "citation_collection"),
            IntentType.DATA_ANALYSIS: ("data_analysis", "statistics", "chart_generation"),
            IntentType.CODE_ANALYSIS: ("code_analysis", "security_review", "refactoring"),
            IntentType.LEARNING: ("learning_plan", "practice_generation"),
            IntentType.PRESENTATION_GENERATION: ("presentation_generation", "document_generation"),
            IntentType.DOCUMENT_GENERATION: ("document_generation", "validator"),
            IntentType.WORKFLOW_EXECUTION: ("workflow_execution", "approval_gate"),
        }
        return mapping.get(intent_type, ("general_assistance",))

    def _detect_risk(self, intent_type: IntentType, text: str) -> RiskLevel:
        if any(term in text.casefold() for term in ("secret", "private", "confidential", "pii", "delete", "execute code", "shell")):
            return RiskLevel.CRITICAL
        if intent_type in {IntentType.RESEARCH, IntentType.DATA_ANALYSIS, IntentType.CODE_ANALYSIS}:
            return RiskLevel.HIGH
        if intent_type in {IntentType.DOCUMENT_GENERATION, IntentType.PRESENTATION_GENERATION}:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _detect_strategy(self, intent_type: IntentType) -> StrategyType:
        if intent_type in {IntentType.RESUME_ANALYSIS, IntentType.RESEARCH}:
            return StrategyType.RESEARCH_AND_VALIDATE
        if intent_type in {IntentType.DATA_ANALYSIS, IntentType.CODE_ANALYSIS}:
            return StrategyType.DATA_ANALYSIS_PIPELINE
        if intent_type in {IntentType.DOCUMENT_GENERATION, IntentType.PRESENTATION_GENERATION}:
            return StrategyType.DOCUMENT_PIPELINE
        if intent_type in {IntentType.WORKFLOW_EXECUTION, IntentType.AUTOMATION}:
            return StrategyType.WORKFLOW_EXECUTION
        return StrategyType.SINGLE_MODEL
