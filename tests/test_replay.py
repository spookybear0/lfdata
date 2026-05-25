from pathlib import Path

from lfdata.importer import TdfImporter
from lfdata.replay.replay import LFReplaySystem


def test_replay_system_with_real_game() -> None:
    real_path = Path(__file__).parent.parent / 'assets' / 'sm5_sanitized.tdf'
    importer = TdfImporter(real_path)
    game = importer.parse()

    replay = LFReplaySystem(game)
    records = replay.run()

    assert len(records) > 0
    assert records[0].time == 0
    assert records[0].description == '* Mission Start *'

    zap_record = next((r for r in records if 'zaps' in r.description), None)
    assert zap_record is not None
    assert len(zap_record.player_changes) > 0

    for player in replay.game_state.players.values():
        assert player.lives >= 0
        assert player.shots >= 0
        assert player.special_points >= 0
