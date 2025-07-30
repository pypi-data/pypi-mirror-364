"""
Graphora Client Library

A Python client for interacting with the Graphora API.
"""

from graphora.client import GraphoraClient
from graphora.models import (
    OntologyResponse,
    TransformResponse,
    TransformStatus,
    MergeResponse,
    MergeStatus,
    GraphResponse,
    DocumentMetadata,
    DocumentType,
    # Quality validation models
    QualityResults,
    QualityViolation,
    QualityMetrics,
    QualityRuleType,
    QualitySeverity,
    ApprovalRequest,
    RejectQualityRequest,
    QualityApprovalResponse,
    QualityRejectionResponse,
    QualityViolationsResponse,
    QualitySummaryResponse,
    QualityDeleteResponse,
    QualityHealthResponse
)

__version__ = "0.3.0"  # Updated to include quality validation features
