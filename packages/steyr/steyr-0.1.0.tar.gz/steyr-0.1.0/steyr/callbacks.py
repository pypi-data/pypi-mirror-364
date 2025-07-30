"""Provide callbacks to `pulldown-cmark`."""

from latex2mathml.converter import convert
from pygments import highlight  # pyright: ignore[reportUnknownVariableType]
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer


def math_callback(buffer: str, display: bool) -> str:  # noqa: FBT001
    """Convert a LaTeX string to MathML."""
    return convert(buffer, "display" if display else "inline")


def code_callback(buffer: str, language: str | None) -> str:
    """Highlight a codeblock of the given language."""
    lexer = get_lexer_by_name(language) if language else guess_lexer(buffer)

    formatter: HtmlFormatter[str] = HtmlFormatter(
        cssclass=f"language-{language}",
        nobackground=True,
        wrapcode=True,
    )

    return highlight(buffer, lexer, formatter)
