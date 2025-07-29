from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class PivotGroupByTypes(Enum):
    """
    The groupby types of pivot field.

    """
    Value = 0
    Seconds = 1
    Minutes = 2
    Hours = 3
    Days = 4
    Months = 5
    Quarters = 6
    Years = 7

