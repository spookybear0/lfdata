"""Tests for the AnimationOverviewPanel class."""

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


class DummyWidget:
    """A universal mocked Tkinter widget to prevent library/display dependencies."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._state: str = 'normal'
        self.image: Any = None
        self.text: str = ''
        self._items: list[str] = []
        self._selection: list[Any] = []
        self._mapped: bool = True
        self._options: dict[str, Any] = {}

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self._mapped = True

    def pack(self, *args: Any, **kwargs: Any) -> None:
        self._mapped = True

    def place(self, *args: Any, **kwargs: Any) -> None:
        self._mapped = True

    def pack_propagate(self, *args: Any, **kwargs: Any) -> None:
        pass

    def grid_propagate(self, *args: Any, **kwargs: Any) -> None:
        pass

    def grid_remove(self, *args: Any, **kwargs: Any) -> None:
        self._mapped = False

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

    def winfo_ismapped(self) -> bool:
        return self._mapped

    def winfo_width(self) -> int:
        return 300

    def winfo_height(self) -> int:
        return 150

    def __setitem__(self, key: str, value: Any) -> None:
        self._options[key] = value
        if key == 'state':
            self._state = value
        elif key == 'text':
            self.text = str(value)
        elif key == 'image':
            self.image = value

    def __getitem__(self, key: str) -> Any:
        return self._options.get(key)

    def config(self, *args: Any, **kwargs: Any) -> None:
        self._options.update(kwargs)
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
        if args and isinstance(args[0], int):
            idx = args[0]
            if 0 <= idx < len(self._items):
                return self._items[idx]
        return ''

    # Listbox / Treeview common methods
    def delete(self, *args: Any, **kwargs: Any) -> None:
        self._items = []

    def insert(self, *args: Any, **kwargs: Any) -> str:
        if len(args) >= 2 and isinstance(args[0], str):
            iid = kwargs.get('iid', args[2] if len(args) > 2 else None)
            text = kwargs.get('text', args[3] if len(args) > 3 else '')
            item_name = iid or text
            if item_name:
                self._items.append(str(item_name))
                return str(item_name)
        elif len(args) >= 2:
            self._items.append(str(args[1]))
            return str(args[1])
        return ''

    def curselection(self) -> list[int]:
        res = []
        for s in self._selection:
            if s in self._items:
                res.append(self._items.index(s))
        return res

    def selection_clear(self, *args: Any) -> None:
        self._selection = []

    def selection_set(self, *args: Any) -> None:
        if not args:
            self._selection = []
            return
        val = args[0]
        if isinstance(val, (list, tuple)):
            self._selection = list(val)
        else:
            self._selection = [val]

    def selection(self) -> list[Any]:
        return self._selection

    def get_children(self) -> list[str]:
        return self._items

    def exists(self, item: str) -> bool:
        return item in self._items

    def item(self, item: str, **kwargs: Any) -> None:
        pass

    def identify_row(self, y: int) -> str | None:
        return self._items[0] if self._items else None

    def identify_element(self, x: int, y: int) -> str:
        return 'image'

    def see(self, index: Any) -> None:
        pass

    def yview(self, *args: Any, **kwargs: Any) -> None:
        pass


class DummyCanvas(DummyWidget):
    """Mock Canvas widget for testing."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> None:
        pass

    def create_line(self, *args: Any, **kwargs: Any) -> int:
        return 1

    def create_oval(self, *args: Any, **kwargs: Any) -> int:
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


# Directly monkeypatch the loaded tkinter modules
import tkinter  # noqa: E402
import tkinter.ttk  # noqa: E402

tkinter.StringVar = DummyStringVar
tkinter.Canvas = DummyCanvas
tkinter.ttk.LabelFrame = DummyWidget
tkinter.ttk.Frame = DummyWidget
tkinter.ttk.Label = DummyWidget
tkinter.ttk.Combobox = DummyWidget
tkinter.ttk.Button = DummyWidget
tkinter.ttk.Treeview = DummyWidget
tkinter.NORMAL = 'normal'
tkinter.DISABLED = 'disabled'

from lfdata.ui.animation_overview import AnimationOverviewPanel  # noqa: E402
from lfdata.ui.config_manager import UIConfigManager  # noqa: E402


@pytest.fixture
def manager() -> UIConfigManager:
    """Fixture returning a config manager with animation.

    Returns:
        UIConfigManager: Config manager instance.
    """
    cm = UIConfigManager()
    cm.update_element('time', 'enabled', True)
    cm.update_element('time', 'x', 0.8)
    cm.toggle_prop_animated('time', 'x')
    return cm


def test_animation_overview_load(manager: UIConfigManager) -> None:
    """Tests loading an element into the overview panel."""
    parent = MagicMock()
    panel = AnimationOverviewPanel(parent, manager)

    assert panel.element_name is None

    # Load element
    panel.load_element('time')
    assert panel.element_name == 'time'
    assert panel.cmb_prop['values'] == ['x', 'y', 'size (font size)']
    assert panel.prop_var.get() == 'x'


def test_animation_overview_delete_keyframe(manager: UIConfigManager) -> None:
    """Tests deleting a keyframe from the panel."""
    parent = MagicMock()
    panel = AnimationOverviewPanel(parent, manager)

    panel.load_element('time')

    el = manager.get_element('time')
    assert el is not None
    keyframes = el['x']['keyframes']
    assert len(keyframes) == 1

    panel.selected_kf_idx = 0
    panel._update_edit_state()

    panel._on_delete_click()

    assert len(keyframes) == 0
    assert panel.selected_kf_idx is None
