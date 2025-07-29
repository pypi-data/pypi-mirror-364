from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class QueryTableXls (SpireObject) :
    """Represents a query table in an Excel worksheet.
    
    This class encapsulates the properties and methods for managing query tables in Excel.
    Query tables are used to import data from external data sources such as databases,
    text files, web pages, or other data sources into an Excel worksheet.
    """
    @property
    def AdjustColumnWidth(self)->bool:
        """Gets or sets whether column widths are automatically adjusted when refreshing the query table.
        
        When set to True, Excel will automatically adjust the column widths to fit the imported data
        when the query table is refreshed.
        
        Returns:
            bool: True if column widths are automatically adjusted; otherwise, False.
        """
        GetDllLibXls().QueryTableXls_get_AdjustColumnWidth.argtypes=[c_void_p]
        GetDllLibXls().QueryTableXls_get_AdjustColumnWidth.restype=c_bool
        ret = CallCFunction(GetDllLibXls().QueryTableXls_get_AdjustColumnWidth, self.Ptr)
        return ret

    @AdjustColumnWidth.setter
    def AdjustColumnWidth(self, value:bool):
        GetDllLibXls().QueryTableXls_set_AdjustColumnWidth.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().QueryTableXls_set_AdjustColumnWidth, self.Ptr, value)

    @property
    def PreserveFormatting(self)->bool:
        """Gets or sets whether formatting is preserved when refreshing the query table.
        
        When set to True, any manual formatting applied to the query table will be preserved
        when the query table is refreshed with new data.
        
        Returns:
            bool: True if formatting is preserved during refresh; otherwise, False.
        """
        GetDllLibXls().QueryTableXls_get_PreserveFormatting.argtypes=[c_void_p]
        GetDllLibXls().QueryTableXls_get_PreserveFormatting.restype=c_bool
        ret = CallCFunction(GetDllLibXls().QueryTableXls_get_PreserveFormatting, self.Ptr)
        return ret

    @PreserveFormatting.setter
    def PreserveFormatting(self, value:bool):
        GetDllLibXls().QueryTableXls_set_PreserveFormatting.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().QueryTableXls_set_PreserveFormatting, self.Ptr, value)

