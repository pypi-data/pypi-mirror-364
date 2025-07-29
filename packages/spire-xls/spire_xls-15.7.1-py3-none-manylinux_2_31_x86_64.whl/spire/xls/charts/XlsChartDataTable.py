from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsChartDataTable (  XlsObject, IChartDataTable, IFont, IOptimizedUpdate) :
    """
    Represents the data table of a chart, providing access to borders, background, font, and formatting options.
    """
    @property
    def HasHorzBorder(self)->bool:
        """
        Indicates whether data table has horizontal border.

        """
        GetDllLibXls().XlsChartDataTable_get_HasHorzBorder.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_HasHorzBorder.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataTable_get_HasHorzBorder, self.Ptr)
        return ret

    @HasHorzBorder.setter
    def HasHorzBorder(self, value:bool):
        GetDllLibXls().XlsChartDataTable_set_HasHorzBorder.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataTable_set_HasHorzBorder, self.Ptr, value)

    @property
    def HasVertBorder(self)->bool:
        """
        Indicates whether data table has vertical border.

        """
        GetDllLibXls().XlsChartDataTable_get_HasVertBorder.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_HasVertBorder.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataTable_get_HasVertBorder, self.Ptr)
        return ret

    @HasVertBorder.setter
    def HasVertBorder(self, value:bool):
        GetDllLibXls().XlsChartDataTable_set_HasVertBorder.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataTable_set_HasVertBorder, self.Ptr, value)

    @property
    def HasBorders(self)->bool:
        """
        Indicate whether data table has borders.

        """
        GetDllLibXls().XlsChartDataTable_get_HasBorders.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_HasBorders.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataTable_get_HasBorders, self.Ptr)
        return ret

    @HasBorders.setter
    def HasBorders(self, value:bool):
        GetDllLibXls().XlsChartDataTable_set_HasBorders.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataTable_set_HasBorders, self.Ptr, value)

    @property
    def ShowSeriesKeys(self)->bool:
        """
        Indicates whehter series keys in the data table.

        """
        GetDllLibXls().XlsChartDataTable_get_ShowSeriesKeys.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_ShowSeriesKeys.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataTable_get_ShowSeriesKeys, self.Ptr)
        return ret

    @ShowSeriesKeys.setter
    def ShowSeriesKeys(self, value:bool):
        GetDllLibXls().XlsChartDataTable_set_ShowSeriesKeys.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataTable_set_ShowSeriesKeys, self.Ptr, value)

    @property

    def BackgroundMode(self)->'ChartBackgroundMode':
        """
        Display mode of the background.

        """
        GetDllLibXls().XlsChartDataTable_get_BackgroundMode.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_BackgroundMode.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartDataTable_get_BackgroundMode, self.Ptr)
        objwraped = ChartBackgroundMode(ret)
        return objwraped

    @BackgroundMode.setter
    def BackgroundMode(self, value:'ChartBackgroundMode'):
        GetDllLibXls().XlsChartDataTable_set_BackgroundMode.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartDataTable_set_BackgroundMode, self.Ptr, value.value)

    @property
    def IsBold(self)->bool:
        """
        True if the font is bold. Read / write Boolean.

        """
        GetDllLibXls().XlsChartDataTable_get_IsBold.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_IsBold.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataTable_get_IsBold, self.Ptr)
        return ret

    @IsBold.setter
    def IsBold(self, value:bool):
        GetDllLibXls().XlsChartDataTable_set_IsBold.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataTable_set_IsBold, self.Ptr, value)

    @property

    def KnownColor(self)->'ExcelColors':
        """
        Returns or sets the primary color of the object.

        """
        GetDllLibXls().XlsChartDataTable_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartDataTable_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsChartDataTable_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartDataTable_set_KnownColor, self.Ptr, value.value)

    @property

    def Color(self)->'Color':
        """
        Gets or sets color.

        """
        GetDllLibXls().XlsChartDataTable_get_Color.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartDataTable_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        GetDllLibXls().XlsChartDataTable_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChartDataTable_set_Color, self.Ptr, value.Ptr)


    def SetThemeColor(self ,type:'ThemeColorType',tint:float):
        """

        """
        enumtype:c_int = type.value

        GetDllLibXls().XlsChartDataTable_SetThemeColor.argtypes=[c_void_p ,c_int,c_double]
        CallCFunction(GetDllLibXls().XlsChartDataTable_SetThemeColor, self.Ptr, enumtype,tint)

