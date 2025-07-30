# Stub file for type hints

import enum
from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout
from cesarview.base.cs_base_widget import CSBaseWidget

class CSBaseBox:
    class Direction:
        VERTICAL: int
        HORIZONTAL: int

    def __init__(self, *widgets): ...
    def showEvent(self, event): ...
    def init_first_event(self, event): ...
