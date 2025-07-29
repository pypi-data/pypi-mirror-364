from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ChartTextArea (  XlsObject, IChartDataLabels) :
    """
    Represents a text area in a chart, providing access to text, formatting, alignment, and label options.
    """
    @property
    def Text(self)->str:
        """
        Gets or sets the text of the chart text area.

        Returns:
            str: The text content.
        """
        GetDllLibXls().ChartTextArea_get_Text.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ChartTextArea_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        GetDllLibXls().ChartTextArea_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ChartTextArea_set_Text, self.Ptr, value)

    @property
    def TextRotationAngle(self)->int:
        """
        Gets or sets the rotation angle of the text in degrees.

        Returns:
            int: The rotation angle in degrees.
        """
        GetDllLibXls().ChartTextArea_get_TextRotationAngle.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_TextRotationAngle.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_TextRotationAngle, self.Ptr)
        return ret

    @TextRotationAngle.setter
    def TextRotationAngle(self, value:int):
        GetDllLibXls().ChartTextArea_set_TextRotationAngle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ChartTextArea_set_TextRotationAngle, self.Ptr, value)

    @property

    def FrameFormat(self)->'IChartFrameFormat':
        """
        Gets the frame format of the chart text area.

        Returns:
            IChartFrameFormat: The frame format object.
        """
        GetDllLibXls().ChartTextArea_get_FrameFormat.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_FrameFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartTextArea_get_FrameFormat, self.Ptr)
        ret = None if intPtr==None else XlsChartFrameFormat(intPtr)
        return ret


    @property

    def BackgroundMode(self)->'ChartBackgroundMode':
        """
        Gets or sets the background mode of the chart text area.

        Returns:
            ChartBackgroundMode: The background mode.
        """
        GetDllLibXls().ChartTextArea_get_BackgroundMode.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_BackgroundMode.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_BackgroundMode, self.Ptr)
        objwraped = ChartBackgroundMode(ret)
        return objwraped

    @BackgroundMode.setter
    def BackgroundMode(self, value:'ChartBackgroundMode'):
        GetDllLibXls().ChartTextArea_set_BackgroundMode.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ChartTextArea_set_BackgroundMode, self.Ptr, value.value)

    @property
    def IsAutoMode(self)->bool:
        """
        Gets a value indicating whether the chart text area is in auto mode.

        Returns:
            bool: True if in auto mode; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_IsAutoMode.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_IsAutoMode.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_IsAutoMode, self.Ptr)
        return ret

    @property

    def Parent(self)->'SpireObject':
        """
        Gets the parent object of the chart text area.

        Returns:
            SpireObject: The parent object.
        """
        GetDllLibXls().ChartTextArea_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartTextArea_get_Parent, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @property
    def IsBold(self)->bool:
        """
        Gets or sets a value indicating whether the text is bold.

        Returns:
            bool: True if bold; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_IsBold.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_IsBold.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_IsBold, self.Ptr)
        return ret

    @IsBold.setter
    def IsBold(self, value:bool):
        GetDllLibXls().ChartTextArea_set_IsBold.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ChartTextArea_set_IsBold, self.Ptr, value)

    @property

    def KnownColor(self)->'ExcelColors':
        """
        Gets or sets the known color of the text.

        Returns:
            ExcelColors: The known color.
        """
        GetDllLibXls().ChartTextArea_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        GetDllLibXls().ChartTextArea_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ChartTextArea_set_KnownColor, self.Ptr, value.value)

    @property

    def Color(self)->'Color':
        """
        Gets or sets the color of the text.

        Returns:
            Color: The color object.
        """
        GetDllLibXls().ChartTextArea_get_Color.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartTextArea_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        GetDllLibXls().ChartTextArea_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ChartTextArea_set_Color, self.Ptr, value.Ptr)


    def SetThemeColor(self ,type:'ThemeColorType',tint:float):
        """
        Sets the theme color for the chart text area.

        Args:
            type (ThemeColorType): The type of theme color.
            tint (float): The tint value for the theme color.
        """
        enumtype:c_int = type.value

        GetDllLibXls().ChartTextArea_SetThemeColor.argtypes=[c_void_p ,c_int,c_double]
        CallCFunction(GetDllLibXls().ChartTextArea_SetThemeColor, self.Ptr, enumtype,tint)

