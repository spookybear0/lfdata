"""UI element properties editor panel for the LF data UI."""

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable
from lfdata.ui.config_manager import UIConfigManager


class PropertiesPanel(ttk.LabelFrame):
    """Panel containing form inputs to edit the selected UI element properties."""

    def __init__(
        self,
        parent: tk.Widget,
        config_manager: UIConfigManager,
        on_update_callback: Callable[[], None],
        **kwargs: Any,
    ) -> None:
        """Initializes the properties panel.

        Args:
            parent: The parent tkinter widget.
            config_manager: The configuration manager instance.
            on_update_callback: Callback triggered when properties are modified.
            **kwargs: Additional keyword arguments for the parent widget.
        """
        super().__init__(parent, text=' UI Element Properties ', **kwargs)
        self.config_manager = config_manager
        self.on_update = on_update_callback
        self.selected_element: str | None = None

        self._create_widgets()
        self.clear()

    def _create_widgets(self) -> None:
        """Creates and layouts the form input widgets."""
        self.grid_columnconfigure(1, weight=1)

        # Variables
        self.x_var = tk.StringVar()
        self.y_var = tk.StringVar()
        self.w_var = tk.StringVar()
        self.h_var = tk.StringVar()
        self.align_var = tk.StringVar()
        self.enabled_var = tk.BooleanVar()
        self.font_var = tk.StringVar()
        self.size_var = tk.StringVar()
        self.start_ms_var = tk.StringVar()
        self.end_ms_var = tk.StringVar()
        self.fade_in_ms_var = tk.StringVar()
        self.fade_out_ms_var = tk.StringVar()
        self.formatted_text_var = tk.StringVar()

        # Labels and inputs list for clean layout
        row = 0

        # Enabled Checkbox
        ttk.Label(self, text='Enabled:').grid(
            row=row, column=0, sticky='w', padx=5, pady=3
        )
        self.chk_enabled = ttk.Checkbutton(
            self,
            variable=self.enabled_var,
            command=self._on_check_toggle,
        )
        self.chk_enabled.grid(row=row, column=1, sticky='w', padx=5, pady=3)
        row += 1

        # Coordinates
        self._add_row(row, 'Anchor X (0-1):', self.x_var)
        row += 1
        self._add_row(row, 'Anchor Y (0-1):', self.y_var)
        row += 1
        self._add_row(row, 'Width Extent:', self.w_var)
        row += 1
        self._add_row(row, 'Height Extent:', self.h_var)
        row += 1

        # Alignment
        ttk.Label(self, text='Alignment:').grid(
            row=row, column=0, sticky='w', padx=5, pady=3
        )
        self.cmb_align = ttk.Combobox(
            self,
            textvariable=self.align_var,
            values=['left', 'center', 'right'],
            state='readonly',
        )
        self.cmb_align.grid(row=row, column=1, sticky='ew', padx=5, pady=3)
        self.cmb_align.bind('<<ComboboxSelected>>', self._on_combobox_select)
        row += 1

        # Font & Style
        self._add_row(row, 'Font Family:', self.font_var)
        row += 1
        self._add_row(row, 'Font Size:', self.size_var)
        row += 1

        # Timings (in ms)
        self._add_row(row, 'Start Time (ms):', self.start_ms_var)
        row += 1
        self._add_row(row, 'End Time (ms):', self.end_ms_var)
        row += 1
        self._add_row(row, 'Fade In (ms):', self.fade_in_ms_var)
        row += 1
        self._add_row(row, 'Fade Out (ms):', self.fade_out_ms_var)
        row += 1

        # Formatted Text
        self._add_row(row, 'Formatted Text:', self.formatted_text_var)
        row += 1

    def _add_row(self, row: int, label: str, var: tk.StringVar) -> None:
        """Helper to add a text label and entry row.

        Args:
            row: The row index.
            label: The label text.
            var: The tkinter StringVar to bind.
        """
        ttk.Label(self, text=label).grid(
            row=row, column=0, sticky='w', padx=5, pady=3
        )
        entry = ttk.Entry(self, textvariable=var)
        entry.grid(row=row, column=1, sticky='ew', padx=5, pady=3)
        entry.bind('<FocusOut>', lambda e: self._apply_properties())
        entry.bind('<Return>', lambda e: self._apply_properties())

    def load_element(self, name: str | None) -> None:
        """Loads element configuration values into form variables.

        Args:
            name: The name of the element to load, or None.
        """
        self.selected_element = name
        if not name:
            self.clear()
            return

        el = self.config_manager.get_element(name)
        if not el:
            self.clear()
            return

        self._set_state(tk.NORMAL)

        # Set values
        self.enabled_var.set(bool(el.get('enabled', False)))
        self.x_var.set(f'{el.get("x", 0.0):.3f}')
        self.y_var.set(f'{el.get("y", 0.0):.3f}')

        extents = el.get('extents')
        if extents and len(extents) >= 2:
            self.w_var.set(f'{extents[0]:.3f}')
            self.h_var.set(f'{extents[1]:.3f}')
        else:
            self.w_var.set('')
            self.h_var.set('')

        self.align_var.set(el.get('align', 'left'))

        style = el.get('style', {})
        self.font_var.set(style.get('font', ''))
        self.size_var.set(str(style.get('size', '')))

        self.start_ms_var.set(str(el.get('visible_start_ms', 0)))
        self.end_ms_var.set(str(el.get('visible_end_ms', 0)))
        self.fade_in_ms_var.set(str(el.get('fade_in_ms', 0)))
        self.fade_out_ms_var.set(str(el.get('fade_out_ms', 0)))
        self.formatted_text_var.set(el.get('formatted_text', ''))

    def clear(self) -> None:
        """Clears all input values and disables forms."""
        self.enabled_var.set(False)
        self.x_var.set('')
        self.y_var.set('')
        self.w_var.set('')
        self.h_var.set('')
        self.align_var.set('')
        self.font_var.set('')
        self.size_var.set('')
        self.start_ms_var.set('')
        self.end_ms_var.set('')
        self.fade_in_ms_var.set('')
        self.fade_out_ms_var.set('')
        self.formatted_text_var.set('')

        self._set_state(tk.DISABLED)

    def _set_state(self, state: str) -> None:
        """Helper to set widgets enabled/disabled.

        Args:
            state: The widget state ('normal' or 'disabled').
        """
        for child in self.winfo_children():
            if isinstance(child, ttk.Entry):
                child['state'] = state
            elif isinstance(child, ttk.Combobox):
                child['state'] = 'readonly' if state == tk.NORMAL else state
            elif isinstance(child, ttk.Checkbutton):
                child['state'] = state

    def _on_check_toggle(self) -> None:
        """Handles checkbox clicks immediately."""
        if not self.selected_element:
            return
        self.config_manager.update_element(
            self.selected_element, 'enabled', self.enabled_var.get()
        )
        self.on_update()

    def _on_combobox_select(self, event: tk.Event) -> None:
        """Handles alignment selection immediately.

        Args:
            event: The combobox select event.
        """
        if not self.selected_element:
            return
        self.config_manager.update_element(
            self.selected_element, 'align', self.align_var.get()
        )
        self.on_update()

    def _apply_properties(self) -> None:
        """Parses entry values and applies them back to config manager."""
        if not self.selected_element:
            return

        # Coordinates & sizes
        self._apply_float(self.x_var, 'x')
        self._apply_float(self.y_var, 'y')

        w_str = self.w_var.get().strip()
        h_str = self.h_var.get().strip()
        if w_str and h_str:
            try:
                self.config_manager.update_element(
                    self.selected_element,
                    'extents',
                    [float(w_str), float(h_str)],
                )
            except ValueError:
                pass
        else:
            self.config_manager.update_element(
                self.selected_element, 'extents', None
            )

        # Style & timings
        font_str = self.font_var.get().strip()
        if font_str:
            self.config_manager.update_element(
                self.selected_element, 'font', font_str
            )
        self._apply_int(self.size_var, 'size')

        self._apply_int(self.start_ms_var, 'visible_start_ms')
        self._apply_int(self.end_ms_var, 'visible_end_ms')
        self._apply_int(self.fade_in_ms_var, 'fade_in_ms')
        self._apply_int(self.fade_out_ms_var, 'fade_out_ms')

        txt = self.formatted_text_var.get()
        self.config_manager.update_element(
            self.selected_element, 'formatted_text', txt
        )

        self.on_update()

    def _apply_float(self, var: tk.StringVar, key: str) -> None:
        """Parses a StringVar to float and updates element config.

        Args:
            var: The entry variable.
            key: The config key.
        """
        val_str = var.get().strip()
        if val_str:
            try:
                self.config_manager.update_element(
                    self.selected_element, key, float(val_str)
                )
            except ValueError:
                pass

    def _apply_int(self, var: tk.StringVar, key: str) -> None:
        """Parses a StringVar to int and updates element config.

        Args:
            var: The entry variable.
            key: The config key.
        """
        val_str = var.get().strip()
        if val_str:
            try:
                self.config_manager.update_element(
                    self.selected_element, key, int(val_str)
                )
            except ValueError:
                pass
