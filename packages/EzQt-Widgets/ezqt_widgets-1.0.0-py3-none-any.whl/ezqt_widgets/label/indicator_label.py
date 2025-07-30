# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import (
    Qt,
    QSize,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QFrame,
    QLabel,
)
from PySide6.QtGui import (
    QFont,
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


class IndicatorLabel(QFrame):

    # ///////////////////////////////////////////////////////////////

    def __init__(self, parent=None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.setProperty("type", "IndicatorLabel")

        # Configuration initiale du Frame principal
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)
        self.setContentsMargins(0, 3, 0, 0)
        self.setFixedHeight(30)

        # Création du layout horizontal pour le statut
        self.status_HLayout = QHBoxLayout(self)
        self.status_HLayout.setObjectName("status_HLayout")
        self.status_HLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.status_HLayout.setContentsMargins(0, 0, 0, 0)
        self.status_HLayout.setSpacing(12)

        # Création du label pour le statut
        self.status_label = QLabel(parent)
        self.status_label.setObjectName("status_label")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setLineWidth(0)

        # Ajout du label au layout horizontal
        self.status_HLayout.addWidget(self.status_label, 0, Qt.AlignmentFlag.AlignTop)

        # Création du label pour la LED
        self.status_led = QLabel(parent)
        self.status_led.setObjectName("status_led")
        self.status_led.setFixedSize(QSize(12, 15))
        self.status_led.setFont(QFont("Segoe UI", 10))
        self.status_led.setLineWidth(0)
        self.set_status_neutral()

        # Ajout du label LED au layout horizontal
        self.status_HLayout.addWidget(self.status_led, 0, Qt.AlignmentFlag.AlignTop)

    # STATUS FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def set_status_neutral(self) -> None:
        self.status_label.setText("En attente")
        self.setProperty("class", "none")
        self.refreshStyle()

    # ///////////////////////////////////////////////////////////////

    def set_status_online(self) -> None:
        self.status_label.setText("En ligne")
        self.setProperty("class", "ok")
        self.refreshStyle()

    # ///////////////////////////////////////////////////////////////

    def set_status_partial(self) -> None:
        self.status_label.setText("Services perturbés")
        self.setProperty("class", "partiel")
        self.refreshStyle()

    # ///////////////////////////////////////////////////////////////

    def set_status_offline(self) -> None:
        self.status_label.setText("Hors ligne")
        self.setProperty("class", "ko")
        self.refreshStyle()

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refreshStyle(self) -> None:
        self.style().unpolish(self)
        self.style().polish(self)
