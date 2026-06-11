"""Tests for the UIConfigManager class."""

from pathlib import Path
from typing import Generator
import pytest

from lfdata.ui.config_manager import UIConfigManager


@pytest.fixture
def manager() -> UIConfigManager:
    """Fixture returning a fresh UIConfigManager instance.

    Returns:
        UIConfigManager: A fresh configuration manager.
    """
    return UIConfigManager()


@pytest.fixture
def temp_yaml(tmp_path: Path) -> Generator[Path, None, None]:
    """Fixture returning a temporary path for YAML config.

    Args:
        tmp_path: The pytest temp path.

    Yields:
        Path: A path to a temporary YAML file.
    """
    yield tmp_path / 'test_config.yaml'


def test_initialization(manager: UIConfigManager) -> None:
    """Verifies default values on initialization."""
    assert manager.config is not None
    assert 'elements' in manager.config
    assert manager.tdf_path is None
    assert manager.game is None
    assert not manager.players
    assert manager.config_path is None


def test_load_and_save_config(
    manager: UIConfigManager, temp_yaml: Path
) -> None:
    """Verifies saving and reloading configuration values."""
    manager.update_global_setting('fps', 45)
    manager.update_element('time', 'enabled', False)
    manager.update_element('time', 'size', 99)

    manager.save_config(str(temp_yaml))
    assert temp_yaml.exists()

    new_manager = UIConfigManager()
    new_manager.load_config(str(temp_yaml))

    assert new_manager.config_path == str(temp_yaml)
    assert new_manager.config.get('fps') == 45
    time_el = new_manager.get_element('time')
    assert time_el is not None
    assert time_el.get('enabled') is False
    assert time_el.get('style', {}).get('size') == 99


def test_load_tdf(manager: UIConfigManager) -> None:
    """Verifies loading a real TDF file updates state."""
    real_path = Path('assets') / 'sm5_sanitized.tdf'
    manager.load_tdf(str(real_path))

    assert manager.game is not None
    assert manager.tdf_path == str(real_path)
    assert len(manager.players) > 0
    assert 'None' not in manager.players
    assert manager.get_player_names() == manager.players


def test_update_element_properties(manager: UIConfigManager) -> None:
    """Verifies updating specific properties updates internal config."""
    # Test setting extents
    manager.update_element('scoreboard', 'extents', [0.5, 0.6])
    el = manager.get_element('scoreboard')
    assert el is not None
    assert el.get('extents') == [0.5, 0.6]

    # Test removing extents
    manager.update_element('scoreboard', 'extents', None)
    el = manager.get_element('scoreboard')
    assert el is not None
    assert 'extents' not in el

    # Test setting font
    manager.update_element('time', 'font', 'Arial')
    el = manager.get_element('time')
    assert el is not None
    assert el.get('style', {}).get('font') == 'Arial'

    # Non-existent element retrieval
    assert manager.get_element('non_existent_element') is None


def test_get_lfdata_command(manager: UIConfigManager) -> None:
    """Verifies retrieval of lfdata command in dev and frozen modes."""
    import sys
    import os

    # 1. Dev Mode (sys.frozen is not set)
    if hasattr(sys, 'frozen'):
        delattr(sys, 'frozen')
    cmd = manager.get_lfdata_command()
    assert cmd == [sys.executable, '-m', 'lfdata']

    # 2. Frozen Mode (sys.frozen = True)
    sys.frozen = True
    try:
        cmd_frozen = manager.get_lfdata_command()
        expected_bin = 'lfdata.exe' if os.name == 'nt' else 'lfdata'
        assert expected_bin in cmd_frozen[0]
    finally:
        delattr(sys, 'frozen')


def test_animation_state_and_keyframes(manager: UIConfigManager) -> None:
    """Verifies is_prop_animated, toggle_prop_animated, and update_element."""
    # Initially element x is not animated
    assert manager.is_prop_animated('time', 'x') is False

    # Toggle animated on
    res = manager.toggle_prop_animated('time', 'x')
    assert res is True
    assert manager.is_prop_animated('time', 'x') is True

    # Check that properties were converted to keyframe dicts
    el = manager.get_element('time')
    assert el is not None
    assert isinstance(el.get('x'), dict)
    assert 'keyframes' in el['x']
    assert el['x']['keyframes'][0]['value'] == 0.98

    # Set current time and update property
    manager.current_time_ms = 10000
    manager.update_element('time', 'x', 0.5)

    # Check keyframe list has been updated / new keyframe added
    assert len(el['x']['keyframes']) == 2
    # Find keyframe at 10000ms
    kf_10000 = None
    for kf in el['x']['keyframes']:
        if kf['time'] == 10000:
            kf_10000 = kf
            break
    assert kf_10000 is not None
    assert kf_10000['value'] == 0.5

    # Toggle animated off
    res = manager.toggle_prop_animated('time', 'x')
    assert res is False
    assert manager.is_prop_animated('time', 'x') is False
    # Converted back to constant
    assert el.get('x') == 0.98
