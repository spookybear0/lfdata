"""SQLAlchemy model for game events."""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lfdata.model.base import Base


class GameEvent(Base):
    """Represents a timestamped event that occurs during a LF game.

    Events involve actions performed by one entity on another, or system actions.
    """

    __tablename__ = "game_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[str] = mapped_column(
        ForeignKey("lf_games.game_id", ondelete="CASCADE"), index=True
    )
    time: Mapped[int] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String(10))
    actor_entity_id: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    target_entity_id: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100))
    raw_message: Mapped[str] = mapped_column(String(255))

    # Relationships
    game: Mapped["LFGame"] = relationship("LFGame", back_populates="events")

    def __repr__(self) -> str:
        """Returns a string representation of the event.

        Returns:
            str: The string representation.
        """
        return (
            f"GameEvent(id={self.id}, time={self.time}, "
            f"event_type='{self.event_type}', action='{self.action}')"
        )
