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
    QDate,
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
    QCalendarWidget,
    QDialog,
    QVBoxLayout,
    QPushButton,
)
from datetime import datetime

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

# ///////////////////////////////////////////////////////////////
# FONCTIONS UTILITAIRES
# ///////////////////////////////////////////////////////////////


def format_date(date, format_str="dd/MM/yyyy"):
    """
    Format a QDate object to string.

    Parameters
    ----------
    date : QDate
        The date to format.
    format_str : str, optional
        Format string (default: "dd/MM/yyyy").

    Returns
    -------
    str
        Formatted date string.
    """
    if not date.isValid():
        return ""
    return date.toString(format_str)


def parse_date(date_str, format_str="dd/MM/yyyy"):
    """
    Parse a date string to QDate object.

    Parameters
    ----------
    date_str : str
        The date string to parse.
    format_str : str, optional
        Format string (default: "dd/MM/yyyy").

    Returns
    -------
    QDate
        Parsed QDate object or invalid QDate if parsing fails.
    """
    return QDate.fromString(date_str, format_str)


def get_calendar_icon():
    """Get a default calendar icon."""
    # Create a simple calendar icon
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setPen(QColor("#666666"))
    painter.setBrush(QColor("#f0f0f0"))
    painter.drawRect(0, 0, 15, 15)
    painter.setPen(QColor("#333333"))
    painter.drawText(2, 2, 12, 12, Qt.AlignCenter, "📅")
    painter.end()
    return QIcon(pixmap)


# ///////////////////////////////////////////////////////////////
# CLASSES PRINCIPALES
# ///////////////////////////////////////////////////////////////


class DatePickerDialog(QDialog):
    """
    Dialog for date selection with calendar widget.
    """

    def __init__(self, parent=None, current_date=None):
        super().__init__(parent)
        self.setWindowTitle("Sélectionner une date")
        self.setModal(True)
        self.setFixedSize(300, 250)

        # ////// SETUP LAYOUT
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # ////// CALENDAR WIDGET
        self.calendar = QCalendarWidget(self)
        if current_date and current_date.isValid():
            self.calendar.setSelectedDate(current_date)
        layout.addWidget(self.calendar)

        # ////// BUTTONS
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Annuler", self)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        layout.addLayout(button_layout)

        # ////// CONNECTIONS
        self.calendar.activated.connect(self.accept)

    def selected_date(self):
        """Get the selected date."""
        return self.calendar.selectedDate()


