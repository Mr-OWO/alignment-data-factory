from pathlib import Path
import tempfile
from alignment_data_factory.models import PreferencePair
from alignment_data_factory.pipeline import DatasetPipeline


def test_streaming_export_jsonl_and_parquet():
    pipeline = DatasetPipeline()

    def generate_sample_data():
        yield PreferencePair(
            prompt="Reverse a string in Python",
            chosen="```python\ndef rev(s: str) -> str:\n    return s[::-1]\n```",
            rejected="Just loop backward",
            metadata={"source": "eval_v1"},
        )
        yield PreferencePair(
            prompt="Bad syntax request",
            chosen="```python\ndef bad(\n```",
            rejected="Pass",
            metadata={"source": "eval_v1"},
        )
        yield PreferencePair(
            prompt="Calculate sum",
            chosen="```python\ndef total(arr: list[int]) -> int:\n    return sum(arr)\n```",
            rejected="Use a counter",
            metadata={"source": "eval_v1"},
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        jsonl_path = Path(tmpdir) / "curated.jsonl"
        parquet_path = Path(tmpdir) / "curated.parquet"

        summary = pipeline.export_curated_dataset(
            generate_sample_data(),
            output_jsonl=jsonl_path,
            output_parquet=parquet_path,
        )

        assert summary.total_pairs_evaluated == 3
        assert summary.accepted_pairs == 2
        assert summary.rejected_pairs == 1
        assert summary.acceptance_rate == round(2 / 3, 4)
        assert jsonl_path.exists()
        assert parquet_path.exists()

        # Check line count in JSONL
        with open(jsonl_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            assert len(lines) == 2
