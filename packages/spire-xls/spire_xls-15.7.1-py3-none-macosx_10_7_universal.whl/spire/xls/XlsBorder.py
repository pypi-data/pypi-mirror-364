from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsBorder (  XlsObject, IBorder) :
    """Represents a border in an Excel worksheet.
    
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
#        GetDllLibXls().XlsBorder_GetThemeColor.argtypes=[c_void_p ,c_void_p,c_void_p]
#        GetDllLibXls().XlsBorder_GetThemeColor.restype=c_bool
#        ret = CallCFunction(GetDllLibXls().XlsBorder_GetThemeColor, self.Ptr, intPtrtype,intPtrtint)
#        return ret



    def SetThemeColor(self ,type:'ThemeColorType',tint:float):
        """Sets a theme color for the border.
        
        Args:
            type (ThemeColorType): The theme color type to set.
            tint (float): The tint value to apply to the theme color.
        """
        enumtype:c_int = type.value

        GetDllLibXls().XlsBorder_SetThemeColor.argtypes=[c_void_p ,c_int,c_double]
        CallCFunction(GetDllLibXls().XlsBorder_SetThemeColor, self.Ptr, enumtype,tint)

    @property

    def KnownColor(self)->'ExcelColors':
        """Gets or sets a predefined Excel color for the border.
        
        Returns:
            ExcelColors: An enumeration value representing the Excel color.
        """
        GetDllLibXls().XlsBorder_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsBorder_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsBorder_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        """Sets a predefined Excel color for the border.
        
        Args:
            value (ExcelColors): An enumeration value representing the Excel color.
        """
        GetDllLibXls().XlsBorder_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsBorder_set_KnownColor, self.Ptr, value.value)

    @property

    def OColor(self)->'OColor':
        """Gets the Office color of the border.
        
        Returns:
            OColor: An object representing the Office color.
        """
        GetDllLibXls().XlsBorder_get_OColor.argtypes=[c_void_p]
        GetDllLibXls().XlsBorder_get_OColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsBorder_get_OColor, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def Color(self)->'Color':
        """Gets or sets the primary color of the border.
        
        Use the RGB function to create a color value.
        
        Returns:
            Color: A Color object representing the border color.
        """
        GetDllLibXls().XlsBorder_get_Color.argtypes=[c_void_p]
        GetDllLibXls().XlsBorder_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsBorder_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        """Sets the primary color of the border.
        
        Args:
            value (Color): A Color object representing the border color.
        """
        GetDllLibXls().XlsBorder_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsBorder_set_Color, self.Ptr, value.Ptr)

    @property

    def LineStyle(self)->'LineStyleType':
        """Gets or sets the line style for the border.
        
        Returns:
            LineStyleType: An enumeration value representing the line style.
        """
        GetDllLibXls().XlsBorder_get_LineStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsBorder_get_LineStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsBorder_get_LineStyle, self.Ptr)
        objwraped = LineStyleType(ret)
        return objwraped

    @LineStyle.setter
    def LineStyle(self, value:'LineStyleType'):
        """Sets the line style for the border.
        
        Args:
            value (LineStyleType): An enumeration value representing the line style.
        """
        GetDllLibXls().XlsBorder_set_LineStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsBorder_set_LineStyle, self.Ptr, value.value)

    @property
    def ShowDiagonalLine(self)->bool:
        """Gets or sets a value indicating whether to show diagonal lines.
        
        Returns:
            bool: True if diagonal lines are shown; otherwise, False.
        """
        GetDllLibXls().XlsBorder_get_ShowDiagonalLine.argtypes=[c_void_p]
        GetDllLibXls().XlsBorder_get_ShowDiagonalLine.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsBorder_get_ShowDiagonalLine, self.Ptr)
        return ret

    @ShowDiagonalLine.setter
    def ShowDiagonalLine(self, value:bool):
        """Sets a value indicating whether to show diagonal lines.
        
        Args:
            value (bool): True to show diagonal lines; otherwise, False.
        """
        GetDllLibXls().XlsBorder_set_ShowDiagonalLine.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsBorder_set_ShowDiagonalLine, self.Ptr, value)

    @property

    def BorderIndex(self)->'BordersLineType':
        """Gets the border index indicating which side of the cell this border represents.
        
        Returns:
            BordersLineType: An enumeration value representing the border position.
        """
        GetDllLibXls().XlsBorder_get_BorderIndex.argtypes=[c_void_p]
        GetDllLibXls().XlsBorder_get_BorderIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsBorder_get_BorderIndex, self.Ptr)
        objwraped = BordersLineType(ret)
        return objwraped

    @staticmethod

    def ColorToExcelColor(color:'ExcelColors')->'ExcelColors':
        """Converts a color to an Excel color.
        
        Args:
            color (ExcelColors): The color to convert.
            
        Returns:
            ExcelColors: The converted Excel color.
        """
        enumcolor:c_int = color.value

        GetDllLibXls().XlsBorder_ColorToExcelColor.argtypes=[ c_int]
        GetDllLibXls().XlsBorder_ColorToExcelColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsBorder_ColorToExcelColor,  enumcolor)
        objwraped = ExcelColors(ret)
        return objwraped


    def CopyFrom(self ,baseBorder:'IBorder'):
        """Copies properties from another border.
        
        Args:
            baseBorder (IBorder): The source border to copy properties from.
        """
        intPtrbaseBorder:c_void_p = baseBorder.Ptr

        GetDllLibXls().XlsBorder_CopyFrom.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsBorder_CopyFrom, self.Ptr, intPtrbaseBorder)


    def setLineStyleAndColor(self ,borderLine:'LineStyleType',borderColor:'ExcelColors'):
        """Sets both the line style and color of the border in a single operation.
        
        Args:
            borderLine (LineStyleType): The line style to set.
            borderColor (ExcelColors): The color to set.
        """
        enumborderLine:c_int = borderLine.value
        enumborderColor:c_int = borderColor.value

        GetDllLibXls().XlsBorder_setLineStyleAndColor.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsBorder_setLineStyleAndColor, self.Ptr, enumborderLine,enumborderColor)

