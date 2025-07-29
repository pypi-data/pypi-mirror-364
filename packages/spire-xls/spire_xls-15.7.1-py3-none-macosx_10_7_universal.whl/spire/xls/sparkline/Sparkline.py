from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class Sparkline (  ISparkline) :
    """Represents a tiny chart or graphic in a worksheet cell.
    
    A sparkline provides a visual representation of data trends in a compact form.
    Sparklines are useful for showing patterns in a series of values, especially
    patterns that might be hard to spot in traditional charts due to their size.
    """
    @property

    def DataRange(self)->'CellRange':
        """Gets the cell range containing the data for the sparkline.
        
        Returns:
            CellRange: The range of cells containing the source data for the sparkline.
        """
        GetDllLibXls().Sparkline_get_DataRange.argtypes=[c_void_p]
        GetDllLibXls().Sparkline_get_DataRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Sparkline_get_DataRange, self.Ptr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @DataRange.setter
    def DataRange(self, value:'CellRange'):
        """Sets the cell range containing the data for the sparkline.
        
        Args:
            value (CellRange): The range of cells containing the source data for the sparkline.
        """
        GetDllLibXls().Sparkline_set_DataRange.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().Sparkline_set_DataRange, self.Ptr, value.Ptr)

    @property

    def RefRange(self)->'CellRange':
        """Gets the cell range where the sparkline is displayed.
        
        Returns:
            CellRange: The range of cells where the sparkline is displayed.
        """
        GetDllLibXls().Sparkline_get_RefRange.argtypes=[c_void_p]
        GetDllLibXls().Sparkline_get_RefRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Sparkline_get_RefRange, self.Ptr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @RefRange.setter
    def RefRange(self, value:'CellRange'):
        """Sets the cell range where the sparkline is displayed.
        
        Args:
            value (CellRange): The range of cells where the sparkline is displayed.
        """
        GetDllLibXls().Sparkline_set_RefRange.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().Sparkline_set_RefRange, self.Ptr, value.Ptr)

    @property
    def Column(self)->int:
        """Gets the column index of the cell containing the sparkline.
        
        Returns:
            int: The zero-based column index of the cell containing the sparkline.
        """
        GetDllLibXls().Sparkline_get_Column.argtypes=[c_void_p]
        GetDllLibXls().Sparkline_get_Column.restype=c_int
        ret = CallCFunction(GetDllLibXls().Sparkline_get_Column, self.Ptr)
        return ret

    @property
    def Row(self)->int:
        """Gets the row index of the cell containing the sparkline.
        
        Returns:
            int: The zero-based row index of the cell containing the sparkline.
        """
        GetDllLibXls().Sparkline_get_Row.argtypes=[c_void_p]
        GetDllLibXls().Sparkline_get_Row.restype=c_int
        ret = CallCFunction(GetDllLibXls().Sparkline_get_Row, self.Ptr)
        return ret

