from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ChartSerie (  XlsChartSerie) :
    """
    Represents a single data series in a chart, providing access to its data points, labels, values, and formatting.
    """
    @property
    def DataPoints(self)->'ChartDataPointsCollection':
        """
        Gets the data points collection for the chart series. Read-only.

        Returns:
            ChartDataPointsCollection: The collection of data points in the series.
        """
        GetDllLibXls().ChartSerie_get_DataPoints.argtypes=[c_void_p]
        GetDllLibXls().ChartSerie_get_DataPoints.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSerie_get_DataPoints, self.Ptr)
        ret = None if intPtr==None else ChartDataPointsCollection(intPtr)
        return ret


    @property
    def CategoryLabels(self)->'CellRange':
        """
        Gets or sets the category labels for the series.

        Returns:
            CellRange: The cell range representing the category labels.
        """
        GetDllLibXls().ChartSerie_get_CategoryLabels.argtypes=[c_void_p]
        GetDllLibXls().ChartSerie_get_CategoryLabels.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSerie_get_CategoryLabels, self.Ptr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @CategoryLabels.setter
    def CategoryLabels(self, value:'CellRange'):
        GetDllLibXls().ChartSerie_set_CategoryLabels.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ChartSerie_set_CategoryLabels, self.Ptr, value.Ptr)

    @property
    def Bubbles(self)->'CellRange':
        """
        Gets or sets the bubble sizes for the series.

        Returns:
            CellRange: The cell range representing the bubble sizes.
        """
        GetDllLibXls().ChartSerie_get_Bubbles.argtypes=[c_void_p]
        GetDllLibXls().ChartSerie_get_Bubbles.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSerie_get_Bubbles, self.Ptr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @Bubbles.setter
    def Bubbles(self, value:'CellRange'):
        GetDllLibXls().ChartSerie_set_Bubbles.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ChartSerie_set_Bubbles, self.Ptr, value.Ptr)

    @property
    def Values(self)->'IXLSRange':
        """
        Gets or sets the values range for the series.

        Returns:
            IXLSRange: The cell range representing the values of the series.
        """
        GetDllLibXls().ChartSerie_get_Values.argtypes=[c_void_p]
        GetDllLibXls().ChartSerie_get_Values.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSerie_get_Values, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @Values.setter
    def Values(self, value:'IXLSRange'):
        GetDllLibXls().ChartSerie_set_Values.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ChartSerie_set_Values, self.Ptr, value.Ptr)

    @property
    def Format(self)->'ChartSerieDataFormat':
        """
        Gets the format of the series.

        Returns:
            ChartSerieDataFormat: The format settings for the series.
        """
        GetDllLibXls().ChartSerie_get_Format.argtypes=[c_void_p]
        GetDllLibXls().ChartSerie_get_Format.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSerie_get_Format, self.Ptr)
        ret = None if intPtr==None else ChartSerieDataFormat(intPtr)
        return ret


    @property
    def DataFormat(self)->'ChartSerieDataFormat':
        """
        Gets the data format of the series. Read-only.

        Returns:
            ChartSerieDataFormat: The data format settings for the series.
        """
        GetDllLibXls().ChartSerie_get_DataFormat.argtypes=[c_void_p]
        GetDllLibXls().ChartSerie_get_DataFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSerie_get_DataFormat, self.Ptr)
        ret = None if intPtr==None else ChartSerieDataFormat(intPtr)
        return ret



    def GetSerieNameRange(self)->'CellRange':
        """
        Gets the cell range that contains the name of the series.

        Returns:
            CellRange: The cell range containing the series name.
        """
        GetDllLibXls().ChartSerie_GetSerieNameRange.argtypes=[c_void_p]
        GetDllLibXls().ChartSerie_GetSerieNameRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSerie_GetSerieNameRange, self.Ptr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @property
    def DataLabels(self)->'ChartDataLabels':
        """
        Gets the data labels for the series.

        Returns:
            ChartDataLabels: The data labels associated with the series.
        """
        GetDllLibXls().ChartSerie_get_DataLabels.argtypes=[c_void_p]
        GetDllLibXls().ChartSerie_get_DataLabels.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSerie_get_DataLabels, self.Ptr)
        ret = None if intPtr==None else ChartDataLabels(intPtr)
        return ret


