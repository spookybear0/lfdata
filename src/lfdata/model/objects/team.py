"""SQLAlchemy model for game teams."""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lfdata.model.base import Base


class GameTeam(Base):
    """Represents a team within a LF game.

    Each game mode has specific teams (e.g., Fire Team and Earth Team).
    """

    __tablename__ = 'game_teams'

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[str] = mapped_column(
        ForeignKey('lf_games.game_id', ondelete='CASCADE'), index=True
    )
    team_index: Mapped[int] = mapped_column(Integer)
    desc: Mapped[str] = mapped_column(String(50))
    color_enum: Mapped[int] = mapped_column(Integer)
    color_desc: Mapped[str] = mapped_column(String(50))
    color_rgb: Mapped[str] = mapped_column(String(10))

    # Relationships
    game: Mapped['LFGame'] = relationship('LFGame', back_populates='teams')

    def __repr__(self) -> str:
        """Returns a string representation of the team.

        Returns:
            str: The string representation.
        """
        return f"GameTeam(id={self.id}, desc='{self.desc}')"
