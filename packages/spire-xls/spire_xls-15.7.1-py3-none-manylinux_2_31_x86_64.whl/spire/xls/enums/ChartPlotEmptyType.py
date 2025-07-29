from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ChartPlotEmptyType(Enum):
    """
    Chart plot empty type.

    """
    NotPlotted = 0
    Zero = 1
    Interpolated = 2

