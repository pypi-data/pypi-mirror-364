from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class HistogramAxisFormat (SpireObject) :
    """
    Class provide the options for Histogram and Pareto Chart axis

    """

    def Equals(self ,obj:'SpireObject')->bool:
        """
        Check for the equals an object

        Args:
            obj: input another histogram object

        Returns:
            the boolean value indicates whether the objects are equal or not.

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibXls().HistogramAxisFormat_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().HistogramAxisFormat_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibXls().HistogramAxisFormat_Equals, self.Ptr, intPtrobj)
        return ret

