"""Classes representing the state of players, teams, and the game during
a replay.
"""

from lfdata.model import LFRole


class LFReplayPlayerState:
    """Tracks a single player's state during a game replay."""

    def __init__(self, entity_id: str, role: LFRole, team_index: int) -> None:
        """Initializes the player state with role-based start values.

        Args:
            entity_id: The ID of the game entity.
            role: The LFRole enum representing the player's role.
            team_index: The team index the player belongs to.
        """
        self.entity_id = entity_id
        self.role = role
        self.team_index = team_index
        self.lives = role.start_lives
        self.shots = role.start_shots
        self.missiles = role.start_missiles
        self.score = 0
        self._special_points = 0
        self.max_hp = role.max_hp
        self.hp = role.max_hp
        self.downtime_ends_at_ms = 0
        self.resettable_starts_at_ms = 0
        self.just_went_down_at_ms: int | None = None
        self.captured_bases: set[str] = set()
        self.has_rapid_fire = False
        self.nukes_activated: int = 0
        self.nukes_detonated: int = 0
        self.nuke_cancels: int = 0
        self.own_nuke_cancels: int = 0

    def is_eliminated(self) -> bool:
        """Returns True if the player has no lives left and is out of the
        game.
        """
        return self.lives <= 0

    def is_down(self, current_time_ms: int) -> bool:
        """Returns True if the player is currently deactivated / down.

        Args:
            current_time_ms: The current millisecond timestamp.

        Returns:
            bool: True if the player is currently down, False otherwise.
        """
        return current_time_ms < self.downtime_ends_at_ms

    def can_receive_resupply(self, current_time_ms: int) -> bool:
        """Checks if the player can receive resupply or team boost.

        A player is eligible to receive resupply if they are not down, or if
        they transitioned to down within the last 750 milliseconds.

        Args:
            current_time_ms: The current millisecond timestamp.

        Returns:
            bool: True if eligible, False otherwise.
        """
        if self.is_eliminated():
            return False
        if not self.is_down(current_time_ms):
            return True
        if self.just_went_down_at_ms is not None:
            elapsed_ms = current_time_ms - self.just_went_down_at_ms
            return 0 <= elapsed_ms <= 750
        return False

    def update_downtime(self, current_time_ms: int) -> None:
        """Restores player's HP if their downtime has expired.

        Args:
            current_time_ms: The current millisecond timestamp.
        """
        if self.is_eliminated():
            self.hp = 0
            return
        if self.hp == 0 and current_time_ms >= self.downtime_ends_at_ms:
            self.hp = self.max_hp
            self.just_went_down_at_ms = None

    def resupply_lives_from_medic(self) -> None:
        """Adds lives to player based on role-specific medic resupply values."""
        if self.is_eliminated():
            return
        self.lives = min(
            self.role.max_lives, self.lives + self.role.medic_lives_gain
        )

    def resupply_shots_from_ammo(self) -> None:
        """Adds shots to player based on role-specific ammo resupply values."""
        if self.is_eliminated():
            return
        self.shots = min(
            self.role.max_shots, self.shots + self.role.ammo_shots_gain
        )

    @property
    def special_points(self) -> int:
        """Returns the player's special points.

        Gets the number of special points the player currently has.

        Returns:
            int: The current special points, up to 99.
        """
        return self._special_points

    @special_points.setter
    def special_points(self, value: int) -> None:
        """Sets the player's special points, clamped between 0 and 99.

        Sets the number of special points, ensuring it never goes below 0 or
        exceeds 99.

        Args:
            value: The new special points value.
        """
        self._special_points = max(0, min(99, value))


class LFReplayTeamState:
    """Tracks a single team's state during a game replay."""

    def __init__(
        self, team_index: int, name: str, color_rgb: str = '#ffffff'
    ) -> None:
        """Initializes the team state.

        Args:
            team_index: The team index.
            name: The team name.
            color_rgb: The RGB hex color code.
        """
        self.team_index = team_index
        self.name = name
        self.color_rgb = color_rgb
        self.score = 0
        self.ranking = 1


class LFReplayGameState:
    """Tracks the overall game state, including all players and teams."""

    def __init__(
        self,
        players: list[LFReplayPlayerState],
        teams: list[LFReplayTeamState],
    ) -> None:
        """Initializes the game state.

        Args:
            players: List of player states.
            teams: List of team states.
        """
        self.players = {p.entity_id: p for p in players}
        self.teams = {t.team_index: t for t in teams}

    def update_team_scores_and_rankings(self) -> None:
        """Recalculates team scores and rankings based on player scores."""
        for team in self.teams.values():
            team.score = sum(
                p.score
                for p in self.players.values()
                if p.team_index == team.team_index
            )

        sorted_teams = sorted(
            self.teams.values(), key=lambda t: t.score, reverse=True
        )
        for rank, team in enumerate(sorted_teams, 1):
            team.ranking = rank
