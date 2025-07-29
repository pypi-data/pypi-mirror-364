from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class AddInFunctionsCollection (  XlsAddInFunctionsCollection) :
    """
    Represents a collection of Add-In functions in the workbook.
    """

    def get_Item(self ,index:int)->'ExcelAddInFunction':
        """
        Gets the Add-In function at the specified index.

        Args:
            index (int): The index of the Add-In function.

        Returns:
            ExcelAddInFunction: The Add-In function at the specified index.
        """
        
        GetDllLibXls().AddInFunctionsCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().AddInFunctionsCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().AddInFunctionsCollection_get_Item, self.Ptr, index)
        ret = None if intPtr==None else ExcelAddInFunction(intPtr)
        return ret


