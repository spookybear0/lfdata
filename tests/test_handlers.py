from datetime import datetime
from lfdata.model import LFGame, GameTeam, GameEntity
from lfdata.replay.replay import LFReplaySystem
from lfdata.replay.handlers import LFReplayHandlersMixin


def test_handlers_mixin_integration() -> None:
    # Verify mixin class is inherited
    assert issubclass(LFReplaySystem, LFReplayHandlersMixin)

    # Initialize a mock game to verify handler method presence
    game = LFGame(
        game_id="test_handlers_game",
        timestamp=datetime.now(),
        game_type="SM5",
    )
    # Teams
    t1 = GameTeam(
        game_id="test_handlers_game",
        team_index=0,
        desc="Fire Team",
        color_enum=11,
        color_desc="Fire",
        color_rgb="#FF5000",
    )
    game.teams = [t1]

    # Entities
    cmd = GameEntity(
        game_id="test_handlers_game",
        entity_id="C1",
        type="player",
        desc="Cmd1",
        team_index=0,
        level=1,
        category=1,
        battlesuit="Maverick",
    )
    game.entities = [cmd]
    game.events = []

    replay = LFReplaySystem(game)

    # Verify method presence
    assert hasattr(replay, "_process_event_zap")
    assert hasattr(replay, "_process_event_missile")
    assert hasattr(replay, "_process_event_base_destroy")
    assert hasattr(replay, "_process_event_nuke_detonate")
    assert hasattr(replay, "_process_event_resupply")
    assert hasattr(replay, "_process_event_other")
