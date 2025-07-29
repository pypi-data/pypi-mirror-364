from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class SortComparsionType(Enum):
    """
    Represents the sort by in the range.

    """
    Values = 0
    BackgroundColor = 1
    FontColor = 2
    Icon = 3

