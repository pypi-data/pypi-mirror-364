# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import (
    Signal,
    QTimer,
)
from PySide6.QtWidgets import (
    QWidget,
)
from PySide6.QtGui import (
    QPainter,
    QPen,
    QColor,
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


class CircularLoader(QWidget):
    timerReset = Signal()
    clicked = Signal()

    # ///////////////////////////////////////////////////////////////

    def __init__(self, parent=None, duration=5000, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.setProperty("type", "CircularLoader")
        self.duration = duration
        self.elapsed = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgress)

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def mousePressEvent(self, event) -> None:
        self.clicked.emit()

    # ///////////////////////////////////////////////////////////////

    def startTimer(self) -> None:
        self.timer.start(1000)

    # ///////////////////////////////////////////////////////////////

    def stopTimer(self) -> None:
        self.timer.stop()

    # ///////////////////////////////////////////////////////////////

    def updateProgress(self) -> None:
        self.elapsed += 1000
        if self.elapsed > self.duration:
            self.resetTimer()
        self.update()  # Mettre à jour le dessin

    # ///////////////////////////////////////////////////////////////

    def resetTimer(self) -> None:
        self.elapsed = 0  # Réinitialise le timer
        self.timerReset.emit()
        self.update()

    # UI FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Taille du widget
        size = min(self.width(), self.height())

        # Épaisseur du trait adaptée à la taille
        penWidth = size * 0.1  # 10% de la taille du widget
        if penWidth < 1:
            penWidth = 1  # Minimum d'un pixel

        # Arc gris (fond)
        painter.setPen(QPen(QColor(86, 86, 86), penWidth))
        painter.drawEllipse(
            penWidth, penWidth, size - 2 * penWidth, size - 2 * penWidth
        )

        # Arc coloré
        painter.setPen(QPen(QColor(150, 205, 50), penWidth))
        angle = int((self.elapsed / self.duration) * 360 * 16)
        painter.drawArc(
            penWidth, penWidth, size - 2 * penWidth, size - 2 * penWidth, 0, angle
        )
