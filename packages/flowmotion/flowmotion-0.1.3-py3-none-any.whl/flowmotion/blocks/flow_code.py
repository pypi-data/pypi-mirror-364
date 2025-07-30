from .flow_block import FlowBlock


class FlowCode(FlowBlock):
    """
    Block for displaying syntax-highlighted code in flowmotion.

    Inherits from FlowBlock with is_code set to True.
    """

    def __init__(self, filepath, font="JetBrains Mono", font_size=18):
        """
        Initialize a FlowCode block.

        Args:
            filepath (str): Path to the source code file.
            font (str): Font used for rendering (default: JetBrains Mono).
            font_size (int): Font size in px (default: 18).
        """
        super().__init__(filepath, font, font_size, True)
