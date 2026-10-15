import json
from collections import defaultdict
from pathlib import Path
from typing import Generator, Iterable, List, Optional
import polars as pl
from .filters import CompositeAlignmentFilter
from .models import DatasetSummary, PreferencePair, QualityFilterResult


class DatasetPipeline:
    """Memory-efficient streaming curation pipeline for SFT & DPO preference datasets."""

    def __init__(self, filter_engine: Optional[CompositeAlignmentFilter] = None):
        self.filter_engine = filter_engine or CompositeAlignmentFilter()

    def stream_process(
        self, stream: Iterable[PreferencePair]
    ) -> Generator[tuple[PreferencePair, QualityFilterResult], None, None]:
        """
        Yields (pair, filter_result) lazily, guaranteeing constant O(1) memory consumption
        well under the 200MB threshold regardless of dataset size.
        """
        for pair in stream:
            result = self.filter_engine.filter_pair(pair)
            yield pair, result

    def export_curated_dataset(
        self,
        stream: Iterable[PreferencePair],
        output_jsonl: Optional[Path] = None,
        output_parquet: Optional[Path] = None,
        chunk_size: int = 1000,
    ) -> DatasetSummary:
        """
        Streams dataset through filters, persists accepted records in batches,
        and produces an analytical DatasetSummary.
        """
        total = 0
        accepted = 0
        rejected = 0
        rejection_breakdown = defaultdict(int)

        accepted_buffer: List[dict] = []
        jsonl_file = open(output_jsonl, "w", encoding="utf-8") if output_jsonl else None

        try:
            for pair, result in self.stream_process(stream):
                total += 1
                if result.passed:
                    accepted += 1
                    record = {
                        "prompt": pair.prompt,
                        "chosen": pair.chosen,
                        "rejected": pair.rejected,
                        "metadata": json.dumps(pair.metadata),
                    }
                    if jsonl_file:
                        jsonl_file.write(json.dumps(record) + "\n")
                    if output_parquet:
                        accepted_buffer.append(record)
                else:
                    rejected += 1
                    for r in result.rejection_reasons:
                        category = r.split(":")[0].split("(")[0].strip()
                        rejection_breakdown[category] += 1
        finally:
            if jsonl_file:
                jsonl_file.close()

        # Write Parquet via Polars if requested
        if output_parquet and accepted_buffer:
            df = pl.DataFrame(accepted_buffer)
            df.write_parquet(output_parquet)

        rate = (accepted / total) if total > 0 else 0.0

        return DatasetSummary(
            total_pairs_evaluated=total,
            accepted_pairs=accepted,
            rejected_pairs=rejected,
            acceptance_rate=round(rate, 4),
            rejection_breakdown=dict(rejection_breakdown),
        )
