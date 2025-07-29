from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class AlertStyleType(Enum):
    """
    Possible error style values:

    """
    Stop = 0
    Warning = 1
    Info = 2

