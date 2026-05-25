"""Visual HUD elements generator for LF video frames."""

import bisect
from typing import Any

from lfdata.model import LFGame
from lfdata.replay import LFReplaySystem
from lfdata.replay.state import LFReplayPlayerState, LFReplayTeamState
from lfdata.video.element import UIElement, UIElementStyle

DEFAULT_CONFIG: dict[str, Any] = {
    "font": "Verdana",
    "style": "normal",
    "size": 20,
    "color": "#ffffffff",
    "background_color": "#00000000",
    "fade_out_time": 2.0,
    "fps": 60,
    "extra_footage_ms": 10000,
    "player_name": None,
    "resolution": [1920, 1080],
    "animation": "ease-in-out",
    "elements": {
        "game_type": {
            "enabled": True,
            "x": 0.1,
            "y": 0.9,
            "align": "left",
            "style": {"size": 10},
        },
        "time": {
            "enabled": True,
            "x": 0.9,
            "y": 0.5,
            "align": "right",
            "style": {"size": 20},
        },
        "player_name": {
            "enabled": True,
            "x": 0.5,
            "y": 0.05,
            "align": "center",
            "style": {"size": 18},
        },
        "player_role": {
            "enabled": True,
            "x": 0.5,
            "y": 0.09,
            "align": "center",
            "style": {"size": 16},
        },
        "player_lives": {
            "enabled": True,
            "x": 0.2,
            "y": 0.13,
            "align": "left",
            "style": {"size": 18},
        },
        "player_shots": {
            "enabled": True,
            "x": 0.4,
            "y": 0.13,
            "align": "left",
            "style": {"size": 18},
        },
        "player_missiles": {
            "enabled": True,
            "x": 0.6,
            "y": 0.13,
            "align": "left",
            "style": {"size": 18},
        },
        "player_special_points": {
            "enabled": True,
            "x": 0.8,
            "y": 0.13,
            "align": "left",
            "style": {"size": 18},
        },
        "player_score": {
            "enabled": True,
            "x": 0.9,
            "y": 0.05,
            "align": "right",
            "style": {"size": 18},
        },
        "scoreboard": {
            "enabled": True,
            "x": 0.1,
            "y": 0.6,
            "align": "left",
        },
        "downtime": {
            "enabled": True,
            "top_left": [0.3, 0.3],
            "bottom_right": [0.7, 0.35],
        },
        "player_events": {
            "enabled": True,
            "x": 0.5,
            "y": 0.4,
            "align": "center",
            "style": {"size": 18},
        },
        "game_events": {
            "enabled": True,
            "x": 0.5,
            "y": 0.45,
            "align": "center",
            "style": {"size": 20},
        },
    },
}


def _merge_configs(base: dict[str, Any], loaded: dict[str, Any]) -> dict[str, Any]:
    """Recursively merges a loaded configuration dict into base defaults.

    Args:
        base: The default configuration dictionary.
        loaded: The user-supplied configuration dictionary.

    Returns:
        dict[str, Any]: The recursively merged configuration dictionary.
    """
    result: dict[str, Any] = {}
    for k, v in base.items():
        if k in loaded:
            if isinstance(v, dict) and isinstance(loaded[k], dict):
                result[k] = _merge_configs(v, loaded[k])
            else:
                result[k] = loaded[k]
        else:
            if isinstance(v, dict):
                result[k] = _merge_configs(v, {})
            else:
                result[k] = v
    for k, v in loaded.items():
        if k not in result:
            result[k] = v
    return result


def apply_animation(p: float, name: str) -> float:
    """Applies the specified animation function to progress value p.

    Args:
        p: Linear progress value from 0.0 to 1.0.
        name: Name of the animation function.

    Returns:
        float: The interpolated progress value.
    """
    p = max(0.0, min(1.0, p))
    if name == "linear":
        return p
    elif name == "ease-in":
        return p * p
    elif name == "ease-out":
        return p * (2.0 - p)
    elif name == "ease-in-out":
        return p * p * (3.0 - 2.0 * p)
    else:
        return p


