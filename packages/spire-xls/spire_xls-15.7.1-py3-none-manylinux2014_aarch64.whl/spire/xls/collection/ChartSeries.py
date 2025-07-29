from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ChartSeries (  XlsChartSeries) :
    """
    Represents a collection of chart series in a chart.
    """
    @dispatch
    def Add(self ,serieToAdd:ChartSerie)->ChartSerie:
        """
        Adds an existing ChartSerie to the collection.

        Args:
            serieToAdd (ChartSerie): The chart series to add.
        Returns:
            ChartSerie: The added chart series.
        """
        intPtrserieToAdd:c_void_p = serieToAdd.Ptr

        GetDllLibXls().ChartSeries_Add.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().ChartSeries_Add.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSeries_Add, self.Ptr, intPtrserieToAdd)
        ret = None if intPtr==None else ChartSerie(intPtr)
        return ret



    def ClearDataFormats(self ,format:'ChartSerieDataFormat'):
        """
        Clears the data formats for the specified chart series data format.

        Args:
            format (ChartSerieDataFormat): The data format to clear.
        """
        intPtrformat:c_void_p = format.Ptr

        GetDllLibXls().ChartSeries_ClearDataFormats.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().ChartSeries_ClearDataFormats, self.Ptr, intPtrformat)

    @dispatch
    def get_Item(self ,index:int)->ChartSerie:
        """
        Returns a single ChartSerie object from the collection by index.

        Args:
            index (int): The index of the chart series.
        Returns:
            ChartSerie: The chart series at the specified index.
        """
        GetDllLibXls().ChartSeries_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().ChartSeries_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSeries_get_Item, self.Ptr, index)
        ret = None if intPtr==None else ChartSerie(intPtr)
        return ret


    @dispatch
    def get_Item(self ,name:str)->ChartSerie:
        """
        Returns a single ChartSerie object from the collection by name.

        Args:
            name (str): The name of the chart series.
        Returns:
            ChartSerie: The chart series with the specified name.
        """
        
        GetDllLibXls().ChartSeries_get_ItemN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().ChartSeries_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSeries_get_ItemN, self.Ptr, name)
        ret = None if intPtr==None else ChartSerie(intPtr)
        return ret


    @dispatch
    def Add(self)->ChartSerie:
        """
        Adds a new empty ChartSerie to the collection.

        Returns:
            ChartSerie: The newly added chart series.
        """
        GetDllLibXls().ChartSeries_Add1.argtypes=[c_void_p]
        GetDllLibXls().ChartSeries_Add1.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSeries_Add1, self.Ptr)
        ret = None if intPtr==None else ChartSerie(intPtr)
        return ret


    @dispatch
    def Add(self ,name:str)->ChartSerie:
        """
        Adds a new ChartSerie with the specified name to the collection.

        Args:
            name (str): The name of the new chart series.
        Returns:
            ChartSerie: The newly added chart series.
        """
        
        GetDllLibXls().ChartSeries_AddN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().ChartSeries_AddN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSeries_AddN, self.Ptr, name)
        ret = None if intPtr==None else ChartSerie(intPtr)
        return ret


    @dispatch
    def Add(self ,serieType:ExcelChartType)->ChartSerie:
        """
        Adds a new ChartSerie with the specified chart type to the collection.

        Args:
            serieType (ExcelChartType): The type of the chart series.
        Returns:
            ChartSerie: The newly added chart series.
        """
        enumserieType:c_int = serieType.value

        GetDllLibXls().ChartSeries_AddS.argtypes=[c_void_p ,c_int]
        GetDllLibXls().ChartSeries_AddS.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSeries_AddS, self.Ptr, enumserieType)
        ret = None if intPtr==None else ChartSerie(intPtr)
        return ret


    @dispatch
    def Add(self ,name:str,serieType:ExcelChartType)->ChartSerie:
        """
        Adds a new ChartSerie with the specified name and chart type to the collection.

        Args:
            name (str): The name of the new chart series.
            serieType (ExcelChartType): The type of the chart series.
        Returns:
            ChartSerie: The newly added chart series.
        """
        enumserieType:c_int = serieType.value

        GetDllLibXls().ChartSeries_AddNS.argtypes=[c_void_p ,c_void_p,c_int]
        GetDllLibXls().ChartSeries_AddNS.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartSeries_AddNS, self.Ptr, name,enumserieType)
        ret = None if intPtr==None else ChartSerie(intPtr)
        return ret


    @dispatch
    def Add(self ,area:str,isVertical:bool)->int:
        """
        Adds a new chart series based on the specified area and orientation.

        Args:
            area (str): The area reference for the series.
            isVertical (bool): Whether the series is vertical.
        Returns:
            int: The index of the added series.
        """
        
        GetDllLibXls().ChartSeries_AddAI.argtypes=[c_void_p ,c_void_p,c_bool]
        GetDllLibXls().ChartSeries_AddAI.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartSeries_AddAI, self.Ptr, area,isVertical)
        return ret

    @property
    def CategoryData(self)->str:
        """
        Gets or sets the category data for the chart series.

        Returns:
            str: The category data string.
        """
        GetDllLibXls().ChartSeries_get_CategoryData.argtypes=[c_void_p]
        GetDllLibXls().ChartSeries_get_CategoryData.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ChartSeries_get_CategoryData, self.Ptr))
        return ret


    @CategoryData.setter
    def CategoryData(self, value:str):
        GetDllLibXls().ChartSeries_set_CategoryData.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ChartSeries_set_CategoryData, self.Ptr, value)

