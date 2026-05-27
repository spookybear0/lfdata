"""Enums representing LF team colors and metadata."""

import enum


class LFTeamColor(enum.Enum):
    """Defines team colors used in LF games with internal name and RGB color code.

    Includes display names and RGB hex values.
    """

    FIRE = (11, 'Fire', '#FF5000')
    EARTH = (13, 'Earth', '#A0FF00')
    NONE = (0, 'None', '#808080')

    def __init__(self, color_enum: int, display_name: str, rgb: str):
        """Initializes the team color.

        Args:
            color_enum: The integer ID from TDF files.
            display_name: The display name of the color.
            rgb: The CSS/RGB hex color value.
        """
        self.color_enum = color_enum
        self.display_name = display_name
        self.rgb = rgb

    @classmethod
    def from_enum(cls, color_enum: int) -> 'LFTeamColor':
        """Retrieves a team color by its TDF color code.

        Args:
            color_enum: The color code integer.

        Returns:
            LFTeamColor: The matching color enum.

        Raises:
            ValueError: If the color_enum is not valid.
        """
        for color in cls:
            if color.color_enum == color_enum:
                return color
        raise ValueError(f'Invalid color enum: {color_enum}')
