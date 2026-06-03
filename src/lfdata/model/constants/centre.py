"""Enums representing LF centres and metadata."""

import dataclasses
import enum


@dataclasses.dataclass(frozen=True)
class LFCentreStats:
    """Statistics and metadata for a centre.

    Attributes:
        country_code: The country code integer.
        location_code: The location code integer.
        arena_name: The name of the arena.
    """

    country_code: int
    location_code: int
    arena_name: str

    @property
    def centre_code(self) -> str:
        """Returns the centre code string (e.g. '4-43')."""
        return f'{self.country_code}-{self.location_code}'


class LFCentre(enum.Enum):
    """Defines centres used in LF games with country, location, and arena name."""

    BRISBANE = LFCentreStats(1, 1, 'Brisbane')
    ST_GEORGE = LFCentreStats(4, 2, 'St George')
    INVASION = LFCentreStats(4, 43, 'Invasion')
    AUCKLAND_WAIRAU = LFCentreStats(3, 3, 'Auckland Wairau')
    SYRACUSE = LFCentreStats(4, 23, 'Syracuse')
    LOVELAND = LFCentreStats(4, 19, 'Loveland')
    CARMICHAEL = LFCentreStats(4, 3, 'Lasertag of Carmichael')
    ATLANTIS = LFCentreStats(4, 12, 'Atlantis Laser Tag')
    DARMSTADT = LFCentreStats(21, 70, 'LaserTag Darmstadt')
    DETROIT = LFCentreStats(4, 6, 'Detroit')
    AUCKLAND_GAME_OVER = LFCentreStats(3, 7, 'Auckland Game Over')
    HUDDERSFIELD = LFCentreStats(7, 10, 'Huddersfield')
    PETERBOROUGH = LFCentreStats(7, 2, 'Peterborough')
    SYDNEY_UNDERWORLD = LFCentreStats(1, 64, 'Sydney Underworld')
    CHELTANHAM = LFCentreStats(7, 13, 'Cheltanham')

    def __init__(self, stats: LFCentreStats) -> None:
        """Initializes the centre.

        Args:
            stats: The centre metadata statistics object.
        """
        self.country_code = stats.country_code
        self.location_code = stats.location_code
        self.arena_name = stats.arena_name
        self.centre_code = stats.centre_code

    @classmethod
    def from_code(cls, centre_code: str) -> 'LFCentre':
        """Retrieves a centre by its centre code (e.g. '4-43').

        Args:
            centre_code: The centre code string.

        Returns:
            LFCentre: The matching centre enum.

        Raises:
            ValueError: If the centre_code is not valid.
        """
        for centre in cls:
            if centre.centre_code == centre_code:
                return centre
        raise ValueError(f'Invalid centre code: {centre_code}')
