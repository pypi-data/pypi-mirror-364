from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class PivotValueFilterType(Enum):
    """

    """
    Equal = 0
    NotEqual = 1
    GreaterThan = 2
    GreaterThanOrEqual = 3
    LessThan = 4
    LessThanOrEqual = 5
    Between = 6
    NotBetween = 7

