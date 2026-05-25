"""Visual HUD elements generator for LF video frames."""

from lfdata.model import LFGame
from lfdata.replay import LFReplaySystem
from lfdata.video.element import UIElement


class VisualElementGenerator:
    """Generates the list of UI elements for a player at a specific time."""

    def __init__(self, game: LFGame, player_name: str | None = None):
        """Initializes the HUD element generator.

        Args:
            game: The LFGame data object.
            player_name: The codename of the player to focus the HUD on, or None.
        """
        self.game = game
        self.player_name = player_name
        self.entity_id = self._find_player_entity_id()

    def _find_player_entity_id(self) -> str | None:
        """Finds the entity ID matching the player codename.

        Returns:
            str | None: The entity ID if found, otherwise None.
        """
        if not self.player_name:
            return None
        for entity in self.game.entities:
            if (
                entity.type == "player"
                and entity.desc.lower() == self.player_name.lower()
            ):
                return entity.entity_id
        return None

    def generate_at(self, time_ms: int) -> list[UIElement]:
        """Generates HUD elements at a specific millisecond timestamp.

        This method simulates the game replay up to the timestamp, compiles
        basic, player, and scoreboard HUD elements, and returns them.

        Args:
            time_ms: The millisecond timestamp to generate elements for.

        Returns:
            list[UIElement]: The list of generated UI elements.
        """
        replay = LFReplaySystem(self.game)
        replay.run_up_to(time_ms)

        elements: list[UIElement] = []
        elements.extend(self._generate_basic_elements(replay, time_ms))
        elements.append(self._generate_scoreboard(replay, time_ms))
        elements.extend(self._generate_player_hud(replay, time_ms))

        return elements

    def _generate_basic_elements(
        self, replay: LFReplaySystem, time_ms: int
    ) -> list[UIElement]:
        """Generates the basic Game Type and Time HUD elements.

        This helper extracts game type and calculates capped game timer
        formatted as MM:SS.

        Args:
            replay: The simulated replay system.
            time_ms: The current millisecond timestamp.

        Returns:
            list[UIElement]: The basic HUD elements.
        """
        elements: list[UIElement] = []

        # Game type (bottom left)
        elements.append(
            UIElement(
                element_type="text",
                position="bottom left",
                text=f"Game Type: {self.game.game_type}",
            )
        )

        # Time (top right)
        actual_duration = self.game.duration
        if replay.game_ended_at is not None:
            actual_duration = replay.game_ended_at

        display_ms = time_ms
        if actual_duration is not None and display_ms > actual_duration:
            display_ms = actual_duration

        total_seconds = display_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        time_text = f"Time: {minutes:02d}:{seconds:02d}"

        elements.append(
            UIElement(
                element_type="text",
                position="top right",
                text=time_text,
            )
        )
        return elements

    def _generate_scoreboard(self, replay: LFReplaySystem, time_ms: int) -> UIElement:
        """Generates the structured Scoreboard HUD element.

        This helper computes scores, team totals, and player deactivation or
        elimination states for all active teams.

        Args:
            replay: The simulated replay system.
            time_ms: The current millisecond timestamp.

        Returns:
            UIElement: The scoreboard UI element.
        """
        sorted_teams = sorted(
            replay.game_state.teams.values(),
            key=lambda t: t.score,
            reverse=True,
        )

        teams_data = []
        for team in sorted_teams:
            players_data = []
            team_players = [
                p
                for p in replay.game_state.players.values()
                if p.team_index == team.team_index
            ]
            team_players.sort(key=lambda p: p.score, reverse=True)

            tot_score = 0
            tot_lives = 0
            tot_shots = 0
            tot_missiles = 0
            tot_spec = 0

            for p in team_players:
                codename = replay.entity_names.get(p.entity_id, p.entity_id)
                players_data.append(
                    {
                        "codename": codename,
                        "role_name": p.role.display_name,
                        "score": p.score,
                        "lives": p.lives,
                        "shots": p.shots,
                        "missiles": p.missiles,
                        "special_points": p.special_points,
                        "is_down": p.is_down(time_ms),
                        "is_eliminated": p.is_eliminated(),
                    }
                )
                tot_score += p.score
                tot_lives += p.lives
                tot_shots += p.shots
                tot_missiles += p.missiles
                tot_spec += p.special_points

            teams_data.append(
                {
                    "team_name": team.name,
                    "team_score": team.score,
                    "color_rgb": team.color_rgb,
                    "players": players_data,
                    "totals": {
                        "score": tot_score,
                        "lives": tot_lives,
                        "shots": tot_shots,
                        "missiles": tot_missiles,
                        "special_points": tot_spec,
                    },
                }
            )

        return UIElement(
            element_type="scoreboard",
            position="bottom left",
            scoreboard_data={"teams": teams_data},
        )

    def _generate_player_hud(
        self, replay: LFReplaySystem, time_ms: int
    ) -> list[UIElement]:
        """Generates focused player-specific HUD elements.

        This helper creates player name, role, stats, and downtime progress
        HUD elements if a player is focused.

        Args:
            replay: The simulated replay system.
            time_ms: The current millisecond timestamp.

        Returns:
            list[UIElement]: Focused player elements, or empty list.
        """
        if not self.entity_id:
            return []

        player_state = replay.game_state.players.get(self.entity_id)
        if not player_state:
            return []

        elements: list[UIElement] = []

        # Player name (top center)
        elements.append(
            UIElement(
                element_type="text",
                position="top center",
                text=f"Player: {self.player_name}",
            )
        )

        # Player role (top center)
        elements.append(
            UIElement(
                element_type="text",
                position="top center",
                text=f"Role: {player_state.role.display_name}",
            )
        )

        # Player score (top right)
        elements.append(
            UIElement(
                element_type="text",
                position="top right",
                text=f"Score: {player_state.score}",
            )
        )

        # Player lives (top left)
        elements.append(
            UIElement(
                element_type="text",
                position="top left",
                text=f"Lives: {player_state.lives}",
            )
        )

        # Player shots (top left)
        elements.append(
            UIElement(
                element_type="text",
                position="top left",
                text=f"Shots: {player_state.shots}",
            )
        )

        # Player missiles (top left)
        if player_state.role.start_missiles > 0:
            elements.append(
                UIElement(
                    element_type="text",
                    position="top left",
                    text=f"Missiles: {player_state.missiles}",
                )
            )

        # Player special points (top left)
        elements.append(
            UIElement(
                element_type="text",
                position="top left",
                text=f"Special Points: {player_state.special_points}",
            )
        )

        # Downtime bar
        if player_state.is_down(time_ms):
            safe_rem = max(0, player_state.resettable_starts_at - time_ms)
            res_base = max(time_ms, player_state.resettable_starts_at)
            resettable_rem = max(0, player_state.downtime_ends_at - res_base)
            elements.append(
                UIElement(
                    element_type="downtime_bar",
                    position="bottom center",
                    safe_ms=safe_rem,
                    resettable_ms=resettable_rem,
                )
            )

        return elements