#
#    def GetThemeColor(self ,type:'ThemeColorType&',tint:'Double&')->bool:
#        """
#
#        """
#        intPtrtype:c_void_p = type.Ptr
#        intPtrtint:c_void_p = tint.Ptr
#
#        GetDllLibXls().XlsChartDataTable_GetThemeColor.argtypes=[c_void_p ,c_void_p,c_void_p]
#        GetDllLibXls().XlsChartDataTable_GetThemeColor.restype=c_bool
#        ret = CallCFunction(GetDllLibXls().XlsChartDataTable_GetThemeColor, self.Ptr, intPtrtype,intPtrtint)
#        return ret


    @property
    def IsItalic(self)->bool:
        """
        True if the font style is italic. Read / write Boolean.

        """
        GetDllLibXls().XlsChartDataTable_get_IsItalic.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_IsItalic.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataTable_get_IsItalic, self.Ptr)
        return ret

    @IsItalic.setter
    def IsItalic(self, value:bool):
        GetDllLibXls().XlsChartDataTable_set_IsItalic.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataTable_set_IsItalic, self.Ptr, value)

    @property
    def Size(self)->float:
        """
        Returns or sets the size of the font. Read / write Variant.

        """
        GetDllLibXls().XlsChartDataTable_get_Size.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_Size.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartDataTable_get_Size, self.Ptr)
        return ret

    @Size.setter
    def Size(self, value:float):
        GetDllLibXls().XlsChartDataTable_set_Size.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartDataTable_set_Size, self.Ptr, value)

    @property
    def IsStrikethrough(self)->bool:
        """
        True if the font is struck through with a horizontal line. Read / write Boolean

        """
        GetDllLibXls().XlsChartDataTable_get_IsStrikethrough.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_IsStrikethrough.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataTable_get_IsStrikethrough, self.Ptr)
        return ret

    @IsStrikethrough.setter
    def IsStrikethrough(self, value:bool):
        GetDllLibXls().XlsChartDataTable_set_IsStrikethrough.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataTable_set_IsStrikethrough, self.Ptr, value)

    @property
    def IsSubscript(self)->bool:
        """
        True if the font is formatted as subscript. False by default. Read / write Boolean.

        """
        GetDllLibXls().XlsChartDataTable_get_IsSubscript.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_IsSubscript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataTable_get_IsSubscript, self.Ptr)
        return ret

    @IsSubscript.setter
    def IsSubscript(self, value:bool):
        GetDllLibXls().XlsChartDataTable_set_IsSubscript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataTable_set_IsSubscript, self.Ptr, value)

    @property
    def IsSuperscript(self)->bool:
        """
        True if the font is formatted as superscript. False by default. Read/write Boolean

        """
        GetDllLibXls().XlsChartDataTable_get_IsSuperscript.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_IsSuperscript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataTable_get_IsSuperscript, self.Ptr)
        return ret

    @IsSuperscript.setter
    def IsSuperscript(self, value:bool):
        GetDllLibXls().XlsChartDataTable_set_IsSuperscript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataTable_set_IsSuperscript, self.Ptr, value)

    @property

    def Underline(self)->'FontUnderlineType':
        """
        Returns or sets the type of underline applied to the font.

        """
        GetDllLibXls().XlsChartDataTable_get_Underline.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_Underline.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartDataTable_get_Underline, self.Ptr)
        objwraped = FontUnderlineType(ret)
        return objwraped

    @Underline.setter
    def Underline(self, value:'FontUnderlineType'):
        GetDllLibXls().XlsChartDataTable_set_Underline.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartDataTable_set_Underline, self.Ptr, value.value)

    @property

    def FontName(self)->str:
        """
        Returns or sets the font name. Read / write string.

        """
        GetDllLibXls().XlsChartDataTable_get_FontName.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_FontName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartDataTable_get_FontName, self.Ptr))
        return ret


    @FontName.setter
    def FontName(self, value:str):
        GetDllLibXls().XlsChartDataTable_set_FontName.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChartDataTable_set_FontName, self.Ptr, value)

    @property

    def VerticalAlignment(self)->'FontVertialAlignmentType':
        """
        Returns or sets font vertical alignment.

        """
        GetDllLibXls().XlsChartDataTable_get_VerticalAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_VerticalAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartDataTable_get_VerticalAlignment, self.Ptr)
        objwraped = FontVertialAlignmentType(ret)
        return objwraped

    @VerticalAlignment.setter
    def VerticalAlignment(self, value:'FontVertialAlignmentType'):
        GetDllLibXls().XlsChartDataTable_set_VerticalAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartDataTable_set_VerticalAlignment, self.Ptr, value.value)

    @property
    def IsAutoColor(self)->bool:
        """
        Indicates whether color has automatic color. Read-only.

        """
        GetDllLibXls().XlsChartDataTable_get_IsAutoColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_IsAutoColor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataTable_get_IsAutoColor, self.Ptr)
        return ret

    @property

    def StrikethroughType(self)->str:
        """

        """
        GetDllLibXls().XlsChartDataTable_get_StrikethroughType.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_get_StrikethroughType.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartDataTable_get_StrikethroughType, self.Ptr))
        return ret


    @StrikethroughType.setter
    def StrikethroughType(self, value:str):
        GetDllLibXls().XlsChartDataTable_set_StrikethroughType.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChartDataTable_set_StrikethroughType, self.Ptr, value)


    def GenerateNativeFont(self)->'Font':
        """

        """
        GetDllLibXls().XlsChartDataTable_GenerateNativeFont.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataTable_GenerateNativeFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartDataTable_GenerateNativeFont, self.Ptr)
        ret = None if intPtr==None else Font(intPtr)
        return ret


    def BeginUpdate(self):
        """

        """
        GetDllLibXls().XlsChartDataTable_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsChartDataTable_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """

        """
        GetDllLibXls().XlsChartDataTable_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsChartDataTable_EndUpdate, self.Ptr)


    def Clone(self ,parent:'SpireObject')->'XlsChartDataTable':
        """

        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsChartDataTable_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsChartDataTable_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartDataTable_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else XlsChartDataTable(intPtr)
        return ret


