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
        - Configurable default selection by ID (index)
        - Smooth animations with easing curves
        - Click events for option selection
        - Uses IDs internally for robust value handling

    Parameters
    ----------
    items : List[str]
        List of option texts to display.
    default_id : int, optional
        Default selected option ID (index) (default: 0).
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
        Get or set the currently selected option text.
    value_id : int
        Get or set the currently selected option ID.
    options : List[str]
        Get the list of available options.
    default_id : int
        Get or set the default option ID.
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
    valueIdChanged(int)
        Emitted when the selected value ID changes.
    """

    clicked = Signal()
    valueChanged = Signal(str)
    valueIdChanged = Signal(int)

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        items: List[str],
        default_id: int = 0,
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
        self._value_id = 0
        self._options_list = items
        self._default_id = default_id
        self._options: Dict[int, FramedLabel] = {}  # Changed to use int keys
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
        for i, option_text in enumerate(self._options_list):
            self.add_option(option_id=i, option_text=option_text)

        # ////// INITIALIZE SELECTOR
        if self._options_list:
            self.initialize_selector(self._default_id)

    # PROPERTY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    @property
    def value(self) -> str:
        """Get or set the currently selected option text."""
        if 0 <= self._value_id < len(self._options_list):
            return self._options_list[self._value_id]
        return ""

    @value.setter
    def value(self, new_value: str) -> None:
        """Set the selected option by text."""
        try:
            new_id = self._options_list.index(new_value)
            self.value_id = new_id
        except ValueError:
            pass  # Value not found in list

    @property
    def value_id(self) -> int:
        """Get or set the currently selected option ID."""
        return self._value_id

    @value_id.setter
    def value_id(self, new_id: int) -> None:
        """Set the selected option by ID."""
        if 0 <= new_id < len(self._options_list) and new_id != self._value_id:
            self._value_id = new_id
            if new_id in self._options:
                self.move_selector(self._options[new_id])
            self.valueChanged.emit(self.value)
            self.valueIdChanged.emit(new_id)

    @property
    def options(self) -> List[str]:
        """Get the list of available options."""
        return self._options_list.copy()

    @property
    def default_id(self) -> int:
        """Get or set the default option ID."""
        return self._default_id

    @default_id.setter
    def default_id(self, value: int) -> None:
        """Set the default option ID."""
        if 0 <= value < len(self._options_list):
            self._default_id = value
            if not self._value_id and self._options_list:
                self.value_id = value

    @property
    def selected_option(self) -> Optional[FramedLabel]:
        """Get the currently selected option widget."""
        return self._options.get(self._value_id)

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

    def initialize_selector(self, default_id: int = 0) -> None:
        """Initialize the selector with default position."""
        if 0 <= default_id < len(self._options_list):
            self._default_id = default_id
            selected_option = self._options.get(default_id)

            if selected_option:
                # ////// SET INITIAL VALUE
                self._value_id = default_id

                # ////// POSITION SELECTOR
                default_pos = self.grid.indexOf(selected_option)
                self.grid.addWidget(self.selector, 0, default_pos)
                self.selector.lower()  # Ensure selector stays below
                self.selector.update()  # Force refresh if needed

    def add_option(self, option_id: int, option_text: str) -> None:
        """Add a new option to the toggle radio."""
        # ////// CREATE OPTION LABEL
        option = FramedLabel(option_text.capitalize(), self)  # Capitalize for display
        option.setObjectName(f"opt_{option_id}")
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
        option.mousePressEvent = (
            lambda event, option_id=option_id: self.toggle_selection(option_id)
        )

        # ////// STORE OPTION
        self._options[option_id] = option

    # UTILITY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def get_value_option(self) -> Optional[FramedLabel]:
        """Get the currently selected option widget."""
        return self._options.get(self._value_id)

    def toggle_selection(self, option_id: int) -> None:
        """Handle option selection."""
        if option_id != self._value_id:
            self._value_id = option_id
            self.clicked.emit()
            self.valueChanged.emit(self.value)
            self.valueIdChanged.emit(option_id)
            self.move_selector(self._options[option_id])

    def move_selector(self, option: FramedLabel) -> None:
        """Animate the selector to the selected option."""
        # ////// GET START AND END GEOMETRIES
        start_geometry = self.selector.geometry()
        end_geometry = option.geometry()

        # ////// CREATE GEOMETRY ANIMATION
        self._selector_animation = QPropertyAnimation(self.selector, b"geometry")
        self._selector_animation.setDuration(
            self._animation_duration
        )  # Custom duration
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
            # Estimate text width using font metrics (use capitalized text for display)
            font_metrics = self.fontMetrics()
            text_width = font_metrics.horizontalAdvance(option_text.capitalize())

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
                text_width = font_metrics.horizontalAdvance(option_text.capitalize())
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
