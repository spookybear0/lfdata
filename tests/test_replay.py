from pathlib import Path

from lfdata.importer import TdfImporter
from lfdata.replay.replay import LFReplaySystem


def test_replay_system_with_real_game() -> None:
    real_path = Path(__file__).parent.parent / "assets" / "sm5_sanitized.tdf"
    importer = TdfImporter(real_path)
    game = importer.parse()

    replay = LFReplaySystem(game)
    records = replay.run()

    assert len(records) > 0
    assert records[0].time == 0
    assert records[0].description == "* Mission Start *"

    zap_record = next((r for r in records if "zaps" in r.description), None)
    assert zap_record is not None
    assert len(zap_record.player_changes) > 0

    for player in replay.game_state.players.values():
        assert player.lives >= 0
        assert player.shots >= 0
        assert player.special_points >= 0


def test_replay_system_rules() -> None:
    from datetime import datetime
    from lfdata.model import LFGame, GameTeam, GameEntity, GameEvent

    # 1. Create a game
    game = LFGame(game_id="test_rule_game", timestamp=datetime.now(), game_type="SM5")

    # 2. Add two teams
    t1 = GameTeam(
        game_id="test_rule_game",
        team_index=0,
        desc="Fire Team",
        color_enum=11,
        color_desc="Fire",
        color_rgb="#FF5000",
    )
    t2 = GameTeam(
        game_id="test_rule_game",
        team_index=1,
        desc="Earth Team",
        color_enum=13,
        color_desc="Earth",
        color_rgb="#00FF00",
    )
    game.teams = [t1, t2]

    # 3. Add entities
    # Commander on team 0
    cmd = GameEntity(
        game_id="test_rule_game",
        entity_id="C1",
        type="player",
        desc="Cmd1",
        team_index=0,
        level=1,
        category=1,
        battlesuit="Maverick",
    )
    # Scout on team 1
    sct = GameEntity(
        game_id="test_rule_game",
        entity_id="S2",
        type="player",
        desc="Sct2",
        team_index=1,
        level=1,
        category=3,
        battlesuit="Interceptor",
    )
    # Medic on team 1
    med = GameEntity(
        game_id="test_rule_game",
        entity_id="M2",
        type="player",
        desc="Med2",
        team_index=1,
        level=1,
        category=4,
        battlesuit="Medic",
    )
    game.entities = [cmd, sct, med]

    # 4. Add events
    events = [
        # Mission start
        GameEvent(
            game_id="test_rule_game",
            time=0,
            event_type="0100",
            action="start",
            raw_message="",
        ),
        # Scout zaps Commander (DAMAGED_OPPONENT - Commander has 3 HP, so HP becomes 2, no life lost)
        GameEvent(
            game_id="test_rule_game",
            time=1000,
            event_type="0205",
            actor_entity_id="S2",
            target_entity_id="C1",
            action="zaps",
            raw_message="",
        ),
        # Scout zaps Commander again (DAMAGED_OPPONENT - Commander HP becomes 1)
        GameEvent(
            game_id="test_rule_game",
            time=2000,
            event_type="0205",
            actor_entity_id="S2",
            target_entity_id="C1",
            action="zaps",
            raw_message="",
        ),
        # Scout zaps Commander again (DOWNED_OPPONENT - Commander HP becomes 0, goes down, loses 1 life)
        GameEvent(
            game_id="test_rule_game",
            time=3000,
            event_type="0206",
            actor_entity_id="S2",
            target_entity_id="C1",
            action="zaps",
            raw_message="",
        ),
        # Scout locks and missiles Commander at time 12000 (after downtime ends at 11000)
        # Downs Commander, takes 2 lives
        GameEvent(
            game_id="test_rule_game",
            time=12000,
            event_type="0306",
            actor_entity_id="S2",
            target_entity_id="C1",
            action="missiled",
            raw_message="",
        ),
        # Team Life Boost from Medic on team 1 (time 13000).
        # Scout is active (time 13000), so Scout is resupplied.
        # Commander is on team 0, so not resupplied.
        # Medic is the actor, so not resupplied.
        GameEvent(
            game_id="test_rule_game",
            time=13000,
            event_type="0512",
            actor_entity_id="M2",
            action="life_boost",
            raw_message="",
        ),
    ]
    game.events = events

    replay = LFReplaySystem(game)
    replay.run()

    # Verify state after events:
    players = replay.game_state.players
    cmd_state = players["C1"]
    sct_state = players["S2"]
    med_state = players["M2"]

    # Commander started with 15 lives.
    # Got downed once at 3000 (-1 life -> 14 lives).
    # Got missiled at 12000 (-2 lives -> 12 lives).
    assert cmd_state.lives == 12
    assert cmd_state.hp == 0
    assert cmd_state.downtime_ends_at == 20000  # 12000 + 8000

    # Scout started with 15 lives.
    # Medic resupplied lives to team at 13000.
    # Scout gained 3 lives (from 15 to 18).
    assert sct_state.lives == 18
    # Medic itself should NOT gain lives.
    assert med_state.lives == 20
