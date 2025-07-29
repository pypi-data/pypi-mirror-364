from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ChartsCollection (  XlsChartsCollection) :
    """

    """
    @dispatch

    def get_Item(self ,index:int)->Chart:
        """
        Gets a chart object by item index.

        """
        
        GetDllLibXls().ChartsCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().ChartsCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartsCollection_get_Item, self.Ptr, index)
        ret = None if intPtr==None else Chart(intPtr)
        return ret


    @dispatch

    def get_Item(self ,name:str)->Chart:
        """
        Get a chart object by name.

        """
        
        GetDllLibXls().ChartsCollection_get_ItemN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().ChartsCollection_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartsCollection_get_ItemN, self.Ptr, name)
        ret = None if intPtr==None else Chart(intPtr)
        return ret


    @dispatch

    def Add(self)->ChartSheet:
        """
        Adds a new chart.

        Returns:
            Created chart object.

        """
        GetDllLibXls().ChartsCollection_Add.argtypes=[c_void_p]
        GetDllLibXls().ChartsCollection_Add.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartsCollection_Add, self.Ptr)
        ret = None if intPtr==None else ChartSheet(intPtr)
        return ret


    @dispatch

    def Add(self ,name:str)->ChartSheet:
        """
        Add a new chart with name.

        Args:
            name: chart name.

        Returns:
            Created chart object.

        """
        
        GetDllLibXls().ChartsCollection_AddN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().ChartsCollection_AddN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartsCollection_AddN, self.Ptr, name)
        ret = None if intPtr==None else ChartSheet(intPtr)
        return ret


    @dispatch

    def Add(self ,chart:ChartSheet)->ChartSheet:
        """
        Adds chart to the collection.

        Args:
            chart: Chart to add.

        Returns:
            Added chart object.

        """
        intPtrchart:c_void_p = chart.Ptr

        GetDllLibXls().ChartsCollection_AddC.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().ChartsCollection_AddC.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartsCollection_AddC, self.Ptr, intPtrchart)
        ret = None if intPtr==None else ChartSheet(intPtr)
        return ret



    def Remove(self ,name:str)->'ChartSheet':
        """
        Removes chart object from the collection.

        Args:
            name: Name of the chart to remove.

        """
        
        GetDllLibXls().ChartsCollection_Remove.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().ChartsCollection_Remove.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartsCollection_Remove, self.Ptr, name)
        ret = None if intPtr==None else ChartSheet(intPtr)
        return ret


