from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class UnknownVariableAction(Enum):
    """
    Defines action that must be taken when meeting unknown variable during template markers processing.

    """
    Exception = 0
    Skip = 1
    ReplaceBlank = 2

