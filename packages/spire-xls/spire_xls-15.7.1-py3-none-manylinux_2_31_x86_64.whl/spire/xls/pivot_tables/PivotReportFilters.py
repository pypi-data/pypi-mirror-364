from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class PivotReportFilters (SpireObject) :
    """Collection of report filters in a PivotTable.
    
    This class represents a collection of report filters (page filters) in a PivotTable
    and provides methods to add, remove, and access filters in the collection.
    """
    @dispatch
    def get_Item(self ,index:int)->PivotReportFilter:
        """Gets the report filter at the specified index.
        
        Args:
            index (int): The zero-based index of the report filter to retrieve.
            
        Returns:
            PivotReportFilter: The report filter at the specified index.
        """
        
        GetDllLibXls().PivotReportFilters_get_ItemI.argtypes=[c_void_p ,c_int]
        GetDllLibXls().PivotReportFilters_get_ItemI.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().PivotReportFilters_get_ItemI, self.Ptr, index)
        ret = None if intPtr==None else PivotReportFilter(intPtr)
        return ret

    @dispatch
    def get_Item(self ,name:str)->PivotReportFilter:
        """Gets the report filter with the specified name.
        
        Args:
            name (str): The name of the report filter to retrieve.
            
        Returns:
            PivotReportFilter: The report filter with the specified name.
        """
        
        GetDllLibXls().PivotReportFilters_get_Item.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().PivotReportFilters_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().PivotReportFilters_get_Item, self.Ptr, name)
        ret = None if intPtr==None else PivotReportFilter(intPtr)
        return ret



    def RemoveAt(self ,index:int):
        """Removes the report filter at the specified index.
        
        Args:
            index (int): The zero-based index of the report filter to remove.
        """
        
        GetDllLibXls().PivotReportFilters_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().PivotReportFilters_RemoveAt, self.Ptr, index)

    def Clear(self):
        """Removes all report filters from the collection.
        """
        GetDllLibXls().PivotReportFilters_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().PivotReportFilters_Clear, self.Ptr)


    def Remove(self ,item:'PivotReportFilter')->bool:
        """Removes the specified report filter from the collection.
        
        Args:
            item (PivotReportFilter): The report filter to remove.
            
        Returns:
            bool: True if the report filter was successfully removed; otherwise, False.
        """
        intPtritem:c_void_p = item.Ptr

        GetDllLibXls().PivotReportFilters_Remove.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().PivotReportFilters_Remove.restype=c_bool
        ret = CallCFunction(GetDllLibXls().PivotReportFilters_Remove, self.Ptr, intPtritem)
        return ret


    def Add(self ,item:'PivotReportFilter'):
        """Adds a report filter to the collection.
        
        Args:
            item (PivotReportFilter): The report filter to add.
        """
        intPtritem:c_void_p = item.Ptr

        GetDllLibXls().PivotReportFilters_Add.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().PivotReportFilters_Add, self.Ptr, intPtritem)

