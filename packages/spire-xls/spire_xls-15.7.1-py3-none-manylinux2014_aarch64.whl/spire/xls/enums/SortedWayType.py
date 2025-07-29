from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class SortedWayType(Enum):
    """
    Represents the algorithm to sort.

    """
    QuickSort = 0
    HeapSort = 1
    InsertionSort = 2

