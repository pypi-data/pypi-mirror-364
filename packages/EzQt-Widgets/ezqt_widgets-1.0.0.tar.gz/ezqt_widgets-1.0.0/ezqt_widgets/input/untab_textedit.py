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


class UntabTextEdit(QPlainTextEdit):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setProperty("type", "UntabTextEdit")

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def keyPressEvent(self, event) -> None:
        """
        Overridden method from QPlainTextEdit. Modifies the behavior of the paste operation.

        Args:
            event: The event that triggers the method.
        """
        if event.matches(QKeySequence.StandardKey.Paste):
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            text = text.replace("\t", "\n")  # Replace tabs with newlines
            lines = text.split("\n")  # Split the text into lines
            lines = [line for line in lines if line.strip()]  # Remove empty lines
            text = "\n".join(lines)  # Join the lines back together
            self.insertPlainText(text)
        else:
            super().keyPressEvent(event)
