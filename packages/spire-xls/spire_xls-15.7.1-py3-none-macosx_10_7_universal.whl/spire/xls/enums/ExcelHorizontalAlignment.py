from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ExcelHorizontalAlignment(Enum):
    """
    Represents different horizontal alignments

    """
    Left = 0
    Center = 1
    Right = 2
    LeftMiddle = 3
    CenterMiddle = 4
    RightMiddle = 5

