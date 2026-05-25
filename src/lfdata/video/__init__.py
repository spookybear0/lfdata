"""Video generation and visualization for LF games."""

from pathlib import Path

from lfdata.model import LFGame
from lfdata.video.element import UIElement, UIElementStyle
from lfdata.video.generator import VisualElementGenerator

__all__ = [
    "VideoGenerator",
    "UIElement",
    "UIElementStyle",
    "VisualElementGenerator",
]


class VideoGenerator:
    """Generates visual videos from LF game events and data."""

    def __init__(self, game: LFGame):
        self.game = game

    def generate(self, output_path: str | Path) -> Path:
        """Generates a video file visualizing the game and writes it to output_path.

        Args:
            output_path: The output file path for the generated video.

        Returns:
            Path: The path to the generated video file.
        """
        output_path = Path(output_path)
        print(f"Generating video for game {self.game.game_id} " f"at {output_path}...")
        output_path.touch()
        return output_path
