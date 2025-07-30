# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORTS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import Signal, QTimer, Qt, QSize
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor
import re


# UTILITY FUNCTIONS
# ///////////////////////////////////////////////////////////////
def parse_css_color(color_str):
    """Parse CSS color strings (rgb, rgba, hex, named colors) to QColor."""
    if isinstance(color_str, QColor):
        return color_str

    color_str = str(color_str).strip()

    # Parse rgb(r, g, b)
    rgb_match = re.match(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", color_str)
    if rgb_match:
        r, g, b = map(int, rgb_match.groups())
        return QColor(r, g, b)

    # Parse rgba(r, g, b, a)
    rgba_match = re.match(r"rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)", color_str)
    if rgba_match:
        r, g, b, a = rgba_match.groups()
        r, g, b = map(int, [r, g, b])
        a = float(a) * 255  # Convert 0-1 to 0-255
        return QColor(r, g, b, int(a))

    # Fallback to QColor constructor (hex, named colors, etc.)
    return QColor(color_str)


# CLASS
# ///////////////////////////////////////////////////////////////


class CircularTimer(QWidget):
    """
    CircularTimer est un timer circulaire animé pour indiquer une progression ou un temps écoulé.

    Paramètres
    ----------
    duration : int
        Durée totale de l'animation en millisecondes (par défaut 5000).
    ring_color : QColor | str
        Couleur de l'arc de progression (par défaut #ff0000).
        Supporte: hex (#ff0000), rgb(255,0,0), rgba(255,0,0,0.5), noms (red).
    node_color : QColor | str
        Couleur du centre (par défaut #ffffff).
        Supporte: hex (#ffffff), rgb(255,255,255), rgba(255,255,255,0.8), noms (white).
    ring_width_mode : str, optionnel
        "small", "medium" (défaut), ou "large". Contrôle dynamiquement l'épaisseur de l'arc.
    pen_width : int | float, optionnel
        Épaisseur de l'arc (prioritaire sur ring_width_mode si défini).
    loop : bool, optionnel
        Si True, le timer boucle automatiquement à chaque cycle (par défaut False).
    parent : QWidget, optionnel
        Parent Qt.

    Signaux
    -------
    timerReset()
        Émis lorsque le timer est réinitialisé.
    clicked()
        Émis lors d'un clic sur le widget.
    cycleCompleted()
        Émis à chaque fin de cycle (même si loop=False).

    Propriétés
    ----------
    duration : int
        Durée totale de l'animation.
    elapsed : int
        Temps écoulé depuis le début de l'animation.
    running : bool
        Indique si le timer est en cours d'animation.
    ring_color : QColor
        Couleur de l'arc de progression.
    node_color : QColor
        Couleur du centre.
    ring_width_mode : str
        "small", "medium", "large". Contrôle dynamiquement l'épaisseur de l'arc.
    pen_width : float
        Épaisseur de l'arc (prioritaire sur ring_width_mode).
    loop : bool
        Si True, le timer boucle automatiquement à chaque cycle.
    """

    timerReset = Signal()
    clicked = Signal()
    cycleCompleted = Signal()

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        parent=None,
        duration=5000,
        ring_color="#0078d4",
        node_color="#2d2d2d",
        ring_width_mode="medium",
        pen_width=None,
        loop=False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)
        self.setProperty("type", "CircularTimer")

        # ////// INITIALIZE VARIABLES
        self._duration = duration
        self._elapsed = 0
        self._running = False
        self._ring_color = parse_css_color(ring_color)
        self._node_color = parse_css_color(node_color)
        self._ring_width_mode = ring_width_mode
        self._pen_width = pen_width
        self._loop = bool(loop)
        self._last_update = None
        self._interval = 16  # ~60 FPS

        # ////// SETUP TIMER
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer)

    # PROPERTY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):
        self._duration = int(value)
        self.update()

    @property
    def elapsed(self):
        return self._elapsed

    @elapsed.setter
    def elapsed(self, value):
        self._elapsed = int(value)
        self.update()

    @property
    def running(self):
        return self._running

    @property
    def ring_color(self):
        return self._ring_color

    @ring_color.setter
    def ring_color(self, value):
        self._ring_color = parse_css_color(value)
        self.update()

    @property
    def node_color(self):
        return self._node_color

    @node_color.setter
    def node_color(self, value):
        self._node_color = parse_css_color(value)
        self.update()

    @property
    def ring_width_mode(self):
        return self._ring_width_mode

    @ring_width_mode.setter
    def ring_width_mode(self, value):
        if value not in ("small", "medium", "large"):
            value = "medium"
        self._ring_width_mode = value
        self.update()

    @property
    def pen_width(self):
        return self._pen_width

    @pen_width.setter
    def pen_width(self, value):
        self._pen_width = float(value) if value is not None else None
        self.update()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value):
        self._loop = bool(value)

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def mousePressEvent(self, event) -> None:
        self.clicked.emit()

    # TIMER FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def startTimer(self) -> None:
        """Démarre le timer circulaire."""
        self.stopTimer()  # Toujours arrêter avant de démarrer
        self._running = True
        self._last_update = None
        self.timer.start(self._interval)

    def stopTimer(self) -> None:
        """Arrête le timer circulaire."""
        self.resetTimer()  # Toujours repartir de zéro
        self._running = False
        self.timer.stop()

    def resetTimer(self) -> None:
        """Réinitialise le timer circulaire."""
        self._elapsed = 0
        self._last_update = None
        self.timerReset.emit()
        self.update()

    def _on_timer(self):
        """Callback interne pour l'animation fluide."""
        import time

        now = time.monotonic() * 1000  # ms
        if self._last_update is None:
            self._last_update = now
            return
        delta = now - self._last_update
        self._last_update = now
        self._elapsed += delta
        if self._elapsed > self._duration:
            self.cycleCompleted.emit()
            if self._loop:
                self.resetTimer()
                self._running = True
                self._last_update = now
                # Le timer continue (pas d'arrêt)
            else:
                self.resetTimer()
                self.stopTimer()
        self.update()

    # PAINT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def minimumSizeHint(self):
        """Taille minimale recommandée pour le widget."""
        return QSize(24, 24)

    def paintEvent(self, event) -> None:
        """Dessine le timer circulaire animé."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        size = min(self.width(), self.height())

        # ////// PEN WIDTH (mode dynamique ou valeur fixe)
        if self._pen_width is not None:
            penWidth = self._pen_width
        else:
            if self._ring_width_mode == "small":
                penWidth = max(size * 0.12, 3)
            elif self._ring_width_mode == "large":
                penWidth = max(size * 0.28, 3)
            else:  # medium
                penWidth = max(size * 0.18, 3)

        # ////// NODE CIRCLE (centrage précis)
        center = size / 2
        node_radius = (size - 2 * penWidth) / 2 - penWidth / 2
        if node_radius > 0:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._node_color)
            painter.drawEllipse(
                center - node_radius,
                center - node_radius,
                2 * node_radius,
                2 * node_radius,
            )

        # ////// RING ARC (sens horaire, départ 12h)
        painter.setPen(QPen(self._ring_color, penWidth, Qt.SolidLine, Qt.RoundCap))
        angle = int((self._elapsed / self._duration) * 360 * 16)
        painter.drawArc(
            penWidth,
            penWidth,
            size - 2 * penWidth,
            size - 2 * penWidth,
            90 * 16,
            -angle,  # sens horaire
        )

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget's style (useful after dynamic stylesheet changes)."""
        # // REFRESH STYLE
        self.style().unpolish(self)
        self.style().polish(self)
        # //////
