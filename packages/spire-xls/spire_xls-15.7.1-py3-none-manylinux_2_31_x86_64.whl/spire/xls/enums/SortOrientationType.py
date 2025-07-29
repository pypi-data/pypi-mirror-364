from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class SortOrientationType(Enum):
    """
    Represents the sort orientation.

    """
    TopToBottom = 0
    LeftToRight = 1

