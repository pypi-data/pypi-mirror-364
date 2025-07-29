from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsHPageBreak (  XlsObject) :
    """Represents a horizontal page break in an Excel worksheet.
    
    This class provides properties and methods for manipulating horizontal page breaks
    in Excel worksheets, including position, extent, and type settings. It extends
    the XlsObject class to provide page break specific functionality.
    """
    @property
    def Row(self)->int:
        """Gets the row index where the horizontal page break is located.
        
        Returns:
            int: The zero-based row index of the page break.
        """
        GetDllLibXls().XlsHPageBreak_get_Row.argtypes=[c_void_p]
        GetDllLibXls().XlsHPageBreak_get_Row.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsHPageBreak_get_Row, self.Ptr)
        return ret

    @property

    def Type(self)->'PageBreakType':
        """Gets or sets the type of the page break.
        
        Returns:
            PageBreakType: An enumeration value representing the type of page break.
        """
        GetDllLibXls().XlsHPageBreak_get_Type.argtypes=[c_void_p]
        GetDllLibXls().XlsHPageBreak_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsHPageBreak_get_Type, self.Ptr)
        objwraped = PageBreakType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'PageBreakType'):
        """Sets the type of the page break.
        
        Args:
            value (PageBreakType): An enumeration value representing the type of page break.
        """
        GetDllLibXls().XlsHPageBreak_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsHPageBreak_set_Type, self.Ptr, value.value)

    @property
    def StartColumn(self)->int:
        """Gets or sets the starting column index of this horizontal page break.
        
        Returns:
            int: The zero-based starting column index of the page break.
        """
        GetDllLibXls().XlsHPageBreak_get_StartColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsHPageBreak_get_StartColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsHPageBreak_get_StartColumn, self.Ptr)
        return ret

    @StartColumn.setter
    def StartColumn(self, value:int):
        """Sets the starting column index of this horizontal page break.
        
        Args:
            value (int): The zero-based starting column index of the page break.
        """
        GetDllLibXls().XlsHPageBreak_set_StartColumn.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsHPageBreak_set_StartColumn, self.Ptr, value)

    @property
    def EndColumn(self)->int:
        """Gets or sets the ending column index of this horizontal page break.
        
        Returns:
            int: The zero-based ending column index of the page break.
        """
        GetDllLibXls().XlsHPageBreak_get_EndColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsHPageBreak_get_EndColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsHPageBreak_get_EndColumn, self.Ptr)
        return ret

    @EndColumn.setter
    def EndColumn(self, value:int):
        """Sets the ending column index of this horizontal page break.
        
        Args:
            value (int): The zero-based ending column index of the page break.
        """
        GetDllLibXls().XlsHPageBreak_set_EndColumn.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsHPageBreak_set_EndColumn, self.Ptr, value)

    @property

    def Extent(self)->'PageBreakExtentType':
        """Gets the extent type of the page break.
        
        Returns:
            PageBreakExtentType: An enumeration value representing the extent of the page break.
        """
        GetDllLibXls().XlsHPageBreak_get_Extent.argtypes=[c_void_p]
        GetDllLibXls().XlsHPageBreak_get_Extent.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsHPageBreak_get_Extent, self.Ptr)
        objwraped = PageBreakExtentType(ret)
        return objwraped


    def Clone(self ,parent:'SpireObject')->'XlsHPageBreak':
        """Creates a clone of this horizontal page break.
        
        Args:
            parent (SpireObject): The parent object for the cloned page break.
            
        Returns:
            XlsHPageBreak: A new XlsHPageBreak object that is a copy of this instance.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsHPageBreak_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsHPageBreak_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsHPageBreak_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else XlsHPageBreak(intPtr)
        return ret


