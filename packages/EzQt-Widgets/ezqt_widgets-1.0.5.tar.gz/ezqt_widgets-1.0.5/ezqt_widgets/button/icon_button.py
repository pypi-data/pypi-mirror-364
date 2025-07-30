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
from PySide6.QtGui import (
    QIcon,
    QPixmap,
    QPainter,
    QColor,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QToolButton,
    QSizePolicy,
)

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////


# ///////////////////////////////////////////////////////////////
# FONCTIONS UTILITAIRES
# ///////////////////////////////////////////////////////////////


def colorize_pixmap(pixmap, color="#FFFFFF", opacity=0.5):
    """Recolore un QPixmap avec la couleur et l'opacité données."""
    result = QPixmap(pixmap.size())
    result.fill(Qt.transparent)
    painter = QPainter(result)
    painter.setOpacity(opacity)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(result.rect(), QColor(color))
    painter.end()
    return result


def load_icon_from_source(source) -> QIcon:
    """
    Load icon from various sources (QIcon, path, URL, etc.).

    Parameters
    ----------
    source : QIcon or str
        Icon source (QIcon, path, resource, URL, or SVG).

    Returns
    -------
    QIcon
        Loaded icon or None if failed.
    """
    # ////// HANDLE NONE
    if source is None:
        return None
    # ////// HANDLE QICON
    elif isinstance(source, QIcon):
        return source
    # ////// HANDLE STRING (PATH, URL, SVG)
    elif isinstance(source, str):

        # ////// HANDLE URL
        if source.startswith("http://") or source.startswith("https://"):
            print(f"Loading icon from URL: {source}")
            try:
                import requests

                response = requests.get(source, timeout=5)
                response.raise_for_status()
                if "image" not in response.headers.get("Content-Type", ""):
                    raise ValueError("URL does not point to an image file.")
                image_data = response.content

                # ////// HANDLE SVG FROM URL
                if source.lower().endswith(".svg"):
                    from PySide6.QtSvg import QSvgRenderer
                    from PySide6.QtCore import QByteArray

                    renderer = QSvgRenderer(QByteArray(image_data))
                    pixmap = QPixmap(QSize(16, 16))
                    pixmap.fill(Qt.transparent)
                    painter = QPainter(pixmap)
                    renderer.render(painter)
                    painter.end()
                    return QIcon(pixmap)

                # ////// HANDLE RASTER IMAGE FROM URL
                else:
                    pixmap = QPixmap()
                    if not pixmap.loadFromData(image_data):
                        raise ValueError("Failed to load image data from URL.")
                    pixmap = colorize_pixmap(pixmap, "#FFFFFF", 0.5)
                    return QIcon(pixmap)
            except Exception as e:
                print(f"Failed to load icon from URL: {e}")
                return None

        # ////// HANDLE LOCAL SVG
        elif source.lower().endswith(".svg"):
            try:
                from PySide6.QtSvg import QSvgRenderer
                from PySide6.QtCore import QFile

                file = QFile(source)
                if not file.open(QFile.ReadOnly):
                    raise ValueError(f"Cannot open SVG file: {source}")
                svg_data = file.readAll()
                file.close()
                renderer = QSvgRenderer(svg_data)
                pixmap = QPixmap(QSize(16, 16))
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                return QIcon(pixmap)
            except Exception as e:
                print(f"Failed to load SVG icon: {e}")
                return None

        # ////// HANDLE LOCAL/RESOURCE RASTER IMAGE
        else:
            icon = QIcon(source)
            if icon.isNull():
                print(f"Invalid icon path: {source}")
                return None
            return icon

    # ////// HANDLE INVALID TYPE
    else:
        print(f"Invalid icon source type: {type(source)}")
        return None


# ///////////////////////////////////////////////////////////////
# CLASSES PRINCIPALES
# ///////////////////////////////////////////////////////////////