class DateButton(QToolButton):
    """
    Button widget for date selection with integrated calendar.

    Features:
        - Displays current selected date
        - Opens calendar dialog on click
        - Configurable date format
        - Placeholder text when no date selected
        - Calendar icon with customizable appearance
        - Date validation and parsing

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget (default: None).
    date : QDate or str, optional
        Initial date (QDate, date string, or None for current date).
    date_format : str, optional
        Format for displaying the date (default: "dd/MM/yyyy").
    placeholder : str, optional
        Text to display when no date is selected (default: "Sélectionner une date").
    show_calendar_icon : bool, optional
        Whether to show calendar icon (default: True).
    icon_size : QSize or tuple, optional
        Size of the calendar icon (default: QSize(16, 16)).
    min_width : int, optional
        Minimum width of the button (default: None, auto-calculated).
    min_height : int, optional
        Minimum height of the button (default: None, auto-calculated).
    *args, **kwargs :
        Additional arguments passed to QToolButton.

    Properties
    ----------
    date : QDate
        Get or set the selected date.
    date_string : str
        Get or set the date as formatted string.
    date_format : str
        Get or set the date format.
    placeholder : str
        Get or set the placeholder text.
    show_calendar_icon : bool
        Get or set calendar icon visibility.
    icon_size : QSize
        Get or set the icon size.
    min_width : int
        Get or set the minimum width.
    min_height : int
        Get or set the minimum height.

    Signals
    -------
    dateChanged(QDate)
        Emitted when the date changes.
    dateSelected(QDate)
        Emitted when a date is selected from calendar.
    """

    dateChanged = Signal(QDate)
    dateSelected = Signal(QDate)

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        parent=None,
        date=None,
        date_format="dd/MM/yyyy",
        placeholder="Sélectionner une date",
        show_calendar_icon=True,
        icon_size=QSize(16, 16),
        min_width=None,
        min_height=None,
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        self.setProperty("type", "DateButton")

        # ////// INITIALIZE VARIABLES
        self._date_format = date_format
        self._placeholder = placeholder
        self._show_calendar_icon = show_calendar_icon
        self._icon_size = (
            QSize(*icon_size)
            if isinstance(icon_size, (tuple, list))
            else QSize(icon_size)
        )
        self._min_width = min_width
        self._min_height = min_height
        self._current_date = QDate()

        # ////// SETUP UI COMPONENTS
        self.date_label = QLabel()
        self.icon_label = QLabel()

        # ////// CONFIGURE LABELS
        self.date_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.date_label.setStyleSheet("background-color: transparent;")

        # ////// SETUP LAYOUT
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.date_label)
        layout.addWidget(self.icon_label)

        # ////// CONFIGURE SIZE POLICY
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # ////// SET INITIAL VALUES
        if date:
            self.date = date
        else:
            self.date = QDate.currentDate()

        self.show_calendar_icon = show_calendar_icon
        self._update_display()

    # PROPERTY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    @property
    def date(self):
        """Get or set the selected date."""
        return self._current_date

    @date.setter
    def date(self, value):
        """Set the date from QDate, string, or None."""
        if isinstance(value, str):
            new_date = parse_date(value, self._date_format)
        elif isinstance(value, QDate):
            new_date = value
        elif value is None:
            new_date = QDate()
        else:
            return

        if new_date != self._current_date:
            self._current_date = new_date
            self._update_display()
            self.dateChanged.emit(self._current_date)

    @property
    def date_string(self):
        """Get or set the date as formatted string."""
        return format_date(self._current_date, self._date_format)

    @date_string.setter
    def date_string(self, value):
        """Set the date from a formatted string."""
        self.date = value

    @property
    def date_format(self):
        """Get or set the date format."""
        return self._date_format

    @date_format.setter
    def date_format(self, value):
        """Set the date format."""
        self._date_format = str(value)
        self._update_display()

    @property
    def placeholder(self):
        """Get or set the placeholder text."""
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value):
        """Set the placeholder text."""
        self._placeholder = str(value)
        self._update_display()

    @property
    def show_calendar_icon(self):
        """Get or set calendar icon visibility."""
        return self._show_calendar_icon

    @show_calendar_icon.setter
    def show_calendar_icon(self, value):
        """Set calendar icon visibility."""
        self._show_calendar_icon = bool(value)
        if self._show_calendar_icon:
            self.icon_label.show()
            self.icon_label.setPixmap(get_calendar_icon().pixmap(self._icon_size))
            self.icon_label.setFixedSize(self._icon_size)
        else:
            self.icon_label.hide()

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
        if self._show_calendar_icon:
            self.icon_label.setPixmap(get_calendar_icon().pixmap(self._icon_size))
            self.icon_label.setFixedSize(self._icon_size)

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

    def clear_date(self):
        """Clear the selected date."""
        self.date = None

    def set_today(self):
        """Set the date to today."""
        self.date = QDate.currentDate()

    def open_calendar(self):
        """Open the calendar dialog."""
        dialog = DatePickerDialog(self, self._current_date)
        if dialog.exec() == QDialog.Accepted:
            selected_date = dialog.selected_date()
            if selected_date.isValid():
                self.date = selected_date
                self.dateSelected.emit(selected_date)

    def _update_display(self):
        """Update the display text."""
        if self._current_date.isValid():
            display_text = format_date(self._current_date, self._date_format)
        else:
            display_text = self._placeholder

        self.date_label.setText(display_text)

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.open_calendar()
        super().mousePressEvent(event)

    # OVERRIDE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def sizeHint(self) -> QSize:
        """Get the recommended size for the button."""
        return QSize(150, 30)

    def minimumSizeHint(self) -> QSize:
        """Get the minimum size hint for the button."""
        # ////// CALCULATE BASE SIZE
        base_size = super().minimumSizeHint()

        # ////// CALCULATE TEXT SPACE
        text_width = self.date_label.fontMetrics().horizontalAdvance(
            self.date_string if self._current_date.isValid() else self._placeholder
        )

        # ////// CALCULATE ICON SPACE
        icon_width = self._icon_size.width() if self._show_calendar_icon else 0

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
