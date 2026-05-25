from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from lfdata.model import Base, LFGame, ScoreHistory


def test_create_score_history() -> None:
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

        score = ScoreHistory(
            game_id='test_game_123',
            time=5978,
            entity_id='#1u96zA',
            old_score=0,
            delta_score=500,
            new_score=500,
        )
        session.add(score)
        session.commit()

        retrieved = session.query(ScoreHistory).filter_by(
            game_id='test_game_123', entity_id='#1u96zA'
        ).first()
        assert retrieved is not None
        assert retrieved.time == 5978
        assert retrieved.old_score == 0
        assert retrieved.delta_score == 500
        assert retrieved.new_score == 500
        assert retrieved.game.game_id == 'test_game_123'
        assert repr(retrieved) == (
            "ScoreHistory(id=1, entity_id='#1u96zA', "
            "delta_score=500, new_score=500)"
        )
