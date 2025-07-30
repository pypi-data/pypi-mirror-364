# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import (
    Signal,
)
from PySide6.QtWidgets import (
    QLabel,
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


class ToggleLabel(QLabel):
    onClick = Signal()

    # ///////////////////////////////////////////////////////////////

    def __init__(self, parent=None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.setProperty("type", "ToggleLabel")
        self.state = "closed"
        self.set_state_closed()

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def mousePressEvent(self, event) -> None:
        self.toggle_state()
        self.onClick.emit()
        super().mousePressEvent(event)

    # STATUS FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def toggle_state(self) -> None:
        # //////
        if self.state == "closed":
            self.state = "opened"
            self.setProperty("class", "drop_down")
        # //////
        else:
            self.state = "closed"
            self.setProperty("class", "drop_up")

        # //////
        self.refreshStyle()

    # ///////////////////////////////////////////////////////////////

    def set_state_closed(self) -> None:
        self.state = "closed"
        self.setProperty("class", "drop_up")
        # //////
        self.refreshStyle()

    # ///////////////////////////////////////////////////////////////

    def set_state_opened(self) -> None:
        self.state = "opened"
        self.setProperty("class", "drop_down")
        # //////
        self.refreshStyle()

    # ///////////////////////////////////////////////////////////////

    def get_state(self) -> None:
        return self.state

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refreshStyle(self) -> None:
        self.style().unpolish(self)
        self.style().polish(self)
