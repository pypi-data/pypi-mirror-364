from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class PagesOrderType(Enum):
    """
    Page order type

    """
    DownThenOver = 0
    OverThenDown = 1

