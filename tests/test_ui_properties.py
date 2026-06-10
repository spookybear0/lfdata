"""Tests for the PropertiesPanel class."""

from typing import Any
from unittest.mock import MagicMock
import pytest


# Universal Dummy definitions to prevent conflicts in sys.modules
class DummyStringVar:
    """Mock StringVar for testing."""

    def __init__(self, value: str = '') -> None:
        self._val = str(value)

    def get(self) -> str:
        return self._val

    def set(self, value: str) -> None:
        self._val = str(value)


class DummyBooleanVar:
    """Mock BooleanVar for testing."""

    def __init__(self, value: bool = False) -> None:
        self._val = bool(value)

    def get(self) -> bool:
        return self._val

    def set(self, value: bool) -> None:
        self._val = bool(value)


class DummyWidget:
    """A universal mocked Tkinter widget to prevent library/display dependencies."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._state: str = 'normal'
        self.image: Any = None
        self.text: str = ''
        self._items: list[str] = []
        self._selection: list[int] = []

    def grid(self, *args: Any, **kwargs: Any) -> None:
        pass

    def pack(self, *args: Any, **kwargs: Any) -> None:
        pass

    def place(self, *args: Any, **kwargs: Any) -> None:
        pass

    def pack_propagate(self, *args: Any, **kwargs: Any) -> None:
        pass

    def grid_propagate(self, *args: Any, **kwargs: Any) -> None:
        pass

    def bind(self, *args: Any, **kwargs: Any) -> None:
        pass

    def grid_columnconfigure(self, *args: Any, **kwargs: Any) -> None:
        pass

    def grid_rowconfigure(self, *args: Any, **kwargs: Any) -> None:
        pass

    def rowconfigure(self, *args: Any, **kwargs: Any) -> None:
        pass

    def columnconfigure(self, *args: Any, **kwargs: Any) -> None:
        pass

    def winfo_children(self) -> list[Any]:
        return []

    def __setitem__(self, key: str, value: Any) -> None:
        if key == 'state':
            self._state = value
        elif key == 'text':
            self.text = str(value)
        elif key == 'image':
            self.image = value

    def config(self, *args: Any, **kwargs: Any) -> None:
        if 'image' in kwargs:
            self.image = kwargs['image']
        if 'text' in kwargs:
            self.text = kwargs['text']

    def configure(self, *args: Any, **kwargs: Any) -> None:
        self.config(*args, **kwargs)

    def update_idletasks(self) -> None:
        pass

    def update(self) -> None:
        pass

    def after(self, *args: Any, **kwargs: Any) -> None:
        pass

    def title(self, *args: Any, **kwargs: Any) -> None:
        pass

    def geometry(self, *args: Any, **kwargs: Any) -> None:
        pass

    def minsize(self, *args: Any, **kwargs: Any) -> None:
        pass

    def destroy(self) -> None:
        pass

    def add(self, *args: Any, **kwargs: Any) -> None:
        pass

    def set(self, *args: Any, **kwargs: Any) -> None:
        pass

    def get(self, *args: Any, **kwargs: Any) -> Any:
        return ''

    # Listbox methods
    def delete(self, start: int, end: Any = None) -> None:
        self._items = []

    def insert(self, index: Any, item: str) -> None:
        self._items.append(item)

    def curselection(self) -> list[int]:
        return self._selection

    def selection_clear(self, *args: Any) -> None:
        self._selection = []

    def selection_set(self, index: int) -> None:
        self._selection = [index]

    def see(self, index: int) -> None:
        pass

    def yview(self, *args: Any, **kwargs: Any) -> None:
        pass


# Directly monkeypatch the loaded tkinter modules
import tkinter  # noqa: E402
import tkinter.ttk  # noqa: E402

tkinter.StringVar = DummyStringVar
tkinter.BooleanVar = DummyBooleanVar
tkinter.ttk.LabelFrame = DummyWidget
tkinter.ttk.Label = DummyWidget
tkinter.ttk.Entry = DummyWidget
tkinter.ttk.Combobox = DummyWidget
tkinter.ttk.Checkbutton = DummyWidget
tkinter.NORMAL = 'normal'
tkinter.DISABLED = 'disabled'

from lfdata.ui.properties import PropertiesPanel  # noqa: E402
from lfdata.ui.config_manager import UIConfigManager  # noqa: E402


@pytest.fixture
def manager() -> UIConfigManager:
    """Fixture returning a fresh config manager.

    Returns:
        UIConfigManager: Config manager instance.
    """
    cm = UIConfigManager()
    cm.update_element('time', 'enabled', True)
    cm.update_element('time', 'x', 0.8)
    cm.update_element('time', 'y', 0.2)
    cm.update_element('time', 'align', 'right')
    cm.update_element('time', 'font', 'advanced_pixel_lcd-7')
    cm.update_element('time', 'size', 40)
    cm.update_element('time', 'visible_start_ms', 1000)
    return cm


def test_properties_load_element(manager: UIConfigManager) -> None:
    """Tests loading an element into properties panel form variables."""
    update_called = False

    def on_update() -> None:
        nonlocal update_called
        update_called = True

    parent = MagicMock()
    panel = PropertiesPanel(parent, manager, on_update)

    # Initial state should be disabled/clear
    assert panel.selected_element is None

    # Load element
    panel.load_element('time')
    assert panel.selected_element == 'time'
    assert panel.enabled_var.get() is True
    assert panel.x_var.get() == '0.800'
    assert panel.y_var.get() == '0.200'
    assert panel.align_var.get() == 'right'
    assert panel.font_var.get() == 'advanced_pixel_lcd-7'
    assert panel.size_var.get() == '40'
    assert panel.start_ms_var.get() == '1000'


def test_properties_clear(manager: UIConfigManager) -> None:
    """Tests clearing the properties panel."""
    parent = MagicMock()
    panel = PropertiesPanel(parent, manager, lambda: None)

    panel.load_element('time')
    panel.load_element(None)

    assert panel.selected_element is None
    assert panel.x_var.get() == ''
    assert panel.y_var.get() == ''
    assert panel.align_var.get() == ''
    assert panel.font_var.get() == ''


def test_properties_apply(manager: UIConfigManager) -> None:
    """Tests applying form changes updates config manager."""
    update_called = False

    def on_update() -> None:
        nonlocal update_called
        update_called = True

    parent = MagicMock()
    panel = PropertiesPanel(parent, manager, on_update)

    panel.load_element('time')

    # Change values in variables
    panel.x_var.set('0.15')
    panel.y_var.set('0.85')
    panel.w_var.set('0.3')
    panel.h_var.set('0.2')
    panel.size_var.set('25')
    panel.start_ms_var.set('5000')

    # Apply changes
    panel._apply_properties()

    assert update_called is True
    el = manager.get_element('time')
    assert el is not None
    assert el.get('x') == 0.15
    assert el.get('y') == 0.85
    assert el.get('extents') == [0.3, 0.2]
    assert el.get('style', {}).get('size') == 25
    assert el.get('visible_start_ms') == 5000
