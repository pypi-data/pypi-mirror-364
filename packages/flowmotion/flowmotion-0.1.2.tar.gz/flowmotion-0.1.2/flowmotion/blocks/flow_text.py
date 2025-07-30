from manim import *

from .highlighter import FlowPlainTextHighlighter
from .flow_document import FlowDocument


class FlowText(FlowDocument):
    """
    Plain text document renderer for flowmotion.

    Uses FlowPlainTextHighlighter to display unstyled or uniformly styled
    text, suitable for comments, explanations, or non-code content.
    """

    def __init__(
        self,
        filepath,
        font="JetBrains Mono",
        font_size=18,
        max_lines_per_chunk=21,
    ):
        """
        Initialize a plain text document.

        Args:
            filepath (str): Path to the text file.
            font (str): Font used for rendering (default: JetBrains Mono).
            font_size (int): Font size in px (default: 18).
            max_lines_per_chunk (int): Max lines per render group (default: 21).
        """
        super().__init__(
            filepath,
            font,
            font_size,
            max_lines_per_chunk,
            FlowPlainTextHighlighter(),
        )
