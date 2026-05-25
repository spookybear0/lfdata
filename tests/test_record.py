from lfdata.replay.record import LFReplayEventRecord


def test_event_record_repr() -> None:
    record = LFReplayEventRecord(
        event_id=42,
        time=5000,
        description="Player 1 zaps Player 2",
        player_changes={},
        team_changes={},
    )
    assert record.event_id == 42
    assert record.time == 5000
    assert record.description == "Player 1 zaps Player 2"
    assert repr(record) == (
        "LFReplayEventRecord(time=5000, description='Player 1 zaps Player 2')"
    )
