import pytest

from lfdata.model import LFTeamColor


def test_lf_team_color_enum() -> None:
    fire = LFTeamColor.FIRE
    assert fire.color_enum == 11
    assert fire.display_name == "Fire"
    assert fire.rgb == "#FF5000"


def test_lf_team_color_from_enum() -> None:
    assert LFTeamColor.from_enum(11) == LFTeamColor.FIRE
    assert LFTeamColor.from_enum(13) == LFTeamColor.EARTH

    with pytest.raises(ValueError):
        LFTeamColor.from_enum(99)
