# Stub file for type hints

import enum
import os
from typing import Callable, Any
from PySide6.QtGui import QFont
from cesarview.base.cs_base_btn import CSBaseBtn

class CSBtn:
    class ICON:
        SEARCH: str
        CHECK: str
        EDIT: str
        EMAIL: str
        STAR: str
        TRASH: str

    class Plain:
        def __init__(self, name: str = None, callback: Callable[[str], any] = None, width: int = 120, height: int = 40, text_size: int = None, text_weight: QFont.Weight = None, text_color: str = None, text_hover_color: str = None, text_pressed_color: str = None, bg_color: str = None, bg_hover_color: str = None, bg_pressed_color: str = None, bordered: bool = False, border_color: str = None, border_hover_color: str = None, border_pressed_color: str = None, border_width: int = None, border_style: str = 'solid', disabled: bool = False, style: 'CSBtn.STYLE' = None, icon_path: str = None, icon: 'CSBtn.ICON' = None, both: bool = False, icon_right: bool = False, parent: Any = None): ...

    class Circle:
        def __init__(self, name: str = None, callback: Callable[[str], any] = None, width: int = 40, text_size: int = None, text_weight: QFont.Weight = None, text_color: str = None, text_hover_color: str = None, text_pressed_color: str = None, bg_color: str = None, bg_hover_color: str = None, bg_pressed_color: str = None, bordered: bool = False, border_color: str = None, border_hover_color: str = None, border_pressed_color: str = None, border_radius: int = None, border_width: int = None, border_style: str = 'solid', disabled: bool = False, style: 'CSBtn.STYLE' = None, icon_path: str = None, icon: 'CSBtn.ICON' = None, both: bool = False, icon_right: bool = False, parent: Any = None): ...

    class Round:
        def __init__(self, name: str = None, callback: Callable[[str], any] = None, width: int = 120, height: int = 40, text_size: int = None, text_weight: QFont.Weight = None, text_color: str = None, text_hover_color: str = None, text_pressed_color: str = None, bg_color: str = None, bg_hover_color: str = None, bg_pressed_color: str = None, bordered: bool = False, border_color: str = None, border_hover_color: str = None, border_pressed_color: str = None, border_radius: int = None, border_width: int = None, border_style: str = 'solid', disabled: bool = False, style: 'CSBtn.STYLE' = None, icon_path: str = None, icon: 'CSBtn.ICON' = None, both: bool = False, icon_right: bool = False, parent: Any = None): ...

