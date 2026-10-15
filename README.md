# Alignment-Data-Factory: SFT & RLHF/DPO Preference Dataset Curation Pipeline

[![CI](https://github.com/Mr-OWO/alignment-data-factory/actions/workflows/ci.yml/badge.svg)](https://github.com/Mr-OWO/alignment-data-factory/actions)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance data curation and alignment pipeline for Supervised Fine-Tuning (SFT) and Direct Preference Optimization (DPO / RLHF). It filters synthetic and scraped model completions using Abstract Syntax Tree (AST) compilation checks, sycophancy detection, verbosity/length-bias normalization, and repetitive n-gram degradation prevention.

Designed for memory-constrained environments, `alignment-data-factory` processes multi-million row datasets via lazy generators, guaranteeing operational RAM consumption strictly under 200MB.

---

## 🏛️ Pipeline Architecture

```
                       +---------------------------------------+
                       | Raw Candidate Triplet Stream          |
                       |  (prompt, chosen_raw, rejected_raw)   |
                       +-------------------+-------------------+
                                           |
                                           v
                       +---------------------------------------+
                       |      Composite Alignment Filter       |
                       +-------------------+-------------------+
                                           |
           +-------------------------------+-------------------------------+
           |                               |                               |
           v                               v                               v
+----------------------+       +-----------------------+       +-----------------------+
|  AST Code Verifier   |       |  Sycophancy Detector  |       | Length Bias & N-Grams |
| - Python `ast.parse` |       | - False premise check |       | - Ratio > 3.5x normal |
| - JS/TS delimiter &  |       | - Unearned flattery   |       | - Repetitive looping  |
|   bracket parsing    |       | - Blind deference     |       |   degradation metric  |
+----------+-----------+       +-----------+-----------+       +-----------+-----------+
           |                               |                               |
           +-------------------------------+-------------------------------+
                                           |
                                           v
                       +---------------------------------------+
                       |     Decision Gate: Accepted/Rejected  |
                       +-------------------+-------------------+
                                           |
                     +---------------------+---------------------+
                     |                                           |
                     v                                           v
      +-----------------------------+             +-----------------------------+
      |  Accepted Pair Exporter     |             |  Audit Breakdown Telemetry  |
      |  - Streaming JSONL          |             |  - Acceptance Rate %        |
      |  - High-Speed Polars Parquet|             |  - Rejection Reason Metrics |
      +-----------------------------+             +-----------------------------+
```

---

## 🚀 Key Features

- **AST Code Verification:** Ensures all code snippets (Python, TypeScript, JavaScript) embedded in model completions compile without syntax errors or unclosed blocks before ingestion into fine-tuning sets.
- **Sycophancy & Deference Mitigation:** Detects and prunes model completions that pander to incorrect user presuppositions or display unearned flattery.
- **Verbosity & Length-Bias Normalization:** Counters RLHF reward-hacking where models generate artificially padded, low-entropy text.
- **Repetitive N-Gram Loop Suppression:** Detects token degenerations and loops common in quantized or temperature-unstable models.
- **Low-Memory Streaming (Sub-200MB RAM):** Leverages Python generator streaming and Polars columnar chunking to curate millions of pairs with minimal resident memory.

---

## 📦 Installation

```bash
git clone https://github.com/Mr-OWO/alignment-data-factory.git
cd alignment-data-factory
pip install -e ".[dev]"
```

---

## 💡 Quick Start

```python
from alignment_data_factory import DatasetPipeline, PreferencePair

pipeline = DatasetPipeline()

def sample_stream():
    yield PreferencePair(
        prompt="Write a Python function to compute Fibonacci numbers.",
        chosen="```python\ndef fib(n: int) -> int:\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b\n```",
        rejected="You are completely right! Just use a loop or recursion.",
        metadata={"domain": "algorithms"}
    )

summary = pipeline.export_curated_dataset(
    sample_stream(),
    output_jsonl="curated_dpo.jsonl",
    output_parquet="curated_dpo.parquet"
)

print(f"Accepted: {summary.accepted_pairs}/{summary.total_pairs_evaluated}")
print(f"Acceptance Rate: {summary.acceptance_rate * 100:.2f}%")
```

---

## 🧪 Testing & Verification

```bash
pytest tests/ -v
ruff check src/ tests/
```

---

## 👤 Author
**Wisdom Ogechi Owabor**
- Full-Stack Software Engineer & Python AI Systems Specialist
- Portfolio: [wisdomowabor.online](https://wisdomowabor.online)
- GitHub: [@Mr-OWO](https://github.com/Mr-OWO)
