# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QFrame, QLabel
from PySide6.QtGui import QFont, QMouseEvent

# ///////////////////////////////////////////////////////////////
# CLASSES PRINCIPALES
# ///////////////////////////////////////////////////////////////


class ClickableTagLabel(QFrame):
    """
    Tag-like clickable label with toggleable state.

    Features:
        - Clickable tag with enabled/disabled state
        - Emits signals on click and state change
        - Customizable text, font, min width/height
        - Customizable status color (traditional name or hex)
        - QSS-friendly (type/class/status properties)
        - Automatic minimum size calculation
        - Keyboard focus and accessibility

    Parameters
    ----------
    name : str, optional
        Text to display in the tag (default: "").
    enabled : bool, optional
        Initial state (default: False).
    status_color : str, optional
        Color when selected (default: "#0078d4").
    min_width : int, optional
        Minimum width (default: None, auto-calculated).
    min_height : int, optional
        Minimum height (default: None, auto-calculated).
    parent : QWidget, optional
        Parent widget (default: None).
    *args, **kwargs :
        Additional arguments passed to QFrame.

    Properties
    ----------
    name : str
        Get or set the tag text.
    enabled : bool
        Get or set the enabled state.
    status_color : str
        Get or set the status color.
    min_width : int
        Get or set the minimum width.
    min_height : int
        Get or set the minimum height.

    Signals
    -------
    clicked()
        Emitted when the tag is clicked.
    toggle_keyword(str)
        Emitted with the tag name when toggled.
    stateChanged(bool)
        Emitted when the enabled state changes.
    """

    clicked = Signal()
    toggle_keyword = Signal(str)
    stateChanged = Signal(bool)

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        name: str = "",
        enabled: bool = False,
        status_color: str = "#0078d4",
        min_width=None,
        min_height=None,
        parent=None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)
        self.setProperty("type", "ClickableTagLabel")

        # ////// SETUP FRAME
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)
        self.setContentsMargins(4, 0, 4, 0)
        self.setFixedHeight(20)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # ////// INITIALIZE VARIABLES
        self._name = name
        self._enabled = enabled
        self._status_color = status_color
        self._min_width = min_width
        self._min_height = min_height

        # ////// SETUP LAYOUT
        self.status_HLayout = QHBoxLayout(self)
        self.status_HLayout.setObjectName("status_HLayout")
        self.status_HLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.status_HLayout.setContentsMargins(0, 0, 0, 0)
        self.status_HLayout.setSpacing(12)

        # ////// SETUP LABEL
        self.status_label = QLabel(self)
        self.status_label.setObjectName("tag")
        self.status_label.setFont(QFont("Segoe UI", 8))
        self.status_label.setLineWidth(0)
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.status_label.setStyleSheet("color: rgb(86, 86, 86);")
        self.status_HLayout.addWidget(self.status_label, 0, Qt.AlignmentFlag.AlignTop)

        # ////// INITIAL VALUES
        self.name = name
        
        # Appliquer l'état initial avec les propriétés QSS
        if enabled:
            self.setProperty("class", "enabled")
            self.setProperty("status", "selected")
            self.status_label.setStyleSheet(f"color: {self._status_color};")
        else:
            self.setProperty("class", "disabled")
            self.setProperty("status", "unselected")
            self.status_label.setStyleSheet("color: rgb(86, 86, 86);")
        
        self._enabled = enabled
        self.refresh_style()

    # PROPERTY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    @property
    def name(self) -> str:
        """Get or set the tag text."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
        self.status_label.setText(value)
        self.setObjectName(value)
        self.updateGeometry()

    @property
    def enabled(self) -> bool:
        """Get or set the enabled state."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        if self._enabled != value:
            self._enabled = value
            if value:
                self.setProperty("class", "enabled")
                self.setProperty("status", "selected")
                self.status_label.setStyleSheet(f"color: {self._status_color};")
            else:
                self.setProperty("class", "disabled")
                self.setProperty("status", "unselected")
                self.status_label.setStyleSheet("color: rgb(86, 86, 86);")
            self.refresh_style()
            self.adjustSize()
            self.stateChanged.emit(value)

    @property
    def status_color(self) -> str:
        """Get or set the status color."""
        return self._status_color

    @status_color.setter
    def status_color(self, value: str) -> None:
        """Set the status color (traditional name or hex)."""
        self._status_color = value
        if self._enabled:
            self.status_label.setStyleSheet(f"color: {value};")
            self.refresh_style()

    @property
    def min_width(self):
        """Get or set the minimum width."""
        return self._min_width

    @min_width.setter
    def min_width(self, value):
        self._min_width = value
        self.updateGeometry()

    @property
    def min_height(self):
        """Get or set the minimum height."""
        return self._min_height

    @min_height.setter
    def min_height(self, value):
        self._min_height = value
        self.updateGeometry()

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.enabled = not self.enabled
            self.toggle_keyword.emit(self.name)
            self.clicked.emit()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.enabled = not self.enabled
            self.toggle_keyword.emit(self.name)
            self.clicked.emit()
        else:
            super().keyPressEvent(event)

    # SIZE HINTS
    # ///////////////////////////////////////////////////////////////

    def sizeHint(self) -> QSize:
        return QSize(80, 24)

    def minimumSizeHint(self) -> QSize:
        font_metrics = self.status_label.fontMetrics()
        text_width = font_metrics.horizontalAdvance(self.name)
        min_width = self._min_width if self._min_width is not None else text_width + 16
        min_height = (
            self._min_height
            if self._min_height is not None
            else max(font_metrics.height() + 8, 20)
        )
        return QSize(min_width, min_height)

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        self.style().unpolish(self)
        self.style().polish(self)
