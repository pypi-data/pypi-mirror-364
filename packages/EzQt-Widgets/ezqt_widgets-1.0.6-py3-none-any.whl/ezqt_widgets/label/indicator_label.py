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
    QHBoxLayout,
    QSizePolicy,
    QFrame,
    QLabel,
)
from PySide6.QtGui import (
    QFont,
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


class IndicatorLabel(QFrame):
    """
    IndicatorLabel is a dynamic status indicator widget based on QFrame, designed for displaying a status label and a colored LED in Qt applications.

    This widget encapsulates a QLabel for the status text and a QLabel for the LED, both arranged horizontally. The possible states are defined in a configurable dictionary (status_map), allowing for flexible text, color, and state property assignment.

    Features:
        - Dynamic states defined via a status_map dictionary (text, state, color)
        - Property-based access to the current status (status)
        - Emits a statusChanged(str) signal when the status changes
        - Allows custom status sets and colors for various use cases
        - Suitable for online/offline indicators, service status, etc.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget (default: None).
    status_map : dict, optional
        Dictionary defining possible states. Each key is a state name, and each value is a dict with keys:
            - text (str): The label to display
            - state (str): The value set as a Qt property for styling
            - color (str): The LED color (any valid CSS color)
        Example:
            {
                "neutral": {"text": "En attente", "state": "none", "color": "#A0A0A0"},
                "online": {"text": "En ligne", "state": "ok", "color": "#4CAF50"},
                ...
            }
    initial_status : str, optional
        The initial status key to use (default: "neutral").
    *args, **kwargs :
        Additional arguments passed to QFrame.

    Properties
    ----------
    status : str
        Get or set the current status key.

    Signals
    -------
    statusChanged(str)
        Emitted when the status changes.
    """

    statusChanged = Signal(str)

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self, parent=None, status_map=None, initial_status="neutral", *args, **kwargs
    ) -> None:
        super().__init__(parent, *args, **kwargs)
        self.setProperty("type", "IndicatorLabel")

        # Default status map
        self.status_map = status_map or {
            "neutral": {"text": "En attente", "state": "none", "color": "#A0A0A0"},
            "online": {"text": "En ligne", "state": "ok", "color": "#4CAF50"},
            "partial": {
                "text": "Services perturbés",
                "state": "partiel",
                "color": "#FFC107",
            },
            "offline": {"text": "Hors ligne", "state": "ko", "color": "#F44336"},
        }
        self._status = None

        # Frame setup
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)
        self.setContentsMargins(4, 2, 4, 2)
        self.setFixedHeight(24)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        # Layout
        self.status_HLayout = QHBoxLayout(self)
        self.status_HLayout.setObjectName("status_HLayout")
        self.status_HLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.status_HLayout.setContentsMargins(0, 0, 0, 0)
        self.status_HLayout.setSpacing(8)

        # Status label
        self.status_label = QLabel(self)
        self.status_label.setObjectName("status_label")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setLineWidth(0)
        self.status_HLayout.addWidget(self.status_label, 0, Qt.AlignmentFlag.AlignTop)

        # LED label
        self.status_led = QLabel(self)
        self.status_led.setObjectName("status_led")
        self.status_led.setFixedSize(QSize(13, 16))
        self.status_led.setFont(QFont("Segoe UI", 10))
        self.status_led.setLineWidth(0)
        self.status_HLayout.addWidget(self.status_led, 0, Qt.AlignmentFlag.AlignTop)

        # Set initial status
        self.set_status(initial_status)

    # PROPERTY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    @property
    def status(self) -> str:
        """Get or set the current status key."""
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        """Set the current status key."""
        self.set_status(value)

    # UTILITY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def set_status(self, status: str) -> None:
        """Set the current status key."""
        if status not in self.status_map:
            raise ValueError(f"Unknown status: {status}")
        if status == self._status:
            return
        data = self.status_map[status]
        self.status_label.setText(data["text"])
        self.setProperty("state", data["state"])
        # Set LED color (simple background color)
        self.status_led.setStyleSheet(
            f"""
            background-color: {data['color']};
            border: 2px solid rgb(66, 66, 66);
            border-radius: 6px;
            margin-top: 3px;
            """
        )
        self._status = status
        self.refresh_style()
        self.statusChanged.emit(status)

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget's style (useful after dynamic stylesheet changes)."""
        self.style().unpolish(self)
        self.style().polish(self)
