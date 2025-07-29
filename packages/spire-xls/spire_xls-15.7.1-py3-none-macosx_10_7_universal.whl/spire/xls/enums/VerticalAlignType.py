from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class VerticalAlignType(Enum):
    """
    Vertical alignment type.

    """
    Top = 0
    Center = 1
    Bottom = 2
    Justify = 3
    Distributed = 4

