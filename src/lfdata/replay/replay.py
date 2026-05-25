"""Replay system orchestrator for simulating and recording LF game state changes."""

from lfdata.model import GameEvent, LFGame, LFRole, LFTeamType
from lfdata.replay.record import LFReplayEventRecord
from lfdata.replay.state import (
    LFReplayGameState,
    LFReplayPlayerState,
    LFReplayTeamState,
)


class LFReplaySystem:
    """Orchestrates the replay simulation from a parsed game."""

    def __init__(self, game: LFGame) -> None:
        """Initializes the replay system.

        Args:
            game: The LF game object containing teams, entities, and events.
        """
        self.game = game
        self.player_states: list[LFReplayPlayerState] = []
        self.team_states: list[LFReplayTeamState] = []
        self.entity_names: dict[str, str] = {e.entity_id: e.desc for e in game.entities}
        self._init_states()
        self.game_state = LFReplayGameState(self.player_states, self.team_states)
        self.records: list[LFReplayEventRecord] = []
        self.game_ended_at: int | None = None

    def _init_states(self) -> None:
        """Initializes player and team states based on game metadata."""
        player_team_indices = {
            e.team_index for e in self.game.entities if e.type == "player"
        }

        for team in self.game.teams:
            if team.team_index not in player_team_indices:
                continue
            try:
                team_type = LFTeamType.from_index(team.team_index)
                name = team_type.display_name
            except ValueError:
                name = team.desc
            self.team_states.append(
                LFReplayTeamState(
                    team_index=team.team_index,
                    name=name,
                    color_rgb=team.color_rgb,
                )
            )

        for entity in self.game.entities:
            if entity.type == "player":
                try:
                    role = LFRole.from_id(entity.category)
                except ValueError:
                    role = LFRole.SCOUT
                self.player_states.append(
                    LFReplayPlayerState(entity.entity_id, role, entity.team_index)
                )

    def run(self) -> list[LFReplayEventRecord]:
        """Runs the game replay through all events in chronological order.

        Returns:
            list[LFReplayEventRecord]: The list of event records generated.
        """
        sorted_events = sorted(self.game.events, key=lambda e: e.time)

        for event in sorted_events:
            # First, update all player states for the current event time
            for player in self.game_state.players.values():
                player.update_downtime(event.time)

            player_snap, team_snap = self._take_snapshot()

            description = self._dispatch_event(event)

            self.game_state.update_team_scores_and_rankings()
            player_changes, team_changes = self._build_changes(player_snap, team_snap)

            record = LFReplayEventRecord(
                event_id=event.id or 0,
                time=event.time,
                description=description,
                player_changes=player_changes,
                team_changes=team_changes,
            )
            self.records.append(record)

            if self._is_game_over():
                self.game_ended_at = event.time
                break

        return self.records

    def run_up_to(self, time_ms: int) -> None:
        """Simulates the game replay up to a specific millisecond timestamp.

        Args:
            time_ms: The millisecond timestamp to simulate up to (inclusive).
        """
        sorted_events = sorted(self.game.events, key=lambda e: e.time)

        for event in sorted_events:
            if event.time > time_ms:
                break

            for player in self.game_state.players.values():
                player.update_downtime(event.time)

            self._dispatch_event(event)
            self.game_state.update_team_scores_and_rankings()

            if self._is_game_over():
                self.game_ended_at = event.time
                return

        # Final update to the target timestamp
        for player in self.game_state.players.values():
            player.update_downtime(time_ms)

    def _dispatch_event(self, event: GameEvent) -> str:
        """Dispatches a game event to its specific handler method.

        Args:
            event: The game event to dispatch.

        Returns:
            str: The event description string.
        """
        ev_type = event.event_type
        if ev_type in ["0205", "0206", "0207", "0208"]:
            description = self._process_event_zap(event)
        elif ev_type in ["0306", "0308"]:
            description = self._process_event_missile(event)
        elif ev_type in ["0204", "0303", "0B03"]:
            description = self._process_event_base_destroy(event)
        elif ev_type == "0405":
            description = self._process_event_nuke_detonate(event)
        elif ev_type in ["0500", "0502", "0510", "0512"]:
            description = self._process_event_resupply(event)
        else:
            description = self._process_event_other(event)

        # Check team elimination after processing the event
        self._check_team_elimination(event.time)

        return description

    def _decrement_shots(self, actor_id: str | None) -> None:
        """Helper to decrement shots left for non-ammo players.

        Args:
            actor_id: The ID of the acting player.
        """
        if actor_id and actor_id in self.game_state.players:
            player = self.game_state.players[actor_id]
            if player.role != LFRole.AMMO and not player.is_eliminated():
                player.shots = max(0, player.shots - 1)

    def _process_event_zap(self, event: GameEvent) -> str:
        """Processes zapping events.

        Args:
            event: The zapping event.

        Returns:
            str: The event description string.
        """
        actor = self.game_state.players.get(event.actor_entity_id)
        target = self.game_state.players.get(event.target_entity_id)

        self._decrement_shots(event.actor_entity_id)
        actor_name = self.entity_names.get(event.actor_entity_id, event.actor_entity_id)
        target_name = self.entity_names.get(
            event.target_entity_id, event.target_entity_id
        )

        if (
            actor
            and target
            and not actor.is_eliminated()
            and not target.is_eliminated()
        ):
            if actor.team_index == target.team_index:
                # Friendly fire: penalize actor, target is unaffected
                actor.score -= 100
            else:
                actor.score += 100
                actor.special_points += 1

                # Check target state
                if event.event_type in ["0205", "0207"]:  # DAMAGED_OPPONENT / TEAM
                    target.hp = max(1, target.hp - 1)
                elif event.event_type in ["0206", "0208"]:  # DOWNED_OPPONENT / TEAM
                    if not target.is_down(event.time):
                        target.lives = max(0, target.lives - 1)
                        target.score -= 20
                    target.hp = 0
                    target.downtime_ends_at = event.time + 8000
                    target.resettable_starts_at = event.time + 4000

        return f"{actor_name} zaps {target_name}"

    def _process_event_missile(self, event: GameEvent) -> str:
        """Processes missile zapping events.

        Args:
            event: The missile event.

        Returns:
            str: The event description string.
        """
        actor = self.game_state.players.get(event.actor_entity_id)
        target = self.game_state.players.get(event.target_entity_id)

        if actor and not actor.is_eliminated():
            actor.missiles = max(0, actor.missiles - 1)

        actor_name = self.entity_names.get(event.actor_entity_id, event.actor_entity_id)
        target_name = self.entity_names.get(
            event.target_entity_id, event.target_entity_id
        )

        if (
            actor
            and target
            and not actor.is_eliminated()
            and not target.is_eliminated()
        ):
            if actor.team_index == target.team_index:
                # Friendly fire missile: penalize actor, target unaffected
                actor.score -= 500
            else:
                actor.score += 500
                actor.special_points += 2

                # Missile immediately downs target
                if not target.is_down(event.time):
                    target.lives = max(0, target.lives - 2)
                    target.score -= 100
                target.hp = 0
                target.downtime_ends_at = event.time + 8000
                target.resettable_starts_at = event.time + 4000

        return f"{actor_name} missiles {target_name}"

    def _process_event_base_destroy(self, event: GameEvent) -> str:
        """Processes base destruction/capture events.

        Args:
            event: The base destruction/capture event.

        Returns:
            str: The event description string.
        """
        actor = self.game_state.players.get(event.actor_entity_id)
        actor_name = self.entity_names.get(event.actor_entity_id, event.actor_entity_id)
        target_name = self.entity_names.get(
            event.target_entity_id, event.target_entity_id
        )

        if event.event_type != "0B03":
            self._decrement_shots(event.actor_entity_id)

        target_entity = None
        for entity in self.game.entities:
            if entity.entity_id == event.target_entity_id:
                target_entity = entity
                break

        if actor and not actor.is_eliminated() and target_entity:
            if (
                target_entity.team_index != actor.team_index
                and event.target_entity_id not in actor.captured_bases
            ):
                actor.captured_bases.add(event.target_entity_id)
                actor.score += 1001
                actor.special_points += 5

        if event.event_type == "0B03":
            return f"{actor_name} is awarded {target_name}"
        return f"{actor_name} destroys {target_name}"

    def _process_event_nuke_detonate(self, event: GameEvent) -> str:
        """Processes nuke detonation events.

        Args:
            event: The nuke detonation event.

        Returns:
            str: The event description string.
        """
        actor = self.game_state.players.get(event.actor_entity_id)
        actor_name = self.entity_names.get(event.actor_entity_id, event.actor_entity_id)

        if actor and not actor.is_eliminated():
            actor.score += 500
            for player in self.game_state.players.values():
                if player.team_index != actor.team_index and not player.is_eliminated():
                    player.lives = max(0, player.lives - 3)
                    player.hp = 0
                    player.downtime_ends_at = event.time + 8000
                    player.resettable_starts_at = event.time + 4000

        return f"{actor_name} detonates nuke"

    def _process_event_resupply(self, event: GameEvent) -> str:
        """Processes resupply (ammo, lives, team boosts) events.

        Args:
            event: The resupply event.

        Returns:
            str: The event description string.
        """
        actor = self.game_state.players.get(event.actor_entity_id)
        actor_name = self.entity_names.get(event.actor_entity_id, event.actor_entity_id)
        target_name = self.entity_names.get(
            event.target_entity_id, event.target_entity_id
        )

        if actor and actor.is_eliminated():
            return ""

        if event.event_type == "0500":
            target = self.game_state.players.get(event.target_entity_id)
            if target and not target.is_eliminated():
                target.resupply_shots_from_ammo()
            return f"{actor_name} resupplies {target_name}"

        if event.event_type == "0502":
            target = self.game_state.players.get(event.target_entity_id)
            if target and not target.is_eliminated():
                target.resupply_lives_from_medic()
            return f"{actor_name} resupplies {target_name}"

        if event.event_type == "0510":
            if actor:
                for player in self.game_state.players.values():
                    if (
                        player.team_index == actor.team_index
                        and player.entity_id != actor.entity_id
                        and not player.is_eliminated()
                        and not player.is_down(event.time)
                    ):
                        player.resupply_shots_from_ammo()
            return f"{actor_name} resupplies team"

        if event.event_type == "0512":
            if actor:
                for player in self.game_state.players.values():
                    if (
                        player.team_index == actor.team_index
                        and player.entity_id != actor.entity_id
                        and not player.is_eliminated()
                        and not player.is_down(event.time)
                    ):
                        player.resupply_lives_from_medic()
            return f"{actor_name} resupplies team"

        return ""

    def _process_event_other(self, event: GameEvent) -> str:
        """Processes other miscellaneous events.

        Args:
            event: The miscellaneous event.

        Returns:
            str: The event description string.
        """
        actor_name = self.entity_names.get(event.actor_entity_id, event.actor_entity_id)
        target_name = self.entity_names.get(
            event.target_entity_id, event.target_entity_id
        )

        if event.event_type == "0100":
            return "* Mission Start *"
        if event.event_type == "0101":
            return "* Mission End *"
        if event.event_type == "0201":
            self._decrement_shots(event.actor_entity_id)
            return f"{actor_name} misses"
        if event.event_type == "0202":
            self._decrement_shots(event.actor_entity_id)
            return f"{actor_name} misses base"
        if event.event_type == "0203":
            self._decrement_shots(event.actor_entity_id)
            return f"{actor_name} zaps {target_name}"
        if event.event_type == "0300":
            return f"{actor_name} locking {target_name}"
        if event.event_type == "0400":
            actor = self.game_state.players.get(event.actor_entity_id)
            if actor and not actor.is_eliminated():
                actor.special_points = max(0, actor.special_points - 15)
            return f"{actor_name} activates rapid fire"
        if event.event_type == "0404":
            actor = self.game_state.players.get(event.actor_entity_id)
            if actor and not actor.is_eliminated():
                actor.special_points = max(0, actor.special_points - 20)
            return f"{actor_name} activates nuke"
        if event.event_type == "0600":
            actor = self.game_state.players.get(event.actor_entity_id)
            if actor and not actor.is_eliminated():
                gp = self.game.penalty
                penalty_val = gp if gp is not None else -1000
                actor.score += penalty_val
            return f"{actor_name} is penalized"
        if event.event_type == "0900":
            return f"{actor_name} completes an achievement!"
        if event.event_type == "0902":
            return f"{actor_name} earns a reward!"

        return event.action

    def _take_snapshot(
        self,
    ) -> tuple[dict[str, dict[str, any]], dict[int, dict[str, any]]]:
        """Takes a snapshot of the current state of players and teams.

        Returns:
            tuple: A dictionary of player snapshots and team snapshots.
        """
        player_snap = {}
        for p in self.game_state.players.values():
            player_snap[p.entity_id] = {
                "score": p.score,
                "lives": p.lives,
                "shots": p.shots,
                "missiles": p.missiles,
                "special_points": p.special_points,
            }
        team_snap = {}
        for t in self.game_state.teams.values():
            team_snap[t.team_index] = {
                "score": t.score,
                "ranking": t.ranking,
            }
        return player_snap, team_snap

    def _build_changes(
        self,
        player_snap: dict[str, dict[str, any]],
        team_snap: dict[int, dict[str, any]],
    ) -> tuple[dict[str, dict[str, any]], dict[int, dict[str, any]]]:
        """Calculates state changes by comparing against the snapshots.

        Args:
            player_snap: Player state snapshot before the event.
            team_snap: Team state snapshot before the event.

        Returns:
            tuple: A dictionary of player state changes and team state changes.
        """
        player_changes = {}
        for p in self.game_state.players.values():
            old = player_snap[p.entity_id]
            changes = {}
            for attr in [
                "score",
                "lives",
                "shots",
                "missiles",
                "special_points",
            ]:
                new_val = getattr(p, attr)
                if new_val != old[attr]:
                    changes[attr] = new_val
            if changes:
                player_changes[p.entity_id] = changes

        team_changes = {}
        for t in self.game_state.teams.values():
            old = team_snap[t.team_index]
            changes = {}
            for attr in ["score", "ranking"]:
                new_val = getattr(t, attr)
                if new_val != old[attr]:
                    changes[attr] = new_val
            if changes:
                team_changes[t.team_index] = changes

        return player_changes, team_changes

    def _check_team_elimination(self, event_time: int) -> None:
        """Checks if any team has been completely eliminated.

        If a team is eliminated, all players of the other team(s) are awarded
        all bases they haven't captured yet.

        Args:
            event_time: The current event timestamp in milliseconds.
        """
        active_teams = set()
        for player in self.game_state.players.values():
            active_teams.add(player.team_index)

        eliminated_teams = set()
        for team_idx in active_teams:
            team_players = [
                p for p in self.game_state.players.values() if p.team_index == team_idx
            ]
            if all(p.is_eliminated() for p in team_players):
                eliminated_teams.add(team_idx)

        if eliminated_teams:
            all_bases = [
                e
                for e in self.game.entities
                if e.type
                in (
                    "standard-target",
                    "generator-target",
                )
            ]
            for player in self.game_state.players.values():
                if (
                    player.team_index not in eliminated_teams
                    and not player.is_eliminated()
                ):
                    for base in all_bases:
                        if (
                            base.team_index != player.team_index
                            and base.entity_id not in player.captured_bases
                        ):
                            player.captured_bases.add(base.entity_id)
                            player.score += 1001
                            player.special_points += 5

    def _is_game_over(self) -> bool:
        """Checks if the game has ended prematurely.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        player_teams = {p.team_index for p in self.game_state.players.values()}
        if not player_teams:
            return False

        for team_idx in player_teams:
            team_players = [
                p for p in self.game_state.players.values() if p.team_index == team_idx
            ]
            if all(p.is_eliminated() for p in team_players):
                return True
        return False
