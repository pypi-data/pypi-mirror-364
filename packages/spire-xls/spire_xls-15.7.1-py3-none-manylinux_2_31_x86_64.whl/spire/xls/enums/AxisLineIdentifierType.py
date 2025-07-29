from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class AxisLineIdentifierType(Enum):
    """
    Axis line indentifier type.

    """
    AxisLineItself = 0
    MajorGridLine = 1
    MinorGridLine = 2
    WallsOrFloor = 3

