"""Tests for the LayoutCanvas class."""

from typing import Any
from unittest.mock import MagicMock, patch
import pytest


class DummyCanvas:
    """A dummy canvas class to mock tkinter Canvas in tests."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def bind(self, *args: Any, **kwargs: Any) -> None:
        pass

    def delete(self, *args: Any, **kwargs: Any) -> None:
        pass

    def create_line(self, *args: Any, **kwargs: Any) -> int:
        return 1

    def create_rectangle(self, *args: Any, **kwargs: Any) -> int:
        return 1

    def create_text(self, *args: Any, **kwargs: Any) -> int:
        return 1

    def create_window(self, *args: Any, **kwargs: Any) -> int:
        return 1

    def itemconfig(self, *args: Any, **kwargs: Any) -> None:
        pass

    def yview_scroll(self, *args: Any, **kwargs: Any) -> None:
        pass

    def bbox(self, *args: Any, **kwargs: Any) -> tuple[int, int, int, int]:
        return (0, 0, 100, 100)


# Mock tkinter before importing canvas to avoid TclError in headless testing

with patch('tkinter.Canvas', DummyCanvas), patch('tkinter.Tk', MagicMock):
    from lfdata.ui.canvas import LayoutCanvas  # noqa: E402

from lfdata.ui.config_manager import UIConfigManager  # noqa: E402


class DummyEvent:
    """Mock Tkinter event for simulated user actions."""

    def __init__(self, x: int, y: int) -> None:
        """Initializes the mock event.

        Args:
            x: Mouse X coordinate.
            y: Mouse Y coordinate.
        """
        self.x = x
        self.y = y


@pytest.fixture
def mock_root() -> MagicMock:
    """Fixture returning a mock root window.

    Returns:
        MagicMock: A mock tkinter root.
    """
    return MagicMock()


@pytest.fixture
def manager() -> UIConfigManager:
    """Fixture returning a config manager with enabled elements.

    Returns:
        UIConfigManager: The configuration manager.
    """
    cm = UIConfigManager()
    cm.update_element('time', 'enabled', True)
    cm.update_element('time', 'x', 0.5)
    cm.update_element('time', 'y', 0.5)
    cm.update_element('time', 'align', 'center')
    cm.update_element('time', 'extents', [0.2, 0.1])
    return cm


def test_canvas_bounds_calculation(
    mock_root: MagicMock, manager: UIConfigManager
) -> None:
    """Tests that relative element coordinates map correctly to canvas bounds."""
    called_name: str | None = None

    def on_select(name: str | None) -> None:
        nonlocal called_name
        called_name = name

    canvas = LayoutCanvas(mock_root, manager, on_select)
    el = manager.get_element('time')
    assert el is not None

    # Width: 640, Height: 360
    # time: x=0.5, y=0.5, extents=[0.2, 0.1], align='center'
    # w_canvas = 0.2 * 640 = 128
    # h_canvas = 0.1 * 360 = 36
    # x_anchor = 0.5 * 640 = 320
    # y_anchor = 0.5 * 360 = 180
    # x1 = 320 - 64 = 256
    # x2 = 256 + 128 = 384
    # y1 = 180
    # y2 = 180 + 36 = 216
    x1, y1, x2, y2 = canvas._get_element_bounds('time', el)
    assert x1 == pytest.approx(256.0)
    assert y1 == pytest.approx(180.0)
    assert x2 == pytest.approx(384.0)
    assert y2 == pytest.approx(216.0)


def test_canvas_selection_via_click(
    mock_root: MagicMock, manager: UIConfigManager
) -> None:
    """Tests simulating a click event inside element bounds updates selection."""
    selected_name: str | None = None

    def on_select(name: str | None) -> None:
        nonlocal selected_name
        selected_name = name

    canvas = LayoutCanvas(mock_root, manager, on_select)
    canvas.refresh_elements()

    # Click inside 'time' element bounds (256 <= x <= 384, 180 <= y <= 216)
    click_element = DummyEvent(300, 190)

    # Mock tkinter canvas methods
    canvas.find_withtag = MagicMock(return_value=[1])
    canvas.gettags = MagicMock(return_value=('el:time', 'element'))

    canvas._on_click(click_element)
    assert canvas.selected_element == 'time'
    assert selected_name == 'time'


def test_canvas_drag_move(
    mock_root: MagicMock, manager: UIConfigManager
) -> None:
    """Tests dragging a selected element updates its coordinates."""
    selected_name: str | None = None

    def on_select(name: str | None) -> None:
        nonlocal selected_name
        selected_name = name

    canvas = LayoutCanvas(mock_root, manager, on_select)
    canvas.selected_element = 'time'
    canvas._drag_mode = 'move'
    canvas._start_x = 300.0
    canvas._start_y = 190.0
    canvas._element_start_x = 0.5
    canvas._element_start_y = 0.5

    # Drag 64 pixels right (0.1 of width) and 36 pixels down (0.1 of height)
    drag_event = DummyEvent(364, 226)
    canvas._on_drag(drag_event)

    el = manager.get_element('time')
    assert el is not None
    assert el.get('x') == pytest.approx(0.6)
    assert el.get('y') == pytest.approx(0.6)
    assert selected_name == 'time'


def test_canvas_drag_resize(
    mock_root: MagicMock, manager: UIConfigManager
) -> None:
    """Tests dragging the resize handle updates the element extents."""
    selected_name: str | None = None

    def on_select(name: str | None) -> None:
        nonlocal selected_name
        selected_name = name

    canvas = LayoutCanvas(mock_root, manager, on_select)
    canvas.selected_element = 'time'
    canvas._drag_mode = 'resize'
    canvas._start_x = 384.0
    canvas._start_y = 216.0
    canvas._element_start_w = 0.2
    canvas._element_start_h = 0.1

    # Resize mouse move 32 pixels wider (+0.05) and 18 pixels taller (+0.05)
    drag_event = DummyEvent(416, 234)
    canvas._on_drag(drag_event)

    el = manager.get_element('time')
    assert el is not None
    extents = el.get('extents')
    assert extents is not None
    assert extents[0] == pytest.approx(0.25)
    assert extents[1] == pytest.approx(0.15)


def test_canvas_update_callback_on_release(
    mock_root: MagicMock, manager: UIConfigManager
) -> None:
    """Tests that the update callback is invoked on release after dragging."""
    update_called = False

    def on_update() -> None:
        nonlocal update_called
        update_called = True

    canvas = LayoutCanvas(
        mock_root, manager, lambda name: None, on_update_callback=on_update
    )
    # Test release without drag_mode does not trigger
    canvas._drag_mode = None
    canvas._on_release(DummyEvent(0, 0))
    assert not update_called

    # Test release with drag_mode triggers
    canvas._drag_mode = 'move'
    canvas._on_release(DummyEvent(0, 0))
    assert update_called
    assert canvas._drag_mode is None


def test_canvas_with_animated_properties(
    mock_root: MagicMock, manager: UIConfigManager
) -> None:
    """Tests that canvas resolves animated property dicts correctly."""
    # Toggle animation on property 'x'
    manager.toggle_prop_animated('time', 'x')
    el = manager.get_element('time')
    assert el is not None
    assert isinstance(el.get('x'), dict)

    canvas = LayoutCanvas(mock_root, manager, lambda name: None)

    # Set keyframe value to 0.8
    el['x']['keyframes'][0]['value'] = 0.8

    # Width: 640, Height: 360
    # time: x=0.8 resolved, y=0.5, extents=[0.2, 0.1], align='center'
    # w_canvas = 0.2 * 640 = 128
    # h_canvas = 0.1 * 360 = 36
    # x_anchor = 0.8 * 640 = 512
    # y_anchor = 0.5 * 360 = 180
    # x1 = 512 - 64 = 448
    # x2 = 448 + 128 = 576
    x1, y1, x2, y2 = canvas._get_element_bounds('time', el)
    assert x1 == pytest.approx(448.0)
    assert x2 == pytest.approx(576.0)
