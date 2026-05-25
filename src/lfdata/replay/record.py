"""Class representing a snapshot of the game state changes after a specific event."""


class LFReplayEventRecord:
    """Represents a record of changes caused by a single event in the replay."""

    def __init__(
        self,
        event_id: int,
        time: int,
        description: str,
        player_changes: dict[str, dict[str, any]],
        team_changes: dict[int, dict[str, any]],
    ):
        """Initializes the event record.

        Args:
            event_id: The ID of the event record in the database.
            time: The millisecond timestamp of the event.
            description: A string description of the event.
            player_changes: A dictionary of player entity_id to attribute changes.
            team_changes: A dictionary of team_index to attribute changes.
        """
        self.event_id = event_id
        self.time = time
        self.description = description
        self.player_changes = player_changes
        self.team_changes = team_changes

    def __repr__(self) -> str:
        """Returns a string representation of the event record.

        Returns:
            str: The string representation.
        """
        return (
            f"LFReplayEventRecord(time={self.time}, "
            f"description='{self.description}')"
        )
