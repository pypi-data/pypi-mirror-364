# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import (
    Qt,
    QSize,
    Signal,
)
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
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


class FramedLabel(QFrame):
    """
    FramedLabel is a flexible label widget based on QFrame, designed for advanced styling and layout in Qt applications.

    This widget encapsulates a QLabel inside a QFrame, allowing you to benefit from QFrame's styling and layout capabilities
    while providing a simple interface for text display, alignment, and dynamic style updates.

    Features:
        - Property-based access to the label text (text) and alignment (alignment)
        - Emits a textChanged(str) signal when the text changes
        - Allows custom stylesheet injection for advanced appearance
        - Suitable for use as a header, section label, or any context where a styled label is needed

    Parameters
    ----------
    text : str, optional
        The initial text to display in the label (default: "").
    parent : QWidget, optional
        The parent widget (default: None).
    alignment : Qt.AlignmentFlag, optional
        The alignment of the label text (default: Qt.AlignmentFlag.AlignCenter).
    style_sheet : str, optional
        Custom stylesheet to apply to the QFrame (default: None, uses transparent background).
    min_width : int, optional
        Minimum width constraint for the widget (default: None).
    min_height : int, optional
        Minimum height constraint for the widget (default: None).
    *args, **kwargs :
        Additional arguments passed to QFrame.

    Properties
    ----------
    text : str
        Get or set the label text.
    alignment : Qt.AlignmentFlag
        Get or set the label alignment.
    min_width : int
        Get or set the minimum width constraint.
    min_height : int
        Get or set the minimum height constraint.

    Signals
    -------
    textChanged(str)
        Emitted when the label text changes.
    """

    textChanged = Signal(str)

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        text="",
        parent=None,
        alignment=Qt.AlignmentFlag.AlignCenter,
        style_sheet=None,
        min_width=None,
        min_height=None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)
        self.setProperty("type", "FramedLabel")

        # ////// INITIALIZE MINIMUM SIZE PROPERTIES
        self._min_width = min_width
        self._min_height = min_height

        # // STYLE SHEET
        self.setStyleSheet(style_sheet or "background-color: transparent;")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # //////

        # // LAYOUT SETUP
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(alignment)
        # //////

        # // LABEL SETUP
        self.label = QLabel(text, self)
        self._alignment = alignment
        self.label.setAlignment(alignment)
        layout.addWidget(self.label)
        # //////

    # PROPERTY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    @property
    def text(self) -> str:
        """Get or set the label text."""
        # // GET TEXT
        return self.label.text()
        # //////

    @text.setter
    def text(self, value: str) -> None:
        """Set the label text."""
        # // SET TEXT
        if not isinstance(value, str):
            value = str(value)
        if value != self.label.text():
            self.label.setText(value)
            self.textChanged.emit(value)
        # //////

    @property
    def alignment(self) -> Qt.AlignmentFlag:
        """Get or set the alignment of the label."""
        # // GET ALIGNMENT
        return self._alignment
        # //////

    @alignment.setter
    def alignment(self, value: Qt.AlignmentFlag) -> None:
        """Set the alignment of the label."""
        # // SET ALIGNMENT
        self._alignment = value
        self.label.setAlignment(value)
        # Optionally update layout alignment as well
        if self.layout():
            self.layout().setAlignment(value)
        # //////

    @property
    def min_width(self):
        """Get or set the minimum width."""
        return self._min_width

    @min_width.setter
    def min_width(self, value):
        """Set the minimum width."""
        self._min_width = value
        self.updateGeometry()

    @property
    def min_height(self):
        """Get or set the minimum height."""
        return self._min_height

    @min_height.setter
    def min_height(self, value):
        """Set the minimum height."""
        self._min_height = value
        self.updateGeometry()

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def minimumSizeHint(self) -> QSize:
        """Get the minimum size hint for the widget."""
        # ////// CALCULATE BASE SIZE
        base_size = super().minimumSizeHint()

        # ////// CALCULATE TEXT SIZE
        font_metrics = self.fontMetrics()
        text_width = font_metrics.horizontalAdvance(self.text)
        text_height = font_metrics.height()

        # ////// ADD PADDING AND MARGINS
        content_width = text_width + 16  # 8px padding on each side
        content_height = text_height + 8  # 4px padding top/bottom

        # ////// APPLY MINIMUM CONSTRAINTS
        min_width = self._min_width if self._min_width is not None else content_width
        min_height = (
            self._min_height if self._min_height is not None else content_height
        )

        return QSize(max(min_width, content_width), max(min_height, content_height))

    def refresh_style(self) -> None:
        """Refresh the widget's style (useful after dynamic stylesheet changes)."""
        # // REFRESH STYLE
        self.style().unpolish(self)
        self.style().polish(self)
        # //////
