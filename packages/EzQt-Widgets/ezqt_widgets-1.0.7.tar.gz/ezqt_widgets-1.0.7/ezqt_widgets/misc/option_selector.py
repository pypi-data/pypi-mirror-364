# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////
from typing import Dict, List, Optional

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import (
    Qt,
    Signal,
    QPropertyAnimation,
    QEasingCurve,
    QSize,
)
from PySide6.QtWidgets import (
    QFrame,
    QSizePolicy,
    QGridLayout,
)

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from ezqt_widgets.label.framed_label import FramedLabel

# ///////////////////////////////////////////////////////////////
# FONCTIONS UTILITAIRES
# ///////////////////////////////////////////////////////////////

# ///////////////////////////////////////////////////////////////
# CLASSES PRINCIPALES
# ///////////////////////////////////////////////////////////////


class OptionSelector(QFrame):
    """
    Option selector widget with animated selector.

    Features:
        - Multiple selectable options displayed as labels
        - Animated selector that moves between options
        - Single selection mode (radio behavior)
        - Configurable default selection
        - Smooth animations with easing curves
        - Click events for option selection

    Parameters
    ----------
    items : List[str]
        List of option texts to display.
    default : str, optional
        Default selected option (default: "").
    min_width : int, optional
        Minimum width constraint for the widget (default: None).
    min_height : int, optional
        Minimum height constraint for the widget (default: None).
    orientation : str, optional
        Layout orientation: "horizontal" or "vertical" (default: "horizontal").
    animation_duration : int, optional
        Duration of the selector animation in milliseconds (default: 300).
    parent : QWidget, optional
        The parent widget (default: None).
    *args, **kwargs :
        Additional arguments passed to QFrame.

    Properties
    ----------
    value : str
        Get or set the currently selected option.
    options : List[str]
        Get the list of available options.
    default : str
        Get or set the default option.
    selected_option : FramedLabel
        Get the currently selected option widget.
    orientation : str
        Get or set the layout orientation ("horizontal" or "vertical").
    min_width : int
        Get or set the minimum width constraint.
    min_height : int
        Get or set the minimum height constraint.
    animation_duration : int
        Get or set the animation duration in milliseconds.

    Signals
    -------
    clicked()
        Emitted when an option is clicked.
    valueChanged(str)
        Emitted when the selected value changes.
    """

    clicked = Signal()
    valueChanged = Signal(str)

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        items: List[str],
        default: str = "",
        min_width=None,
        min_height=None,
        orientation="horizontal",
        animation_duration=300,
        parent=None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)
        self.setProperty("type", "OptionSelector")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ////// INITIALIZE VARIABLES
        self._value = ""
        self._options_list = items
        self._default = default
        self._options: Dict[str, FramedLabel] = {}
        self._selector_animation = None
        self._min_width = min_width
        self._min_height = min_height
        self._orientation = orientation.lower()
        self._animation_duration = animation_duration

        # ////// SETUP GRID LAYOUT
        self.grid = QGridLayout(self)
        self.grid.setObjectName("grid")
        self.grid.setSpacing(4)
        self.grid.setContentsMargins(4, 4, 4, 4)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ////// CREATE SELECTOR
        self.selector = QFrame(self)
        self.selector.setObjectName("selector")
        self.selector.setProperty("type", "OptionSelector_Selector")

        # ////// ADD OPTIONS
        for option in self._options_list:
            self.add_option(option_text=option)

        # ////// INITIALIZE SELECTOR
        if self._options_list:
            self.initialize_selector(self._default or self._options_list[0])

    # PROPERTY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    @property
    def value(self) -> str:
        """Get or set the currently selected option."""
        return self._value

    @value.setter
    def value(self, new_value: str) -> None:
        """Set the selected option."""
        if new_value in self._options_list and new_value != self._value:
            self._value = new_value
            if new_value in self._options:
                self.move_selector(self._options[new_value])
            self.valueChanged.emit(new_value)

    @property
    def options(self) -> List[str]:
        """Get the list of available options."""
        return self._options_list.copy()

    @property
    def default(self) -> str:
        """Get or set the default option."""
        return self._default

    @default.setter
    def default(self, value: str) -> None:
        """Set the default option."""
        self._default = value
        if value in self._options_list and not self._value:
            self.value = value

    @property
    def selected_option(self) -> Optional[FramedLabel]:
        """Get the currently selected option widget."""
        return self._options.get(self._value)

    @property
    def orientation(self) -> str:
        """Get or set the orientation of the selector."""
        return self._orientation

    @orientation.setter
    def orientation(self, value: str) -> None:
        """Set the orientation of the selector."""
        if value.lower() in ["horizontal", "vertical"]:
            self._orientation = value.lower()
            self.updateGeometry()

    @property
    def min_width(self):
        """Get or set the minimum width of the widget."""
        return self._min_width

    @min_width.setter
    def min_width(self, value):
        """Set the minimum width of the widget."""
        self._min_width = value
        self.updateGeometry()

    @property
    def min_height(self):
        """Get or set the minimum height of the widget."""
        return self._min_height

    @min_height.setter
    def min_height(self, value):
        """Set the minimum height of the widget."""
        self._min_height = value
        self.updateGeometry()

    @property
    def animation_duration(self):
        """Get or set the animation duration in milliseconds."""
        return self._animation_duration

    @animation_duration.setter
    def animation_duration(self, value):
        """Set the animation duration in milliseconds."""
        self._animation_duration = value

    # UI SETUP FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def initialize_selector(self, default: str = "") -> None:
        """Initialize the selector with default position."""
        self._default = default

        if self._options:
            # ////// GET DEFAULT OPTION
            first_option_key = next(iter(self._options_list), None)
            selected_option = self._options.get(
                self._default.capitalize(), self._options.get(first_option_key)
            )

            if selected_option:
                # ////// SET INITIAL VALUE
                self._value = selected_option.label.text()

                # ////// POSITION SELECTOR
                default_pos = self.grid.indexOf(selected_option)
                self.grid.addWidget(self.selector, 0, default_pos)
                self.selector.lower()  # Ensure selector stays below
                self.selector.update()  # Force refresh if needed

    def add_option(self, option_text: str) -> None:
        """Add a new option to the toggle radio."""
        # ////// CREATE OPTION LABEL
        option = FramedLabel(option_text, self)
        option.setObjectName(f"opt_{option_text}")
        option.setFrameShape(QFrame.NoFrame)
        option.setFrameShadow(QFrame.Raised)
        option.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        option.setProperty("type", "OptionSelector_Option")

        # ////// ADD TO GRID BASED ON ORIENTATION
        option_index = len(self._options.items())
        if self._orientation == "horizontal":
            self.grid.addWidget(option, 0, option_index)
        else:  # vertical
            self.grid.addWidget(option, option_index, 0)

        # ////// SETUP CLICK HANDLER
        option.mousePressEvent = lambda event, option=option: self.toggle_selection(
            option
        )

        # ////// STORE OPTION
        self._options[option_text] = option

    # UTILITY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def get_value_option(self) -> Optional[FramedLabel]:
        """Get the currently selected option widget."""
        return self._options.get(self._value)

    def toggle_selection(self, option: FramedLabel) -> None:
        """Handle option selection."""
        new_value = option.label.text()

        if new_value != self._value:
            self._value = new_value
            self.clicked.emit()
            self.valueChanged.emit(new_value)
            self.move_selector(option)

    def move_selector(self, option: FramedLabel) -> None:
        """Animate the selector to the selected option."""
        # ////// GET START AND END GEOMETRIES
        start_geometry = self.selector.geometry()
        end_geometry = option.geometry()

        # ////// CREATE GEOMETRY ANIMATION
        self._selector_animation = QPropertyAnimation(self.selector, b"geometry")
        self._selector_animation.setDuration(self._animation_duration)  # Custom duration
        self._selector_animation.setStartValue(start_geometry)
        self._selector_animation.setEndValue(end_geometry)
        self._selector_animation.setEasingCurve(QEasingCurve.OutCubic)

        # ////// ENSURE SELECTOR STAYS BELOW
        self.selector.lower()

        # ////// START ANIMATION
        self._selector_animation.start()

    # OVERRIDE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def sizeHint(self) -> QSize:
        """Get the recommended size for the widget."""
        return QSize(200, 40)

    def minimumSizeHint(self) -> QSize:
        """Get the minimum size hint for the widget."""
        # ////// CALCULATE BASE SIZE
        base_size = super().minimumSizeHint()

        # ////// CALCULATE OPTIONS DIMENSIONS
        max_option_width = 0
        max_option_height = 0

        for option_text in self._options_list:
            # Estimate text width using font metrics
            font_metrics = self.fontMetrics()
            text_width = font_metrics.horizontalAdvance(option_text)

            # Add padding and margins
            option_width = text_width + 16  # 8px padding on each side
            option_height = max(font_metrics.height() + 8, 30)  # 4px padding top/bottom

            max_option_width = max(max_option_width, option_width)
            max_option_height = max(max_option_height, option_height)

        # ////// CALCULATE TOTAL DIMENSIONS BASED ON ORIENTATION
        if self._orientation == "horizontal":
            # Horizontal: options side by side with individual widths
            total_width = 0
            for option_text in self._options_list:
                font_metrics = self.fontMetrics()
                text_width = font_metrics.horizontalAdvance(option_text)
                option_width = text_width + 16  # 8px padding on each side
                total_width += option_width
            total_width += (len(self._options_list) - 1) * self.grid.spacing()
            total_height = max_option_height
        else:
            # Vertical: options stacked
            total_width = max_option_width
            total_height = max_option_height * len(self._options_list)
            total_height += (len(self._options_list) - 1) * self.grid.spacing()

        # ////// ADD GRID MARGINS
        total_width += 8  # Grid margins (4px on each side)
        total_height += 8  # Grid margins (4px on each side)

        # ////// APPLY MINIMUM CONSTRAINTS
        min_width = self._min_width if self._min_width is not None else total_width
        min_height = self._min_height if self._min_height is not None else total_height

        return QSize(max(min_width, total_width), max(min_height, total_height))

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget's style (useful after dynamic stylesheet changes)."""
        # // REFRESH STYLE
        self.style().unpolish(self)
        self.style().polish(self)
        # //////
