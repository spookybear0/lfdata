"""Normalizer for LF game types."""

import re


class GameTypeNormalizer:
    """Normalizes game types using regex pattern matching.

    Maintains a list of regexes that map to target normalized game type
    strings, and uses them to identify a standardized name for game types.
    """

    def __init__(self) -> None:
        """Initializes the normalizer with default regex mappings."""
        self._mappings: list[tuple[re.Pattern[str], str]] = [
            (re.compile(r'Space\s*Marines\s*5'), 'SM5'),
            (re.compile(r'SM5'), 'SM5'),
            (re.compile(r'Laser\s*[bB]all'), 'Laserball'),
        ]

    def normalize(self, game_type: str) -> str | None:
        """Derives a normalized game type from the given raw game type.

        Iterates through the compiled regular expression mappings and matches
        against the raw game type string. Returns the first matching normalized
        value.

        Args:
            game_type: The raw game type string to normalize.

        Returns:
            str | None: The normalized game type string, or None if no
                pattern matches.
        """
        for pattern, replacement in self._mappings:
            if pattern.search(game_type):
                return replacement
        return None
