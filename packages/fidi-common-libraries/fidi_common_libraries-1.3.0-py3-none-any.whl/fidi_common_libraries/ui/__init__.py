"""
Biblioteca de Interação com Interface do Usuário para Sistema RM.

Esta biblioteca encapsula operações comuns do Pywinauto para tornar o código
mais robusto, legível e manutenível, seguindo as melhores práticas de automação de UI.

"""

from .core.application import RMApplication
from .core.element_finder import ElementFinder
from .core.interactions import UIInteractions
from .core.waits import UIWaits
from .core.position_finder import PositionFinder, ScreenRegion, PositionReference
from .core.image_finder import ImageFinder, ImageMatchResult
from .exceptions.ui_exceptions import (
    UIConnectionError,
    UIElementNotFoundError,
    UIInteractionError,
    UITimeoutError
)

__version__ = "1.3.0"
__all__ = [
    "RMApplication",
    "ElementFinder", 
    "UIInteractions",
    "UIWaits",
    "PositionFinder",
    "ImageFinder",
    "ScreenRegion",
    "PositionReference",
    "ImageMatchResult",
    "UIConnectionError",
    "UIElementNotFoundError", 
    "UIInteractionError",
    "UITimeoutError"
]