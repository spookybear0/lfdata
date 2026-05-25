"""Classes representing the state of players, teams, and the game during a replay."""


class LFReplayPlayerState:
    """Tracks a single player's state during a game replay."""

    def __init__(self, entity_id: str, role: str, team_index: int):
        """Initializes the player state with role-based start values.

        Args:
            entity_id: The ID of the game entity.
            role: The role name (e.g. Commander, Scout).
            team_index: The team index the player belongs to.
        """
        self.entity_id = entity_id
        self.role = role
        self.team_index = team_index
        self.lives = 0
        self.shots = 0
        self.missiles = 0
        self.score = 0
        self.special_points = 0
        self._init_startup_state()

    def _init_startup_state(self) -> None:
        """Initializes role-based lives, shots, and missiles."""
        role_lower = self.role.lower()
        if role_lower == 'commander':
            self.lives = 15
            self.shots = 30
            self.missiles = 5
        elif role_lower == 'heavy':
            self.lives = 10
            self.shots = 20
            self.missiles = 5
        elif role_lower == 'scout':
            self.lives = 15
            self.shots = 30
            self.missiles = 0
        elif role_lower == 'medic':
            self.lives = 20
            self.shots = 15
            self.missiles = 0
        elif role_lower == 'ammo':
            self.lives = 10
            self.shots = 0
            self.missiles = 0

    def resupply_lives_from_medic(self) -> None:
        """Adds lives to player based on role-specific medic resupply values."""
        role_lower = self.role.lower()
        gain = 0
        max_lives = 0
        if role_lower == 'scout':
            gain, max_lives = 3, 30
        elif role_lower == 'medic':
            gain, max_lives = 0, 20
        elif role_lower == 'ammo':
            gain, max_lives = 3, 20
        elif role_lower == 'heavy':
            gain, max_lives = 3, 20
        elif role_lower == 'commander':
            gain, max_lives = 4, 30

        self.lives = min(max_lives, self.lives + gain)

    def resupply_shots_from_ammo(self) -> None:
        """Adds shots to player based on role-specific ammo resupply values."""
        role_lower = self.role.lower()
        gain = 0
        max_shots = 0
        if role_lower == 'scout':
            gain, max_shots = 10, 60
        elif role_lower == 'medic':
            gain, max_shots = 5, 20
        elif role_lower == 'heavy':
            gain, max_shots = 5, 40
        elif role_lower == 'commander':
            gain, max_shots = 5, 60

        self.shots = min(max_shots, self.shots + gain)


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