class IconButton(QToolButton):
    """
    Enhanced button widget with icon and optional text support.

    Features:
        - Icon support from various sources (QIcon, path, URL, SVG)
        - Optional text display with configurable visibility
        - Customizable icon size and spacing
        - Property-based access to icon and text
        - Signals for icon and text changes
        - Hover and click effects

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget (default: None).
    icon : QIcon or str, optional
        The icon to display (QIcon, path, resource, URL, or SVG).
    text : str, optional
        The button text (default: "").
    icon_size : QSize or tuple, optional
        Size of the icon (default: QSize(20, 20)).
    text_visible : bool, optional
        Whether the text is initially visible (default: True).
    spacing : int, optional
        Spacing between icon and text in pixels (default: 10).
    min_width : int, optional
        Minimum width of the button (default: None, auto-calculated).
    min_height : int, optional
        Minimum height of the button (default: None, auto-calculated).
    *args, **kwargs :
        Additional arguments passed to QToolButton.

    Properties
    ----------
    icon : QIcon
        Get or set the button icon.
    text : str
        Get or set the button text.
    icon_size : QSize
        Get or set the icon size.
    text_visible : bool
        Get or set text visibility.
    spacing : int
        Get or set spacing between icon and text.
    min_width : int
        Get or set the minimum width of the button.
    min_height : int
        Get or set the minimum height of the button.

    Signals
    -------
    iconChanged(QIcon)
        Emitted when the icon changes.
    textChanged(str)
        Emitted when the text changes.
    """

    iconChanged = Signal(QIcon)
    textChanged = Signal(str)

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        parent=None,
        icon=None,
        text="",
        icon_size=QSize(20, 20),
        text_visible=True,
        spacing=10,
        min_width=None,
        min_height=None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)
        self.setProperty("type", "IconButton")

        # ////// INITIALIZE VARIABLES
        self._icon_size = (
            QSize(*icon_size)
            if isinstance(icon_size, (tuple, list))
            else QSize(icon_size)
        )
        self._text_visible = text_visible
        self._spacing = spacing
        self._current_icon = None
        self._min_width = min_width
        self._min_height = min_height

        # ////// SETUP UI COMPONENTS
        self.icon_label = QLabel()
        self.text_label = QLabel()

        # ////// CONFIGURE TEXT LABEL
        self.text_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("background-color: transparent;")

        # ////// SETUP LAYOUT
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(spacing)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)

        # ////// CONFIGURE SIZE POLICY
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # ////// SET INITIAL VALUES
        if icon:
            self.icon = icon
        if text:
            self.text = text
        self.text_visible = text_visible

    # PROPERTY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    @property
    def icon(self):
        """Get or set the button icon."""
        return self._current_icon

    @icon.setter
    def icon(self, value):
        """Set the button icon from various sources."""
        icon = load_icon_from_source(value)
        if icon:
            self._current_icon = icon
            self.icon_label.setPixmap(icon.pixmap(self._icon_size))
            self.icon_label.setFixedSize(self._icon_size)
            self.icon_label.setStyleSheet("background-color: transparent;")
            self.iconChanged.emit(icon)

    @property
    def text(self):
        """Get or set the button text."""
        return self.text_label.text()

    @text.setter
    def text(self, value):
        """Set the button text."""
        if value != self.text_label.text():
            self.text_label.setText(str(value))
            self.textChanged.emit(str(value))

    @property
    def icon_size(self):
        """Get or set the icon size."""
        return self._icon_size

    @icon_size.setter
    def icon_size(self, value):
        """Set the icon size."""
        self._icon_size = (
            QSize(*value) if isinstance(value, (tuple, list)) else QSize(value)
        )
        if self._current_icon:
            self.icon_label.setPixmap(self._current_icon.pixmap(self._icon_size))
            self.icon_label.setFixedSize(self._icon_size)

    @property
    def text_visible(self):
        """Get or set text visibility."""
        return self._text_visible

    @text_visible.setter
    def text_visible(self, value):
        """Set text visibility."""
        self._text_visible = bool(value)
        if self._text_visible:
            self.text_label.show()
        else:
            self.text_label.hide()

    @property
    def spacing(self):
        """Get or set spacing between icon and text."""
        return self._spacing

    @spacing.setter
    def spacing(self, value):
        """Set spacing between icon and text."""
        self._spacing = int(value)
        layout = self.layout()
        if layout:
            layout.setSpacing(self._spacing)

    @property
    def min_width(self):
        """Get or set the minimum width of the button."""
        return self._min_width

    @min_width.setter
    def min_width(self, value):
        """Set the minimum width of the button."""
        self._min_width = value
        self.updateGeometry()

    @property
    def min_height(self):
        """Get or set the minimum height of the button."""
        return self._min_height

    @min_height.setter
    def min_height(self, value):
        """Set the minimum height of the button."""
        self._min_height = value
        self.updateGeometry()

    # UTILITY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def clear_icon(self):
        """Remove the current icon."""
        self._current_icon = None
        self.icon_label.clear()
        self.iconChanged.emit(QIcon())

    def clear_text(self):
        """Clear the button text."""
        self.text = ""

    def toggle_text_visibility(self):
        """Toggle text visibility."""
        self.text_visible = not self.text_visible

    def set_icon_color(self, color="#FFFFFF", opacity=0.5):
        """Apply color and opacity to the current icon."""
        if self._current_icon:
            pixmap = self._current_icon.pixmap(self._icon_size)
            colored_pixmap = colorize_pixmap(pixmap, color, opacity)
            self.icon_label.setPixmap(colored_pixmap)

    # OVERRIDE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def sizeHint(self) -> QSize:
        """Get the recommended size for the button."""
        return QSize(100, 40)

    def minimumSizeHint(self) -> QSize:
        """Get the minimum size hint for the button."""
        # ////// CALCULATE BASE SIZE
        base_size = super().minimumSizeHint()

        # ////// CALCULATE ICON SPACE
        icon_width = self._icon_size.width() if self._current_icon else 0

        # ////// CALCULATE TEXT SPACE
        text_width = 0
        if self._text_visible and self.text:
            text_width = self.text_label.fontMetrics().horizontalAdvance(self.text)

        # ////// CALCULATE TOTAL WIDTH
        total_width = (
            icon_width
            + text_width
            + self._spacing
            + 20  # margins (10px left + 10px right)
        )

        # ////// APPLY MINIMUM CONSTRAINTS
        min_width = self._min_width if self._min_width is not None else total_width
        min_height = (
            self._min_height
            if self._min_height is not None
            else max(base_size.height(), self._icon_size.height() + 8)
        )

        return QSize(max(min_width, total_width), min_height)

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget's style (useful after dynamic stylesheet changes)."""
        # // REFRESH STYLE
        self.style().unpolish(self)
        self.style().polish(self)
        # //////
