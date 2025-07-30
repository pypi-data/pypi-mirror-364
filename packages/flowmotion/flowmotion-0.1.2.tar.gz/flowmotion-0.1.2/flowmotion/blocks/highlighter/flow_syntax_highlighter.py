from pygments import lex
from pygments.token import Token
from pygments.lexers import get_lexer_by_name

from .flow_highlighter import FlowHighlighter


class FlowSyntaxHighlighter(FlowHighlighter):
    """
    Syntax-based highlighter using Pygments for flowmotion animations.

    Applies color-coded styling to code lines based on token types, enabling
    visually rich Manim renderings of code solutions.
    """

    def __init__(self, language):
        """
        Initialize with a language lexer and color mapping.

        Args:
            language (str): Language name recognized by Pygments (e.g., "python", "cpp").
        """
        self.lexer = get_lexer_by_name(language)
        self.colors = {
            # Keywords
            Token.Keyword: "#ff2e88",  # Neon Pink
            Token.Keyword.Type: "#00f9e5",  # Electric Cyan
            # Names
            Token.Name.Function: "#4fc3f7",  # Neon Sky Blue
            Token.Name.Class: "#ffe600",  # Neon Yellow
            Token.Name.Namespace: "#ff6ac1",  # Light Magenta
            Token.Name.Variable: "#ff4081",  # Bright Pink for variables
            Token.Name.Builtin: "#ff6bcb",  # Neon Violet (for built-ins like cout, cin)
            Token.Name: "#f1f1f1",  # Soft White fallback
            # Literals
            Token.Literal.Number: "#ff9100",  # Orange Glow
            Token.Literal.Number.Integer: "#ff9100",
            Token.Literal.Number.Float: "#ffcc00",  # Bright Yellow-Orange
            Token.Literal.String: "#72f98f",  # Neon Green
            Token.Literal.String.Double: "#72f98f",
            Token.Literal.String.Char: "#a2ffb1",  # Soft neon green for char
            Token.Literal.String.Escape: "#00ffc3",  # Aqua for escape sequences
            # Operators & Punctuation
            Token.Operator: "#00e5ff",  # Aqua Blue
            Token.Punctuation: "#cfcfcf",  # Light Gray
            # Comments
            Token.Comment.Single: "#4c4c4c",  # Dark Gray
            Token.Comment.Multiline: "#4c4c4c",  # Dark Gray
            Token.Comment.Preproc: "#ff6ac1",  # Light Magenta (for #include, etc.)
            Token.Comment: "#4c4c4c",  # General fallback
            # Text & whitespace
            Token.Text: "#ffffff",  # White for base text
        }

    def highlight(self, line: str) -> str:
        """
        Highlight a line using Pygments token types and mapped colors.

        Args:
            line (str): Code line to be styled.

        Returns:
            str: Marked-up line with span tags and color attributes.
        """
        return "".join(
            self._wrap(value.replace("\n", ""), self.colors.get(ttype, "#ffffff"))
            for ttype, value in lex(line, self.lexer)
        )
