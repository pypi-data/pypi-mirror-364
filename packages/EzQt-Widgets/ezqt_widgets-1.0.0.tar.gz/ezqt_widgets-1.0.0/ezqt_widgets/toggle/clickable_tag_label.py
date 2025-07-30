# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import (
    Signal,
    Qt,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QSizePolicy,
    QFrame,
    QLabel,
)
from PySide6.QtGui import (
    QFont,
    QMouseEvent,
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


class ClickableTagLabel(QFrame):
    _enabled = False
    # //////
    clicked = Signal()
    toggle_keyword = Signal(str)

    # ///////////////////////////////////////////////////////////////

    def __init__(self, parent=None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.setProperty("type", "ClickableTagLabel")

        # Configuration initiale du Frame principal
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)
        self.setContentsMargins(4, 0, 4, 0)
        self.setFixedHeight(20)

        # Création du layout horizontal pour le statut
        self.status_HLayout = QHBoxLayout(self)
        self.status_HLayout.setObjectName("status_HLayout")
        self.status_HLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.status_HLayout.setContentsMargins(0, 0, 0, 0)
        self.status_HLayout.setSpacing(12)

        # Création du label pour le statut
        self.status_label = QLabel(parent)
        self.status_label.setObjectName("tag")
        self.status_label.setFont(QFont("Segoe UI", 8))
        self.status_label.setLineWidth(0)
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.status_label.setStyleSheet("color: rgb(86, 86, 86);")

        # Ajout du label au layout horizontal
        self.status_HLayout.addWidget(self.status_label, 0, Qt.AlignmentFlag.AlignTop)

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_state()
            self.toggle_keyword.emit(self.get_name())
            self.clicked.emit()
        super().mousePressEvent(event)

    # NAME FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def set_name(self, text: str) -> None:
        self.status_label.setText(text)
        self.setObjectName(text)

    # ///////////////////////////////////////////////////////////////

    def get_name(self) -> None:
        return self.status_label.text()

    # STATUS FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def toggle_state(self) -> None:
        # //////
        if not self._enabled:
            self.set_enabled()
            self._enabled = True
        # //////
        else:
            self.set_disabled()
            self._enabled = False

    # ///////////////////////////////////////////////////////////////

    def set_enabled(self) -> None:
        self.setProperty("class", "enabled")
        self.refreshStyle()
        # //////
        self.adjustSize()

    # ///////////////////////////////////////////////////////////////

    def set_disabled(self) -> None:
        self.setProperty("class", "disabled")
        self.refreshStyle()
        # //////
        self.adjustSize()

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refreshStyle(self) -> None:
        self.style().unpolish(self)
        self.style().polish(self)
