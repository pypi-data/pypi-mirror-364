# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtWidgets import (
    QLineEdit,
    QCompleter,
)
from PySide6.QtCore import (
    Qt,
    QStringListModel,
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


class AutoCompleteInput(QLineEdit):
    """
    QLineEdit subclass with autocompletion support.
    You can provide a list of suggestions (strings) to be used for autocompletion.

    Parameters
    ----------
    suggestions : list of str, optional
        List of strings to use for autocompletion (default: empty list).
    case_sensitive : bool, optional
        Whether the autocompletion is case sensitive (default: False).
    """

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(self, *args, suggestions=None, case_sensitive=False, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setProperty("type", "AutoCompleteInput")

        # ////// INITIALIZE VARIABLES
        self._suggestions = suggestions or []
        self._case_sensitive = case_sensitive
        # ////// SETUP COMPLETER
        self._completer = QCompleter(self)
        self._model = QStringListModel(self._suggestions, self)
        self._completer.setModel(self._model)
        self._completer.setCaseSensitivity(
            Qt.CaseSensitive if self._case_sensitive else Qt.CaseInsensitive
        )
        self._completer.setFilterMode(Qt.MatchContains)
        self.setCompleter(self._completer)

    # PROPERTY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    @property
    def suggestions(self):
        """Get or set the list of suggestions for autocompletion."""
        return self._suggestions

    @suggestions.setter
    def suggestions(self, value):
        self._suggestions = list(value)
        self._model.setStringList(self._suggestions)
        # ////// UPDATE COMPLETER MODEL
        self._completer.setModel(self._model)

    @property
    def case_sensitive(self):
        """Get or set whether autocompletion is case sensitive."""
        return self._case_sensitive

    @case_sensitive.setter
    def case_sensitive(self, value):
        self._case_sensitive = bool(value)
        # ////// UPDATE CASE SENSITIVITY AND FILTER MODE
        self._completer.setCaseSensitivity(
            Qt.CaseSensitive if self._case_sensitive else Qt.CaseInsensitive
        )
        self._completer.setFilterMode(Qt.MatchContains)

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget's style (useful after dynamic stylesheet changes)."""
        # // REFRESH STYLE
        self.style().unpolish(self)
        self.style().polish(self)
        # //////
