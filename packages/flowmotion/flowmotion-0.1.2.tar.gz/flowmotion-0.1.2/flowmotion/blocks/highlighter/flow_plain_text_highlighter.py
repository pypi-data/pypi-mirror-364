from .flow_highlighter import FlowHighlighter


class FlowPlainTextHighlighter(FlowHighlighter):
    """
    Simple highlighter that applies a uniform color to the entire line.

    Useful for minimal styling or fallback rendering when no syntax-specific
    highlighting is needed.
    """

    def __init__(self, color="#FFFFFF"):
        """
        Initialize with a default or custom text color.

        Args:
            color (str): Hex color code for the line text (default: white).
        """
        self.color = color

    def highlight(self, line: str) -> str:
        """
        Wrap the line in a span with the configured color.

        Args:
            line (str): Code line to be highlighted.

        Returns:
            str: Colored line wrapped in a span tag.
        """
        return self._wrap(line, self.color)
