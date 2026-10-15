import ast
import re
from typing import List, Optional
from pydantic import BaseModel


class CodeValidationResult(BaseModel):
    is_valid: bool
    language: str
    error_message: Optional[str] = None
    snippet_preview: str


class ASTCodeVerifier:
    """Verifies syntactic correctness of code blocks embedded in LLM completions."""

    @staticmethod
    def extract_code_blocks(text: str) -> List[tuple[str, str]]:
        """
        Extracts code blocks formatted as ```lang ... ``` from markdown text.
        Returns list of (language, code_content).
        """
        pattern = r"```([a-zA-Z0-9_-]*)\n(.*?)```"
        matches = re.findall(pattern, text, flags=re.DOTALL)
        results = []
        for lang, code in matches:
            lang_clean = lang.strip().lower() or "generic"
            results.append((lang_clean, code.strip()))
        return results

    @classmethod
    def verify_python(cls, code: str) -> CodeValidationResult:
        """Parses Python code using native ast.parse."""
        preview = code[:120].replace("\n", " ") + ("..." if len(code) > 120 else "")
        try:
            ast.parse(code)
            return CodeValidationResult(is_valid=True, language="python", snippet_preview=preview)
        except SyntaxError as e:
            return CodeValidationResult(
                is_valid=False,
                language="python",
                error_message=f"SyntaxError at line {e.lineno}, offset {e.offset}: {e.msg}",
                snippet_preview=preview,
            )
        except Exception as e:
            return CodeValidationResult(
                is_valid=False,
                language="python",
                error_message=f"AST Parse Exception: {str(e)}",
                snippet_preview=preview,
            )

    @classmethod
    def verify_javascript_or_typescript(cls, code: str) -> CodeValidationResult:
        """
        Heuristic syntactic validator for JS/TS: checks balanced braces, brackets,
        parentheses, string quotes, and structural keywords.
        """
        preview = code[:120].replace("\n", " ") + ("..." if len(code) > 120 else "")

        # Check balanced brackets
        stack = []
        pairs = {")": "(", "}": "{", "]": "["}
        in_single_quote = False
        in_double_quote = False
        in_backtick = False
        escaped = False

        for char in code:
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue

            if char == "'" and not in_double_quote and not in_backtick:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote and not in_backtick:
                in_double_quote = not in_double_quote
            elif char == '`' and not in_single_quote and not in_double_quote:
                in_backtick = not in_backtick

            if in_single_quote or in_double_quote or in_backtick:
                continue

            if char in "({[":
                stack.append(char)
            elif char in ")}]":
                if not stack or stack[-1] != pairs[char]:
                    return CodeValidationResult(
                        is_valid=False,
                        language="typescript",
                        error_message=f"Unmatched closing delimiter: '{char}'",
                        snippet_preview=preview,
                    )
                stack.pop()

        if in_single_quote or in_double_quote or in_backtick:
            return CodeValidationResult(
                is_valid=False,
                language="typescript",
                error_message="Unclosed string literal or template backtick",
                snippet_preview=preview,
            )

        if stack:
            return CodeValidationResult(
                is_valid=False,
                language="typescript",
                error_message=f"Unclosed opening delimiters remaining on stack: {stack}",
                snippet_preview=preview,
            )

        return CodeValidationResult(is_valid=True, language="typescript", snippet_preview=preview)

    @classmethod
    def verify_all_blocks(cls, text: str) -> List[CodeValidationResult]:
        """Extracts and verifies every code block found in completion text."""
        blocks = cls.extract_code_blocks(text)
        results = []
        for lang, code in blocks:
            if lang in ("python", "py"):
                results.append(cls.verify_python(code))
            elif lang in ("typescript", "ts", "javascript", "js", "tsx", "jsx"):
                results.append(cls.verify_javascript_or_typescript(code))
        return results
