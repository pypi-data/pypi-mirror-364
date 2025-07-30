# -*- coding: utf-8 -*-
"""
ToggleIcon - Widget de label avec icônes toggleables.

Ce module fournit un widget ToggleIcon qui affiche une icône qui change
selon l'état (ouvert/fermé) et émet un signal lors du clic.
"""

# IMPORT BASE
# ///////////////////////////////////////////////////////////////
import re
from typing import Union, Optional

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import (
    Signal,
    QSize,
    Qt,
    QPointF,
    QRectF,
)
from PySide6.QtGui import (
    QIcon,
    QPixmap,
    QPainter,
    QColor,
)
from PySide6.QtWidgets import (
    QLabel,
)
from PySide6.QtSvg import QSvgRenderer

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

## ==> GLOBALS
# ///////////////////////////////////////////////////////////////

## ==> FUNCTIONS
# ///////////////////////////////////////////////////////////////


def colorize_pixmap(pixmap: QPixmap, color: QColor) -> QPixmap:
    """
    Applique une couleur à un QPixmap avec opacité.

    Paramètres
    ----------
    pixmap : QPixmap
        Le pixmap à colorer.
    color : QColor
        La couleur à appliquer.

    Retourne
    --------
    QPixmap
        Le pixmap coloré.
    """
    if pixmap.isNull():
        return pixmap

    colored_pixmap = QPixmap(pixmap.size())
    colored_pixmap.fill(Qt.transparent)

    painter = QPainter(colored_pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
    painter.setOpacity(color.alphaF())
    painter.fillRect(colored_pixmap.rect(), color)
    painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()

    return colored_pixmap


def load_icon_from_source(
    source: Union[str, QIcon, QPixmap], size: QSize = None
) -> QPixmap:
    """
    Charge une icône depuis différentes sources (chemin, URL, QIcon, QPixmap).

    Paramètres
    ----------
    source : str | QIcon | QPixmap
        Source de l'icône (chemin de fichier, URL, QIcon, ou QPixmap).
    size : QSize, optionnel
        Taille souhaitée pour l'icône.

    Retourne
    --------
    QPixmap
        Le pixmap de l'icône chargée.
    """
    if isinstance(source, QPixmap):
        pixmap = source
    elif isinstance(source, QIcon):
        pixmap = source.pixmap(size or QSize(16, 16))
    elif isinstance(source, str):
        if source.startswith(("http://", "https://")):
            # Chargement depuis URL
            try:
                import requests

                response = requests.get(source, timeout=5)
                response.raise_for_status()
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
            except Exception:
                # Fallback vers icône par défaut
                pixmap = QPixmap(16, 16)
                pixmap.fill(Qt.transparent)
        elif source.lower().endswith(".svg"):
            # Chargement SVG
            renderer = QSvgRenderer(source)
            if renderer.isValid():
                pixmap = QPixmap(size or QSize(16, 16))
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
            else:
                pixmap = QPixmap(16, 16)
                pixmap.fill(Qt.transparent)
        else:
            # Chargement depuis fichier
            pixmap = QPixmap(source)
    else:
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)

    if not pixmap.isNull() and size:
        pixmap = pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    return pixmap


## ==> VARIABLES
# ///////////////////////////////////////////////////////////////

# CLASS
# ///////////////////////////////////////////////////////////////


