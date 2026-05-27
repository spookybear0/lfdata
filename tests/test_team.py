from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from lfdata.model import Base, LFGame, GameTeam


def test_create_team() -> None:
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

        team = GameTeam(
            game_id='test_game_123',
            team_index=0,
            desc='Fire Team',
            color_enum=11,
            color_desc='Fire',
            color_rgb='#FF5000',
        )
        session.add(team)
        session.commit()

        retrieved = (
            session.query(GameTeam)
            .filter_by(game_id='test_game_123', team_index=0)
            .first()
        )
        assert retrieved is not None
        assert retrieved.desc == 'Fire Team'
        assert retrieved.color_enum == 11
        assert retrieved.color_desc == 'Fire'
        assert retrieved.color_rgb == '#FF5000'
        assert retrieved.game.game_id == 'test_game_123'
        assert repr(retrieved) == "GameTeam(id=1, desc='Fire Team')"
