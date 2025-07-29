from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from spire.xls.XlsFont import *
from ctypes import *
import abc

class XlsChartDataLabels (  XlsObject, IChartDataLabels, IChartTextArea, IFont, IOptimizedUpdate) :
    """
    Represents a collection of data labels in a chart, providing access to label content, formatting, and positioning options.
    """
    @property
    def HasSeriesName(self)->bool:
        """
        Gets a value indicating whether this instance has series name.
        """
        GetDllLibXls().XlsChartDataLabels_get_HasSeriesName.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_HasSeriesName.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_HasSeriesName, self.Ptr)
        return ret

    @HasSeriesName.setter
    def HasSeriesName(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_HasSeriesName.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_HasSeriesName, self.Ptr, value)

    @property
    def HasCategoryName(self)->bool:
        """
        Gets a value indicating whether this instance has category name.
        """
        GetDllLibXls().XlsChartDataLabels_get_HasCategoryName.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_HasCategoryName.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_HasCategoryName, self.Ptr)
        return ret

    @HasCategoryName.setter
    def HasCategoryName(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_HasCategoryName.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_HasCategoryName, self.Ptr, value)

    @property
    def HasValue(self)->bool:
        """
        Gets a value indicating whether this instance has value.
        """
        GetDllLibXls().XlsChartDataLabels_get_HasValue.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_HasValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_HasValue, self.Ptr)
        return ret

    @HasValue.setter
    def HasValue(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_HasValue.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_HasValue, self.Ptr, value)

    @property
    def HasPercentage(self)->bool:
        """
        Gets a value indicating whether this instance has percentage.
        """
        GetDllLibXls().XlsChartDataLabels_get_HasPercentage.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_HasPercentage.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_HasPercentage, self.Ptr)
        return ret

    @HasPercentage.setter
    def HasPercentage(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_HasPercentage.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_HasPercentage, self.Ptr, value)

    @property
    def HasBubbleSize(self)->bool:
        """
        Gets a value indicating whether this instance has bubble size.
        """
        GetDllLibXls().XlsChartDataLabels_get_HasBubbleSize.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_HasBubbleSize.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_HasBubbleSize, self.Ptr)
        return ret

    @HasBubbleSize.setter
    def HasBubbleSize(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_HasBubbleSize.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_HasBubbleSize, self.Ptr, value)

    @property
    def HasFormula(self)->bool:
        """
        Gets a value indicating whether this instance has formula.
        """
        GetDllLibXls().XlsChartDataLabels_get_HasFormula.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_HasFormula.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_HasFormula, self.Ptr)
        return ret

    @property
    def Delimiter(self)->str:
        """
        Gets or sets the delimiter.
        """
        GetDllLibXls().XlsChartDataLabels_get_Delimiter.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_Delimiter.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartDataLabels_get_Delimiter, self.Ptr))
        return ret

    @Delimiter.setter
    def Delimiter(self, value:str):
        GetDllLibXls().XlsChartDataLabels_set_Delimiter.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_Delimiter, self.Ptr, value)

    @property
    def HasLegendKey(self)->bool:
        """
        Gets a value indicating whether this instance has legend key.
        """
        GetDllLibXls().XlsChartDataLabels_get_HasLegendKey.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_HasLegendKey.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_HasLegendKey, self.Ptr)
        return ret

    @HasLegendKey.setter
    def HasLegendKey(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_HasLegendKey.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_HasLegendKey, self.Ptr, value)

    @property
    def HasManualLayout(self)->bool:
        """
        Indicates whether border formatting object was created. Read-only.
        """
        GetDllLibXls().XlsChartDataLabels_get_HasManualLayout.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_HasManualLayout.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_HasManualLayout, self.Ptr)
        return ret

    @property
    def Position(self)->'DataLabelPositionType':
        """
        Gets or sets the position.
        """
        GetDllLibXls().XlsChartDataLabels_get_Position.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_Position.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_Position, self.Ptr)
        objwraped = DataLabelPositionType(ret)
        return objwraped

    @Position.setter
    def Position(self, value:'DataLabelPositionType'):
        GetDllLibXls().XlsChartDataLabels_set_Position.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_Position, self.Ptr, value.value)

    @property
    def ShowLeaderLines(self)->bool:
        """
        Gets a value indicating whether this instance shows leader lines.
        """
        GetDllLibXls().XlsChartDataLabels_get_ShowLeaderLines.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_ShowLeaderLines.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_ShowLeaderLines, self.Ptr)
        return ret

    @ShowLeaderLines.setter
    def ShowLeaderLines(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_ShowLeaderLines.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_ShowLeaderLines, self.Ptr, value)

    @property
    def NumberFormat(self)->str:
        """
        Gets or sets the number format.
        """
        GetDllLibXls().XlsChartDataLabels_get_NumberFormat.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_NumberFormat.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartDataLabels_get_NumberFormat, self.Ptr))
        return ret

    @NumberFormat.setter
    def NumberFormat(self, value:str):
        GetDllLibXls().XlsChartDataLabels_set_NumberFormat.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_NumberFormat, self.Ptr, value)

    @property
    def IsTextWrapped(self)->bool:
        """
        Gets a value indicating whether this instance is text wrapped.
        """
        GetDllLibXls().XlsChartDataLabels_get_IsTextWrapped.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_IsTextWrapped.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_IsTextWrapped, self.Ptr)
        return ret

    @IsTextWrapped.setter
    def IsTextWrapped(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_IsTextWrapped.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_IsTextWrapped, self.Ptr, value)

    @property
    def IsResizeShapeToFitText(self)->bool:
        """
        Gets a value indicating whether this instance is resize shape to fit text.
        """
        GetDllLibXls().XlsChartDataLabels_get_IsResizeShapeToFitText.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_IsResizeShapeToFitText.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_IsResizeShapeToFitText, self.Ptr)
        return ret

    @IsResizeShapeToFitText.setter
    def IsResizeShapeToFitText(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_IsResizeShapeToFitText.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_IsResizeShapeToFitText, self.Ptr, value)

    @property
    def IsBold(self)->bool:
        """
        True if the font is bold. Read / write Boolean.
        """
        GetDllLibXls().XlsChartDataLabels_get_IsBold.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_IsBold.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_IsBold, self.Ptr)
        return ret

    @IsBold.setter
    def IsBold(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_IsBold.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_IsBold, self.Ptr, value)

    @property
    def KnownColor(self)->'ExcelColors':
        """
        Returns or sets the primary color of the object.
        """
        GetDllLibXls().XlsChartDataLabels_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsChartDataLabels_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_KnownColor, self.Ptr, value.value)

    @property
    def Color(self)->'Color':
        """
        Gets or sets color.
        """
        GetDllLibXls().XlsChartDataLabels_get_Color.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    @Color.setter
    def Color(self, value:'Color'):
        GetDllLibXls().XlsChartDataLabels_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_Color, self.Ptr, value.Ptr)

    def SetThemeColor(self ,type:'ThemeColorType',tint:float):
        """
        Sets the theme color.
        """
        enumtype:c_int = type.value

        GetDllLibXls().XlsChartDataLabels_SetThemeColor.argtypes=[c_void_p ,c_int,c_double]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_SetThemeColor, self.Ptr, enumtype,tint)

    @property
    def IsItalic(self)->bool:
        """
        True if the font style is italic. Read / write Boolean.
        """
        GetDllLibXls().XlsChartDataLabels_get_IsItalic.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_IsItalic.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_IsItalic, self.Ptr)
        return ret

    @IsItalic.setter
    def IsItalic(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_IsItalic.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_IsItalic, self.Ptr, value)

    @property
    def Size(self)->float:
        """
        Returns or sets the size of the font. Read / write Variant.
        """
        GetDllLibXls().XlsChartDataLabels_get_Size.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_Size.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_Size, self.Ptr)
        return ret

    @Size.setter
    def Size(self, value:float):
        GetDllLibXls().XlsChartDataLabels_set_Size.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_Size, self.Ptr, value)

    @property
    def IsStrikethrough(self)->bool:
        """
        True if the font is struck through with a horizontal line. Read / write Boolean
        """
        GetDllLibXls().XlsChartDataLabels_get_IsStrikethrough.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_IsStrikethrough.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_IsStrikethrough, self.Ptr)
        return ret

    @IsStrikethrough.setter
    def IsStrikethrough(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_IsStrikethrough.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_IsStrikethrough, self.Ptr, value)

    @property
    def IsSubscript(self)->bool:
        """
        True if the font is formatted as subscript. False by default. Read / write Boolean.
        """
        GetDllLibXls().XlsChartDataLabels_get_IsSubscript.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_IsSubscript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_IsSubscript, self.Ptr)
        return ret

    @IsSubscript.setter
    def IsSubscript(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_IsSubscript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_IsSubscript, self.Ptr, value)

    @property
    def IsSuperscript(self)->bool:
        """
        True if the font is formatted as superscript. False by default. Read/write Boolean
        """
        GetDllLibXls().XlsChartDataLabels_get_IsSuperscript.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_IsSuperscript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_IsSuperscript, self.Ptr)
        return ret

    @IsSuperscript.setter
    def IsSuperscript(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_IsSuperscript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_IsSuperscript, self.Ptr, value)

    @property
    def Underline(self)->'FontUnderlineType':
        """
        Returns or sets the type of underline applied to the font.
        """
        GetDllLibXls().XlsChartDataLabels_get_Underline.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_Underline.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_Underline, self.Ptr)
        objwraped = FontUnderlineType(ret)
        return objwraped

    @Underline.setter
    def Underline(self, value:'FontUnderlineType'):
        GetDllLibXls().XlsChartDataLabels_set_Underline.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_Underline, self.Ptr, value.value)

    @property
    def FontName(self)->str:
        """
        Returns or sets the font name. Read / write string.
        """
        GetDllLibXls().XlsChartDataLabels_get_FontName.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_FontName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartDataLabels_get_FontName, self.Ptr))
        return ret

    @FontName.setter
    def FontName(self, value:str):
        GetDllLibXls().XlsChartDataLabels_set_FontName.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_FontName, self.Ptr, value)

    @property
    def VerticalAlignment(self)->'FontVertialAlignmentType':
        """
        Returns or sets font vertical alignment.
        """
        GetDllLibXls().XlsChartDataLabels_get_VerticalAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_VerticalAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_VerticalAlignment, self.Ptr)
        objwraped = FontVertialAlignmentType(ret)
        return objwraped

    @VerticalAlignment.setter
    def VerticalAlignment(self, value:'FontVertialAlignmentType'):
        GetDllLibXls().XlsChartDataLabels_set_VerticalAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_VerticalAlignment, self.Ptr, value.value)

    @property
    def IsAutoColor(self)->bool:
        """
        Indicates whether color has automatic color. Read-only.
        """
        GetDllLibXls().XlsChartDataLabels_get_IsAutoColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_IsAutoColor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_IsAutoColor, self.Ptr)
        return ret

    @property
    def StrikethroughType(self)->str:
        """
        Gets or sets the strikethrough type.
        """
        GetDllLibXls().XlsChartDataLabels_get_StrikethroughType.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_StrikethroughType.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartDataLabels_get_StrikethroughType, self.Ptr))
        return ret

    @StrikethroughType.setter
    def StrikethroughType(self, value:str):
        GetDllLibXls().XlsChartDataLabels_set_StrikethroughType.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_StrikethroughType, self.Ptr, value)

    def GenerateNativeFont(self)->'Font':
        """
        Generates a native font.
        """
        GetDllLibXls().XlsChartDataLabels_GenerateNativeFont.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_GenerateNativeFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartDataLabels_GenerateNativeFont, self.Ptr)
        ret = None if intPtr==None else Font(intPtr)
        return ret

    @property
    def Text(self)->str:
        """
        Gets or sets text.
        """
        GetDllLibXls().XlsChartDataLabels_get_Text.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartDataLabels_get_Text, self.Ptr))
        return ret

    @Text.setter
    def Text(self, value:str):
        GetDllLibXls().XlsChartDataLabels_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_Text, self.Ptr, value)

    @property
    def FrameFormat(self)->'IChartFrameFormat':
        """
        Gets or sets the frame format.
        """
        GetDllLibXls().XlsChartDataLabels_get_FrameFormat.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_FrameFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_FrameFormat, self.Ptr)
        ret = None if intPtr==None else XlsChartFrameFormat(intPtr)
        return ret

    @property
    def TextRotationAngle(self)->int:
        """
        Text rotation angle. between -90 and 90.
        """
        GetDllLibXls().XlsChartDataLabels_get_TextRotationAngle.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_TextRotationAngle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_TextRotationAngle, self.Ptr)
        return ret

    @TextRotationAngle.setter
    def TextRotationAngle(self, value:int):
        GetDllLibXls().XlsChartDataLabels_set_TextRotationAngle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_TextRotationAngle, self.Ptr, value)

    @property
    def BackgroundMode(self)->'ChartBackgroundMode':
        """
        Display mode of the background.
        """
        GetDllLibXls().XlsChartDataLabels_get_BackgroundMode.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_BackgroundMode.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_BackgroundMode, self.Ptr)
        objwraped = ChartBackgroundMode(ret)
        return objwraped

    @BackgroundMode.setter
    def BackgroundMode(self, value:'ChartBackgroundMode'):
        GetDllLibXls().XlsChartDataLabels_set_BackgroundMode.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_BackgroundMode, self.Ptr, value.value)

    @property
    def IsAutoMode(self)->bool:
        """
        True if background is set to automatic.
        """
        GetDllLibXls().XlsChartDataLabels_get_IsAutoMode.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_IsAutoMode.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_IsAutoMode, self.Ptr)
        return ret

    @property
    def Format(self)->'XlsChartSerieDataFormat':
        """
        Gets or sets the format.
        """
        GetDllLibXls().XlsChartDataLabels_get_Format.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_Format.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_Format, self.Ptr)
        ret = None if intPtr==None else XlsChartSerieDataFormat(intPtr)
        return ret

    @property
    def Font(self)->'XlsFont':
        """
        Gets or sets the font.
        """
        GetDllLibXls().XlsChartDataLabels_get_Font.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_Font.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_Font, self.Ptr)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret

    @property
    def ValueFromCell(self)->'CellRange':
        """
        Set Range for value. above Excel 2013
        """
        GetDllLibXls().XlsChartDataLabels_get_ValueFromCell.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_ValueFromCell.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_ValueFromCell, self.Ptr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret

    @ValueFromCell.setter
    def ValueFromCell(self, value:'CellRange'):
        GetDllLibXls().XlsChartDataLabels_set_ValueFromCell.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_ValueFromCell, self.Ptr, value.Ptr)

    @property
    def IsWMode(self)->bool:
        """
        false value Specifies that the Width shall be interpreted as the Right of the chart element..
        """
        GetDllLibXls().XlsChartDataLabels_get_IsWMode.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_IsWMode.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_IsWMode, self.Ptr)
        return ret

    @IsWMode.setter
    def IsWMode(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_IsWMode.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_IsWMode, self.Ptr, value)

    @property
    def IsHMode(self)->bool:
        """
        false value Specifies that the Height shall be interpreted as the Bottom of the chart element..
        """
        GetDllLibXls().XlsChartDataLabels_get_IsHMode.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_IsHMode.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_IsHMode, self.Ptr)
        return ret

    @IsHMode.setter
    def IsHMode(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_IsHMode.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_IsHMode, self.Ptr, value)

    @property
    def IsXMode(self)->bool:
        """
        true value Specifies that the X shall be interpreted as the Left of the chart element..
        """
        GetDllLibXls().XlsChartDataLabels_get_IsXMode.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_IsXMode.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_IsXMode, self.Ptr)
        return ret

    @IsXMode.setter
    def IsXMode(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_IsXMode.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_IsXMode, self.Ptr, value)

    @property
    def IsYMode(self)->bool:
        """
        true value Specifies that the Y shall be interpreted as the Top of the chart element..
        """
        GetDllLibXls().XlsChartDataLabels_get_IsYMode.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_IsYMode.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_IsYMode, self.Ptr)
        return ret

    @IsYMode.setter
    def IsYMode(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_IsYMode.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_IsYMode, self.Ptr, value)

    @property
    def X(self)->int:
        """
        X-position of upper-left corner. 1/4000 of chart plot. IsXMode Shall set to True
        """
        GetDllLibXls().XlsChartDataLabels_get_X.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_X.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_X, self.Ptr)
        return ret

    @X.setter
    def X(self, value:int):
        GetDllLibXls().XlsChartDataLabels_set_X.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_X, self.Ptr, value)

    @property
    def Y(self)->int:
        """
        Y-position of upper-left corner. 1/4000 of chart plot. IsYMode Shall set to True
        """
        GetDllLibXls().XlsChartDataLabels_get_Y.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_Y.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_Y, self.Ptr)
        return ret

    @Y.setter
    def Y(self, value:int):
        GetDllLibXls().XlsChartDataLabels_set_Y.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_Y, self.Ptr, value)

    @property
    def TextArea(self)->'XlsChartDataLabelArea':
        """
        Text of area.
        """
        GetDllLibXls().XlsChartDataLabels_get_TextArea.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_TextArea.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_TextArea, self.Ptr)
        ret = None if intPtr==None else XlsChartDataLabelArea(intPtr)
        return ret

    @property
    def HasWedgeCallout(self)->bool:
        """
        Gets a value indicating whether this instance has wedge callout.
        """
        GetDllLibXls().XlsChartDataLabels_get_HasWedgeCallout.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_HasWedgeCallout.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_HasWedgeCallout, self.Ptr)
        return ret

    @HasWedgeCallout.setter
    def HasWedgeCallout(self, value:bool):
        GetDllLibXls().XlsChartDataLabels_set_HasWedgeCallout.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_HasWedgeCallout, self.Ptr, value)

    @property
    def Height(self)->int:
        """
        Y-size. 1/4000 of chart plot. IsHMode Shall set to True
        """
        GetDllLibXls().XlsChartDataLabels_get_Height.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_Height.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_Height, self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:int):
        GetDllLibXls().XlsChartDataLabels_set_Height.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_Height, self.Ptr, value)

    @property
    def Width(self)->int:
        """
        X-size. 1/4000 of chart plot. IsWMode Shall set to True
        """
        GetDllLibXls().XlsChartDataLabels_get_Width.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_Width.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_Width, self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:int):
        GetDllLibXls().XlsChartDataLabels_set_Width.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_set_Width, self.Ptr, value)

    @property
    def Index(self)->int:
        """
        Gets the index.
        """
        GetDllLibXls().XlsChartDataLabels_get_Index.argtypes=[c_void_p]
        GetDllLibXls().XlsChartDataLabels_get_Index.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartDataLabels_get_Index, self.Ptr)
        return ret

    def BeginUpdate(self):
        """
        Begins the update.
        """
        GetDllLibXls().XlsChartDataLabels_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """
        Ends the update.
        """
        GetDllLibXls().XlsChartDataLabels_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsChartDataLabels_EndUpdate, self.Ptr)

