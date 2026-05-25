"""Classes representing the state of players, teams, and the game during a replay."""

from lfdata.model import LFRole


class LFReplayPlayerState:
    """Tracks a single player's state during a game replay."""

    def __init__(self, entity_id: str, role: LFRole, team_index: int):
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
        self.special_points = 0

    def resupply_lives_from_medic(self) -> None:
        """Adds lives to player based on role-specific medic resupply values."""
        self.lives = min(
            self.role.max_lives, self.lives + self.role.medic_lives_gain
        )

    def resupply_shots_from_ammo(self) -> None:
        """Adds shots to player based on role-specific ammo resupply values."""
        self.shots = min(
            self.role.max_shots, self.shots + self.role.ammo_shots_gain
        )


class LFReplayTeamState:
    """Tracks a single team's state during a game replay."""

    def __init__(self, team_index: int, name: str):
        """Initializes the team state.

        Args:
            team_index: The team index.
            name: The team name.
        """
        self.team_index = team_index
        self.name = name
        self.score = 0
        self.ranking = 1


class LFReplayGameState:
    """Tracks the overall game state, including all players and teams."""

    def __init__(
        self,
        players: list[LFReplayPlayerState],
        teams: list[LFReplayTeamState],
    ):
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
