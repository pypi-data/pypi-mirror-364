# flowmotion/blocks/flow_document.py
from manim import *
from .highlighter import FlowHighlighter
from ..core.flow_motion import FlowMotion


class FlowDocument(FlowMotion):
    def __init__(
        self,
        filepath,
        font,
        font_size=18,
        max_lines_per_chunk=21,
        highlighter=FlowHighlighter(),
    ):
        super().__init__()
        self.filepath = filepath
        self.highlighter = highlighter
        self.font = font
        self.font_size = font_size
        self.max_lines_per_chunk = max_lines_per_chunk

        self.line_num = 0
        self.line_num_color = "#555555"

        self.content = self._read(self.filepath)
        self.chunks = self._split(self.content)

        self.markup_chunks = self.create_markup_chunks(self.chunks)

    def __len__(self):
        return len(self.chunks)

    def __iter__(self):
        return iter(self.markup_chunks)

    def _read(self, document_path):
        with open(document_path, "r") as file:
            return file.read()

    def _split(self, content: str):
        lines = content.split("\n")
        return [
            "\n".join(lines[i : i + self.max_lines_per_chunk])
            for i in range(0, len(lines), self.max_lines_per_chunk)
        ]

    def _next_line_num(self):
        self.line_num += 1
        return self.line_num

    def create_markup(self, content: str) -> MarkupText:
        formatted_lines = []
        lines = content.split("\n")

        for line in lines:
            # Generate the syntax-highlighted line
            highlighted = self.highlighter.highlight(line)
            line_number = self.highlighter._wrap(
                str(self._next_line_num()).rjust(3) + " ", self.line_num_color
            )
            formatted_lines.append(line_number + highlighted)

        # Join lines with newlines and create a MarkupText object
        full_markup = "\n".join(formatted_lines)
        return MarkupText(full_markup, font=self.font, font_size=self.font_size)

    def create_markup_chunks(self, chunks):
        markup_chunks = []
        for chunk in chunks:
            markup_chunk = self.create_markup(chunk)
            markup_chunk.to_corner(UL, buff=0.5).shift(DOWN * 0.325)
            markup_chunks.append(markup_chunk)
        return markup_chunks
