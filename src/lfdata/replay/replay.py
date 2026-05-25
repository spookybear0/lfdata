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

    def __init__(self, game: LFGame):
        """Initializes the replay system.

        Args:
            game: The LF game object containing teams, entities, and events.
        """
        self.game = game
        self.player_states: list[LFReplayPlayerState] = []
        self.team_states: list[LFReplayTeamState] = []
        self.entity_names: dict[str, str] = {
            e.entity_id: e.desc for e in game.entities
        }
        self._init_states()
        self.game_state = LFReplayGameState(
            self.player_states, self.team_states
        )
        self.records: list[LFReplayEventRecord] = []

    def _init_states(self) -> None:
        """Initializes player and team states based on game metadata."""
        for team in self.game.teams:
            try:
                team_type = LFTeamType.from_index(team.team_index)
                name = team_type.display_name
            except ValueError:
                name = team.desc
            self.team_states.append(LFReplayTeamState(team.team_index, name))

        for entity in self.game.entities:
            if entity.type == 'player':
                try:
                    role = LFRole.from_id(entity.category)
                except ValueError:
                    role = LFRole.SCOUT
                self.player_states.append(
                    LFReplayPlayerState(
                        entity.entity_id, role, entity.team_index
                    )
                )

    def run(self) -> list[LFReplayEventRecord]:
        """Runs the game replay through all events in chronological order.

        Returns:
            list[LFReplayEventRecord]: The list of event records generated.
        """
        sorted_events = sorted(self.game.events, key=lambda e: e.time)

        for event in sorted_events:
            player_snap, team_snap = self._take_snapshot()

            description = ''
            ev_type = event.event_type
            if ev_type in ['0205', '0206']:
                description = self._process_event_zap(event)
            elif ev_type == '0306':
                description = self._process_event_missile(event)
            elif ev_type in ['0204', '0303', '0B03']:
                description = self._process_event_base_destroy(event)
            elif ev_type == '0405':
                description = self._process_event_nuke_detonate(event)
            elif ev_type in ['0500', '0502', '0510', '0512']:
                description = self._process_event_resupply(event)
            else:
                description = self._process_event_other(event)

            self.game_state.update_team_scores_and_rankings()
            player_changes, team_changes = self._build_changes(
                player_snap, team_snap
            )

            record = LFReplayEventRecord(
                event_id=event.id or 0,
                time=event.time,
                description=description,
                player_changes=player_changes,
                team_changes=team_changes,
            )
            self.records.append(record)

        return self.records

    def _decrement_shots(self, actor_id: str | None) -> None:
        """Helper to decrement shots left for non-ammo players.

        Args:
            actor_id: The ID of the acting player.
        """
        if actor_id and actor_id in self.game_state.players:
            player = self.game_state.players[actor_id]
            if player.role != LFRole.AMMO:
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
        actor_name = self.entity_names.get(
            event.actor_entity_id, event.actor_entity_id
        )
        target_name = self.entity_names.get(
            event.target_entity_id, event.target_entity_id
        )

        if actor and target:
            if actor.team_index == target.team_index:
                actor.score -= 100
            else:
                actor.score += 100
                actor.special_points += 1
                target.score -= 20
                target.lives = max(0, target.lives - 1)

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

        if actor:
            actor.missiles = max(0, actor.missiles - 1)

        actor_name = self.entity_names.get(
            event.actor_entity_id, event.actor_entity_id
        )
        target_name = self.entity_names.get(
            event.target_entity_id, event.target_entity_id
        )

        if actor and target:
            if actor.team_index == target.team_index:
                actor.score -= 500
            else:
                actor.score += 500
                actor.special_points += 2
                target.score -= 100
                target.lives = max(0, target.lives - 2)

        return f"{actor_name} missiles {target_name}"

    def _process_event_base_destroy(self, event: GameEvent) -> str:
        """Processes base destruction/capture events.

        Args:
            event: The base destruction/capture event.

        Returns:
            str: The event description string.
        """
        actor = self.game_state.players.get(event.actor_entity_id)
        actor_name = self.entity_names.get(
            event.actor_entity_id, event.actor_entity_id
        )
        target_name = self.entity_names.get(
            event.target_entity_id, event.target_entity_id
        )

        if event.event_type != '0B03':
            self._decrement_shots(event.actor_entity_id)

        if actor:
            actor.score += 1001
            actor.special_points += 5

        if event.event_type == '0B03':
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
        actor_name = self.entity_names.get(
            event.actor_entity_id, event.actor_entity_id
        )

        if actor:
            actor.score += 500
            for player in self.game_state.players.values():
                if player.team_index != actor.team_index:
                    player.lives = max(0, player.lives - 3)

        return f"{actor_name} detonates nuke"

    def _process_event_resupply(self, event: GameEvent) -> str:
        """Processes resupply (ammo, lives, team boosts) events.

        Args:
            event: The resupply event.

        Returns:
            str: The event description string.
        """
        actor = self.game_state.players.get(event.actor_entity_id)
        actor_name = self.entity_names.get(
            event.actor_entity_id, event.actor_entity_id
        )
        target_name = self.entity_names.get(
            event.target_entity_id, event.target_entity_id
        )

        if event.event_type == '0500':
            target = self.game_state.players.get(event.target_entity_id)
            if target:
                target.resupply_shots_from_ammo()
            return f"{actor_name} resupplies {target_name}"

        if event.event_type == '0502':
            target = self.game_state.players.get(event.target_entity_id)
            if target:
                target.resupply_lives_from_medic()
            return f"{actor_name} resupplies {target_name}"

        if event.event_type == '0510':
            if actor:
                for player in self.game_state.players.values():
                    if player.team_index == actor.team_index:
                        player.resupply_shots_from_ammo()
            return f"{actor_name} resupplies team"

        if event.event_type == '0512':
            if actor:
                for player in self.game_state.players.values():
                    if player.team_index == actor.team_index:
                        player.resupply_lives_from_medic()
            return f"{actor_name} resupplies team"

        return ''

    def _process_event_other(self, event: GameEvent) -> str:
        """Processes other miscellaneous events.

        Args:
            event: The miscellaneous event.

        Returns:
            str: The event description string.
        """
        actor_name = self.entity_names.get(
            event.actor_entity_id, event.actor_entity_id
        )
        target_name = self.entity_names.get(
            event.target_entity_id, event.target_entity_id
        )

        if event.event_type == '0100':
            return '* Mission Start *'
        if event.event_type == '0101':
            return '* Mission End *'
        if event.event_type == '0201':
            self._decrement_shots(event.actor_entity_id)
            return f"{actor_name} misses"
        if event.event_type == '0202':
            self._decrement_shots(event.actor_entity_id)
            return f"{actor_name} misses base"
        if event.event_type == '0203':
            self._decrement_shots(event.actor_entity_id)
            return f"{actor_name} zaps {target_name}"
        if event.event_type == '0300':
            return f"{actor_name} locking {target_name}"
        if event.event_type == '0400':
            actor = self.game_state.players.get(event.actor_entity_id)
            if actor:
                actor.special_points = max(0, actor.special_points - 15)
            return f"{actor_name} activates rapid fire"
        if event.event_type == '0404':
            actor = self.game_state.players.get(event.actor_entity_id)
            if actor:
                actor.special_points = max(0, actor.special_points - 20)
            return f"{actor_name} activates nuke"
        if event.event_type == '0600':
            return f"{actor_name} is penalized"
        if event.event_type == '0900':
            return f"{actor_name} completes an achievement!"
        if event.event_type == '0902':
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
                'score': p.score,
                'lives': p.lives,
                'shots': p.shots,
                'missiles': p.missiles,
                'special_points': p.special_points,
            }
        team_snap = {}
        for t in self.game_state.teams.values():
            team_snap[t.team_index] = {
                'score': t.score,
                'ranking': t.ranking,
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
                'score',
                'lives',
                'shots',
                'missiles',
                'special_points',
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
            for attr in ['score', 'ranking']:
                new_val = getattr(t, attr)
                if new_val != old[attr]:
                    changes[attr] = new_val
            if changes:
                team_changes[t.team_index] = changes

        return player_changes, team_changes
