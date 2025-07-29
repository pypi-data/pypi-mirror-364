from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ExcelQuartileCalculation(Enum):
    """
    It represents Quartile calculation used for Box and Whisker Chart series

    """
    InclusiveMedian = 0
    ExclusiveMedian = 1

