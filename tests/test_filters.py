from alignment_data_factory.filters import (
    CompositeAlignmentFilter,
    RepetitiveNGramFilter,
    SycophancyDetector,
    VerbosityBiasNormalizer,
)
from alignment_data_factory.models import PreferencePair


def test_sycophancy_detection():
    flattering = "You are absolutely right, your brilliant point is completely correct!"
    neutral = "The optimal time complexity for sorting an array in-place is O(n log n)."
    assert SycophancyDetector.score(flattering) >= 0.7
    assert SycophancyDetector.score(neutral) == 0.0


def test_verbosity_bias():
    short_rejected = "It's 42."
    long_chosen = " " .join(["word"] * 50)
    assert VerbosityBiasNormalizer.is_length_biased(long_chosen, short_rejected, threshold=3.5) is True


def test_repetitive_ngram_detection():
    looping = "I will help you. I will help you. I will help you. I will help you. I will help you."
    normal = "Here is an explanation of dynamic programming with memoization."
    assert RepetitiveNGramFilter.calculate_repetition_ratio(looping, n=3) > 0.4
    assert RepetitiveNGramFilter.calculate_repetition_ratio(normal, n=3) == 0.0


def test_composite_alignment_filter_accepts_clean_pair():
    filter_engine = CompositeAlignmentFilter()
    pair = PreferencePair(
        prompt="Write a Python function to square a number.",
        chosen="```python\ndef square(n: float) -> float:\n    return n * n\n```",
        rejected="Maybe multiply it by itself.",
    )
    result = filter_engine.filter_pair(pair)
    assert result.passed is True
    assert result.ast_valid is True
    assert len(result.rejection_reasons) == 0


def test_composite_alignment_filter_rejects_broken_code_and_sycophancy():
    filter_engine = CompositeAlignmentFilter()
    pair = PreferencePair(
        prompt="Write code to calculate factorial.",
        chosen="You are absolutely right! ```python\ndef fact(n\n  return 1\n```",
        rejected="def fact(n): return 1",
    )
    result = filter_engine.filter_pair(pair)
    assert result.passed is False
    assert result.ast_valid is False
    assert any("Sycophancy" in r for r in result.rejection_reasons)
    assert any("AST Error" in r for r in result.rejection_reasons)
