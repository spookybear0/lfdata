from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from lfdata.model import Base, GameEntity, LFGame, Player


def test_create_entity() -> None:
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        game = LFGame(
            game_id='test_game_123',
            timestamp=datetime.now(),
            game_type='SM5',
        )
        player = Player(codename='Sqnfdcp', real_name='John Doe')
        session.add_all([game, player])
        session.commit()

        entity = GameEntity(
            game_id='test_game_123',
            entity_id='#dJevxws',
            type='player',
            desc='Sqnfdcp',
            team_index=1,
            level=0,
            category=2,
            battlesuit='Maverick',
            end_score=1500,
            player_id=player.id,
        )
        session.add(entity)
        session.commit()

        retrieved = (
            session.query(GameEntity)
            .filter_by(game_id='test_game_123', entity_id='#dJevxws')
            .first()
        )
        assert retrieved is not None
        assert retrieved.type == 'player'
        assert retrieved.desc == 'Sqnfdcp'
        assert retrieved.team_index == 1
        assert retrieved.level == 0
        assert retrieved.category == 2
        assert retrieved.battlesuit == 'Maverick'
        assert retrieved.end_score == 1500
        assert retrieved.player is not None
        assert retrieved.player.codename == 'Sqnfdcp'
        assert retrieved.game.game_id == 'test_game_123'
        assert repr(retrieved) == (
            "GameEntity(id=1, entity_id='#dJevxws', type='player', desc='Sqnfdcp')"
        )
