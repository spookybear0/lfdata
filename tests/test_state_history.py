from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from lfdata.model import Base, LFGame, PlayerStateHistory


def test_create_state_history() -> None:
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

        state = PlayerStateHistory(
            game_id='test_game_123',
            time=19,
            entity_id='#Mc0hTQ8',
            state=0,
        )
        session.add(state)
        session.commit()

        retrieved = (
            session.query(PlayerStateHistory)
            .filter_by(game_id='test_game_123', entity_id='#Mc0hTQ8')
            .first()
        )
        assert retrieved is not None
        assert retrieved.time == 19
        assert retrieved.state == 0
        assert retrieved.game.game_id == 'test_game_123'
        assert repr(retrieved) == (
            "PlayerStateHistory(id=1, entity_id='#Mc0hTQ8', state=0)"
        )
