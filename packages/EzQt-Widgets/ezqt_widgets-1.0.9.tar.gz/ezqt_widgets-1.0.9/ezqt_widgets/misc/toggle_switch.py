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
    QPropertyAnimation,
    QEasingCurve,
    Property,
)
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
)
from PySide6.QtWidgets import (
    QWidget,
    QSizePolicy,
)

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

## ==> GLOBALS
# ///////////////////////////////////////////////////////////////

## ==> VARIABLES
# ///////////////////////////////////////////////////////////////

## ==> CLASSES
# ///////////////////////////////////////////////////////////////


class ToggleSwitch(QWidget):
    """
    Modern toggle switch widget with animated sliding circle.

    Features:
        - Smooth animation when toggling
        - Customizable colors for on/off states
        - Configurable size and border radius
        - Click to toggle functionality
        - Property-based access to state
        - Signal emitted on state change

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget (default: None).
    checked : bool, optional
        Initial state of the toggle (default: False).
    width : int, optional
        Width of the toggle switch (default: 50).
    height : int, optional
        Height of the toggle switch (default: 24).
    *args, **kwargs :
        Additional arguments passed to QWidget.

    Properties
    ----------
    checked : bool
        Get or set the toggle state.
    width : int
        Get or set the width of the toggle.
    height : int
        Get or set the height of the toggle.

    Signals
    -------
    toggled(bool)
        Emitted when the toggle state changes.
    """

    toggled = Signal(bool)

    def __init__(
        self,
        parent=None,
        checked=False,
        width=50,
        height=24,
        animation=True,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)
        
        # Configuration
        self._checked = checked
        self._width = width
        self._height = height
        self._circle_radius = (height - 4) // 2  # Circle radius with 2px margin
        self._animation_duration = 200
        self._animation_enabled = animation
        
        # Colors (will be overridden by CSS)
        self._bg_color_off = QColor(44, 49, 58)  # Default dark theme
        self._bg_color_on = QColor(150, 205, 50)  # Default accent color
        self._circle_color = QColor(255, 255, 255)
        self._border_color = QColor(52, 59, 72)
        
        # Initialize position first
        self._circle_position = self._get_circle_position()
        
        # Animation (after _circle_position is initialized)
        self._animation = QPropertyAnimation(self, b"circle_position")
        self._animation.setDuration(self._animation_duration)
        self._animation.setEasingCurve(QEasingCurve.InOutQuart)
        
        # Setup
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(width, height)
        self.setCursor(Qt.PointingHandCursor)
        
    def _get_circle_position(self) -> int:
        """Calculate circle position based on state."""
        if self._checked:
            return self._width - self._height + 2  # Right position
        else:
            return 2  # Left position
    
    def _get_circle_position_property(self) -> int:
        """Property getter for animation."""
        return self._circle_position
    
    def _set_circle_position_property(self, position: int):
        """Property setter for animation."""
        self._circle_position = position
        self.update()
    
    # Property for animation
    circle_position = Property(int, _get_circle_position_property, _set_circle_position_property)
    
    @property
    def checked(self) -> bool:
        """Get the current toggle state."""
        return self._checked
    
    @checked.setter
    def checked(self, value: bool):
        """Set the toggle state with animation."""
        if self._checked != value:
            self._checked = value
            # Ensure _circle_position exists before animating
            if hasattr(self, '_circle_position'):
                self._animate_circle()
            else:
                self._circle_position = self._get_circle_position()
                self.update()
            self.toggled.emit(self._checked)
    
    @property
    def width(self) -> int:
        """Get the width of the toggle."""
        return self._width
    
    @width.setter
    def width(self, value: int):
        """Set the width of the toggle."""
        self._width = value
        self.setFixedWidth(value)
        self._circle_position = self._get_circle_position()
        self.update()
    
    @property
    def height(self) -> int:
        """Get the height of the toggle."""
        return self._height
    
    @height.setter
    def height(self, value: int):
        """Set the height of the toggle."""
        self._height = value
        self._circle_radius = (value - 4) // 2
        self.setFixedHeight(value)
        self._circle_position = self._get_circle_position()
        self.update()
    
    @property
    def animation(self) -> bool:
        """Get the animation state."""
        return self._animation_enabled
    
    @animation.setter
    def animation(self, value: bool):
        """Set the animation state."""
        self._animation_enabled = value
    
    def _animate_circle(self):
        """Animate the circle to its new position."""
        if not self._animation_enabled:
            # Update position immediately without animation
            self._circle_position = self._get_circle_position()
            self.update()
            return
            
        try:
            start_pos = self._circle_position
            end_pos = self._get_circle_position()
            
            self._animation.setStartValue(start_pos)
            self._animation.setEndValue(end_pos)
            self._animation.start()
        except Exception as e:
            # Fallback: update position immediately without animation
            self._circle_position = self._get_circle_position()
            self.update()
    
    def toggle(self):
        """Toggle the switch state."""
        self.checked = not self._checked
    
    def mousePressEvent(self, event):
        """Handle mouse press to toggle the switch."""
        if event.button() == Qt.LeftButton:
            self.toggle()
        super().mousePressEvent(event)
    
    def paintEvent(self, event):
        """Custom paint event to draw the toggle switch."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate dimensions
        rect = self.rect()
        border_radius = self._height // 2
        
        # Get colors from stylesheet or use defaults
        palette = self.palette()
        
        # Background color based on state
        if self._checked:
            bg_color = QColor(150, 205, 50)  # Accent color when checked
        else:
            bg_color = QColor(44, 49, 58)  # Dark background when unchecked
        
        # Border color
        border_color = QColor(52, 59, 72)
        
        # Circle color
        circle_color = QColor(255, 255, 255)
        
        # Draw background
        painter.setPen(QPen(border_color, 1))
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(rect, border_radius, border_radius)
        
        # Draw circle
        circle_x = self._circle_position
        circle_y = self._height // 2
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(circle_color))
        painter.drawEllipse(circle_x, circle_y - self._circle_radius, 
                           self._circle_radius * 2, self._circle_radius * 2)
    
    def sizeHint(self) -> QSize:
        """Return the recommended size for the widget."""
        return QSize(self._width, self._height)
    
    def minimumSizeHint(self) -> QSize:
        """Return the minimum size for the widget."""
        return QSize(self._width, self._height) 