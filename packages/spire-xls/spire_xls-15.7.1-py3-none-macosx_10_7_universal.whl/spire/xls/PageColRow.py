from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class PageColRow (SpireObject) :
    """Represents the column and row information for a page in Excel.
    
    This class encapsulates the starting and ending row and column indices for a page
    in an Excel worksheet. It is used to define the boundaries of a page for printing
    and pagination purposes.
    """
    def StartRow(self)->int:
        """Gets the starting row index of the page.
        
        Returns:
            int: The zero-based index of the first row on the page.
        """
        GetDllLibXls().PageColRow_StartRow.argtypes=[c_void_p]
        GetDllLibXls().PageColRow_StartRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().PageColRow_StartRow, self.Ptr)
        return ret

    def EndRow(self)->int:
        """Gets the ending row index of the page.
        
        Returns:
            int: The zero-based index of the last row on the page.
        """
        GetDllLibXls().PageColRow_EndRow.argtypes=[c_void_p]
        GetDllLibXls().PageColRow_EndRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().PageColRow_EndRow, self.Ptr)
        return ret

    def StartCol(self)->int:
        """Gets the starting column index of the page.
        
        Returns:
            int: The zero-based index of the first column on the page.
        """
        GetDllLibXls().PageColRow_StartCol.argtypes=[c_void_p]
        GetDllLibXls().PageColRow_StartCol.restype=c_int
        ret = CallCFunction(GetDllLibXls().PageColRow_StartCol, self.Ptr)
        return ret

    def EndCol(self)->int:
        """Gets the ending column index of the page.
        
        Returns:
            int: The zero-based index of the last column on the page.
        """
        GetDllLibXls().PageColRow_EndCol.argtypes=[c_void_p]
        GetDllLibXls().PageColRow_EndCol.restype=c_int
        ret = CallCFunction(GetDllLibXls().PageColRow_EndCol, self.Ptr)
        return ret

