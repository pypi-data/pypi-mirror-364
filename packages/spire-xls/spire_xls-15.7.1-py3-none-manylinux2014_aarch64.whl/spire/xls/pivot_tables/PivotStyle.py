from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class PivotStyle (SpireObject) :
    """Represents the style of a PivotTable element.
    
    This class provides functionality for managing the style of elements in a PivotTable,
    including font, borders, and fill properties.
    """
    @property

    def Parent(self)->'PivotTableStyle':
        """Gets the parent PivotTableStyle of this style.
        
        Returns:
            PivotTableStyle: The parent PivotTableStyle object.
        """
        GetDllLibXls().PivotStyle_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().PivotStyle_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().PivotStyle_get_Parent, self.Ptr)
        ret = None if intPtr==None else PivotTableStyle(intPtr)
        return ret


    @property

    def Font(self)->'ExcelFont':
        """Gets the font settings for the PivotTable element.
        
        Returns:
            ExcelFont: The font object containing font settings.
        """
        GetDllLibXls().PivotStyle_get_Font.argtypes=[c_void_p]
        GetDllLibXls().PivotStyle_get_Font.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().PivotStyle_get_Font, self.Ptr)
        ret = None if intPtr==None else ExcelFont(intPtr)
        return ret


    @Font.setter
    def Font(self, value:'ExcelFont'):
        """Sets the font settings for the PivotTable element.
        
        Args:
            value (ExcelFont): The font object containing font settings to apply.
        """
        GetDllLibXls().PivotStyle_set_Font.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().PivotStyle_set_Font, self.Ptr, value.Ptr)

    @property

    def Borders(self)->'XlsBordersCollection':
        """Gets the border settings for the PivotTable element.
        
        Returns:
            XlsBordersCollection: The collection of border objects.
        """
        GetDllLibXls().PivotStyle_get_Borders.argtypes=[c_void_p]
        GetDllLibXls().PivotStyle_get_Borders.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().PivotStyle_get_Borders, self.Ptr)
        ret = None if intPtr==None else XlsBordersCollection(intPtr)
        return ret


    @Borders.setter
    def Borders(self, value:'XlsBordersCollection'):
        """Sets the border settings for the PivotTable element.
        
        Args:
            value (XlsBordersCollection): The collection of border objects to apply.
        """
        GetDllLibXls().PivotStyle_set_Borders.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().PivotStyle_set_Borders, self.Ptr, value.Ptr)

    @property

    def Fill(self)->'XlsFill':
        """Gets the fill settings for the PivotTable element.
        
        Returns:
            XlsFill: The fill object containing fill settings.
        """
        GetDllLibXls().PivotStyle_get_Fill.argtypes=[c_void_p]
        GetDllLibXls().PivotStyle_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().PivotStyle_get_Fill, self.Ptr)
        ret = None if intPtr==None else XlsFill(intPtr)
        return ret


    @Fill.setter
    def Fill(self, value:'XlsFill'):
        """Sets the fill settings for the PivotTable element.
        
        Args:
            value (XlsFill): The fill object containing fill settings to apply.
        """
        GetDllLibXls().PivotStyle_set_Fill.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().PivotStyle_set_Fill, self.Ptr, value.Ptr)

