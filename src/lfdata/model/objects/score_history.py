"""SQLAlchemy model for game score history."""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lfdata.model.base import Base


class ScoreHistory(Base):
    """Represents a score update event for a game entity.

    These score updates are parsed from the ';5/score' record type.
    """

    __tablename__ = 'score_history'

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[str] = mapped_column(
        ForeignKey('lf_games.game_id', ondelete='CASCADE'), index=True
    )
    time: Mapped[int] = mapped_column(Integer)
    entity_id: Mapped[str] = mapped_column(String(50), index=True)
    old_score: Mapped[int] = mapped_column(Integer)
    delta_score: Mapped[int] = mapped_column(Integer)
    new_score: Mapped[int] = mapped_column(Integer)

    # Relationships
    game: Mapped['LFGame'] = relationship(
        'LFGame', back_populates='score_history'
    )

    def __repr__(self) -> str:
        """Returns a string representation of the score history entry.

        Returns:
            str: The string representation.
        """
        return (
            f"ScoreHistory(id={self.id}, entity_id='{self.entity_id}', "
            f'delta_score={self.delta_score}, new_score={self.new_score})'
        )