class ToggleIcon(QLabel):
    """
    ToggleIcon est un label avec icônes toggleables pour indiquer un état ouvert/fermé.

    Paramètres
    ----------
    opened_icon : str | QIcon | QPixmap, optionnel
        Icône à afficher quand l'état est "opened". Si None, utilise paintEvent.
    closed_icon : str | QIcon | QPixmap, optionnel
        Icône à afficher quand l'état est "closed". Si None, utilise paintEvent.
    icon_size : int, optionnel
        Taille des icônes en pixels (par défaut 16).
    icon_color : QColor | str, optionnel
        Couleur à appliquer aux icônes (par défaut blanc avec 0.5 opacité).
    initial_state : str, optionnel
        État initial ("opened" ou "closed", par défaut "closed").
    min_width : int, optionnel
        Largeur minimale du widget.
    min_height : int, optionnel
        Hauteur minimale du widget.
    parent : QWidget, optionnel
        Parent Qt.

    Signaux
    -------
    stateChanged(str)
        Émis quand l'état change ("opened" ou "closed").
    clicked()
        Émis lors d'un clic sur le widget.

    Propriétés
    ----------
    state : str
        État actuel ("opened" ou "closed").
    opened_icon : QPixmap
        Icône de l'état ouvert.
    closed_icon : QPixmap
        Icône de l'état fermé.
    icon_size : int
        Taille des icônes.
    icon_color : QColor
        Couleur des icônes.
    min_width : int
        Largeur minimale.
    min_height : int
        Hauteur minimale.
    """

    stateChanged = Signal(str)  # "opened" ou "closed"
    clicked = Signal()

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        parent=None,
        opened_icon=None,
        closed_icon=None,
        icon_size=16,
        icon_color=None,
        initial_state="closed",
        min_width=None,
        min_height=None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)
        self.setProperty("type", "ToggleIcon")

        # ////// INITIALIZE VARIABLES
        self._icon_size = icon_size
        self._icon_color = (
            QColor(255, 255, 255, 128) if icon_color is None else QColor(icon_color)
        )
        self._min_width = min_width
        self._min_height = min_height
        self._state = initial_state

        # ////// SETUP ICONS
        self._use_custom_icons = opened_icon is not None or closed_icon is not None

        if self._use_custom_icons:
            # Utiliser les icônes fournies en argument
            self._opened_icon = (
                load_icon_from_source(
                    opened_icon, QSize(self._icon_size, self._icon_size)
                )
                if opened_icon is not None
                else None
            )
            self._closed_icon = (
                load_icon_from_source(
                    closed_icon, QSize(self._icon_size, self._icon_size)
                )
                if closed_icon is not None
                else None
            )
        else:
            # Utiliser le paintEvent pour dessiner les icônes
            self._opened_icon = None
            self._closed_icon = None

        # ////// SETUP WIDGET
        self.setFocusPolicy(Qt.StrongFocus)
        self._update_icon()
        self._apply_initial_state()

    # PROPERTY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value not in ("opened", "closed"):
            value = "closed"
        if self._state != value:
            self._state = value
            self._update_icon()
            self.stateChanged.emit(self._state)

    @property
    def opened_icon(self):
        return self._opened_icon

    @opened_icon.setter
    def opened_icon(self, value):
        self._opened_icon = load_icon_from_source(
            value, QSize(self._icon_size, self._icon_size)
        )
        if self._state == "opened":
            self._update_icon()

    @property
    def closed_icon(self):
        return self._closed_icon

    @closed_icon.setter
    def closed_icon(self, value):
        self._closed_icon = load_icon_from_source(
            value, QSize(self._icon_size, self._icon_size)
        )
        if self._state == "closed":
            self._update_icon()

    @property
    def icon_size(self):
        return self._icon_size

    @icon_size.setter
    def icon_size(self, value):
        self._icon_size = int(value)
        # Recharger les icônes avec la nouvelle taille
        if hasattr(self, "_opened_icon"):
            self._opened_icon = load_icon_from_source(
                self._opened_icon, QSize(self._icon_size, self._icon_size)
            )
        if hasattr(self, "_closed_icon"):
            self._closed_icon = load_icon_from_source(
                self._closed_icon, QSize(self._icon_size, self._icon_size)
            )
        self._update_icon()

    @property
    def icon_color(self):
        return self._icon_color

    @icon_color.setter
    def icon_color(self, value):
        self._icon_color = QColor(value)
        self._update_icon()

    @property
    def min_width(self):
        return self._min_width

    @min_width.setter
    def min_width(self, value):
        self._min_width = int(value) if value is not None else None
        self.updateGeometry()

    @property
    def min_height(self):
        return self._min_height

    @min_height.setter
    def min_height(self, value):
        self._min_height = int(value) if value is not None else None
        self.updateGeometry()

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def mousePressEvent(self, event) -> None:
        """Gère les événements de clic."""
        self.toggle_state()
        self.clicked.emit()
        super().mousePressEvent(event)

    def keyPressEvent(self, event) -> None:
        """Gère les événements clavier."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.toggle_state()
            self.clicked.emit()
        super().keyPressEvent(event)

    def paintEvent(self, event) -> None:
        """Dessine l'icône si aucune icône personnalisée n'est fournie, centrée dans un carré."""
        if not self._use_custom_icons:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            try:
                rect = self.rect()
                # Calculer le carré centré
                side = min(rect.width(), rect.height())
                x0 = rect.center().x() - side // 2
                y0 = rect.center().y() - side // 2
                square = QRectF(x0, y0, side, side)
                center_x = square.center().x()
                center_y = square.center().y()
                arrow_size = max(2, self._icon_size // 4)
                painter.setPen(Qt.NoPen)
                painter.setBrush(self._icon_color)
                if self._state == "opened":
                    points = [
                        QPointF(center_x - arrow_size, center_y - arrow_size // 2),
                        QPointF(center_x + arrow_size, center_y - arrow_size // 2),
                        QPointF(center_x, center_y + arrow_size // 2),
                    ]
                else:
                    points = [
                        QPointF(center_x - arrow_size, center_y + arrow_size // 2),
                        QPointF(center_x + arrow_size, center_y + arrow_size // 2),
                        QPointF(center_x, center_y - arrow_size // 2),
                    ]
                painter.drawPolygon(points)
            finally:
                painter.end()
        else:
            super().paintEvent(event)

    def minimumSizeHint(self) -> QSize:
        """Calcule une taille carrée minimale basée sur l'icône et les marges."""
        icon_size = self._icon_size
        margins = self.contentsMargins()
        base = icon_size + max(
            margins.left() + margins.right(), margins.top() + margins.bottom()
        )
        min_side = base
        if self._min_width is not None:
            min_side = max(min_side, self._min_width)
        if self._min_height is not None:
            min_side = max(min_side, self._min_height)
        return QSize(min_side, min_side)

    # STATE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def toggle_state(self) -> None:
        """Bascule entre les états ouvert et fermé."""
        self.state = "opened" if self._state == "closed" else "closed"

    def set_state_opened(self) -> None:
        """Force l'état à ouvert."""
        self.state = "opened"

    def set_state_closed(self) -> None:
        """Force l'état à fermé."""
        self.state = "closed"

    def is_opened(self) -> bool:
        """Retourne True si l'état est ouvert."""
        return self._state == "opened"

    def is_closed(self) -> bool:
        """Retourne True si l'état est fermé."""
        return self._state == "closed"

    # UTILITY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def _update_icon(self) -> None:
        """Met à jour l'icône affichée selon l'état actuel et centre le QPixmap."""
        if self._state == "opened":
            self.setProperty("class", "drop_down")
        else:
            self.setProperty("class", "drop_up")
        if self._use_custom_icons:
            icon = self._opened_icon if self._state == "opened" else self._closed_icon
            if not self._icon_color.isValid() or self._icon_color == QColor(
                255, 255, 255, 128
            ):
                colored_icon = colorize_pixmap(icon, self._icon_color)
            else:
                colored_icon = colorize_pixmap(icon, self._icon_color)
            self.setPixmap(colored_icon)
            self.setAlignment(Qt.AlignCenter)
        else:
            self.setPixmap(QPixmap())
            self.update()
        self.refresh_style()

    def _apply_initial_state(self) -> None:
        """Applique l'état initial et met à jour les propriétés QSS."""
        if self._state == "opened":
            self.setProperty("class", "drop_down")
        else:
            self.setProperty("class", "drop_up")
        self.refresh_style()

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Rafraîchit le style du widget."""
        self.style().unpolish(self)
        self.style().polish(self)
