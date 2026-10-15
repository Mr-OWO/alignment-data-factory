from alignment_data_factory.ast_verifier import ASTCodeVerifier


def test_python_valid_syntax():
    code = """
def calculate_elo(r_a: float, r_b: float, score: float, k: float = 32.0) -> tuple[float, float]:
    expected = 1.0 / (1.0 + 10.0 ** ((r_b - r_a) / 400.0))
    new_a = r_a + k * (score - expected)
    new_b = r_b + k * ((1.0 - score) - (1.0 - expected))
    return new_a, new_b
"""
    result = ASTCodeVerifier.verify_python(code)
    assert result.is_valid is True
    assert result.error_message is None


def test_python_syntax_error():
    broken_code = """
def broken_fn(x, y
    return x + y
"""
    result = ASTCodeVerifier.verify_python(broken_code)
    assert result.is_valid is False
    assert "SyntaxError" in result.error_message


def test_typescript_valid_syntax():
    ts_code = """
interface ModelScore {
  accuracy: number;
  helpfulness: number;
}

export function evaluateModel(scores: ModelScore[]): number {
  return scores.reduce((acc, curr) => acc + curr.accuracy, 0) / scores.length;
}
"""
    result = ASTCodeVerifier.verify_javascript_or_typescript(ts_code)
    assert result.is_valid is True


def test_typescript_unmatched_delimiter():
    broken_ts = """
function broken(a: number) {
  if (a > 0) {
    return [1, 2, 3;
  }
}
"""
    result = ASTCodeVerifier.verify_javascript_or_typescript(broken_ts)
    assert result.is_valid is False
    assert "Unmatched closing delimiter" in result.error_message


def test_extract_all_blocks_from_markdown():
    md = """
Here is Python solution:
```python
def foo():
    return 42
```

And TypeScript solution:
```typescript
const bar = (x: number): number => x * 2;
```
"""
    blocks = ASTCodeVerifier.verify_all_blocks(md)
    assert len(blocks) == 2
    assert all(b.is_valid for b in blocks)
