"""
Graphora Models

Data models for the Graphora client library.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Document types supported by Graphora."""
    TXT = "txt"
    PDF = "pdf"
    DOCX = "docx"
    CSV = "csv"
    JSON = "json"
    YAML = "yaml"
    XML = "xml"


class DocumentMetadata(BaseModel):
    """Metadata for a document."""
    source: str
    document_type: DocumentType
    tags: List[str] = Field(default_factory=list)
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentInfo(BaseModel):
    """Information about a document."""
    filename: str
    size: int
    document_type: DocumentType
    metadata: Optional[DocumentMetadata] = None


class OntologyResponse(BaseModel):
    """Response from ontology validation."""
    id: str


class TransformationStage(str, Enum):
    """Stages of the transformation process."""
    UPLOAD = "upload"
    PARSING = "parsing"
    EXTRACTION = "extraction"
    VALIDATION = "validation"
    INDEXING = "indexing"
    COMPLETED = "completed"


class ResourceMetrics(BaseModel):
    """Resource usage metrics for a transformation."""
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    duration_seconds: float = 0.0


class StageProgress(BaseModel):
    """Progress information for a transformation stage."""
    stage: TransformationStage
    progress: float = 0.0  # 0.0 to 1.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metrics: Optional[ResourceMetrics] = None
    message: Optional[str] = None


class TransformStatus(BaseModel):
    """Status of a transformation."""
    transform_id: str
    status: str
    progress: float = 0.0  # 0.0 to 1.0
    stage_progress: List[StageProgress] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    resource_metrics: Optional[ResourceMetrics] = None


class TransformResponse(BaseModel):
    """Response from document upload."""
    id: str
    upload_timestamp: datetime
    status: str
    document_info: DocumentInfo


class MergeStatus(BaseModel):
    """Status of a merge process."""
    merge_id: str
    status: str
    progress: float = 0.0  # 0.0 to 1.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    conflicts_count: int = 0
    resolved_count: int = 0


class MergeResponse(BaseModel):
    """Response from starting a merge process."""
    merge_id: str
    status: str
    start_time: datetime


class ResolutionStrategy(str, Enum):
    """Strategies for resolving conflicts."""
    ACCEPT = "accept"
    REJECT = "reject"
    MODIFY = "modify"
    MERGE = "merge"


class ConflictResolution(BaseModel):
    """Information about a conflict requiring resolution."""
    id: str
    entity_id: str
    entity_type: str
    properties: Dict[str, Any]
    conflict_type: str
    source: Optional[str] = None
    target: Optional[str] = None
    suggested_resolution: Optional[ResolutionStrategy] = None
    confidence: Optional[float] = None


class Node(BaseModel):
    """A node in the graph."""
    id: str
    labels: List[str]
    properties: Dict[str, Any]


class Edge(BaseModel):
    """An edge in the graph."""
    id: str
    type: str
    source: str
    target: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphResponse(BaseModel):
    """Response containing graph data."""
    nodes: List[Node] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
    total_nodes: Optional[int] = None
    total_edges: Optional[int] = None


class NodeChange(BaseModel):
    """A change to a node in the graph."""
    id: Optional[str] = None  # None for new nodes
    labels: List[str]
    properties: Dict[str, Any]
    is_deleted: bool = False


class EdgeChange(BaseModel):
    """A change to an edge in the graph."""
    id: Optional[str] = None  # None for new edges
    type: str
    source: str
    target: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    is_deleted: bool = False


class SaveGraphRequest(BaseModel):
    """Request to save changes to the graph."""
    nodes: List[NodeChange] = Field(default_factory=list)
    edges: List[EdgeChange] = Field(default_factory=list)
    version: Optional[int] = None  # For optimistic concurrency control


class SaveGraphResponse(BaseModel):
    """Response from saving changes to the graph."""
    data: GraphResponse
    messages: Optional[List[str]] = None


# Quality Validation Models

class QualityRuleType(str, Enum):
    """Types of quality rules that can be applied."""
    FORMAT = "format"
    BUSINESS = "business"
    CROSS_ENTITY = "cross_entity"
    DISTRIBUTION = "distribution"
    CONSISTENCY = "consistency"


