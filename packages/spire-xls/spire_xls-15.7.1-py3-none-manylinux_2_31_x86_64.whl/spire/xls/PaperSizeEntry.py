from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class PaperSizeEntry (SpireObject) :
    """

    """
    def Width(self)->float:
        """
        Gets the width of the paper size.

        Returns:
            float: The width of the paper size.
        """
        GetDllLibXls().PaperSizeEntry_Width.argtypes=[c_void_p]
        GetDllLibXls().PaperSizeEntry_Width.restype=c_double
        ret = CallCFunction(GetDllLibXls().PaperSizeEntry_Width, self.Ptr)
        return ret

    def Height(self)->float:
        """
        Gets the height of the paper size.

        Returns:
            float: The height of the paper size.
        """
        GetDllLibXls().PaperSizeEntry_Height.argtypes=[c_void_p]
        GetDllLibXls().PaperSizeEntry_Height.restype=c_double
        ret = CallCFunction(GetDllLibXls().PaperSizeEntry_Height, self.Ptr)
        return ret

