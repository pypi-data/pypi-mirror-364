# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtWidgets import (
    QLineEdit,
)
from PySide6.QtCore import Signal
from PySide6.QtGui import (
    QIcon,
    QKeyEvent,
    QAction,
)

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

## ==> GLOBALS
# ///////////////////////////////////////////////////////////////

## ==> FUNCTIONS
# ///////////////////////////////////////////////////////////////

## ==> VARIABLES
# ///////////////////////////////////////////////////////////////

# CLASS
# ///////////////////////////////////////////////////////////////


class SearchInput(QLineEdit):
    """
    QLineEdit subclass for search input with integrated history and optional search icon.

    Features:
        - Maintains a history of submitted searches
        - Navigate history with up/down arrows
        - Emits a searchSubmitted(str) signal on validation (Enter)
        - Optional search icon (left or right)
        - Optional clear button

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget (default: None).
    max_history : int, optional
        Maximum number of history entries to keep (default: 20).
    search_icon : QIcon or str, optional
        Icon to display as search icon (default: None).
    icon_position : str, optional
        'left' or 'right' (default: 'left').
    clear_button : bool, optional
        Whether to show a clear button (default: True).
    """

    searchSubmitted = Signal(str)

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        parent=None,
        max_history=20,
        search_icon=None,
        icon_position="left",
        clear_button=True,
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        self.setProperty("type", "SearchInput")

        # ////// SETUP PROPERTIES
        self.setPlaceholderText("Search...")
        self.setClearButtonEnabled(clear_button)

        # ////// INITIALIZE VARIABLES
        self._search_icon = search_icon
        self._icon_position = icon_position
        self._clear_button = clear_button
        self._history = []
        self._history_index = -1
        self._max_history = max_history

        # ////// SETUP ICON
        if search_icon:
            icon = (
                QIcon(search_icon)
                if not isinstance(search_icon, QIcon)
                else search_icon
            )
            action = QAction(icon, "Search", self)
            if icon_position == "right":
                self.addAction(action, QLineEdit.TrailingPosition)
            else:
                self.addAction(action, QLineEdit.LeadingPosition)

        # ////// CLEAR BUTTON
        self.setClearButtonEnabled(clear_button)

    # HISTORY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def add_to_history(self, text: str):
        """Add a search term to the history, avoiding duplicates and enforcing max size."""
        text = text.strip()
        if not text:
            return
        if text in self._history:
            self._history.remove(text)
        self._history.insert(0, text)
        if len(self._history) > self._max_history:
            self._history = self._history[: self._max_history]
        self._history_index = -1

    def get_history(self):
        """Return the current search history as a list."""
        return list(self._history)

    def clear_history(self):
        """Clear the search history."""
        self._history.clear()
        self._history_index = -1

    def set_history(self, history_list):
        """Replace the search history with a new list."""
        self._history = list(history_list)
        self._history_index = -1

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # ////// NAVIGATE HISTORY
        if event.key() == 16777235:  # Qt.Key_Up
            if self._history:
                if self._history_index + 1 < len(self._history):
                    self._history_index += 1
                    self.setText(self._history[self._history_index])
                    self.selectAll()
            return
        elif event.key() == 16777237:  # Qt.Key_Down
            if self._history_index > 0:
                self._history_index -= 1
                self.setText(self._history[self._history_index])
                self.selectAll()
            elif self._history_index == 0:
                self._history_index = -1
                self.clear()
            return
        # ////// SUBMIT SEARCH
        elif event.key() in (16777220, 16777221):  # Qt.Key_Return, Qt.Key_Enter
            text = self.text().strip()
            if text:
                self.add_to_history(text)
                self.searchSubmitted.emit(text)
            return
        super().keyPressEvent(event)

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget's style (useful after dynamic stylesheet changes)."""
        # // REFRESH STYLE
        self.style().unpolish(self)
        self.style().polish(self)
        # //////
