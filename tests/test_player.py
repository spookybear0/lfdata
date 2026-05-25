from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from lfdata.model import Base, Player


def test_create_player() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        player = Player(codename="Sqnfdcp", real_name="John Doe")
        session.add(player)
        session.commit()

        retrieved = session.query(Player).filter_by(codename="Sqnfdcp").first()
        assert retrieved is not None
        assert retrieved.codename == "Sqnfdcp"
        assert retrieved.real_name == "John Doe"
        assert repr(retrieved) == "Player(id=1, codename='Sqnfdcp')"
