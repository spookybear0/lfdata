from lfdata.replay.state import (
    LFReplayGameState,
    LFReplayPlayerState,
    LFReplayTeamState,
)


def test_player_state_initialization() -> None:
    commander = LFReplayPlayerState(
        entity_id='#1', role='commander', team_index=0
    )
    assert commander.lives == 15
    assert commander.shots == 30
    assert commander.missiles == 5

    scout = LFReplayPlayerState(entity_id='#2', role='scout', team_index=1)
    assert scout.lives == 15
    assert scout.shots == 30
    assert scout.missiles == 0

    heavy = LFReplayPlayerState(entity_id='#3', role='heavy', team_index=0)
    assert heavy.lives == 10
    assert heavy.shots == 20
    assert heavy.missiles == 5


def test_team_state_initialization() -> None:
    team = LFReplayTeamState(team_index=0, name='Fire Team')
    assert team.team_index == 0
    assert team.name == 'Fire Team'
    assert team.score == 0
    assert team.ranking == 1


def test_game_state_updates() -> None:
    p1 = LFReplayPlayerState(entity_id='#1', role='commander', team_index=0)
    p2 = LFReplayPlayerState(entity_id='#2', role='scout', team_index=1)
    t1 = LFReplayTeamState(team_index=0, name='Fire Team')
    t2 = LFReplayTeamState(team_index=1, name='Earth Team')

    game_state = LFReplayGameState(players=[p1, p2], teams=[t1, t2])

    p1.score = 500
    p2.score = 1000
    game_state.update_team_scores_and_rankings()

    assert t1.score == 500
    assert t2.score == 1000
    assert t1.ranking == 2
    assert t2.ranking == 1
