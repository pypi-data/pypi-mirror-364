from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class AutoFormatOptions(Enum):
    """
    Represents auto format options.

    """
    Number = 1
    Border = 2
    Font = 4
    Patterns = 8
    Alignment = 16
    Width_Height = 32
    none = 0
    All = 63

