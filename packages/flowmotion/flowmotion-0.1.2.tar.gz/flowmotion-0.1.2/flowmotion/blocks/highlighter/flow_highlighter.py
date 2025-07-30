class FlowHighlighter:
    """
    Base class for applying line-based highlights during code animations in flowmotion.

    Designed to be subclassed with custom highlight logic for visual emphasis in Manim scenes.
    """

    def highlight(self, line: str) -> str:
        """
        Apply highlighting to a line of code.

        Args:
            line (str): Code line to highlight.

        Returns:
            str: Highlighted line with formatting/markup.

        Raises:
            NotImplementedError: Must be implemented in subclasses.
        """
        raise NotImplementedError

    def _escape(self, text: str):
        """
        Escape HTML special characters for safe rendering.

        Args:
            text (str): Raw text to escape.

        Returns:
            str: Text with &, <, > replaced by HTML-safe entities.
        """
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _wrap(self, text: str, color: str):
        """
        Wrap text in a span tag with a foreground color.

        Args:
            text (str): Text to style.
            color (str): Hex color code to apply.

        Returns:
            str: HTML span string with escaped text and color.
        """
        return f'<span foreground="{color}">{self._escape(text)}</span>'
