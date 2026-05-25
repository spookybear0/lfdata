"""SQLAlchemy model for player state history."""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lfdata.model.base import Base


class PlayerStateHistory(Base):
    """Represents a state update event for a game entity.

    These state updates are parsed from the ';9/player-state' record type.
    """

    __tablename__ = 'player_state_history'

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[str] = mapped_column(
        ForeignKey('lf_games.game_id', ondelete='CASCADE'), index=True
    )
    time: Mapped[int] = mapped_column(Integer)
    entity_id: Mapped[str] = mapped_column(String(50), index=True)
    state: Mapped[int] = mapped_column(Integer)

    # Relationships
    game: Mapped['LFGame'] = relationship(
        'LFGame', back_populates='state_history'
    )

    def __repr__(self) -> str:
        """Returns a string representation of the state history entry.

        Returns:
            str: The string representation.
        """
        return (
            f"PlayerStateHistory(id={self.id}, entity_id='{self.entity_id}', "
            f"state={self.state})"
        )
