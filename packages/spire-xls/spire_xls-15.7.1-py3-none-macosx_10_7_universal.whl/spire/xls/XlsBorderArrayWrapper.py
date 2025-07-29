from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsBorderArrayWrapper (  XlsObject, IBorder) :
    """Represents a wrapper for border array in Excel.
    
    This class provides properties and methods for manipulating borders in Excel,
    including accessing and modifying border colors, line styles, and diagonal lines.
    It extends XlsObject and implements the IBorder interface.
    """
#
#    def GetThemeColor(self ,type:'ThemeColorType&',tint:'Double&')->bool:
#        """
#
#        """
#        intPtrtype:c_void_p = type.Ptr
#        intPtrtint:c_void_p = tint.Ptr
#
#        GetDllLibXls().XlsBorderArrayWrapper_GetThemeColor.argtypes=[c_void_p ,c_void_p,c_void_p]
#        GetDllLibXls().XlsBorderArrayWrapper_GetThemeColor.restype=c_bool
#        ret = CallCFunction(GetDllLibXls().XlsBorderArrayWrapper_GetThemeColor, self.Ptr, intPtrtype,intPtrtint)
#        return ret



    def SetThemeColor(self ,type:'ThemeColorType',tint:float):
        """Sets a theme color for the border.
        
        Args:
            type (ThemeColorType): The theme color type to set.
            tint (float): The tint value to apply to the theme color.
        """
        enumtype:c_int = type.value

        GetDllLibXls().XlsBorderArrayWrapper_SetThemeColor.argtypes=[c_void_p ,c_int,c_double]
        CallCFunction(GetDllLibXls().XlsBorderArrayWrapper_SetThemeColor, self.Ptr, enumtype,tint)

    @property

    def KnownColor(self)->'ExcelColors':
        """Gets or sets the known color of the border.
        
        Returns:
            ExcelColors: An enumeration value representing the Excel color.
        """
        GetDllLibXls().XlsBorderArrayWrapper_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsBorderArrayWrapper_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsBorderArrayWrapper_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        """Sets the known color of the border.
        
        Args:
            value (ExcelColors): An enumeration value representing the Excel color.
        """
        GetDllLibXls().XlsBorderArrayWrapper_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsBorderArrayWrapper_set_KnownColor, self.Ptr, value.value)

    @property

    def OColor(self)->'OColor':
        """Gets the Office color of the border.
        
        Returns:
            OColor: An object representing the Office color.
        """
        GetDllLibXls().XlsBorderArrayWrapper_get_OColor.argtypes=[c_void_p]
        GetDllLibXls().XlsBorderArrayWrapper_get_OColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsBorderArrayWrapper_get_OColor, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def Color(self)->'Color':
        """Gets or sets the color of the border.
        
        Returns:
            Color: A Color object representing the border color.
        """
        GetDllLibXls().XlsBorderArrayWrapper_get_Color.argtypes=[c_void_p]
        GetDllLibXls().XlsBorderArrayWrapper_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsBorderArrayWrapper_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        """Sets the color of the border.
        
        Args:
            value (Color): A Color object representing the border color.
        """
        GetDllLibXls().XlsBorderArrayWrapper_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsBorderArrayWrapper_set_Color, self.Ptr, value.Ptr)

    @property

    def LineStyle(self)->'LineStyleType':
        """Gets or sets the line style of the border.
        
        Returns:
            LineStyleType: An enumeration value representing the line style.
        """
        GetDllLibXls().XlsBorderArrayWrapper_get_LineStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsBorderArrayWrapper_get_LineStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsBorderArrayWrapper_get_LineStyle, self.Ptr)
        objwraped = LineStyleType(ret)
        return objwraped

    @LineStyle.setter
    def LineStyle(self, value:'LineStyleType'):
        """Sets the line style of the border.
        
        Args:
            value (LineStyleType): An enumeration value representing the line style.
        """
        GetDllLibXls().XlsBorderArrayWrapper_set_LineStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsBorderArrayWrapper_set_LineStyle, self.Ptr, value.value)

    @property
    def ShowDiagonalLine(self)->bool:
        """Gets or sets a value indicating whether to show diagonal lines.
        
        Returns:
            bool: True if diagonal lines are shown; otherwise, False.
        """
        GetDllLibXls().XlsBorderArrayWrapper_get_ShowDiagonalLine.argtypes=[c_void_p]
        GetDllLibXls().XlsBorderArrayWrapper_get_ShowDiagonalLine.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsBorderArrayWrapper_get_ShowDiagonalLine, self.Ptr)
        return ret

    @ShowDiagonalLine.setter
    def ShowDiagonalLine(self, value:bool):
        """Sets a value indicating whether to show diagonal lines.
        
        Args:
            value (bool): True to show diagonal lines; otherwise, False.
        """
        GetDllLibXls().XlsBorderArrayWrapper_set_ShowDiagonalLine.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsBorderArrayWrapper_set_ShowDiagonalLine, self.Ptr, value)

