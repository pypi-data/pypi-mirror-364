from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ChartLegend (  XlsChartLegend) :
    """

    """
    @property

    def TextArea(self)->'ChartTextArea':
        """
        Return text area of legend.

        """
        GetDllLibXls().ChartLegend_get_TextArea.argtypes=[c_void_p]
        GetDllLibXls().ChartLegend_get_TextArea.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartLegend_get_TextArea, self.Ptr)
        ret = None if intPtr==None else ChartTextArea(intPtr)
        return ret


    @property

    def LegendEntries(self)->'ChartLegendEntriesColl':
        """
        Represents legend entries collection. Read only.

        """
        GetDllLibXls().ChartLegend_get_LegendEntries.argtypes=[c_void_p]
        GetDllLibXls().ChartLegend_get_LegendEntries.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartLegend_get_LegendEntries, self.Ptr)
        ret = None if intPtr==None else ChartLegendEntriesColl(intPtr)
        return ret


