"""SFT & RLHF/DPO Preference Dataset Curation Pipeline."""

__version__ = "1.0.0"

from .models import PreferencePair, QualityFilterResult, DatasetSummary
from .ast_verifier import ASTCodeVerifier, CodeValidationResult
from .filters import (
    SycophancyDetector,
    VerbosityBiasNormalizer,
    RepetitiveNGramFilter,
    CompositeAlignmentFilter,
)
from .pipeline import DatasetPipeline
from .quality_audit import DatasetQualityAuditor

__all__ = [
    "PreferencePair",
    "QualityFilterResult",
    "DatasetSummary",
    "ASTCodeVerifier",
    "CodeValidationResult",
    "SycophancyDetector",
    "VerbosityBiasNormalizer",
    "RepetitiveNGramFilter",
    "CompositeAlignmentFilter",
    "DatasetPipeline",
    "DatasetQualityAuditor",
]
