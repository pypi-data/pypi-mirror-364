"""
Módulo core para automação de UI.

Este módulo contém as classes e funções principais para interação com interfaces gráficas,
incluindo gerenciamento de aplicações, localização de elementos, interações com elementos,
mecanismos de espera, localização por posição e reconhecimento de imagem.
"""

from .application import RMApplication
from .element_finder import ElementFinder
from .interactions import UIInteractions
from .waits import UIWaits
from .position_finder import PositionFinder, ScreenRegion, PositionReference
from .image_finder import ImageFinder, ImageMatchResult

__all__ = [
    "RMApplication",
    "ElementFinder",
    "UIInteractions",
    "UIWaits",
    "PositionFinder",
    "ScreenRegion",
    "PositionReference",
    "ImageFinder",
    "ImageMatchResult"
]