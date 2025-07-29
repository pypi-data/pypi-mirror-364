from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ChartParagraphType(Enum):
    """
    MS Chart Font Type

    """
    none = 0
    Default = 1
    RichText = 2

