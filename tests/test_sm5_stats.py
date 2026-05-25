from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from lfdata.model import Base, LFGame, Sm5Stats


def test_create_sm5_stats() -> None:
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        game = LFGame(
            game_id='test_game_123',
            timestamp=datetime.now(),
            game_type='SM5',
        )
        session.add(game)
        session.commit()

        stats = Sm5Stats(
            game_id='test_game_123',
            entity_id='#fwqiZ',
            shots_hit=58,
            shots_fired=62,
            times_zapped=11,
            times_missiled=0,
            missile_hits=0,
            nukes_detonated=0,
            nukes_activated=0,
            nuke_cancels=0,
            medic_hits=0,
            own_medic_hits=0,
            medic_nukes=0,
            scout_rapid=0,
            life_boost=1,
            ammo_boost=0,
            lives_left=0,
            shots_left=30,
            penalties=0,
            shot3_hit=0,
            own_nuke_cancels=0,
            shot_opponent=4,
            shot_team=0,
            missiled_opponent=0,
            missiled_team=0,
        )
        session.add(stats)
        session.commit()

        retrieved = session.query(Sm5Stats).filter_by(
            game_id='test_game_123', entity_id='#fwqiZ'
        ).first()
        assert retrieved is not None
        assert retrieved.shots_hit == 58
        assert retrieved.shots_fired == 62
        assert retrieved.times_zapped == 11
        assert retrieved.life_boost == 1
        assert retrieved.shots_left == 30
        assert retrieved.shot_opponent == 4
        assert retrieved.game.game_id == 'test_game_123'
        assert repr(retrieved) == (
            "Sm5Stats(id=1, game_id='test_game_123', entity_id='#fwqiZ')"
        )
