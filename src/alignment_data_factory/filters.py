import re
from collections import Counter
from typing import List, Tuple
from .ast_verifier import ASTCodeVerifier
from .models import PreferencePair, QualityFilterResult


class SycophancyDetector:
    """Detects sycophantic deference, excessive flattery, or blind validation of false premises."""

    SYCOPHANTIC_PATTERNS = [
        r"\byou are absolutely right\b",
        r"\bas an astute (observer|user) like you\b",
        r"\byour brilliant (point|observation)\b",
        r"\bi couldn'?t agree more with your genius\b",
        r"\byou are completely correct, forgive me\b",
        r"\bthat is an insightful and flawless perspective\b",
    ]

    @classmethod
    def score(cls, text: str) -> float:
        text_lower = text.lower()
        matches = 0
        for pattern in cls.SYCOPHANTIC_PATTERNS:
            if re.search(pattern, text_lower):
                matches += 1
        if matches == 0:
            return 0.0
        return min(1.0, 0.4 + (matches * 0.3))


class VerbosityBiasNormalizer:
    """Detects and normalizes length bias where a response is inflated with verbose boilerplate."""

    @classmethod
    def calculate_ratio(cls, chosen: str, rejected: str) -> float:
        c_len = len(chosen.split())
        r_len = len(rejected.split())
        if r_len == 0:
            return 1.0
        return c_len / r_len

    @classmethod
    def is_length_biased(cls, chosen: str, rejected: str, threshold: float = 3.5) -> bool:
        """Returns True if chosen is disproportionately longer (> 3.5x) without justification."""
        return cls.calculate_ratio(chosen, rejected) > threshold


class RepetitiveNGramFilter:
    """Calculates n-gram repetition density to detect degeneration loops."""

    @classmethod
    def calculate_repetition_ratio(cls, text: str, n: int = 3) -> float:
        tokens = re.findall(r"\w+", text.lower())
        if len(tokens) < n * 2:
            return 0.0

        ngrams = [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]
        total = len(ngrams)
        unique = len(set(ngrams))
        if total == 0:
            return 0.0
        # Ratio of duplicate ngrams
        return (total - unique) / total


class CompositeAlignmentFilter:
    """Aggregates AST verification, sycophancy, verbosity, and repetition filters."""

    def __init__(
        self,
        max_sycophancy: float = 0.5,
        max_verbosity_ratio: float = 3.5,
        max_repetition_ratio: float = 0.25,
        enforce_ast: bool = True,
    ):
        self.max_sycophancy = max_sycophancy
        self.max_verbosity_ratio = max_verbosity_ratio
        self.max_repetition_ratio = max_repetition_ratio
        self.enforce_ast = enforce_ast

    def filter_pair(self, pair: PreferencePair) -> QualityFilterResult:
        rejection_reasons: List[str] = []

        # 1. AST Code Verification on chosen response
        ast_valid = True
        if self.enforce_ast:
            code_results = ASTCodeVerifier.verify_all_blocks(pair.chosen)
            for res in code_results:
                if not res.is_valid:
                    ast_valid = False
                    rejection_reasons.append(f"AST Error in {res.language}: {res.error_message}")

        # 2. Sycophancy Detection
        sycophancy = SycophancyDetector.score(pair.chosen)
        if sycophancy > self.max_sycophancy:
            rejection_reasons.append(
                f"Sycophancy score ({sycophancy:.2f}) exceeds threshold ({self.max_sycophancy})"
            )

        # 3. Verbosity / Length Bias
        verbosity = VerbosityBiasNormalizer.calculate_ratio(pair.chosen, pair.rejected)
        if verbosity > self.max_verbosity_ratio:
            rejection_reasons.append(
                f"Verbosity ratio ({verbosity:.2f}x) exceeds threshold ({self.max_verbosity_ratio}x)"
            )

        # 4. Repetitive N-gram Filtering
        rep_ratio = RepetitiveNGramFilter.calculate_repetition_ratio(pair.chosen)
        if rep_ratio > self.max_repetition_ratio:
            rejection_reasons.append(
                f"Repetitive n-gram ratio ({rep_ratio:.2f}) exceeds threshold ({self.max_repetition_ratio})"
            )

        passed = len(rejection_reasons) == 0

        return QualityFilterResult(
            passed=passed,
            ast_valid=ast_valid,
            sycophancy_score=round(sycophancy, 2),
            verbosity_ratio=round(verbosity, 2),
            repetitive_ngram_ratio=round(rep_ratio, 2),
            rejection_reasons=rejection_reasons,
        )
