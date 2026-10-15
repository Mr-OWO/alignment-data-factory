from alignment_data_factory.quality_audit import DatasetQualityAuditor
from alignment_data_factory.models import PreferencePair


def test_quality_auditor_clean_batch():
    auditor = DatasetQualityAuditor()
    pairs = [
        PreferencePair(
            prompt="Write a Python add function.",
            chosen="```python\ndef add(a, b):\n    return a + b\n```",
            rejected="```python\ndef add(a, b\n    return a + b\n```",
        ),
        PreferencePair(
            prompt="Explain binary search.",
            chosen="Binary search divides a sorted collection in half repeatedly.",
            rejected="You are the greatest person ever and binary search is whatever you say!",
        ),
    ]

    summary = auditor.audit_batch(pairs)
    assert summary.total_pairs_evaluated == 2
    assert summary.accepted_pairs == 2
    assert summary.acceptance_rate == 1.0
    assert summary.rejected_pairs == 0


def test_quality_auditor_empty():
    auditor = DatasetQualityAuditor()
    summary = auditor.audit_batch([])
    assert summary.total_pairs_evaluated == 0
    assert summary.acceptance_rate == 0.0
