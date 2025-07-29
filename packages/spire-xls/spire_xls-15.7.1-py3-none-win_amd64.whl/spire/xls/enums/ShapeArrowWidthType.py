from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ShapeArrowWidthType(Enum):
    """
    Represents arrow head width.

    """
    ArrowHeadNarrow = 0
    ArrowHeadMedium = 1
    ArrowHeadWide = 2

