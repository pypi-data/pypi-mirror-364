# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtWidgets import (
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QProgressBar,
)
from PySide6.QtCore import (
    Signal,
    Qt,
    QSize,
    QRect,
)
from PySide6.QtGui import (
    QIcon,
    QPainter,
    QPixmap,
    QAction,
    QColor,
)
import re

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////


# ///////////////////////////////////////////////////////////////
# FONCTIONS UTILITAIRES
# ///////////////////////////////////////////////////////////////


def password_strength(password: str) -> int:
    """Return a strength score from 0 (weak) to 100 (strong)."""
    score = 0
    if len(password) >= 8:
        score += 25
    if re.search(r"[A-Z]", password):
        score += 15
    if re.search(r"[a-z]", password):
        score += 15
    if re.search(r"\d", password):
        score += 20
    if re.search(r"[^A-Za-z0-9]", password):
        score += 25
    return min(score, 100)


def get_strength_color(score: int) -> str:
    """Return color based on password strength score."""
    if score < 30:
        return "#ff4444"  # Red
    elif score < 60:
        return "#ffaa00"  # Orange
    elif score < 80:
        return "#44aa44"  # Green
    else:
        return "#00aa00"  # Dark green


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


class PasswordInput(QWidget):
    """
    Enhanced password input widget with integrated strength bar and right-side icon.

    Features:
        - QLineEdit in password mode with integrated strength bar
        - Right-side icon with click functionality
        - Icon management system (QIcon, path, URL, SVG)
        - Animated strength bar that fills the bottom border
        - Signal strengthChanged(int) emitted on password change
        - Color-coded strength indicator

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget (default: None).
    show_strength : bool, optional
        Whether to show the password strength bar (default: True).
    strength_bar_height : int, optional
        Height of the strength bar in pixels (default: 3).
    show_icon : str or QIcon, optional
        Icon for show password (default: "https://img.icons8.com/?size=100&id=85130&format=png&color=000000").
    hide_icon : str or QIcon, optional
        Icon for hide password (default: "https://img.icons8.com/?size=100&id=85137&format=png&color=000000").
    icon_size : QSize or tuple, optional
        Size of the icon (default: QSize(16, 16)).
    """

    strengthChanged = Signal(int)
    iconClicked = Signal()

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        parent=None,
        show_strength=True,
        strength_bar_height=3,
        show_icon="https://img.icons8.com/?size=100&id=85130&format=png&color=000000",
        hide_icon="https://img.icons8.com/?size=100&id=85137&format=png&color=000000",
        icon_size=QSize(16, 16),
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        self.setProperty("type", "PasswordInput")

        # ////// INITIALIZE VARIABLES
        self._show_strength = show_strength
        self._strength_bar_height = strength_bar_height
        self._current_strength = 0
        self._icon_size = (
            QSize(*icon_size)
            if isinstance(icon_size, (tuple, list))
            else QSize(icon_size)
        )
        self._show_icon_source = show_icon
        self._hide_icon_source = hide_icon
        self._is_password_visible = False

        # ////// SETUP LAYOUT
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ////// PASSWORD FIELD CONTAINER
        self.field_container = QWidget(self)
        field_layout = QVBoxLayout(self.field_container)
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(2)

        # ////// PASSWORD FIELD
        self.line_edit = PasswordLineEdit(self.field_container)
        self.line_edit.setEchoMode(QLineEdit.Password)
        self.line_edit.setPlaceholderText("Password")
        self.line_edit.setProperty("type", "PasswordInputField")
        self.line_edit.iconClicked.connect(self.toggle_password)
        field_layout.addWidget(self.line_edit)

        # ////// STRENGTH BAR
        self.strength_bar = QProgressBar(self.field_container)
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setFixedHeight(strength_bar_height)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setVisible(show_strength)
        self.strength_bar.setProperty("type", "PasswordStrengthBar")
        field_layout.addWidget(self.strength_bar)
        layout.addWidget(self.field_container)

        # ////// CONNECTIONS
        self.line_edit.textChanged.connect(self.update_strength)

        # ////// INIT STATE
        self.update_strength(self.line_edit.text())
        self._update_stylesheet()
        self._update_icon()

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def toggle_password(self):
        """Show or hide the password."""
        self._is_password_visible = not self._is_password_visible
        new_mode = QLineEdit.Normal if self._is_password_visible else QLineEdit.Password
        self.line_edit.setEchoMode(new_mode)
        self._update_icon()
        self.iconClicked.emit()

    def update_strength(self, text):
        """Update the strength bar and emit the strengthChanged signal."""
        score = password_strength(text)
        self._current_strength = score

        # ////// ANIMATE STRENGTH BAR
        if self._show_strength:
            self.strength_bar.setValue(score)
            self._update_strength_color(score)

        self.strengthChanged.emit(score)

    def _update_icon(self):
        """Update the icon based on current password visibility state."""
        icon_source = (
            self._show_icon_source
            if self._is_password_visible
            else self._hide_icon_source
        )
        icon = load_icon_from_source(icon_source)
        if icon:
            self.line_edit.set_right_icon(icon, self._icon_size)

    def _update_strength_color(self, score):
        """Update the strength bar color based on score."""
        color = get_strength_color(score)
        self.strength_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: none;
                background: transparent;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 1px;
            }}
        """
        )

    def _update_stylesheet(self):
        """Update the main widget stylesheet."""
        strength_style = ""
        if self._show_strength:
            strength_style = f"""
                QProgressBar {{
                    border: none;
                    background: transparent;
                }}
                QProgressBar::chunk {{
                    background-color: {get_strength_color(self._current_strength)};
                    border-radius: 1px;
                }}
            """

        self.setStyleSheet(
            f"""
            PasswordInput {{
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
            }}
            PasswordInput:focus-within {{
                border-color: #0078d4;
            }}
            PasswordInputField {{
                border: none;
                background: transparent;
                color: white;
                padding: 8px;
                padding-right: {self._icon_size.width() + 12}px;
            }}
            {strength_style}
        """
        )

    # PROPERTY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    @property
    def password(self):
        """Get or set the current password."""
        return self.line_edit.text()

    @password.setter
    def password(self, value):
        self.line_edit.setText(value)

    @property
    def show_strength(self):
        """Get or set whether the strength bar is visible."""
        return self._show_strength

    @show_strength.setter
    def show_strength(self, value):
        self._show_strength = bool(value)
        self.strength_bar.setVisible(self._show_strength)
        self._update_stylesheet()

    @property
    def strength_bar_height(self):
        """Get or set the height of the strength bar."""
        return self._strength_bar_height

    @strength_bar_height.setter
    def strength_bar_height(self, value):
        self._strength_bar_height = int(value)
        self.strength_bar.setFixedHeight(self._strength_bar_height)

    @property
    def show_icon(self):
        """Get or set the show password icon source."""
        return self._show_icon_source

    @show_icon.setter
    def show_icon(self, value):
        self._show_icon_source = value
        if self._is_password_visible:
            self._update_icon()

    @property
    def hide_icon(self):
        """Get or set the hide password icon source."""
        return self._hide_icon_source

    @hide_icon.setter
    def hide_icon(self, value):
        self._hide_icon_source = value
        if not self._is_password_visible:
            self._update_icon()

    @property
    def icon_size(self):
        """Get or set the icon size."""
        return self._icon_size

    @icon_size.setter
    def icon_size(self, value):
        self._icon_size = (
            QSize(*value) if isinstance(value, (tuple, list)) else QSize(value)
        )
        self._update_icon()
        self._update_stylesheet()

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget's style (useful after dynamic stylesheet changes)."""
        # // REFRESH STYLE
        self.style().unpolish(self)
        self.style().polish(self)
        # //////


