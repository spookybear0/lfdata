"""SQLAlchemy model for players."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from lfdata.model.base import Base


class Player(Base):
    """Represents a global player across games.

    A player is an individual person who participates in LF games.
    """

    __tablename__ = 'players'

    id: Mapped[int] = mapped_column(primary_key=True)
    codename: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    real_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    def __repr__(self) -> str:
        """Returns a string representation of the player.

        Returns:
            str: The string representation.
        """
        return f"Player(id={self.id}, codename='{self.codename}')"
