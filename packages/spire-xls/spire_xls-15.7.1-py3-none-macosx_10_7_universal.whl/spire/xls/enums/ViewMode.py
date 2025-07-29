from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ViewMode(Enum):
    """
    Defines the view setting of the sheet.

    """
    Normal = 0
    Preview = 1
    Layout = 2

