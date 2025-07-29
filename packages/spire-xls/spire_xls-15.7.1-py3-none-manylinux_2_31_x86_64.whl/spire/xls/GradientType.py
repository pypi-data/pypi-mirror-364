from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class GradientType(Enum):
    """Represents the types of gradients available in Excel.
    
    This enumeration defines the various gradient types that can be applied
    to Excel cell backgrounds, shapes, and other elements that support gradient fills.
    
    Attributes:
        Liniar: A linear gradient that transitions colors in a straight line.
        Circle: A circular gradient that transitions colors from the center outward in a circular pattern.
        Rect: A rectangular gradient that transitions colors from the center outward in a rectangular pattern.
        Shape: A gradient that follows the shape of the object to which it is applied.
    """
    Liniar = 0
    Circle = 1
    Rect = 2
    Shape = 3