def get_fade_alpha(elapsed_ms: int, total_ms: int, function_name: str) -> float:
    """Calculates fade-out alpha (1.0 to 0.0) based on elapsed duration.

    Args:
        elapsed_ms: Milliseconds elapsed since the fade started.
        total_ms: Total duration of the fade in milliseconds.
        function_name: Name of the animation function.

    Returns:
        float: The calculated alpha opacity value.
    """
    if total_ms <= 0:
        return 0.0
    p = elapsed_ms / total_ms
    p = max(0.0, min(1.0, p))
    return 1.0 - apply_animation(p, function_name)


def get_visual_rank(
    team_idx: int,
    t: int,
    transitions: list[tuple[int, float, int]],
    final_rank: int,
    animation_func: str,
) -> float:
    """Calculates the animated visual rank of a team at time t.

    Args:
        team_idx: The team index.
        t: The current millisecond timestamp.
        transitions: The precomputed rank swap transitions.
        final_rank: The final target rank of the team.
        animation_func: The animation function to apply.

    Returns:
        float: The animated visual rank position.
    """
    last_trans = None
    for trans in transitions:
        if trans[0] <= t:
            last_trans = trans
        else:
            break

    if last_trans is None:
        if transitions:
            return transitions[0][1]
        return float(final_rank)

    t_start, v_start, target_rank = last_trans
    elapsed = t - t_start
    if elapsed < 1000:
        p = elapsed / 1000.0
        p_anim = apply_animation(p, animation_func)
        return v_start + (target_rank - v_start) * p_anim
    else:
        return float(target_rank)


