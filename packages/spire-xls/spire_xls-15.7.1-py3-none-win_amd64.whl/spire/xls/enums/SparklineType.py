from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class SparklineType(Enum):
    """
    Defined types of Sparkline chart types.

    """
    Stacked = 0
    Column = 1
    Line = 2

