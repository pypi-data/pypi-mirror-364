from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class TopBottomType(Enum):
    """
    TopBottom type.

    """
    Top = 1
    Bottom = 2
    TopPercent = 3
    BottomPercent = 4

