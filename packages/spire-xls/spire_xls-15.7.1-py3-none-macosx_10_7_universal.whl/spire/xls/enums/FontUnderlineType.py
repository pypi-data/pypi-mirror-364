from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class FontUnderlineType(Enum):
    """
    Font underline types.

    """
    none = 0
    Single = 1
    Double = 2
    SingleAccounting = 33
    DoubleAccounting = 34

