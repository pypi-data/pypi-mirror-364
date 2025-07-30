from manim import MarkupText
from manim import UP, DOWN, LEFT, RIGHT, UL, UR, DR, DL

from ..core.flow_motion import FlowMotion
from .formatter import FlowFormatter


class FlowBlock(FlowMotion):
    """
    Base class for rendering file-based text or code blocks in flowmotion.

    Handles reading, formatting, line chunking, and Manim markup conversion.
    """

    def __init__(
        self, filepath, font="JetBrains Mono", font_size=18, is_code=False, max_lines=21
    ):
        """
        Initialize a FlowBlock.

        Args:
            filepath (str): Path to the text/code file.
            font (str): Font used for rendering (default: JetBrains Mono).
            font_size (int): Font size in px (default: 18).
            is_code (bool): Whether to apply syntax highlighting (default: False).
            max_lines (int): Max lines per chunk/block (default: 21).
        """
        super().__init__()
        self.filepath = filepath
        self.font = font
        self.font_size = font_size
        self.is_code = is_code
        self.max_lines = max_lines

        self.formatter = FlowFormatter(is_code)
        self.content = self.read(filepath)

        self.highlighted_lines = self.formatter.highlight_lines(self.content)

        self.chunks = self.break_lines(self.highlighted_lines, self.max_lines)
        self.markup = self.markup_list(self.chunks)

    def read(self, filepath):
        """
        Read the entire file content.

        Args:
            filepath (str): Path to the file.

        Returns:
            str: File content as a string.
        """
        with open(filepath, "r") as file:
            return file.read()

    def get(self):
        """
        Get the full highlighted text block.

        Returns:
            str: Highlighted lines joined into one string.
        """
        return "\n".join(self.highlighted_lines)

    def break_lines(self, lines: list, max_lines=21):
        """
        Break lines into chunks of size max_lines.

        Args:
            lines (list): List of highlighted lines.
            max_lines (int): Max number of lines per chunk.

        Returns:
            list: List of line chunks.
        """
        return [
            "\n".join(lines[i : i + max_lines]) for i in range(0, len(lines), max_lines)
        ]

    def markup(self, chunk):
        """
        Convert a line chunk to a Manim MarkupText object.

        Args:
            chunk (str): Chunked block of text.

        Returns:
            MarkupText: Positioned and styled Manim text object.
        """
        return (
            MarkupText(text=chunk, font=self.font, font_size=self.font_size)
            .to_corner(UL, buff=0.5)
            .shift(DOWN * 0.325)
        )

    def markup_list(self, chunks):
        """
        Convert all line chunks to MarkupText objects.

        Args:
            chunks (list): List of text chunks.

        Returns:
            list: List of MarkupText objects.
        """
        return [self.markup(chunk) for chunk in chunks]

    def __iter__(self):
        """Enable iteration over markup chunks."""
        return iter(self.markup)

    def __len__(self):
        """Return number of markup chunks."""
        return len(self.markup)

    def __getitem__(self, index):
        """
        Access a specific markup chunk.

        Args:
            index (int): Chunk index.

        Returns:
            MarkupText: The corresponding markup object.
        """
        return self.markup[index]
