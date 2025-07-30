# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtGui import (
    QKeySequence,
)
from PySide6.QtWidgets import (
    QApplication,
    QPlainTextEdit,
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


class TabReplaceTextEdit(QPlainTextEdit):
    """
    QPlainTextEdit subclass that sanitizes pasted text by replacing tab characters according to the chosen mode
    and removing empty lines. Useful for pasting tabular data or ensuring clean input.

    Parameters
    ----------
    tab_replacement : str, optional
        The string to replace tab characters with (default: "\n").
    sanitize_on_paste : bool, optional
        Whether to sanitize pasted text (default: True).
    """

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self, *args, tab_replacement="\n", sanitize_on_paste=True, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.setProperty("type", "TabReplaceTextEdit")

        # ////// INITIALIZE VARIABLES
        self._tab_replacement = tab_replacement
        self._sanitize_on_paste = sanitize_on_paste

    # PROPERTY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    @property
    def tab_replacement(self) -> str:
        """Get or set the string used to replace tab characters."""
        return self._tab_replacement

    @tab_replacement.setter
    def tab_replacement(self, value: str) -> None:
        """Set the string used to replace tab characters."""
        self._tab_replacement = str(value)

    @property
    def sanitize_on_paste(self) -> bool:
        """Enable or disable sanitizing pasted text."""
        return self._sanitize_on_paste

    @sanitize_on_paste.setter
    def sanitize_on_paste(self, value: bool) -> None:
        """Set whether to sanitize pasted text."""
        self._sanitize_on_paste = bool(value)

    # UTILITY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def sanitize_text(self, text: str) -> str:
        """Sanitize the given text according to the current settings."""
        text = text.replace("\t", self._tab_replacement)
        lines = text.split("\n")
        lines = [line for line in lines if line.strip()]
        return "\n".join(lines)

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def keyPressEvent(self, event) -> None:
        """
        Overridden method from QPlainTextEdit. Modifies the behavior of the paste operation.

        Args:
            event: The event that triggers the method.
        """
        if self._sanitize_on_paste and event.matches(QKeySequence.StandardKey.Paste):
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            text = self.sanitize_text(text)
            self.insertPlainText(text)
        else:
            super().keyPressEvent(event)

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget's style (useful after dynamic stylesheet changes)."""
        # // REFRESH STYLE
        self.style().unpolish(self)
        self.style().polish(self)
        # //////
