"""Dataset quality auditor and compliance report generator."""

from typing import List, Dict, Any, Optional
from .models import PreferencePair, QualityFilterResult, DatasetSummary
from .filters import CompositeAlignmentFilter


class DatasetQualityAuditor:
    """Audits preference datasets against AST, sycophancy, and length filters."""

    def __init__(self, alignment_filter: Optional[CompositeAlignmentFilter] = None):
        self.alignment_filter = alignment_filter or CompositeAlignmentFilter()

    def audit_batch(self, pairs: List[PreferencePair]) -> DatasetSummary:
        """Run batch quality audit and generate aggregated telemetry."""
        total = len(pairs)
        if total == 0:
            return DatasetSummary(
                total_pairs_evaluated=0,
                accepted_pairs=0,
                rejected_pairs=0,
                acceptance_rate=0.0,
                rejection_breakdown={},
            )

        accepted = 0
        rejected = 0
        rejection_counts: Dict[str, int] = {}

        for pair in pairs:
            result = self.alignment_filter.filter_pair(pair)
            if result.passed:
                accepted += 1
            else:
                rejected += 1
                for reason in result.rejection_reasons:
                    rejection_counts[reason] = rejection_counts.get(reason, 0) + 1

        return DatasetSummary(
            total_pairs_evaluated=total,
            accepted_pairs=accepted,
            rejected_pairs=rejected,
            acceptance_rate=round(accepted / total, 4),
            rejection_breakdown=rejection_counts,
        )
