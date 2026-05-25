import pytest

from lfdata.model import LFTeamColor, LFTeamType


def test_lf_team_type_enum() -> None:
    fire = LFTeamType.FIRE
    assert fire.team_index == 0
    assert fire.display_name == 'Fire Team'
    assert fire.color == LFTeamColor.FIRE


def test_lf_team_type_from_index() -> None:
    assert LFTeamType.from_index(0) == LFTeamType.FIRE
    assert LFTeamType.from_index(1) == LFTeamType.EARTH

    with pytest.raises(ValueError):
        LFTeamType.from_index(99)
