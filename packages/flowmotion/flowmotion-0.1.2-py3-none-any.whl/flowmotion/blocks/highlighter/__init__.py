"""
Exposes highlighter classes for flowmotion.

Includes:
    - FlowHighlighter: Base class for defining highlight behavior.
    - FlowSyntaxHighlighter: Pygments-based syntax highlighter.
    - FlowPlainTextHighlighter: Single-color fallback highlighter.
"""

from .flow_highlighter import FlowHighlighter
from .flow_syntax_highlighter import FlowSyntaxHighlighter
from .flow_plain_text_highlighter import FlowPlainTextHighlighter

__all__ = ["FlowHighlighter", "FlowSyntaxHighlighter", "FlowPlainTextHighlighter"]
