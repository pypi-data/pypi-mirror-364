from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ConditionalFormatScope(Enum):
    """
    Specifies the scope of a conditional format in Excel.
    """
    DataFields = 0
    Intersections = 1
    Selections = 2