class PasswordLineEdit(QLineEdit):
    """
    QLineEdit subclass with right-side icon support.

    Features:
        - Right-side icon with click functionality
        - Icon management system
        - Signal iconClicked emitted when icon is clicked
    """

    iconClicked = Signal()

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(self, parent=None):
        super().__init__(parent)

        # ////// INITIALIZE VARIABLES
        self._right_icon = None
        self._icon_size = QSize(16, 16)
        self._icon_action = None
        self.setMouseTracking(True)

    # UTILITY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def set_right_icon(self, icon: QIcon, size: QSize = None):
        """Set the right-side icon."""
        if size:
            self._icon_size = (
                QSize(*size) if isinstance(size, (tuple, list)) else QSize(size)
            )

        self._right_icon = icon

        # ////// REMOVE EXISTING ACTION
        if self._icon_action:
            self.removeAction(self._icon_action)

        # ////// ADD NEW ACTION
        if icon:
            self._icon_action = QAction(icon, "", self)
            self._icon_action.triggered.connect(self.iconClicked.emit)
            self.addAction(self._icon_action, QLineEdit.ActionPosition.TrailingPosition)

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def mousePressEvent(self, event):
        """Handle mouse press events for icon clicking."""
        if self._right_icon and event.button() == Qt.LeftButton:
            # ////// CHECK IF CLICK IS IN ICON AREA
            icon_rect = QRect(
                self.width() - self._icon_size.width() - 8,
                (self.height() - self._icon_size.height()) // 2,
                self._icon_size.width(),
                self._icon_size.height(),
            )
            if icon_rect.contains(event.pos()):
                self.iconClicked.emit()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move events for cursor changes."""
        if self._right_icon:
            icon_rect = QRect(
                self.width() - self._icon_size.width() - 8,
                (self.height() - self._icon_size.height()) // 2,
                self._icon_size.width(),
                self._icon_size.height(),
            )
            if icon_rect.contains(event.pos()):
                self.setCursor(Qt.PointingHandCursor)
            else:
                self.setCursor(Qt.IBeamCursor)

        super().mouseMoveEvent(event)
