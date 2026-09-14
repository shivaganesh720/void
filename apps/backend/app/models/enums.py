from enum import StrEnum


class ExecutionMode(StrEnum):
    AUTO = "AUTO"
    GUIDED = "GUIDED"
    MANUAL = "MANUAL"


class IntentType(StrEnum):
    RESUME_ANALYSIS = "resume_analysis"
    JOB_MATCHING = "job_matching"
    DOCUMENT_ANALYSIS = "document_analysis"
    DOCUMENT_GENERATION = "document_generation"
    RESEARCH = "research"
    REPORT_GENERATION = "report_generation"
    DATA_ANALYSIS = "data_analysis"
    SPREADSHEET_ANALYSIS = "spreadsheet_analysis"
    CODE_ANALYSIS = "code_analysis"
    CODE_GENERATION = "code_generation"
    LEARNING = "learning"
    STUDY_PLANNING = "study_planning"
    SUMMARIZATION = "summarization"
    COMPARISON = "comparison"
    PRESENTATION_GENERATION = "presentation_generation"
    IMAGE_ANALYSIS = "image_analysis"
    WORKFLOW_EXECUTION = "workflow_execution"
    AUTOMATION = "automation"
    KNOWLEDGE_QUERY = "knowledge_query"
    GENERAL_ASSISTANCE = "general_assistance"


class StrategyType(StrEnum):
    SINGLE_MODEL = "SINGLE_MODEL"
    SINGLE_AGENT = "SINGLE_AGENT"
    SEQUENTIAL_AGENTS = "SEQUENTIAL_AGENTS"
    PARALLEL_AGENTS = "PARALLEL_AGENTS"
    CONDITIONAL_GRAPH = "CONDITIONAL_GRAPH"
    TOOL_ASSISTED = "TOOL_ASSISTED"
    RESEARCH_AND_VALIDATE = "RESEARCH_AND_VALIDATE"
    DOCUMENT_PIPELINE = "DOCUMENT_PIPELINE"
    DATA_ANALYSIS_PIPELINE = "DATA_ANALYSIS_PIPELINE"
    HUMAN_APPROVAL_PIPELINE = "HUMAN_APPROVAL_PIPELINE"
    WORKFLOW_EXECUTION = "WORKFLOW_EXECUTION"


class ModelMode(StrEnum):
    AUTO = "AUTO"
    HIGH_QUALITY = "HIGH_QUALITY"
    LOW_COST = "LOW_COST"
    FAST = "FAST"
    PRIVATE = "PRIVATE"
    MANUAL = "MANUAL"


class MissionStatus(StrEnum):
    DRAFT = "DRAFT"
    VALIDATING = "VALIDATING"
    PLANNED = "PLANNED"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    APPROVED = "APPROVED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    EXPIRED = "EXPIRED"


class TaskStatus(StrEnum):
    CREATED = "CREATED"
    READY = "READY"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    RETRYING = "RETRYING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    BLOCKED = "BLOCKED"
    TIMED_OUT = "TIMED_OUT"


class PolicyDecision(StrEnum):
    ALLOW = "ALLOW"
    LIMIT = "LIMIT"
    REVIEW = "REVIEW"
    APPROVAL = "APPROVAL"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"


class ApprovalStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"