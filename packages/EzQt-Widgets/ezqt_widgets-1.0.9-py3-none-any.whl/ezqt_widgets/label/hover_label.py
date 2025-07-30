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
from PySide6.QtGui import QPixmap, QIcon

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
    """
    HoverLabel is an interactive QLabel that displays a floating icon when hovered, and emits a signal when the icon is clicked.

    This widget is useful for adding contextual actions or visual cues to labels in a Qt interface.

    Features:
        - Displays a custom icon on hover, with configurable opacity, size, color overlay, and padding
        - Emits a hoverIconClicked signal when the icon is clicked
        - Handles mouse events and cursor changes for better UX
        - Text and icon can be set at construction or via properties
        - Icon can be enabled/disabled dynamically
        - Supports PNG/JPG and SVG icons (local, resource, URL)
        - Robust error handling for icon loading

    Example
    -------
    >>> label = HoverLabel(text="Survolez-moi !", icon="/path/to/icon.png", icon_color="#00BFFF")
    >>> label.icon_enabled = True
    >>> label.icon_padding = 12
    >>> label.clear_icon()

    Use cases
    ---------
    - Contextual action button in a label
    - Info or help icon on hover
    - Visual feedback for interactive labels

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget (default: None).
    icon : QIcon or str, optional
        The icon to display on hover (QIcon, path, resource, URL, or SVG).
    text : str, optional
        The label text (default: "").
    opacity : float, optional
        The opacity of the hover icon (default: 0.5).
    icon_size : QSize or tuple, optional
        The size of the hover icon (default: QSize(16, 16)).
    icon_color : QColor or str, optional
        Optional color overlay to apply to the icon (default: None).
    icon_padding : int, optional
        Padding (in px) to the right of the text for the icon (default: 8).
    icon_enabled : bool, optional
        Whether the icon is shown on hover (default: True).
    min_width : int, optional
        Minimum width of the widget (default: None).
    *args, **kwargs :
        Additional arguments passed to QLabel.

    Properties
    ----------
    opacity : float
        Get or set the opacity of the hover icon.
    hover_icon : QIcon
        Get or set the icon displayed on hover.
    icon_size : QSize
        Get or set the size of the hover icon.
    icon_color : QColor or str or None
        Get or set the color overlay of the hover icon.
    icon_padding : int
        Get or set the right padding for the icon.
    icon_enabled : bool
        Enable or disable the hover icon.

    Signals
    -------
    hoverIconClicked()
        Emitted when the hover icon is clicked.
    """
    hoverIconClicked = Signal()  # Signal personnalisé

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        parent=None,
        icon=None,
        text="",
        opacity=0.5,
        icon_size=QSize(16, 16),
        icon_color=None,
        icon_padding=8,
        icon_enabled=True,
        min_width=None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(text or "", parent, *args, **kwargs)
        self.setProperty("type", "HoverLabel")
        # ////// INITIALIZE VARIABLES
        self.show_hover_icon = False
        self._opacity = opacity
        self._icon_size = (
            QSize(*icon_size)
            if isinstance(icon_size, (tuple, list))
            else QSize(icon_size)
        )
        self._icon_color = icon_color
        self._icon_padding = icon_padding
        self._icon_enabled = icon_enabled
        self._min_width = min_width
        self.setMouseTracking(True)
        # ////// SET ICON (setter gère tout)
        self.hover_icon = icon

    # PROPERTY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    @property
    def opacity(self) -> float:
        """Get or set the opacity of the hover icon."""
        return self._opacity

    @opacity.setter
    def opacity(self, value: float) -> None:
        """Set the opacity of the hover icon."""
        self._opacity = float(value)
        self.update()

    @property
    def hover_icon(self) -> QIcon:
        """Get or set the icon displayed on hover."""
        return self._hover_icon

    @hover_icon.setter
    def hover_icon(self, value) -> None:
        """Set the icon displayed on hover. Accepts QIcon, str (path, resource, URL, or SVG), or None."""
        # ////// HANDLE NONE
        if value is None:
            self._hover_icon = None
        # ////// HANDLE QICON
        elif isinstance(value, QIcon):
            self._hover_icon = value
        # ////// HANDLE STRING (PATH, URL, SVG)
        elif isinstance(value, str):
            # ////// HANDLE URL
            if value.startswith("http://") or value.startswith("https://"):
                print(f"Loading icon from URL: {value}")
                try:
                    import requests
                    response = requests.get(value, timeout=5)
                    response.raise_for_status()
                    if 'image' not in response.headers.get('Content-Type', ''):
                        raise ValueError("URL does not point to an image file.")
                    image_data = response.content
                    # ////// HANDLE SVG FROM URL
                    if value.lower().endswith('.svg'):
                        from PySide6.QtSvg import QSvgRenderer
                        from PySide6.QtCore import QByteArray
                        renderer = QSvgRenderer(QByteArray(image_data))
                        pixmap = QPixmap(self._icon_size)
                        pixmap.fill(Qt.transparent)
                        painter = QPainter(pixmap)
                        renderer.render(painter)
                        painter.end()
                        self._hover_icon = QIcon(pixmap)
                    # ////// HANDLE RASTER IMAGE FROM URL
                    else:
                        pixmap = QPixmap()
                        if not pixmap.loadFromData(image_data):
                            raise ValueError("Failed to load image data from URL (unsupported format or corrupt image).")
                        self._hover_icon = QIcon(pixmap)
                except Exception as e:
                    raise ValueError(f"Failed to load icon from URL: {e}")
            # ////// HANDLE LOCAL SVG
            elif value.lower().endswith('.svg'):
                try:
                    from PySide6.QtSvg import QSvgRenderer
                    from PySide6.QtCore import QFile
                    file = QFile(value)
                    if not file.open(QFile.ReadOnly):
                        raise ValueError(f"Cannot open SVG file: {value}")
                    svg_data = file.readAll()
                    file.close()
                    renderer = QSvgRenderer(svg_data)
                    pixmap = QPixmap(self._icon_size)
                    pixmap.fill(Qt.transparent)
                    painter = QPainter(pixmap)
                    renderer.render(painter)
                    painter.end()
                    self._hover_icon = QIcon(pixmap)
                except Exception as e:
                    raise ValueError(f"Failed to load SVG icon: {e}")
            # ////// HANDLE LOCAL/RESOURCE RASTER IMAGE
            else:
                icon = QIcon(value)
                if icon.isNull():
                    raise ValueError(f"Invalid icon path: {value}")
                self._hover_icon = icon
        # ////// HANDLE INVALID TYPE
        else:
            raise TypeError("hover_icon must be a QIcon, a path string, or None.")
        # ////// UPDATE STYLE
        self.setStyleSheet(f"padding-right: {self._icon_size.width() + self._icon_padding if self._hover_icon and self._icon_enabled else 0}px;")
        self.update()

    @property
    def icon_size(self) -> QSize:
        """Get or set the size of the hover icon."""
        return self._icon_size

    @icon_size.setter
    def icon_size(self, value) -> None:
        """Set the size of the hover icon."""
        if isinstance(value, QSize):
            self._icon_size = value
        elif isinstance(value, (tuple, list)) and len(value) == 2:
            self._icon_size = QSize(*value)
        else:
            raise TypeError(
                "icon_size must be a QSize or a tuple/list of two integers."
            )
        self.setStyleSheet(f"padding-right: {self._icon_size.width() + self._icon_padding if self._hover_icon and self._icon_enabled else 0}px;")
        self.update()

    @property
    def icon_color(self):
        """Get or set the color overlay of the hover icon (QColor, str, or None)."""
        return self._icon_color

    @icon_color.setter
    def icon_color(self, value):
        self._icon_color = value
        self.update()

    @property
    def icon_padding(self) -> int:
        """Get or set the right padding for the icon."""
        return self._icon_padding

    @icon_padding.setter
    def icon_padding(self, value: int) -> None:
        self._icon_padding = int(value)
        self.setStyleSheet(f"padding-right: {self._icon_size.width() + self._icon_padding if self._hover_icon and self._icon_enabled else 0}px;")
        self.update()

    @property
    def icon_enabled(self) -> bool:
        """Enable or disable the hover icon."""
        return self._icon_enabled

    @icon_enabled.setter
    def icon_enabled(self, value: bool) -> None:
        self._icon_enabled = bool(value)
        self.setStyleSheet(f"padding-right: {self._icon_size.width() + self._icon_padding if self._hover_icon and self._icon_enabled else 0}px;")
        self.update()

    def clear_icon(self):
        """Remove the hover icon."""
        # ////// CLEAR ICON
        self._hover_icon = None
        self.setStyleSheet(f"padding-right: 0px;")
        self.update()

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse movement events."""
        vertical_offset = 5
        icon_size = self._icon_size
        icon_x = self.width() - icon_size.width() - 4
        icon_y = (self.height() - icon_size.height()) // 2 + vertical_offset
        icon_rect = QRect(icon_x, icon_y, icon_size.width(), icon_size.height())
        if (
            self.show_hover_icon
            and self._hover_icon
            and icon_rect.contains(event.pos())
        ):
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseMoveEvent(event)

    # ///////////////////////////////////////////////////////////////

    def mousePressEvent(self, event) -> None:
        """Handle mouse press events."""
        vertical_offset = 5
        icon_size = self._icon_size
        icon_x = self.width() - icon_size.width() - 4
        icon_y = (self.height() - icon_size.height()) // 2 + vertical_offset
        icon_rect = QRect(icon_x, icon_y, icon_size.width(), icon_size.height())
        if (
            self.show_hover_icon
            and self._hover_icon
            and icon_rect.contains(event.pos())
        ):
            self.hoverIconClicked.emit()
        super().mousePressEvent(event)

    # ///////////////////////////////////////////////////////////////

    def enterEvent(self, event) -> None:
        """Handle enter events."""
        self.show_hover_icon = True
        self.update()  # Demande de redessiner le widget

    # ///////////////////////////////////////////////////////////////

    def leaveEvent(self, event) -> None:
        """Handle leave events."""
        self.show_hover_icon = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

    # UI FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def paintEvent(self, event) -> None:
        """Paint the widget."""
        super().paintEvent(event)
        # ////// DRAW HOVER ICON IF NEEDED
        if self.show_hover_icon and self._hover_icon:
            painter = QPainter(self)
            painter.setOpacity(self._opacity)
            metrics = self.fontMetrics()

            # ////// CALCULATE ICON SIZE
            icon_height = min(self._icon_size.height(), metrics.height())
            icon_size = QSize(icon_height, icon_height)

            # ////// CALCULATE ICON POSITION
            icon_x = self.width() - icon_size.width() - 4
            icon_y = (self.height() - icon_size.height()) // 2

            # ////// CALCULATE ICON RECTANGLE
            icon_rect = QRect(icon_x, icon_y, icon_size.width(), icon_size.height())

            # ////// GET ICON PIXMAP
            icon_pixmap = self._hover_icon.pixmap(icon_size)
            
            # ////// APPLY COLOR OVERLAY
            if self._icon_color:
                from PySide6.QtGui import QColor, QPixmap, QPainter as QPainter2

                overlay = QPixmap(icon_pixmap.size())
                overlay.fill(Qt.transparent)
                painter2 = QPainter2(overlay)
                color = QColor(self._icon_color)
                painter2.setCompositionMode(
                    QPainter2.CompositionMode.CompositionMode_Source
                )
                painter2.fillRect(overlay.rect(), color)
                painter2.setCompositionMode(
                    QPainter2.CompositionMode.CompositionMode_DestinationIn
                )
                painter2.drawPixmap(0, 0, icon_pixmap)
                painter2.end()
                icon_pixmap = overlay
            painter.drawPixmap(icon_rect, icon_pixmap)

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget's style (useful after dynamic stylesheet changes)."""
        # // REFRESH STYLE
        self.style().unpolish(self)
        self.style().polish(self)
        # //////

    def resizeEvent(self, event):
        """Adjust right margin to make room for the icon."""
        super().resizeEvent(event)

    # ///////////////////////////////////////////////////////////////

    def minimumSizeHint(self):
        """Get the minimum size hint for the widget."""
        base = super().minimumSizeHint()
        min_width = self._min_width if self._min_width is not None else base.width()
        return QSize(min_width, base.height())

    # ///////////////////////////////////////////////////////////////