class QualitySeverity(str, Enum):
    """Severity levels for quality violations."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class QualityViolation(BaseModel):
    """Represents a single quality rule violation."""
    rule_id: str = Field(description="Unique identifier for the rule that was violated")
    rule_type: QualityRuleType = Field(description="Type of quality rule")
    severity: QualitySeverity = Field(description="Severity level of the violation")
    entity_type: Optional[str] = Field(None, description="Type of entity where violation occurred")
    entity_id: Optional[str] = Field(None, description="ID of the specific entity")
    property_name: Optional[str] = Field(None, description="Property name where violation occurred")
    relationship_type: Optional[str] = Field(None, description="Type of relationship if applicable")
    message: str = Field(description="Human-readable description of the violation")
    expected: str = Field(description="What was expected")
    actual: str = Field(description="What was actually found")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in this violation detection")
    suggestion: Optional[str] = Field(None, description="Suggested fix for the violation")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context for the violation")


class QualityMetrics(BaseModel):
    """Overall quality metrics for an extraction."""
    total_entities: int = Field(description="Total number of entities extracted")
    total_relationships: int = Field(description="Total number of relationships extracted")
    total_properties: int = Field(description="Total number of properties across all entities")
    entities_with_violations: int = Field(description="Number of entities that have violations")
    relationships_with_violations: int = Field(description="Number of relationships that have violations")
    total_violations: int = Field(description="Total number of violations found")
    entity_violation_rate: float = Field(description="Percentage of entities with violations")
    relationship_violation_rate: float = Field(description="Percentage of relationships with violations")
    overall_violation_rate: float = Field(description="Overall violation rate")
    avg_entity_confidence: float = Field(description="Average confidence score for entity extraction")
    avg_relationship_confidence: float = Field(description="Average confidence score for relationship extraction")
    confidence_scores_by_type: Dict[str, float] = Field(default_factory=dict, description="Average confidence by entity type")
    property_completeness_rate: float = Field(description="Percentage of required properties that were filled")
    entity_type_coverage: Dict[str, int] = Field(default_factory=dict, description="Count of entities by type")


class QualityResults(BaseModel):
    """Complete quality validation results for a transform."""
    transform_id: str = Field(description="ID of the transform that was validated")
    overall_score: float = Field(ge=0.0, le=100.0, description="Overall quality score (0-100)")
    grade: str = Field(description="Letter grade (A, B, C, D, F)")
    requires_review: bool = Field(description="Whether human review is required")
    violations: List[QualityViolation] = Field(default_factory=list, description="List of all violations found")
    metrics: QualityMetrics = Field(description="Overall quality metrics")
    violations_by_type: Dict[QualityRuleType, int] = Field(default_factory=dict, description="Violation count by rule type")
    violations_by_severity: Dict[QualitySeverity, int] = Field(default_factory=dict, description="Violation count by severity")
    violations_by_entity_type: Dict[str, int] = Field(default_factory=dict, description="Violation count by entity type")
    entity_quality_summary: Dict[str, Dict[str, int]] = Field(default_factory=dict, description="Quality summary by entity type")
    validation_timestamp: datetime = Field(description="When validation was performed")
    validation_duration_ms: int = Field(description="How long validation took in milliseconds")
    rules_applied: int = Field(description="Number of quality rules that were applied")
    validation_config: Dict[str, Any] = Field(default_factory=dict, description="Configuration used for validation")


class ApprovalRequest(BaseModel):
    """Request to approve quality results."""
    approval_comment: Optional[str] = Field(None, description="Optional comment about the approval")


class RejectQualityRequest(BaseModel):
    """Request to reject quality results."""
    rejection_reason: str = Field(description="Required reason for rejecting the quality results")


class QualityApprovalResponse(BaseModel):
    """Response from approving quality results."""
    message: str = Field(description="Success message")
    transform_id: str = Field(description="ID of the transform")
    status: str = Field(description="Approval status")


class QualityRejectionResponse(BaseModel):
    """Response from rejecting quality results."""
    message: str = Field(description="Success message")
    transform_id: str = Field(description="ID of the transform")
    status: str = Field(description="Rejection status")
    reason: str = Field(description="Reason for rejection")


class QualityViolationsResponse(BaseModel):
    """Response containing filtered quality violations."""
    transform_id: str = Field(description="ID of the transform")
    violations: List[QualityViolation] = Field(description="List of filtered violations")
    total_returned: int = Field(description="Number of violations returned")
    filters_applied: Dict[str, Optional[Union[str, QualityRuleType, QualitySeverity]]] = Field(
        description="Filters that were applied to the results"
    )


class QualitySummaryResponse(BaseModel):
    """Response containing quality summary for a user."""
    user_id: str = Field(description="User ID")
    recent_quality_results: List[Dict[str, Any]] = Field(description="List of recent quality result summaries")
    total_returned: int = Field(description="Number of results returned")


class QualityDeleteResponse(BaseModel):
    """Response from deleting quality results."""
    message: str = Field(description="Success message")
    transform_id: str = Field(description="ID of the transform")


class QualityHealthResponse(BaseModel):
    """Response from quality API health check."""
    status: str = Field(description="Health status (healthy/unavailable)")
    quality_api_available: bool = Field(description="Whether quality API is available")
    message: str = Field(description="Health status message")
