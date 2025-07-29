from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XLSXBorderJoinType(Enum):
    """
    shape border join type

    """
    none = 0
    Round = 1
    Bevel = 2
    Mitter = 3