class VisualElementGenerator:
    """Generates the list of UI elements for a player at a specific time."""

    def __init__(
        self,
        game: LFGame,
        player_name: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        """Initializes the HUD element generator.

        Args:
            game: The LFGame data object.
            player_name: The codename of the player to focus the HUD on, or None.
            config: Optional configuration override dictionary.
        """
        self.game = game
        self.player_name = player_name
        self.entity_id = self._find_player_entity_id()
        self.entity_names = {e.entity_id: e.desc for e in game.entities}

        if config is None:
            self.config = DEFAULT_CONFIG
        else:
            self.config = _merge_configs(DEFAULT_CONFIG, config)

        self.snapshots: list[
            tuple[
                int,
                dict[str, LFReplayPlayerState],
                dict[int, LFReplayTeamState],
            ]
        ] = []
        self.event_log: list[dict[str, Any]] = []
        self.team_transitions: dict[int, list[tuple[int, float, int]]] = {}
        self.game_ended_at: int | None = None

        self._precompute_replay()

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

    def _copy_player_state(self, p: LFReplayPlayerState) -> LFReplayPlayerState:
        """Deep-copies essential fields of a player state.

        Args:
            p: The source player state.

        Returns:
            LFReplayPlayerState: The cloned player state.
        """
        new_p = LFReplayPlayerState(p.entity_id, p.role, p.team_index)
        new_p.lives = p.lives
        new_p.shots = p.shots
        new_p.missiles = p.missiles
        new_p.score = p.score
        new_p.special_points = p.special_points
        new_p.max_hp = p.max_hp
        new_p.hp = p.hp
        new_p.downtime_ends_at = p.downtime_ends_at
        new_p.resettable_starts_at = p.resettable_starts_at
        new_p.captured_bases = set(p.captured_bases)
        return new_p

    def _copy_team_state(self, t: LFReplayTeamState) -> LFReplayTeamState:
        """Deep-copies essential fields of a team state.

        Args:
            t: The source team state.

        Returns:
            LFReplayTeamState: The cloned team state.
        """
        new_t = LFReplayTeamState(t.team_index, t.name, t.color_rgb)
        new_t.score = t.score
        new_t.ranking = t.ranking
        return new_t

    def _precompute_replay(self) -> None:
        """Runs simulation once, caching snapshots and transition times."""
        replay = LFReplaySystem(self.game)

        # Initial snapshots at time 0
        self.snapshots.append(
            (
                0,
                {
                    pid: self._copy_player_state(p)
                    for pid, p in replay.game_state.players.items()
                },
                {
                    tid: self._copy_team_state(t)
                    for tid, t in replay.game_state.teams.items()
                },
            )
        )

        team_ranks = {tid: t.ranking for tid, t in replay.game_state.teams.items()}
        self.team_transitions = {tid: [] for tid in team_ranks}
        last_trans_time = {tid: 0 for tid in team_ranks}
        visual_rank_at_last_trans = {
            tid: float(t.ranking) for tid, t in replay.game_state.teams.items()
        }

        eliminated_teams: set[int] = set()
        sorted_events = sorted(self.game.events, key=lambda e: e.time)

        for event in sorted_events:
            for player in replay.game_state.players.values():
                player.update_downtime(event.time)

            desc = replay._dispatch_event(event)
            replay.game_state.update_team_scores_and_rankings()

            # Check newly eliminated teams
            active_teams = {p.team_index for p in replay.game_state.players.values()}
            for team_idx in active_teams:
                if team_idx not in eliminated_teams:
                    team_players = [
                        p
                        for p in replay.game_state.players.values()
                        if p.team_index == team_idx
                    ]
                    if team_players and all(p.is_eliminated() for p in team_players):
                        eliminated_teams.add(team_idx)
                        team_name = replay.game_state.teams[team_idx].name
                        self.event_log.append(
                            {
                                "time": event.time,
                                "desc": f"Team {team_name} Eliminated",
                                "is_important": True,
                                "actor_id": None,
                                "target_id": None,
                            }
                        )

            self.snapshots.append(
                (
                    event.time,
                    {
                        pid: self._copy_player_state(p)
                        for pid, p in replay.game_state.players.items()
                    },
                    {
                        tid: self._copy_team_state(t)
                        for tid, t in replay.game_state.teams.items()
                    },
                )
            )

            is_important = event.event_type in [
                "0100",
                "0101",
                "0404",
                "0405",
                "0204",
                "0303",
                "0B03",
            ]
            if desc:
                self.event_log.append(
                    {
                        "time": event.time,
                        "desc": desc,
                        "is_important": is_important,
                        "actor_id": event.actor_entity_id,
                        "target_id": event.target_entity_id,
                    }
                )

            # Check rank transitions
            for tid, t in replay.game_state.teams.items():
                if t.ranking != team_ranks[tid]:
                    t_last = last_trans_time[tid]
                    v_last = visual_rank_at_last_trans[tid]
                    target_last = team_ranks[tid]

                    elapsed = event.time - t_last
                    if elapsed < 1000:
                        p = elapsed / 1000.0
                        p_anim = apply_animation(
                            p, self.config.get("animation", "ease-in-out")
                        )
                        v_curr = v_last + (target_last - v_last) * p_anim
                    else:
                        v_curr = float(target_last)

                    self.team_transitions[tid].append((event.time, v_curr, t.ranking))
                    last_trans_time[tid] = event.time
                    visual_rank_at_last_trans[tid] = v_curr
                    team_ranks[tid] = t.ranking

        self.game_ended_at = replay.game_ended_at

    def _get_state_at(
        self, time_ms: int
    ) -> tuple[dict[str, LFReplayPlayerState], dict[int, LFReplayTeamState]]:
        """Retrieves and interpolates player/team states at time_ms.

        Args:
            time_ms: The millisecond timestamp.

        Returns:
            tuple: Cloned player and team states at the timestamp.
        """
        times = [snap[0] for snap in self.snapshots]
        idx = bisect.bisect_right(times, time_ms)
        if idx == 0:
            _, players, teams = self.snapshots[0]
        else:
            _, players, teams = self.snapshots[idx - 1]

        cloned_players = {pid: self._copy_player_state(p) for pid, p in players.items()}
        cloned_teams = {tid: self._copy_team_state(t) for tid, t in teams.items()}

        for player in cloned_players.values():
            player.update_downtime(time_ms)

        return cloned_players, cloned_teams

    def _create_ui_element(
        self, element_key: str, text: str | None = None, **kwargs: Any
    ) -> UIElement | None:
        """Resolves configuration and styling to construct a UIElement.

        Args:
            element_key: Key of the element in the configuration.
            text: The optional text string of the element.
            kwargs: Extra attributes for initialization.

        Returns:
            UIElement | None: The element if enabled, otherwise None.
        """
        el_config = self.config.get("elements", {}).get(element_key, {})
        if not el_config.get("enabled", True):
            return None

        style_config = el_config.get("style", {})
        global_style = {
            "font": self.config.get("font", "Verdana"),
            "style": self.config.get("style", "normal"),
            "size": self.config.get("size", 20),
            "color": self.config.get("color", "#ffffffff"),
            "background_color": self.config.get("background_color", "#00000000"),
        }

        font = style_config.get("font", global_style["font"])
        style_type = style_config.get("style", global_style["style"])
        size = style_config.get("size", el_config.get("size", global_style["size"]))
        color = style_config.get("color", global_style["color"])
        bg_color = style_config.get(
            "background_color", global_style["background_color"]
        )

        style = UIElementStyle(
            font=font,
            style=style_type,
            size=size,
            color=color,
            background_color=bg_color,
        )

        x = el_config.get("x")
        y = el_config.get("y")
        align = el_config.get("align")
        top_left = el_config.get("top_left")
        bottom_right = el_config.get("bottom_right")

        # Backward compatibility translation:
        pos_compat = ""
        if x == 0.1 and y == 0.9:
            pos_compat = "bottom left"
        elif x == 0.9 and y == 0.5:
            pos_compat = "top right"
        elif x == 0.5 and y == 0.05:
            pos_compat = "top center"
        elif x == 0.5 and y == 0.09:
            pos_compat = "top center"
        elif x == 0.9 and y == 0.05:
            pos_compat = "top right"
        elif x == 0.2 and y == 0.13:
            pos_compat = "top left"
        elif x == 0.4 and y == 0.13:
            pos_compat = "top left"
        elif x == 0.6 and y == 0.13:
            pos_compat = "top left"
        elif x == 0.8 and y == 0.13:
            pos_compat = "top left"

        kwargs_copy = dict(kwargs)
        elem_type = kwargs_copy.pop("element_type", "text")

        return UIElement(
            element_type=elem_type,
            position=pos_compat,
            text=text,
            style=style,
            x=x,
            y=y,
            align=align,
            top_left=top_left,
            bottom_right=bottom_right,
            **kwargs_copy,
        )

    def _create_scoreboard_element(
        self,
        teams: dict[int, LFReplayTeamState],
        players: dict[str, LFReplayPlayerState],
        time_ms: int,
    ) -> UIElement | None:
        """Constructs the scoreboard element containing animated ranks.

        Args:
            teams: Map of team index to team state.
            players: Map of player ID to player state.
            time_ms: The current millisecond timestamp.

        Returns:
            UIElement | None: The scoreboard element if enabled.
        """
        el_config = self.config.get("elements", {}).get("scoreboard", {})
        if not el_config.get("enabled", True):
            return None

        anim = self.config.get("animation", "ease-in-out")
        teams_data = []

        for team in teams.values():
            trans_list = self.team_transitions.get(team.team_index, [])
            vr = get_visual_rank(
                team.team_index, time_ms, trans_list, team.ranking, anim
            )

            players_data = []
            team_players = [
                p for p in players.values() if p.team_index == team.team_index
            ]
            team_players.sort(key=lambda p: p.score, reverse=True)

            tot_score = 0
            tot_lives = 0
            tot_shots = 0
            tot_missiles = 0
            tot_spec = 0

            for p in team_players:
                codename = self.entity_names.get(p.entity_id, p.entity_id)
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
                    "team_index": team.team_index,
                    "team_name": team.name,
                    "team_score": team.score,
                    "color_rgb": team.color_rgb,
                    "players": players_data,
                    "visual_rank": vr,
                    "totals": {
                        "score": tot_score,
                        "lives": tot_lives,
                        "shots": tot_shots,
                        "missiles": tot_missiles,
                        "special_points": tot_spec,
                    },
                }
            )

        return self._create_ui_element(
            "scoreboard",
            element_type="scoreboard",
            scoreboard_data={"teams": teams_data},
        )

    def generate_at(self, time_ms: int) -> list[UIElement]:
        """Generates HUD elements at a specific millisecond timestamp.

        Args:
            time_ms: The millisecond timestamp.

        Returns:
            list[UIElement]: The list of active UI HUD elements.
        """
        players, teams = self._get_state_at(time_ms)
        elements: list[UIElement] = []

        el_game_type = self._create_ui_element(
            "game_type",
            text=f"Game Type: {self.game.game_type}",
            element_type="text",
        )
        if el_game_type:
            elements.append(el_game_type)

        actual_duration = self.game.duration
        if self.game_ended_at is not None:
            actual_duration = self.game_ended_at

        display_ms = time_ms
        if actual_duration is not None and display_ms > actual_duration:
            display_ms = actual_duration

        total_seconds = display_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        time_text = f"Time: {minutes:02d}:{seconds:02d}"

        el_time = self._create_ui_element("time", text=time_text, element_type="text")
        if el_time:
            elements.append(el_time)

        el_sb = self._create_scoreboard_element(teams, players, time_ms)
        if el_sb:
            elements.append(el_sb)

        if self.entity_id and self.entity_id in players:
            p_state = players[self.entity_id]

            el_pname = self._create_ui_element(
                "player_name",
                text=f"Player: {self.player_name}",
                element_type="text",
            )
            if el_pname:
                elements.append(el_pname)

            el_prole = self._create_ui_element(
                "player_role",
                text=f"Role: {p_state.role.display_name}",
                element_type="text",
            )
            if el_prole:
                elements.append(el_prole)

            el_pscore = self._create_ui_element(
                "player_score", text=f"Score: {p_state.score}", element_type="text"
            )
            if el_pscore:
                elements.append(el_pscore)

            el_plives = self._create_ui_element(
                "player_lives", text=f"Lives: {p_state.lives}", element_type="text"
            )
            if el_plives:
                elements.append(el_plives)

            el_pshots = self._create_ui_element(
                "player_shots", text=f"Shots: {p_state.shots}", element_type="text"
            )
            if el_pshots:
                elements.append(el_pshots)

            if p_state.role.start_missiles > 0:
                el_pmissiles = self._create_ui_element(
                    "player_missiles",
                    text=f"Missiles: {p_state.missiles}",
                    element_type="text",
                )
                if el_pmissiles:
                    elements.append(el_pmissiles)

            el_pspec = self._create_ui_element(
                "player_special_points",
                text=f"Special Points: {p_state.special_points}",
                element_type="text",
            )
            if el_pspec:
                elements.append(el_pspec)

            if p_state.is_down(time_ms):
                safe_rem = max(0, p_state.resettable_starts_at - time_ms)
                res_base = max(time_ms, p_state.resettable_starts_at)
                resettable_rem = max(0, p_state.downtime_ends_at - res_base)

                el_dt = self._create_ui_element(
                    "downtime",
                    element_type="downtime_bar",
                    safe_ms=safe_rem,
                    resettable_ms=resettable_rem,
                )
                if el_dt:
                    elements.append(el_dt)

        anim = self.config.get("animation", "ease-in-out")
        fade_time_s = self.config.get("fade_out_time", 2.0)
        fade_time_ms = int(fade_time_s * 1000)

        if self.entity_id:
            active_p_events = []
            for ev in self.event_log:
                if time_ms - fade_time_ms <= ev["time"] <= time_ms:
                    if (
                        ev["actor_id"] == self.entity_id
                        or ev["target_id"] == self.entity_id
                    ):
                        active_p_events.append(ev)
            if active_p_events:
                recent_ev = active_p_events[-1]
                elapsed = time_ms - recent_ev["time"]
                alpha = get_fade_alpha(elapsed, fade_time_ms, anim)
                el_pevent = self._create_ui_element(
                    "player_events",
                    text=recent_ev["desc"],
                    element_type="text",
                    alpha=alpha,
                )
                if el_pevent:
                    elements.append(el_pevent)

        active_g_events = []
        for ev in self.event_log:
            if time_ms - fade_time_ms <= ev["time"] <= time_ms:
                if ev["is_important"]:
                    active_g_events.append(ev)
        if active_g_events:
            recent_ev = active_g_events[-1]
            elapsed = time_ms - recent_ev["time"]
            alpha = get_fade_alpha(elapsed, fade_time_ms, anim)
            el_gevent = self._create_ui_element(
                "game_events",
                text=recent_ev["desc"],
                element_type="text",
                alpha=alpha,
            )
            if el_gevent:
                elements.append(el_gevent)

        return elements
