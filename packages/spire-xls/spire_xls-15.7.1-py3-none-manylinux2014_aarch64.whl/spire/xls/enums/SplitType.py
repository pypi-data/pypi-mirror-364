from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class SplitType(Enum):
    """
    Split type.

    """
    Position = 0
    Value = 1
    Percent = 2
    Custom = 3

