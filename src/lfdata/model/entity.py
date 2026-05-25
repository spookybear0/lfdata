"""SQLAlchemy model for game entities."""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lfdata.model.base import Base


class GameEntity(Base):
    """Represents an entity in a LF game.

    Entities include players, referees, standard targets, and generator targets.
    """

    __tablename__ = 'game_entities'

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[str] = mapped_column(
        ForeignKey('lf_games.game_id', ondelete='CASCADE'), index=True
    )
    entity_id: Mapped[str] = mapped_column(String(50), index=True)
    type: Mapped[str] = mapped_column(String(50))
    desc: Mapped[str] = mapped_column(String(100))
    team_index: Mapped[int] = mapped_column(Integer)
    level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    category: Mapped[int | None] = mapped_column(Integer, nullable=True)
    battlesuit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    end_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    player_id: Mapped[int | None] = mapped_column(
        ForeignKey('players.id', ondelete='SET NULL'), nullable=True
    )

    # Relationships
    game: Mapped['LFGame'] = relationship('LFGame', back_populates='entities')
    player: Mapped['Player | None'] = relationship('Player')

    def __repr__(self) -> str:
        """Returns a string representation of the entity.

        Returns:
            str: The string representation.
        """
        return (
            f"GameEntity(id={self.id}, entity_id='{self.entity_id}', "
            f"type='{self.type}', desc='{self.desc}')"
        )
