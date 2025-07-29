from manim import *


class FlowScene(Scene):
    def __init__(self, **kwargs):
        config.background_color = "#121212"
        config.pixel_width = 1920
        config.pixel_height = 1080
        config.verbosity = "ERROR"
        config.progress_bar = "none"
        super().__init__(**kwargs)
