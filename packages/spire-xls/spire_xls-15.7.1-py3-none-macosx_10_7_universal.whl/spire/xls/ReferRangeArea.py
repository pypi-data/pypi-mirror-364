from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ReferRangeArea (SpireObject) :
    """Represents a referenced range area in an Excel worksheet.
    
    This class encapsulates information about a range reference in Excel, including the sheet name,
    start and end positions of the range, and whether it's an external reference. It is typically
    used in formulas and named ranges to identify cell ranges.
    """
    @property
    def IsExternalLink(self)->bool:
        """Gets whether this range reference links to an external workbook.
        
        Returns:
            bool: True if the range reference is to an external workbook; otherwise, False.
        """
        GetDllLibXls().ReferRangeArea_get_IsExternalLink.argtypes=[c_void_p]
        GetDllLibXls().ReferRangeArea_get_IsExternalLink.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ReferRangeArea_get_IsExternalLink, self.Ptr)
        return ret

    @property

    def ExternalFileName(self)->str:
        """Gets the file name of the external workbook when IsExternalLink is True.
        
        Returns:
            str: The file name of the external workbook, or an empty string if not applicable.
        """
        GetDllLibXls().ReferRangeArea_get_ExternalFileName.argtypes=[c_void_p]
        GetDllLibXls().ReferRangeArea_get_ExternalFileName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ReferRangeArea_get_ExternalFileName, self.Ptr))
        return ret


    @property

    def SheetName(self)->str:
        """Gets the name of the worksheet containing the referenced range.
        
        Returns:
            str: The name of the worksheet.
        """
        GetDllLibXls().ReferRangeArea_get_SheetName.argtypes=[c_void_p]
        GetDllLibXls().ReferRangeArea_get_SheetName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ReferRangeArea_get_SheetName, self.Ptr))
        return ret


    @property
    def EndColumn(self)->int:
        """Gets the ending column index of the referenced range.
        
        Returns:
            int: The zero-based index of the last column in the range.
        """
        GetDllLibXls().ReferRangeArea_get_EndColumn.argtypes=[c_void_p]
        GetDllLibXls().ReferRangeArea_get_EndColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().ReferRangeArea_get_EndColumn, self.Ptr)
        return ret

    @property
    def StartColumn(self)->int:
        """Gets the starting column index of the referenced range.
        
        Returns:
            int: The zero-based index of the first column in the range.
        """
        GetDllLibXls().ReferRangeArea_get_StartColumn.argtypes=[c_void_p]
        GetDllLibXls().ReferRangeArea_get_StartColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().ReferRangeArea_get_StartColumn, self.Ptr)
        return ret

    @property
    def EndRow(self)->int:
        """Gets the ending row index of the referenced range.
        
        Returns:
            int: The zero-based index of the last row in the range.
        """
        GetDllLibXls().ReferRangeArea_get_EndRow.argtypes=[c_void_p]
        GetDllLibXls().ReferRangeArea_get_EndRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().ReferRangeArea_get_EndRow, self.Ptr)
        return ret

    @property
    def StartRow(self)->int:
        """Gets the starting row index of the referenced range.
        
        Returns:
            int: The zero-based index of the first row in the range.
        """
        GetDllLibXls().ReferRangeArea_get_StartRow.argtypes=[c_void_p]
        GetDllLibXls().ReferRangeArea_get_StartRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().ReferRangeArea_get_StartRow, self.Ptr)
        return ret

class ListReferRangeAreas (IList[ReferRangeArea]):
    """Represents a collection of ReferRangeArea objects.
    
    This class implements the IList interface for ReferRangeArea objects, providing
    standard collection functionality for working with multiple range references.
    It is typically used to manage multiple range references in formulas or named ranges.
    """
    pass