#
#    def GetThemeColor(self ,type:'ThemeColorType&',tint:'Double&')->bool:
#        """
#
#        """
#        intPtrtype:c_void_p = type.Ptr
#        intPtrtint:c_void_p = tint.Ptr
#
#        GetDllLibXls().ChartTextArea_GetThemeColor.argtypes=[c_void_p ,c_void_p,c_void_p]
#        GetDllLibXls().ChartTextArea_GetThemeColor.restype=c_bool
#        ret = CallCFunction(GetDllLibXls().ChartTextArea_GetThemeColor, self.Ptr, intPtrtype,intPtrtint)
#        return ret


    @property
    def IsItalic(self)->bool:
        """
        Gets or sets a value indicating whether the text is italic.

        Returns:
            bool: True if italic; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_IsItalic.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_IsItalic.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_IsItalic, self.Ptr)
        return ret

    @IsItalic.setter
    def IsItalic(self, value:bool):
        GetDllLibXls().ChartTextArea_set_IsItalic.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ChartTextArea_set_IsItalic, self.Ptr, value)

    @property
    def Size(self)->float:
        """
        Gets or sets the font size of the text.

        Returns:
            float: The font size.
        """
        GetDllLibXls().ChartTextArea_get_Size.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_Size.restype=c_double
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_Size, self.Ptr)
        return ret

    @Size.setter
    def Size(self, value:float):
        GetDllLibXls().ChartTextArea_set_Size.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().ChartTextArea_set_Size, self.Ptr, value)

    @property
    def IsStrikethrough(self)->bool:
        """
        Gets or sets a value indicating whether the text is strikethrough.

        Returns:
            bool: True if strikethrough; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_IsStrikethrough.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_IsStrikethrough.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_IsStrikethrough, self.Ptr)
        return ret

    @IsStrikethrough.setter
    def IsStrikethrough(self, value:bool):
        GetDllLibXls().ChartTextArea_set_IsStrikethrough.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ChartTextArea_set_IsStrikethrough, self.Ptr, value)

    @property
    def IsSubscript(self)->bool:
        """
        Gets or sets a value indicating whether the text is subscript.

        Returns:
            bool: True if subscript; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_IsSubscript.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_IsSubscript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_IsSubscript, self.Ptr)
        return ret

    @IsSubscript.setter
    def IsSubscript(self, value:bool):
        GetDllLibXls().ChartTextArea_set_IsSubscript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ChartTextArea_set_IsSubscript, self.Ptr, value)

    @property

    def StrikethroughType(self)->str:
        """
        Gets or sets the strikethrough type of the text.

        Returns:
            str: The strikethrough type.
        """
        GetDllLibXls().ChartTextArea_get_StrikethroughType.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_StrikethroughType.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ChartTextArea_get_StrikethroughType, self.Ptr))
        return ret


    @StrikethroughType.setter
    def StrikethroughType(self, value:str):
        GetDllLibXls().ChartTextArea_set_StrikethroughType.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ChartTextArea_set_StrikethroughType, self.Ptr, value)

    @property
    def IsSuperscript(self)->bool:
        """
        Gets or sets a value indicating whether the text is superscript.

        Returns:
            bool: True if superscript; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_IsSuperscript.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_IsSuperscript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_IsSuperscript, self.Ptr)
        return ret

    @IsSuperscript.setter
    def IsSuperscript(self, value:bool):
        GetDllLibXls().ChartTextArea_set_IsSuperscript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ChartTextArea_set_IsSuperscript, self.Ptr, value)

    @property

    def Underline(self)->'FontUnderlineType':
        """
        Gets or sets the underline type of the text.

        Returns:
            FontUnderlineType: The underline type.
        """
        GetDllLibXls().ChartTextArea_get_Underline.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_Underline.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_Underline, self.Ptr)
        objwraped = FontUnderlineType(ret)
        return objwraped

    @Underline.setter
    def Underline(self, value:'FontUnderlineType'):
        GetDllLibXls().ChartTextArea_set_Underline.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ChartTextArea_set_Underline, self.Ptr, value.value)

    @property

    def FontName(self)->str:
        """
        Gets or sets the font name of the text.

        Returns:
            str: The font name.
        """
        GetDllLibXls().ChartTextArea_get_FontName.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_FontName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ChartTextArea_get_FontName, self.Ptr))
        return ret


    @FontName.setter
    def FontName(self, value:str):
        GetDllLibXls().ChartTextArea_set_FontName.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ChartTextArea_set_FontName, self.Ptr, value)

    @property

    def VerticalAlignment(self)->'FontVertialAlignmentType':
        """
        Gets or sets the vertical alignment of the text.

        Returns:
            FontVertialAlignmentType: The vertical alignment type.
        """
        GetDllLibXls().ChartTextArea_get_VerticalAlignment.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_VerticalAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_VerticalAlignment, self.Ptr)
        objwraped = FontVertialAlignmentType(ret)
        return objwraped

    @VerticalAlignment.setter
    def VerticalAlignment(self, value:'FontVertialAlignmentType'):
        GetDllLibXls().ChartTextArea_set_VerticalAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ChartTextArea_set_VerticalAlignment, self.Ptr, value.value)

    @property
    def IsAutoColor(self)->bool:
        """
        Gets a value indicating whether the text color is set to automatic.

        Returns:
            bool: True if auto color; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_IsAutoColor.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_IsAutoColor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_IsAutoColor, self.Ptr)
        return ret


    def GenerateNativeFont(self)->'Font':
        """
        Generates the native font for the chart text area.

        Returns:
            Font: The native font object.
        """
        GetDllLibXls().ChartTextArea_GenerateNativeFont.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_GenerateNativeFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartTextArea_GenerateNativeFont, self.Ptr)
        ret = None if intPtr==None else Font(intPtr)
        return ret


    def BeginUpdate(self):
        """
        Begins the update process for the chart text area.
        """
        GetDllLibXls().ChartTextArea_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().ChartTextArea_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """
        Ends the update process for the chart text area.
        """
        GetDllLibXls().ChartTextArea_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().ChartTextArea_EndUpdate, self.Ptr)

    @property

    def OColor(self)->'OColor':
        """
        Gets the color object of the text area. Read-only.

        Returns:
            OColor: The color object.
        """
        GetDllLibXls().ChartTextArea_get_OColor.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_OColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartTextArea_get_OColor, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def ParagraphType(self)->'ChartParagraphType':
        """
        Gets or sets the paragraph type of the text area.

        Returns:
            ChartParagraphType: The paragraph type.
        """
        GetDllLibXls().ChartTextArea_get_ParagraphType.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_ParagraphType.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_ParagraphType, self.Ptr)
        objwraped = ChartParagraphType(ret)
        return objwraped

    @ParagraphType.setter
    def ParagraphType(self, value:'ChartParagraphType'):
        GetDllLibXls().ChartTextArea_set_ParagraphType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ChartTextArea_set_ParagraphType, self.Ptr, value.value)

    @property
    def HasTextRotation(self)->bool:
        """
        Gets a value indicating whether the text area has text rotation.

        Returns:
            bool: True if has text rotation; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_HasTextRotation.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_HasTextRotation.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_HasTextRotation, self.Ptr)
        return ret

    @property
    def IsResizeShapeToFitText(self)->bool:
        """
        Gets or sets a value indicating whether the shape is resized to fit the text.

        Returns:
            bool: True if resize to fit text; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_IsResizeShapeToFitText.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_IsResizeShapeToFitText.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_IsResizeShapeToFitText, self.Ptr)
        return ret

    @IsResizeShapeToFitText.setter
    def IsResizeShapeToFitText(self, value:bool):
        GetDllLibXls().ChartTextArea_set_IsResizeShapeToFitText.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ChartTextArea_set_IsResizeShapeToFitText, self.Ptr, value)

    @property
    def IsTextWrapped(self)->bool:
        """
        Gets or sets a value indicating whether the text is wrapped.

        Returns:
            bool: True if text is wrapped; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_IsTextWrapped.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_IsTextWrapped.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_IsTextWrapped, self.Ptr)
        return ret

    @IsTextWrapped.setter
    def IsTextWrapped(self, value:bool):
        GetDllLibXls().ChartTextArea_set_IsTextWrapped.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ChartTextArea_set_IsTextWrapped, self.Ptr, value)

    @property

    def Delimiter(self)->str:
        """
        Gets or sets the delimiter for the text area.

        Returns:
            str: The delimiter string.
        """
        GetDllLibXls().ChartTextArea_get_Delimiter.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_Delimiter.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ChartTextArea_get_Delimiter, self.Ptr))
        return ret


    @Delimiter.setter
    def Delimiter(self, value:str):
        GetDllLibXls().ChartTextArea_set_Delimiter.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ChartTextArea_set_Delimiter, self.Ptr, value)

    @property
    def HasBubbleSize(self)->bool:
        """
        Gets or sets a value indicating whether the bubble size is included in data labels.

        Returns:
            bool: True if bubble size is included; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_HasBubbleSize.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_HasBubbleSize.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_HasBubbleSize, self.Ptr)
        return ret

    @HasBubbleSize.setter
    def HasBubbleSize(self, value:bool):
        GetDllLibXls().ChartTextArea_set_HasBubbleSize.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ChartTextArea_set_HasBubbleSize, self.Ptr, value)

    @property
    def HasCategoryName(self)->bool:
        """
        Gets or sets a value indicating whether the category name is included in data labels.

        Returns:
            bool: True if category name is included; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_HasCategoryName.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_HasCategoryName.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_HasCategoryName, self.Ptr)
        return ret

    @HasCategoryName.setter
    def HasCategoryName(self, value:bool):
        GetDllLibXls().ChartTextArea_set_HasCategoryName.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ChartTextArea_set_HasCategoryName, self.Ptr, value)

    @property
    def HasLegendKey(self)->bool:
        """
        Gets or sets a value indicating whether the legend key is included in data labels.

        Returns:
            bool: True if legend key is included; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_HasLegendKey.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_HasLegendKey.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_HasLegendKey, self.Ptr)
        return ret

    @HasLegendKey.setter
    def HasLegendKey(self, value:bool):
        GetDllLibXls().ChartTextArea_set_HasLegendKey.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ChartTextArea_set_HasLegendKey, self.Ptr, value)

    @property
    def HasPercentage(self)->bool:
        """
        Gets or sets a value indicating whether the percentage is included in data labels.

        Returns:
            bool: True if percentage is included; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_HasPercentage.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_HasPercentage.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_HasPercentage, self.Ptr)
        return ret

    @HasPercentage.setter
    def HasPercentage(self, value:bool):
        GetDllLibXls().ChartTextArea_set_HasPercentage.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ChartTextArea_set_HasPercentage, self.Ptr, value)

    @property
    def HasSeriesName(self)->bool:
        """
        Gets or sets a value indicating whether the series name is included in data labels.

        Returns:
            bool: True if series name is included; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_HasSeriesName.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_HasSeriesName.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_HasSeriesName, self.Ptr)
        return ret

    @HasSeriesName.setter
    def HasSeriesName(self, value:bool):
        GetDllLibXls().ChartTextArea_set_HasSeriesName.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ChartTextArea_set_HasSeriesName, self.Ptr, value)

    @property
    def HasValue(self)->bool:
        """
        Gets or sets a value indicating whether the value is included in data labels.

        Returns:
            bool: True if value is included; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_HasValue.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_HasValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_HasValue, self.Ptr)
        return ret

    @HasValue.setter
    def HasValue(self, value:bool):
        GetDllLibXls().ChartTextArea_set_HasValue.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ChartTextArea_set_HasValue, self.Ptr, value)

    @property

    def Position(self)->'DataLabelPositionType':
        """
        Gets or sets the position of the data labels.

        Returns:
            DataLabelPositionType: The position type.
        """
        GetDllLibXls().ChartTextArea_get_Position.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_Position.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_Position, self.Ptr)
        objwraped = DataLabelPositionType(ret)
        return objwraped

    @Position.setter
    def Position(self, value:'DataLabelPositionType'):
        GetDllLibXls().ChartTextArea_set_Position.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ChartTextArea_set_Position, self.Ptr, value.value)

    @property
    def ShowLeaderLines(self)->bool:
        """
        Gets or sets a value indicating whether to show leader lines for the data labels.

        Returns:
            bool: True if leader lines are shown; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_ShowLeaderLines.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_ShowLeaderLines.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_ShowLeaderLines, self.Ptr)
        return ret

    @ShowLeaderLines.setter
    def ShowLeaderLines(self, value:bool):
        GetDllLibXls().ChartTextArea_set_ShowLeaderLines.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ChartTextArea_set_ShowLeaderLines, self.Ptr, value)

    @property

    def NumberFormat(self)->str:
        """
        Gets or sets the number format for the text area.

        Returns:
            str: The number format string.
        """
        GetDllLibXls().ChartTextArea_get_NumberFormat.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_NumberFormat.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ChartTextArea_get_NumberFormat, self.Ptr))
        return ret


    @NumberFormat.setter
    def NumberFormat(self, value:str):
        GetDllLibXls().ChartTextArea_set_NumberFormat.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ChartTextArea_set_NumberFormat, self.Ptr, value)

    @property
    def HasDataLabels(self)->bool:
        """
        Gets a value indicating whether the text area contains data labels.

        Returns:
            bool: True if contains data labels; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_HasDataLabels.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_HasDataLabels.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_HasDataLabels, self.Ptr)
        return ret

    @property

    def HorizontalAlignType(self)->'HorizontalAlignType':
        """
        Gets or sets the horizontal alignment type of the text area.

        Returns:
            HorizontalAlignType: The horizontal alignment type.
        """
        GetDllLibXls().ChartTextArea_get_HorizontalAlignType.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_HorizontalAlignType.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_HorizontalAlignType, self.Ptr)
        objwraped = HorizontalAlignType(ret)
        return objwraped

    @HorizontalAlignType.setter
    def HorizontalAlignType(self, value:'HorizontalAlignType'):
        GetDllLibXls().ChartTextArea_set_HorizontalAlignType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ChartTextArea_set_HorizontalAlignType, self.Ptr, value.value)

    @property
    def Index(self)->int:
        """
        Gets the index of the text area.

        Returns:
            int: The index value.
        """
        GetDllLibXls().ChartTextArea_get_Index.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_Index.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_Index, self.Ptr)
        return ret

    @property
    def IsShowLabelPercent(self)->bool:
        """
        Gets or sets a value indicating whether to show category label and value as percentage.

        Returns:
            bool: True if show as percentage; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_IsShowLabelPercent.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_IsShowLabelPercent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_IsShowLabelPercent, self.Ptr)
        return ret

    @IsShowLabelPercent.setter
    def IsShowLabelPercent(self, value:bool):
        GetDllLibXls().ChartTextArea_set_IsShowLabelPercent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ChartTextArea_set_IsShowLabelPercent, self.Ptr, value)

    @property
    def IsTrend(self)->bool:
        """
        Gets or sets a value indicating if the current text is assigned to a trend object.

        Returns:
            bool: True if assigned to trend object; otherwise, False.
        """
        GetDllLibXls().ChartTextArea_get_IsTrend.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_IsTrend.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_IsTrend, self.Ptr)
        return ret

    @IsTrend.setter
    def IsTrend(self, value:bool):
        GetDllLibXls().ChartTextArea_set_IsTrend.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ChartTextArea_set_IsTrend, self.Ptr, value)

    @property
    def NumberFormatIndex(self)->int:
        """
        Gets the index to the number format. Read-only.

        Returns:
            int: The number format index.
        """
        GetDllLibXls().ChartTextArea_get_NumberFormatIndex.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_NumberFormatIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_NumberFormatIndex, self.Ptr)
        return ret

    @property

    def ParentWorkbook(self)->'XlsWorkbook':
        """
        Gets the parent workbook of the chart text area.

        Returns:
            XlsWorkbook: The parent workbook object.
        """
        GetDllLibXls().ChartTextArea_get_ParentWorkbook.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_ParentWorkbook.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartTextArea_get_ParentWorkbook, self.Ptr)
        ret = None if intPtr==None else XlsWorkbook(intPtr)
        return ret


    @property
    def X(self)->float:
        """
        Gets or sets the X position of the text area.

        Returns:
            float: The X position.
        """
        GetDllLibXls().ChartTextArea_get_X.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_X.restype=c_float
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_X, self.Ptr)
        return ret

    @X.setter
    def X(self, value:float):
        GetDllLibXls().ChartTextArea_set_X.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibXls().ChartTextArea_set_X, self.Ptr, value)

    @property
    def Y(self)->float:
        """
        Gets or sets the Y position of the text area.

        Returns:
            float: The Y position.
        """
        GetDllLibXls().ChartTextArea_get_Y.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_Y.restype=c_float
        ret = CallCFunction(GetDllLibXls().ChartTextArea_get_Y, self.Ptr)
        return ret

    @Y.setter
    def Y(self, value:float):
        GetDllLibXls().ChartTextArea_set_Y.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibXls().ChartTextArea_set_Y, self.Ptr, value)


    def SetFont(self ,font:'ExcelFont'):
        """
        Sets the font for the chart text area.

        Args:
            font (ExcelFont): The font to set.
        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().ChartTextArea_SetFont.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().ChartTextArea_SetFont, self.Ptr, intPtrfont)

    @property

    def Font(self)->'FontWrapper':
        """
        Gets the font used for the chart text area. Read-only.

        Returns:
            FontWrapper: The font wrapper object.
        """
        GetDllLibXls().ChartTextArea_get_Font.argtypes=[c_void_p]
        GetDllLibXls().ChartTextArea_get_Font.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartTextArea_get_Font, self.Ptr)
        ret = None if intPtr==None else FontWrapper(intPtr)
        return ret


#    @dispatch
#
#    def Clone(self ,parent:SpireObject,fontIndexes:'Dictionary2',dicNewSheetNames:'Dictionary2')->SpireObject:
#        """
#
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrfontIndexes:c_void_p = fontIndexes.Ptr
#        intPtrdicNewSheetNames:c_void_p = dicNewSheetNames.Ptr
#
#        GetDllLibXls().ChartTextArea_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p]
#        GetDllLibXls().ChartTextArea_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().ChartTextArea_Clone, self.Ptr, intPtrparent,intPtrfontIndexes,intPtrdicNewSheetNames)
#        ret = None if intPtr==None else SpireObject(intPtr)
#        return ret
#


    @dispatch

    def Clone(self ,parent:SpireObject)->SpireObject:
        """
        Creates a copy of the current ChartTextArea instance.

        Args:
            parent (SpireObject): The parent object for the cloned text area.
        Returns:
            SpireObject: The cloned ChartTextArea object.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().ChartTextArea_CloneP.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().ChartTextArea_CloneP.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartTextArea_CloneP, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


