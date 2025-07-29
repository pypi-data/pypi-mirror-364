from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ConditionValuePosition(Enum):
    """
    Specifies the position of a condition value in a scale for conditional formatting.
    """
    Third = 2
    Second = 1
    First = 0

