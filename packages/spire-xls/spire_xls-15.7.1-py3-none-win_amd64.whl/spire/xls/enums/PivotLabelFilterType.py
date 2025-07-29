from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class PivotLabelFilterType(Enum):
    """

    """
    Equal = 0
    NotEqual = 1
    GreaterThan = 2
    GreaterThanOrEqual = 3
    LessThan = 4
    LessThanOrEqual = 5
    BeginWith = 6
    NotBeginWith = 7
    EndWith = 8
    NotEndWith = 9
    Contain = 10
    NotContain = 11
    Between = 12
    NotBetween = 13

