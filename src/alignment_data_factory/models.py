from typing import Any, Dict, List
from pydantic import BaseModel, Field


class PreferencePair(BaseModel):
    """Triplets of prompt, chosen completion, and rejected completion for DPO / RLHF."""
    prompt: str = Field(..., min_length=1, description="Instruction or conversational prompt")
    chosen: str = Field(..., min_length=1, description="Preferred response aligned with user intent and safety")
    rejected: str = Field(..., min_length=1, description="Suboptimal or misaligned alternative response")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Provenance, source model, or domain tag")


class QualityFilterResult(BaseModel):
    """Detailed audit metrics for a single preference candidate."""
    passed: bool = Field(..., description="Accepted for dataset ingestion")
    ast_valid: bool = Field(default=True, description="Code blocks compile without syntax errors")
    sycophancy_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Heuristic sycophancy probability")
    verbosity_ratio: float = Field(default=1.0, ge=0.0, description="Ratio of chosen length to rejected length")
    repetitive_ngram_ratio: float = Field(default=0.0, ge=0.0, le=1.0, description="Fraction of repetitive n-grams")
    rejection_reasons: List[str] = Field(default_factory=list, description="Specific alignment criteria failures")


class DatasetSummary(BaseModel):
    """Telemetry report across a processed batch or stream."""
    total_pairs_evaluated: int
    accepted_pairs: int
    rejected_pairs: int
    acceptance_rate: float
    rejection_breakdown: Dict[str, int]
