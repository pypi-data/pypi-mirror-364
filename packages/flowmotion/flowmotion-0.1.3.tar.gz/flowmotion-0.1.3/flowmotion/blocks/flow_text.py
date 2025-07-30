from .flow_block import FlowBlock


class FlowText(FlowBlock):
    """
    Block for displaying plain text with line numbers in flowmotion.

    Inherits from FlowBlock with is_code set to False.
    """

    def __init__(self, filepath, font="JetBrains Mono", font_size=18):
        """
        Initialize a FlowText block.

        Args:
            filepath (str): Path to the text file.
            font (str): Font used for rendering (default: JetBrains Mono).
            font_size (int): Font size in px (default: 18).
        """
        super().__init__(filepath, font, font_size, False)
