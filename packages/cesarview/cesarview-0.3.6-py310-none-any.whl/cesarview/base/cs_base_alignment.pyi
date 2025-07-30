# Stub file for type hints

import enum
from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
from cesarview.base.cs_base_box import CSBaseBox

class CSBaseAlignment:
    class Direction:
        VERTICAL: int
        HORIZONTAL: int

    def __init__(self, *widgets): ...
