from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class LegendPositionType(Enum):
    """
    Legend placement for charts.

    """
    Bottom = 0
    Corner = 1
    Top = 2
    Right = 3
    Left = 4
    NotDocked = 7

