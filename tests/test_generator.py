from datetime import datetime
from lfdata.model import LFGame, GameTeam, GameEntity, GameEvent
from lfdata.video.generator import VisualElementGenerator


def test_visual_element_generator() -> None:
    # 1. Create mock game
    game = LFGame(game_id="test_vid_game", timestamp=datetime.now(), game_type="SM5")

    # Teams
    t1 = GameTeam(
        game_id="test_vid_game",
        team_index=0,
        desc="Fire Team",
        color_enum=11,
        color_desc="Fire",
        color_rgb="#FF5000",
    )
    game.teams = [t1]

    # Entity (Commander on team 0)
    cmd = GameEntity(
        game_id="test_vid_game",
        entity_id="C1",
        type="player",
        desc="Sqnfdcp",
        team_index=0,
        level=1,
        category=1,
        battlesuit="Maverick",
    )
    game.entities = [cmd]

    # E2 downs C1 at 3000 ms
    e2 = GameEntity(
        game_id="test_vid_game",
        entity_id="E2",
        type="player",
        desc="Enemy",
        team_index=1,
        level=1,
        category=3,
        battlesuit="Interceptor",
    )
    game.entities.append(e2)

    events = [
        GameEvent(
            game_id="test_rule_game",
            time=0,
            event_type="0100",
            action="start",
            raw_message="",
        ),
        GameEvent(
            game_id="test_rule_game",
            time=3000,
            event_type="0206",
            actor_entity_id="E2",
            target_entity_id="C1",
            action="zaps",
            raw_message="",
        ),
    ]
    game.events = events

    hud_gen = VisualElementGenerator(game, "Sqnfdcp")

    # 1. Generate at 1000 ms (active player)
    elements_active = hud_gen.generate_at(1000)

    types = [el.element_type for el in elements_active]
    assert "text" in types

    texts = [el.text for el in elements_active if el.text]
    assert "Game Type: SM5" in texts
    assert "Player: Sqnfdcp" in texts
    assert "Role: Commander" in texts
    assert "Score: 0" in texts
    assert "Lives: 15" in texts
    assert "Shots: 30" in texts
    assert "Missiles: 5" in texts
    assert "Special Points: 0" in texts

    assert not any(el.element_type == "downtime_bar" for el in elements_active)

    # 2. Generate at 5000 ms (downed player, safe phase)
    elements_down = hud_gen.generate_at(5000)

    bar_el = next(
        (el for el in elements_down if el.element_type == "downtime_bar"), None
    )
    assert bar_el is not None
    assert bar_el.safe_ms == 2000
    assert bar_el.resettable_ms == 4000


def test_visual_element_generator_new_features() -> None:
    game = LFGame(
        game_id="test_vid_game2",
        timestamp=datetime.now(),
        game_type="SM5",
        duration=4000,
    )
    t1 = GameTeam(
        game_id="test_vid_game2",
        team_index=0,
        desc="Fire Team",
        color_enum=11,
        color_desc="Fire",
        color_rgb="#FF5000",
    )
    game.teams = [t1]
    cmd = GameEntity(
        game_id="test_vid_game2",
        entity_id="C1",
        type="player",
        desc="Player1",
        team_index=0,
        level=1,
        category=1,
        battlesuit="Maverick",
    )
    game.entities = [cmd]
    game.events = [
        GameEvent(
            game_id="test_vid_game2",
            time=0,
            event_type="0100",
            action="start",
            raw_message="",
        )
    ]

    hud_gen = VisualElementGenerator(game, "Player1")

    elements = hud_gen.generate_at(1000)
    texts = [el.text for el in elements if el.text]
    assert "Time: 00:01" in texts

    elements_capped = hud_gen.generate_at(5000)
    texts_capped = [el.text for el in elements_capped if el.text]
    assert "Time: 00:04" in texts_capped

    sb_el = next((el for el in elements if el.element_type == "scoreboard"), None)
    assert sb_el is not None
    assert sb_el.scoreboard_data is not None
    teams = sb_el.scoreboard_data["teams"]
    assert len(teams) == 1
    team_data = teams[0]
    assert team_data["team_name"] == "Fire Team"
    assert team_data["color_rgb"] == "#FF5000"
    assert len(team_data["players"]) == 1
    p_data = team_data["players"][0]
    assert p_data["codename"] == "Player1"
    assert p_data["role_name"] == "Commander"
    assert p_data["score"] == 0
    assert p_data["lives"] == 15
    assert p_data["shots"] == 30
    assert p_data["missiles"] == 5
    assert p_data["special_points"] == 0
    assert team_data["totals"]["score"] == 0
