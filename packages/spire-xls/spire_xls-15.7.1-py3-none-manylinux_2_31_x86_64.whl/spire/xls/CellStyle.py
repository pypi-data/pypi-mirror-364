from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class CellStyle (  CellStyleObject) :
    """Represents a style for cells in an Excel worksheet.
    
    This class extends CellStyleObject and provides properties and methods for 
    defining and manipulating cell styles in Excel worksheets. It allows for accessing
    and modifying borders, fonts, and interior formatting, as well as cloning styles
    for reuse across multiple cells or worksheets.
    """
    @property

    def Borders(self)->'BordersCollection':
        """
        Returns a Borders collection that represents the borders of a style.

        """
        GetDllLibXls().CellStyle_get_Borders.argtypes=[c_void_p]
        GetDllLibXls().CellStyle_get_Borders.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CellStyle_get_Borders, self.Ptr)
        ret = None if intPtr==None else BordersCollection(intPtr)
        return ret


    @property

    def Font(self)->'ExcelFont':
        """
        Returns a Font object that represents the font of the specified object.

        """
        GetDllLibXls().CellStyle_get_Font.argtypes=[c_void_p]
        GetDllLibXls().CellStyle_get_Font.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CellStyle_get_Font, self.Ptr)
        ret = None if intPtr==None else ExcelFont(intPtr)
        return ret


    @property

    def Interior(self)->'ExcelInterior':
        """
        Returns interior object for extended format.

        """
        GetDllLibXls().CellStyle_get_Interior.argtypes=[c_void_p]
        GetDllLibXls().CellStyle_get_Interior.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CellStyle_get_Interior, self.Ptr)
        ret = None if intPtr==None else ExcelInterior(intPtr)
        return ret


    @dispatch

    def clone(self)->'CellStyle':
        """Creates a copy of the current cell style.
        
        This method creates a new CellStyle object with the same formatting attributes
        as the current style.
        
        Returns:
            CellStyle: A new CellStyle object that is a copy of the current style.
        """
        GetDllLibXls().CellStyle_clone.argtypes=[c_void_p]
        GetDllLibXls().CellStyle_clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CellStyle_clone, self.Ptr)
        ret = None if intPtr==None else CellStyle(intPtr)
        return ret


    @dispatch

    def clone(self ,book)->'CellStyle':
        """Creates a copy of the current cell style in the specified workbook.
        
        This method creates a new CellStyle object with the same formatting attributes
        as the current style, but associated with the specified workbook.
        
        Args:
            book: The workbook to create the cloned style in.
            
        Returns:
            CellStyle: A new CellStyle object that is a copy of the current style.
        """
        intPtrbook:c_void_p = book.Ptr

        GetDllLibXls().CellStyle_cloneB.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().CellStyle_cloneB.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CellStyle_cloneB, self.Ptr, intPtrbook)
        ret = None if intPtr==None else CellStyle(intPtr)
        return ret


