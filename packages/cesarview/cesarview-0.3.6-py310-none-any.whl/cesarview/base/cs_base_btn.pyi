# Stub file for type hints

import enum
from typing import Callable, Any
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QFont
from cesarview.helper.cs_colors import CSColors
from cesarview.theme import CSTheme

class CSBaseBtn:
    class SHAPE:
        PLAIN: str
        ROUND: str
        CIRCLE: str

    class STYLE:
        DEFAULT: str
        PRIMARY: str
        SUCCESS: str
        INFO: str
        WARNING: str
        DANGER: str

    def __init__(self, name: str = None, callback: Callable[[str], any] = None, width: int = 40, height: int = 40, bg_color: str = None, bg_hover_color: str = None, bg_pressed_color: str = None, text_size: int = None, text_weight: QFont.Weight = None, text_color: str = None, text_hover_color: str = None, text_pressed_color: str = None, bordered: bool = False, border_color: str = None, border_hover_color: str = None, border_pressed_color: str = None, border_radius: int = None, border_width: int = None, border_style: str = 'solid', shape: SHAPE = SHAPE.PLAIN, style: STYLE = None, icon_path: str = None, icon_right: bool = False, disabled: bool = False, both: bool = False, parent: Any = None): ...
    def setup(self): ...
    def _on_btn_clicked(self): ...
