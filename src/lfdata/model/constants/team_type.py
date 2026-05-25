"""Enums representing LF game teams and metadata."""

import enum

from lfdata.model.constants.color import LFTeamColor


class LFTeamType(enum.Enum):
    """Defines team types in LF SM5 games, linking indexes to team colors.

    Includes display names and the color enum.
    """

    FIRE = (0, 'Fire Team', LFTeamColor.FIRE)
    EARTH = (1, 'Earth Team', LFTeamColor.EARTH)
    NEUTRAL = (2, 'Neutral', LFTeamColor.NONE)

    def __init__(self, team_index: int, display_name: str, color: LFTeamColor):
        """Initializes the team type.

        Args:
            team_index: The index of the team.
            display_name: The display name of the team.
            color: The color enum of the team.
        """
        self.team_index = team_index
        self.display_name = display_name
        self.color = color

    @classmethod
    def from_index(cls, team_index: int) -> 'LFTeamType':
        """Retrieves a team type by its team index.

        Args:
            team_index: The index of the team.

        Returns:
            LFTeamType: The matching team type.

        Raises:
            ValueError: If the team_index is not valid.
        """
        for ttype in cls:
            if ttype.team_index == team_index:
                return ttype
        raise ValueError(f"Invalid team index: {team_index}")
