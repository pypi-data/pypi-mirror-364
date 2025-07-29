from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class GroupShape (XlsShape) :
    """

    """
    def UnGroup(self):
        """
        UnGroup current group shape.

        """
        GetDllLibXls().GroupShape_UnGroup.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().GroupShape_UnGroup, self.Ptr)

