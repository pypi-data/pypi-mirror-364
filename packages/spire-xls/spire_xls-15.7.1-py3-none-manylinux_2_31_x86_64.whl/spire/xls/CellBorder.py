from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class CellBorder (  IBorder, IExcelApplication) :
    """Represents a border of a cell or range of cells in an Excel worksheet.
    
    This class implements IBorder and IExcelApplication interfaces, providing properties
    and methods for manipulating cell borders, including colors, line styles, and
    diagonal lines. It allows for customizing the appearance of cell borders in Excel worksheets.
    """

#
#    def GetThemeColor(self ,type:'ThemeColorType&',tint:'Double&')->bool:
#        """
#
#        """
#        intPtrtype:c_void_p = type.Ptr
#        intPtrtint:c_void_p = tint.Ptr
#
#        GetDllLibXls().CellBorder_GetThemeColor.argtypes=[c_void_p ,c_void_p,c_void_p]
#        GetDllLibXls().CellBorder_GetThemeColor.restype=c_bool
#        ret = CallCFunction(GetDllLibXls().CellBorder_GetThemeColor, self.Ptr, intPtrtype,intPtrtint)
#        return ret



    def SetThemeColor(self ,type:'ThemeColorType',tint:float):
        """Sets the theme color for the border.
        
        This method applies a theme color to the border, with an optional tint value
        to lighten or darken the theme color.
        
        Args:
            type (ThemeColorType): The theme color type to apply to the border.
            tint (float): A value between -1.0 and 1.0 that lightens or darkens the theme color.
                          Positive values lighten, negative values darken.
        """
        enumtype:c_int = type.value

        GetDllLibXls().CellBorder_SetThemeColor.argtypes=[c_void_p ,c_int,c_double]
        CallCFunction(GetDllLibXls().CellBorder_SetThemeColor, self.Ptr, enumtype,tint)

    @property

    def KnownColor(self)->'ExcelColors':
        """
        Returns or sets a ExcelColors value that represents the color of the border

        """
        GetDllLibXls().CellBorder_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().CellBorder_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().CellBorder_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        GetDllLibXls().CellBorder_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().CellBorder_set_KnownColor, self.Ptr, value.value)

    @property

    def Color(self)->'Color':
        """
        Returns or sets the primary color of the object, as shown in the table in the remarks section. Use the RGB function to create a color value. Read/write Color.

        """
        GetDllLibXls().CellBorder_get_Color.argtypes=[c_void_p]
        GetDllLibXls().CellBorder_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CellBorder_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        GetDllLibXls().CellBorder_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().CellBorder_set_Color, self.Ptr, value.Ptr)

    @property

    def OColor(self)->'OColor':
        """
        Returns or sets the primary color of the object. Read/write ExcelColors.

        """
        GetDllLibXls().CellBorder_get_OColor.argtypes=[c_void_p]
        GetDllLibXls().CellBorder_get_OColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CellBorder_get_OColor, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def LineStyle(self)->'LineStyleType':
        """
        Returns or sets the line style for the border. Read/write LineStyleType.

        """
        GetDllLibXls().CellBorder_get_LineStyle.argtypes=[c_void_p]
        GetDllLibXls().CellBorder_get_LineStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().CellBorder_get_LineStyle, self.Ptr)
        objwraped = LineStyleType(ret)
        return objwraped

    @LineStyle.setter
    def LineStyle(self, value:'LineStyleType'):
        GetDllLibXls().CellBorder_set_LineStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().CellBorder_set_LineStyle, self.Ptr, value.value)

    @property
    def ShowDiagonalLine(self)->bool:
        """
        Indicates whether shows diagonal line.

        """
        GetDllLibXls().CellBorder_get_ShowDiagonalLine.argtypes=[c_void_p]
        GetDllLibXls().CellBorder_get_ShowDiagonalLine.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellBorder_get_ShowDiagonalLine, self.Ptr)
        return ret

    @ShowDiagonalLine.setter
    def ShowDiagonalLine(self, value:bool):
        GetDllLibXls().CellBorder_set_ShowDiagonalLine.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellBorder_set_ShowDiagonalLine, self.Ptr, value)

    @property

    def Parent(self)->'SpireObject':
        """

        """
        GetDllLibXls().CellBorder_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().CellBorder_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CellBorder_get_Parent, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def CopyFrom(self ,srcBorder:'CellBorder'):
        """
        Copies styles from source border.

        Args:
            srcBorder: source border.

        """
        intPtrsrcBorder:c_void_p = srcBorder.Ptr

        GetDllLibXls().CellBorder_CopyFrom.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().CellBorder_CopyFrom, self.Ptr, intPtrsrcBorder)

