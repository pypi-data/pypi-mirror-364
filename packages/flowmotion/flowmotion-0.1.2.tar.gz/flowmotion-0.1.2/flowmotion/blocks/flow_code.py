from manim import *

from .highlighter import FlowSyntaxHighlighter
from .flow_document import FlowDocument


class FlowCode(FlowDocument):
    """
    Code document renderer with syntax highlighting for flowmotion.

    Uses FlowSyntaxHighlighter to apply language-aware styling for animated
    algorithm visualizations.
    """

    def __init__(
        self,
        filepath,
        language="cpp",
        font="JetBrains Mono",
        font_size=18,
        max_lines_per_chunk=21,
    ):
        """
        Initialize a syntax-highlighted code document.

        Args:
            filepath (str): Path to the source code file.
            language (str): Language name for syntax highlighting (default: "cpp").
            font (str): Font used for rendering (default: JetBrains Mono).
            font_size (int): Font size in px (default: 18).
            max_lines_per_chunk (int): Max lines per render group (default: 21).
        """
        super().__init__(
            filepath,
            font,
            font_size,
            max_lines_per_chunk,
            FlowSyntaxHighlighter(language),
        )
