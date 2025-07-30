import math
from manim import *
from pygments import lex
from pygments.lexers import CppLexer
from pygments.token import Token


class FlowText:
    def __init__(self, text, font="JetBrains Mono", font_size=18, max_lines=21):
        self.token_colors = self._get_token_colors()
        self.font = font
        self.font_size = font_size
        self.max_lines = max_lines
        self.current_line_num = 0
        self.chunks = self._create_chunks(text)
        self.markup_chunks = [self._highlight_code(chunk) for chunk in self.chunks]

    def _get_current_line_num(self):
        self.current_line_num += 1
        return self.current_line_num

    def _get_token_colors(self):
        token_colors = {
            # 🟣 Keywords
            Token.Keyword: "#ff2e88",  # Neon Pink
            Token.Keyword.Type: "#00f9e5",  # Electric Cyan
            # 🔵 Names
            Token.Name.Function: "#4fc3f7",  # Neon Sky Blue
            Token.Name.Class: "#ffe600",  # Neon Yellow
            Token.Name.Namespace: "#ff6ac1",  # Light Magenta
            Token.Name.Variable: "#ff4081",  # Bright Pink for variables
            Token.Name.Builtin: "#ff6bcb",  # Neon Violet (for built-ins like cout, cin)
            Token.Name: "#f1f1f1",  # Soft White fallback
            # 🔢 Literals
            Token.Literal.Number: "#ff9100",  # Orange Glow
            Token.Literal.Number.Integer: "#ff9100",
            Token.Literal.Number.Float: "#ffcc00",  # Bright Yellow-Orange
            Token.Literal.String: "#72f98f",  # Neon Green
            Token.Literal.String.Double: "#72f98f",
            Token.Literal.String.Char: "#a2ffb1",  # Soft neon green for char
            Token.Literal.String.Escape: "#00ffc3",  # Aqua for escape sequences
            # ➕ Operators & Punctuation
            Token.Operator: "#00e5ff",  # Aqua Blue
            Token.Punctuation: "#cfcfcf",  # Light Gray
            # 🧾 Comments
            Token.Comment.Single: "#4c4c4c",  # Dark Gray
            Token.Comment.Multiline: "#4c4c4c",  # Dark Gray
            Token.Comment.Preproc: "#ff6ac1",  # Light Magenta (for #include, etc.)
            Token.Comment: "#4c4c4c",  # General fallback
            # ⚪ Text & whitespace
            Token.Text: "#ffffff",  # White for base text
        }
        return token_colors

    def _highlight_code(self, code: str, font_size: int = 18) -> MarkupText:
        def color_to_hex(color):
            r, g, b = color_to_rgb(color)
            return "#{:02x}{:02x}{:02x}".format(
                int(r * 255), int(g * 255), int(b * 255)
            )

        grey_color = "#555555"
        formatted_lines = []
        lines = code.split("\n")

        for line in lines:
            # Generate the syntax-highlighted line
            highlighted = ""
            for token_type, value in lex(line, CppLexer()):
                color = self.token_colors.get(token_type, WHITE)
                hex_color = color_to_hex(color)
                value = (
                    value.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                highlighted += f'<span foreground="{hex_color}">{value}</span>'

            # Add grey line number (1-based indexing)
            line_number = f'<span foreground="{grey_color}">{str(self._get_current_line_num()).rjust(3)} </span>'
            formatted_lines.append(line_number + highlighted)

        # Join lines with newlines and create a MarkupText object
        full_markup = "".join(formatted_lines)
        return (
            MarkupText(full_markup, font=self.font, font_size=font_size)
            .to_corner(UL, buff=0.5)
            .shift(DOWN * 0.325)
        )

    def _create_chunks(self, function: str):
        lines = [line for line in function.split("\n")]  # if line.strip()]
        total_lines = len(lines)
        # Initial chunk count assuming fixed-size chunks
        raw_chunks = math.ceil(total_lines / self.max_lines)

        # If last chunk would be much smaller, rebalance
        if total_lines % self.max_lines != 0:
            # Redistribute lines into raw_chunks equally
            base_chunk_size = total_lines // raw_chunks
            remainder = total_lines % raw_chunks

            chunks = []
            start = 0
            for i in range(raw_chunks):
                size = base_chunk_size + (1 if i < remainder else 0)
                end = start + size
                chunks.append("\n".join(lines[start:end]))
                start = end
            return chunks
        else:
            # Perfect split
            return [
                "\n".join(lines[i : i + self.max_lines])
                for i in range(0, total_lines, self.max_lines)
            ]

    def _create_chunks(self, function: str):
        lines = function.split("\n")
        return [
            "\n".join(lines[i : i + self.max_lines])
            for i in range(0, len(lines), self.max_lines)
        ]

    def _animate_chunk(self, markup_chunk):
        return (
            AnimationGroup(
                AddTextLetterByLetter(markup_chunk, time_per_char=0.01),
            ),
            AnimationGroup(FadeOut(markup_chunk)),
        )

    def __len__(self):
        return len(self.markup_chunks)

    def __iter__(self):
        return iter([self._animate_chunk(chunk) for chunk in self.markup_chunks])
