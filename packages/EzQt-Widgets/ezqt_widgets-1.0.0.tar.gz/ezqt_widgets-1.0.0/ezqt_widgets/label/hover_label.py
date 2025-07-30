# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import (
    Signal,
    Qt,
    QSize,
    QRect,
)
from PySide6.QtWidgets import (
    QLabel,
)
from PySide6.QtGui import (
    QPainter,
    QIcon,
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


class HoverLabel(QLabel):
    hoverIconClicked = Signal()  # Signal personnalisé

    def __init__(self, parent=None, icon=None, text="", *args, **kwargs) -> None:
        super().__init__(
            text or "", parent, *args, **kwargs
        )  # Passer le texte en premier, suivi du parent
        self.setProperty("type", "HoverLabel")
        self.hover_icon = QIcon(icon) if icon else None
        self.show_hover_icon = False
        self.opacity = 0.5  # Opacité de l'icône
        self.setMouseTracking(True)  # Activer le suivi de la souris

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def mouseMoveEvent(self, event) -> None:
        vertical_offset = 5
        if self.show_hover_icon and QRect(
            self.width() - 20, (self.height() - 16) // 2 + vertical_offset, 16, 16
        ).contains(event.pos()):
            self.setCursor(
                Qt.CursorShape.PointingHandCursor
            )  # Changer le curseur en main lors du survol de l'icône
        else:
            self.setCursor(
                Qt.CursorShape.ArrowCursor
            )  # Réinitialiser le curseur si ce n'est pas sur l'icône
        super().mouseMoveEvent(event)

    # ///////////////////////////////////////////////////////////////

    def mousePressEvent(self, event) -> None:
        vertical_offset = 5
        if self.show_hover_icon and QRect(
            self.width() - 20, (self.height() - 16) // 2 + vertical_offset, 16, 16
        ).contains(event.pos()):
            self.hoverIconClicked.emit()  # Émission du signal
        super().mousePressEvent(event)

    # ///////////////////////////////////////////////////////////////

    def enterEvent(self, event) -> None:
        self.show_hover_icon = True
        self.update()  # Demande de redessiner le widget

    # ///////////////////////////////////////////////////////////////

    def leaveEvent(self, event) -> None:
        self.show_hover_icon = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

    # UI FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if self.show_hover_icon:
            painter = QPainter(self)
            painter.setOpacity(self.opacity)  # Appliquer l'opacité
            vertical_offset = 5
            icon_size = QSize(16, 16)  # Taille souhaitée de l'icône
            icon_pixmap = self.hover_icon.pixmap(
                icon_size
            )  # Obtenir le QPixmap redimensionné
            icon_rect = QRect(
                self.width() - 20,
                (self.height() - icon_size.height()) // 2 + vertical_offset,
                icon_size.width(),
                icon_size.height(),
            )
            painter.drawPixmap(
                icon_rect, icon_pixmap
            )  # Dessiner le QPixmap redimensionné
