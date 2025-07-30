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
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
)
from PySide6.QtGui import (
    QIcon,
    QPixmap,
    QPainter,
    QColor,
    QPen,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QToolButton,
    QSizePolicy,
    QGraphicsOpacityEffect,
)

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

# ///////////////////////////////////////////////////////////////
# FONCTIONS UTILITAIRES
# ///////////////////////////////////////////////////////////////


def create_spinner_pixmap(size=16, color="#0078d4"):
    """
    Create a spinner pixmap for loading animation.

    Parameters
    ----------
    size : int, optional
        Size of the spinner (default: 16).
    color : str, optional
        Color of the spinner (default: "#0078d4").

    Returns
    -------
    QPixmap
        Spinner pixmap.
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw spinner segments
    pen = QPen(QColor(color))
    pen.setWidth(2)
    painter.setPen(pen)

    center = size // 2
    radius = (size - 4) // 2

    # Draw 8 segments with different opacities
    for i in range(8):
        angle = i * 45
        painter.setOpacity(0.1 + (i * 0.1))
        painter.drawArc(
            center - radius,
            center - radius,
            radius * 2,
            radius * 2,
            angle * 16,
            30 * 16,
        )

    painter.end()
    return pixmap


def create_loading_icon(size=16, color="#0078d4"):
    """
    Create a loading icon with spinner.

    Parameters
    ----------
    size : int, optional
        Size of the icon (default: 16).
    color : str, optional
        Color of the icon (default: "#0078d4").

    Returns
    -------
    QIcon
        Loading icon.
    """
    return QIcon(create_spinner_pixmap(size, color))


def create_success_icon(size=16, color="#28a745"):
    """
    Create a success icon (checkmark).

    Parameters
    ----------
    size : int, optional
        Size of the icon (default: 16).
    color : str, optional
        Color of the icon (default: "#28a745").

    Returns
    -------
    QIcon
        Success icon.
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw checkmark
    pen = QPen(QColor(color))
    pen.setWidth(2)
    painter.setPen(pen)

    # Checkmark path: from bottom-left to top-right, then to bottom-right
    margin = size // 4
    painter.drawLine(margin, size // 2, size // 3, size - margin)
    painter.drawLine(size // 3, size - margin, size - margin, margin)

    painter.end()
    return QIcon(pixmap)


def create_error_icon(size=16, color="#dc3545"):
    """
    Create an error icon (X mark).

    Parameters
    ----------
    size : int, optional
        Size of the icon (default: 16).
    color : str, optional
        Color of the icon (default: "#dc3545").

    Returns
    -------
    QIcon
        Error icon.
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw X mark
    pen = QPen(QColor(color))
    pen.setWidth(2)
    painter.setPen(pen)

    margin = size // 4
    painter.drawLine(margin, margin, size - margin, size - margin)
    painter.drawLine(size - margin, margin, margin, size - margin)

    painter.end()
    return QIcon(pixmap)


# ///////////////////////////////////////////////////////////////
# CLASSES PRINCIPALES
# ///////////////////////////////////////////////////////////////


class LoaderButton(QToolButton):
    """
    Button widget with integrated loading animation.

    Features:
        - Loading state with animated spinner
        - Success state with checkmark icon
        - Error state with X icon
        - Configurable loading, success, and error text/icons
        - Smooth transitions between states
        - Disabled state during loading
        - Customizable animation speed
        - Progress indication support
        - Auto-reset after completion with configurable display times

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget (default: None).
    text : str, optional
        Button text (default: "").
    icon : QIcon or str, optional
        Button icon (default: None).
    loading_text : str, optional
        Text to display during loading (default: "Chargement...").
    loading_icon : QIcon or str, optional
        Icon to display during loading (default: None, auto-generated).
    success_icon : QIcon or str, optional
        Icon to display on success (default: None, auto-generated checkmark).
    error_icon : QIcon or str, optional
        Icon to display on error (default: None, auto-generated X mark).
    animation_speed : int, optional
        Animation speed in milliseconds (default: 100).
    auto_reset : bool, optional
        Whether to auto-reset after loading (default: True).
    success_display_time : int, optional
        Time to display success state in milliseconds (default: 1000).
    error_display_time : int, optional
        Time to display error state in milliseconds (default: 2000).
    min_width : int, optional
        Minimum width of the button (default: None, auto-calculated).
    min_height : int, optional
        Minimum height of the button (default: None, auto-calculated).
    *args, **kwargs :
        Additional arguments passed to QToolButton.

    Properties
    ----------
    text : str
        Get or set the button text.
    icon : QIcon
        Get or set the button icon.
    loading_text : str
        Get or set the loading text.
    loading_icon : QIcon
        Get or set the loading icon.
    success_icon : QIcon
        Get or set the success icon.
    error_icon : QIcon
        Get or set the error icon.
    is_loading : bool
        Get the current loading state.
    animation_speed : int
        Get or set the animation speed.
    auto_reset : bool
        Get or set auto-reset behavior.
    success_display_time : int
        Get or set success display time.
    error_display_time : int
        Get or set error display time.
    min_width : int
        Get or set the minimum width.
    min_height : int
        Get or set the minimum height.

    Signals
    -------
    loadingStarted()
        Emitted when loading starts.
    loadingFinished()
        Emitted when loading finishes successfully.
    loadingFailed(str)
        Emitted when loading fails with error message.
    """

    loadingStarted = Signal()
    loadingFinished = Signal()
    loadingFailed = Signal(str)

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        parent=None,
        text="",
        icon=None,
        loading_text="Chargement...",
        loading_icon=None,
        success_icon=None,
        error_icon=None,
        animation_speed=100,
        auto_reset=True,
        success_display_time=1000,
        error_display_time=2000,
        min_width=None,
        min_height=None,
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        self.setProperty("type", "LoaderButton")

        # ////// INITIALIZE VARIABLES
        self._original_text = text
        self._original_icon = None
        self._loading_text = loading_text
        self._loading_icon = None
        self._success_icon = None
        self._error_icon = None
        self._is_loading = False
        self._animation_speed = animation_speed
        self._auto_reset = auto_reset
        self._success_display_time = success_display_time
        self._error_display_time = error_display_time
        self._min_width = min_width
        self._min_height = min_height
        self._animation_group = None
        self._spinner_animation = None

        # ////// SETUP UI COMPONENTS
        self.text_label = QLabel()
        self.icon_label = QLabel()

        # ////// CONFIGURE LABELS
        self.text_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        )
        self.text_label.setStyleSheet("background-color: transparent;")

        # ////// SETUP LAYOUT
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(8)
        layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)

        # ////// CONFIGURE SIZE POLICY
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # ////// SET INITIAL VALUES
        if icon:
            self.icon = icon
        if text:
            self.text = text

        # ////// SETUP ICONS
        if loading_icon:
            self.loading_icon = loading_icon
        else:
            self.loading_icon = create_loading_icon(16, "#0078d4")

        if success_icon:
            self.success_icon = success_icon
        else:
            self.success_icon = create_success_icon(16, "#28a745")

        if error_icon:
            self.error_icon = error_icon
        else:
            self.error_icon = create_error_icon(16, "#dc3545")

        # ////// SETUP ANIMATIONS
        self._setup_animations()

        # ////// INITIAL DISPLAY
        self._update_display()

    # PROPERTY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    @property
    def text(self):
        """Get or set the button text."""
        return self._original_text

    @text.setter
    def text(self, value):
        """Set the button text."""
        self._original_text = str(value)
        if not self._is_loading:
            self._update_display()

    @property
    def icon(self):
        """Get or set the button icon."""
        return self._original_icon

    @icon.setter
    def icon(self, value):
        """Set the button icon."""
        if isinstance(value, str):
            # Handle string as icon path or URL
            self._original_icon = QIcon(value)
        else:
            self._original_icon = value
        if not self._is_loading:
            self._update_display()

    @property
    def loading_text(self):
        """Get or set the loading text."""
        return self._loading_text

    @loading_text.setter
    def loading_text(self, value):
        """Set the loading text."""
        self._loading_text = str(value)
        if self._is_loading:
            self._update_display()

    @property
    def loading_icon(self):
        """Get or set the loading icon."""
        return self._loading_icon

    @loading_icon.setter
    def loading_icon(self, value):
        """Set the loading icon."""
        if isinstance(value, str):
            # Handle string as icon path or URL
            self._loading_icon = QIcon(value)
        else:
            self._loading_icon = value

    @property
    def success_icon(self):
        """Get or set the success icon."""
        return self._success_icon

    @success_icon.setter
    def success_icon(self, value):
        """Set the success icon."""
        if isinstance(value, str):
            # Handle string as icon path or URL
            self._success_icon = QIcon(value)
        else:
            self._success_icon = value

    @property
    def error_icon(self):
        """Get or set the error icon."""
        return self._error_icon

    @error_icon.setter
    def error_icon(self, value):
        """Set the error icon."""
        if isinstance(value, str):
            # Handle string as icon path or URL
            self._error_icon = QIcon(value)
        else:
            self._error_icon = value

    @property
    def success_display_time(self):
        """Get or set the success display time."""
        return self._success_display_time

    @success_display_time.setter
    def success_display_time(self, value):
        """Set the success display time."""
        self._success_display_time = int(value)

    @property
    def error_display_time(self):
        """Get or set the error display time."""
        return self._error_display_time

    @error_display_time.setter
    def error_display_time(self, value):
        """Set the error display time."""
        self._error_display_time = int(value)

    @property
    def is_loading(self):
        """Get the current loading state."""
        return self._is_loading

    @property
    def animation_speed(self):
        """Get or set the animation speed."""
        return self._animation_speed

    @animation_speed.setter
    def animation_speed(self, value):
        """Set the animation speed."""
        self._animation_speed = int(value)
        if self._spinner_animation:
            self._spinner_animation.setDuration(self._animation_speed)

    @property
    def auto_reset(self):
        """Get or set auto-reset behavior."""
        return self._auto_reset

    @auto_reset.setter
    def auto_reset(self, value):
        """Set auto-reset behavior."""
        self._auto_reset = bool(value)

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

    def start_loading(self):
        """Start the loading animation."""
        if self._is_loading:
            return

        self._is_loading = True
        self.setEnabled(False)
        self._update_display()

        # Start spinner animation using timer
        self._rotation_angle = 0
        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self._rotate_spinner)
        self._animation_timer.start(self._animation_speed // 10)  # Update every 10ms

        self.loadingStarted.emit()

    def _rotate_spinner(self):
        """Rotate the spinner icon."""
        if not self._is_loading:
            return

        self._rotation_angle = (self._rotation_angle + 10) % 360

        # Create a new pixmap with rotation
        if self._loading_icon:
            pixmap = self._loading_icon.pixmap(16, 16)
            if pixmap:
                # Create rotated pixmap
                rotated_pixmap = QPixmap(pixmap.size())
                rotated_pixmap.fill(Qt.transparent)

                painter = QPainter(rotated_pixmap)
                painter.setRenderHint(QPainter.Antialiasing)

                # Move to center and rotate
                painter.translate(pixmap.width() / 2, pixmap.height() / 2)
                painter.rotate(self._rotation_angle)
                painter.translate(-pixmap.width() / 2, -pixmap.height() / 2)

                # Draw the original pixmap
                painter.drawPixmap(0, 0, pixmap)
                painter.end()

                # Set the rotated pixmap
                self.icon_label.setPixmap(rotated_pixmap)

    def stop_loading(self, success=True, error_message=""):
        """Stop the loading animation."""
        if not self._is_loading:
            return

        self._is_loading = False

        # Stop spinner animation
        if hasattr(self, "_animation_timer"):
            self._animation_timer.stop()
            self._animation_timer.deleteLater()

        # Show result state
        if success:
            self._show_success_state()
        else:
            self._show_error_state(error_message)

        # Enable button
        self.setEnabled(True)

        if success:
            self.loadingFinished.emit()
        else:
            self.loadingFailed.emit(error_message)

        # Auto-reset if enabled
        if self._auto_reset:
            display_time = (
                self._success_display_time if success else self._error_display_time
            )
            QTimer.singleShot(display_time, self._reset_to_original)

    def _show_success_state(self):
        """Show success state with success icon."""
        self.text_label.setText("Succès!")
        if self._success_icon:
            self.icon_label.setPixmap(self._success_icon.pixmap(16, 16))
            self.icon_label.show()
        else:
            self.icon_label.hide()

    def _show_error_state(self, error_message=""):
        """Show error state with error icon."""
        if error_message:
            self.text_label.setText(f"Erreur: {error_message}")
        else:
            self.text_label.setText("Erreur")

        if self._error_icon:
            self.icon_label.setPixmap(self._error_icon.pixmap(16, 16))
            self.icon_label.show()
        else:
            self.icon_label.hide()

    def _reset_to_original(self):
        """Reset to original state after auto-reset delay."""
        self._update_display()

    def _setup_animations(self):
        """Setup the spinner rotation animation."""
        # Create opacity effect for smooth transitions
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)

        # Store rotation angle for manual rotation
        self._rotation_angle = 0

    def _update_display(self):
        """Update the display based on current state."""
        if self._is_loading:
            # Show loading state
            self.text_label.setText(self._loading_text)
            if self._loading_icon:
                self.icon_label.setPixmap(self._loading_icon.pixmap(16, 16))
                self.icon_label.show()
            else:
                self.icon_label.hide()
        else:
            # Show normal state
            self.text_label.setText(self._original_text)
            if self._original_icon:
                self.icon_label.setPixmap(self._original_icon.pixmap(16, 16))
                self.icon_label.show()
            else:
                self.icon_label.hide()

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if not self._is_loading and event.button() == Qt.LeftButton:
            super().mousePressEvent(event)

    # OVERRIDE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def sizeHint(self) -> QSize:
        """Get the recommended size for the button."""
        return QSize(120, 30)

    def minimumSizeHint(self) -> QSize:
        """Get the minimum size hint for the button."""
        # ////// CALCULATE BASE SIZE
        base_size = super().minimumSizeHint()

        # ////// CALCULATE TEXT SPACE
        text_width = self.text_label.fontMetrics().horizontalAdvance(
            self._loading_text if self._is_loading else self._original_text
        )

        # ////// CALCULATE ICON SPACE
        icon_width = 16 if (self._loading_icon or self._original_icon) else 0

        # ////// CALCULATE TOTAL WIDTH
        total_width = text_width + icon_width + 16 + 8  # margins + spacing

        # ////// APPLY MINIMUM CONSTRAINTS
        min_width = self._min_width if self._min_width is not None else total_width
        min_height = (
            self._min_height
            if self._min_height is not None
            else max(base_size.height(), 30)
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
