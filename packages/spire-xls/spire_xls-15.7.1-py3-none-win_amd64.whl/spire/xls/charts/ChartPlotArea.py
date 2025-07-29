from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ChartPlotArea (  XlsChartPlotArea) :
    """

    """
    @property

    def Border(self)->'ChartBorder':
        """
        Gets the border of the plot area.

        Returns:
            ChartBorder: The border of the plot area.
        """
        GetDllLibXls().ChartPlotArea_get_Border.argtypes=[c_void_p]
        GetDllLibXls().ChartPlotArea_get_Border.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartPlotArea_get_Border, self.Ptr)
        ret = None if intPtr==None else ChartBorder(intPtr)
        return ret


    @property

    def Interior(self)->'ChartInterior':
        """
        Represents frame interior. Read only

        Returns:
            ChartInterior: The interior of the plot area.
        """
        GetDllLibXls().ChartPlotArea_get_Interior.argtypes=[c_void_p]
        GetDllLibXls().ChartPlotArea_get_Interior.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartPlotArea_get_Interior, self.Ptr)
        ret = None if intPtr==None else ChartInterior(intPtr)
        return ret


    @property

    def Workbook(self)->'Workbook':
        """
        Gets the workbook that contains the plot area.

        Returns:
            Workbook: The workbook that contains the plot area. 
        """
        GetDllLibXls().ChartPlotArea_get_Workbook.argtypes=[c_void_p]
        GetDllLibXls().ChartPlotArea_get_Workbook.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartPlotArea_get_Workbook, self.Ptr)
        ret = None if intPtr==None else Workbook(intPtr)
        return ret


