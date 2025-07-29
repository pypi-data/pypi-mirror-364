from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class CheckState(Enum):
    """
    Specifies check state of the check box.

    """
    Unchecked = 0
    Checked = 1
    Mixed = 2

