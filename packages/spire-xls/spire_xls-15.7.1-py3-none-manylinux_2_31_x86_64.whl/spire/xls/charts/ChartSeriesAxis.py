from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ChartSeriesAxis (  XlsChartSeriesAxis) :
    """

    """
    @property

    def Font(self)->'ExcelFont':
        """
        Returns font used for axis text displaying. Read-only.

        """
        GetDllLibXls().ChartSeriesAxis_get_Font.argtypes=[c_void_p]
        GetDllLibXls().ChartSeriesAxis_get_Font.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSeriesAxis_get_Font, self.Ptr)
        ret = None if intPtr==None else ExcelFont(intPtr)
        return ret


    @property

    def MajorGridLines(self)->'ChartGridLine':
        """
        Returns major gridLines. Read-only.

        """
        GetDllLibXls().ChartSeriesAxis_get_MajorGridLines.argtypes=[c_void_p]
        GetDllLibXls().ChartSeriesAxis_get_MajorGridLines.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSeriesAxis_get_MajorGridLines, self.Ptr)
        ret = None if intPtr==None else ChartGridLine(intPtr)
        return ret


    @property

    def MinorGridLines(self)->'ChartGridLine':
        """
        Returns minor gridLines. Read-only.

        """
        GetDllLibXls().ChartSeriesAxis_get_MinorGridLines.argtypes=[c_void_p]
        GetDllLibXls().ChartSeriesAxis_get_MinorGridLines.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSeriesAxis_get_MinorGridLines, self.Ptr)
        ret = None if intPtr==None else ChartGridLine(intPtr)
        return ret


    @property

    def TitleArea(self)->'ChartTextArea':
        """
        Returns text area for the axis title. Read-only.

        """
        GetDllLibXls().ChartSeriesAxis_get_TitleArea.argtypes=[c_void_p]
        GetDllLibXls().ChartSeriesAxis_get_TitleArea.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSeriesAxis_get_TitleArea, self.Ptr)
        ret = None if intPtr==None else ChartTextArea(intPtr)
        return ret


