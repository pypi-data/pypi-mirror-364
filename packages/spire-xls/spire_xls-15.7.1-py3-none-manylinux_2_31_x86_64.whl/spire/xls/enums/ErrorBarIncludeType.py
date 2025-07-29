from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ErrorBarIncludeType(Enum):
    """
    Represents error bar include values.

    """
    none = 0
    Both = 1
    Plus = 2
    Minus = 3

