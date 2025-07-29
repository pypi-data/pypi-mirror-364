from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ConditionalFormatWrapper (  CommonWrapper, IOptimizedUpdate, IConditionalFormat, IExcelApplication) :
    """
    Represents a conditional format and its properties for a worksheet or range.
    """

    @property
    def DxfId(self)->int:
        """
        Gets or sets the differential formatting (DXF) identifier.

        Returns:
            int: The DXF identifier.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_DxfId.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_DxfId.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_DxfId, self.Ptr)
        return ret

    @DxfId.setter
    def DxfId(self, value:int):
        """
        Sets the differential formatting (DXF) identifier.

        Args:
            value (int): The DXF identifier.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_DxfId.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_DxfId, self.Ptr, value)

    @property
    def Parent(self)->'SpireObject':
        """
        Gets the parent object of the conditional format.

        Returns:
            SpireObject: The parent object.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_Parent, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret

    @property
    def Priority(self)->int:
        """
        Gets or sets the priority of the conditional format.

        Returns:
            int: The priority value.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_Priority.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_Priority.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_Priority, self.Ptr)
        return ret

    @Priority.setter
    def Priority(self, value:int):
        """
        Sets the priority of the conditional format.

        Args:
            value (int): The priority value.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_Priority.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_Priority, self.Ptr, value)

    @property
    def TopBottom(self)->'TopBottom':
        """
        Gets the TopBottom rule for the conditional format.

        Returns:
            TopBottom: The TopBottom rule object.
        """
        from ..TopBottom import TopBottom
        GetDllLibXls().ConditionalFormatWrapper_get_TopBottom.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_TopBottom.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_TopBottom, self.Ptr)
        ret = None if intPtr==None else TopBottom(intPtr)
        return ret

    @property
    def Average(self)->'Average':
        """
        Gets the Average rule for the conditional format.

        Returns:
            Average: The Average rule object.
        """
        from ..Average import Average
        GetDllLibXls().ConditionalFormatWrapper_get_Average.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_Average.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_Average, self.Ptr)
        ret = None if intPtr==None else Average(intPtr)
        return ret

    @property
    def FormatType(self)->'ConditionalFormatType':
        """
        Gets or sets the type of the conditional format.

        Returns:
            ConditionalFormatType: The format type.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_FormatType.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_FormatType.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_FormatType, self.Ptr)
        objwraped = ConditionalFormatType(ret)
        return objwraped

    @FormatType.setter
    def FormatType(self, value:'ConditionalFormatType'):
        """
        Sets the type of the conditional format.

        Args:
            value (ConditionalFormatType): The format type.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_FormatType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_FormatType, self.Ptr, value.value)

    @property
    def StopIfTrue(self)->bool:
        """
        Gets or sets whether to stop evaluating further rules if this rule evaluates to true.

        Returns:
            bool: True to stop if true; otherwise, False.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_StopIfTrue.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_StopIfTrue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_StopIfTrue, self.Ptr)
        return ret

    @StopIfTrue.setter
    def StopIfTrue(self, value:bool):
        """
        Sets whether to stop evaluating further rules if this rule evaluates to true.

        Args:
            value (bool): True to stop if true; otherwise, False.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_StopIfTrue.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_StopIfTrue, self.Ptr, value)

    @property
    def Operator(self)->'ComparisonOperatorType':
        """
        Gets or sets the comparison operator type for the conditional format.

        Returns:
            ComparisonOperatorType: The comparison operator type.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_Operator.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_Operator.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_Operator, self.Ptr)
        objwraped = ComparisonOperatorType(ret)
        return objwraped

    @Operator.setter
    def Operator(self, value:'ComparisonOperatorType'):
        """
        Sets the comparison operator type for the conditional format.

        Args:
            value (ComparisonOperatorType): The comparison operator type.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_Operator.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_Operator, self.Ptr, value.value)

    @property
    def IsBold(self)->bool:
        """
        Gets or sets whether the font is bold in the conditional format.

        Returns:
            bool: True if bold; otherwise, False.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_IsBold.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_IsBold.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_IsBold, self.Ptr)
        return ret

    @IsBold.setter
    def IsBold(self, value:bool):
        """
        Sets whether the font is bold in the conditional format.

        Args:
            value (bool): True if bold; otherwise, False.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_IsBold.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_IsBold, self.Ptr, value)

    @property
    def IsItalic(self)->bool:
        """
        Gets or sets whether the font is italic in the conditional format.

        Returns:
            bool: True if italic; otherwise, False.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_IsItalic.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_IsItalic.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_IsItalic, self.Ptr)
        return ret

    @IsItalic.setter
    def IsItalic(self, value:bool):
        """
        Sets whether the font is italic in the conditional format.

        Args:
            value (bool): True if italic; otherwise, False.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_IsItalic.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_IsItalic, self.Ptr, value)

    @property
    def FontKnownColor(self)->'ExcelColors':
        """
        Gets or sets the known color of the font in the conditional format.

        Returns:
            ExcelColors: The known color of the font.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_FontKnownColor.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_FontKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_FontKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @FontKnownColor.setter
    def FontKnownColor(self, value:'ExcelColors'):
        """
        Sets the known color of the font in the conditional format.

        Args:
            value (ExcelColors): The known color of the font.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_FontKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_FontKnownColor, self.Ptr, value.value)

    @property
    def FontColor(self)->'Color':
        """
        Gets or sets the color of the font in the conditional format.

        Returns:
            Color: The font color.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_FontColor.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_FontColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_FontColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    @FontColor.setter
    def FontColor(self, value:'Color'):
        """
        Sets the color of the font in the conditional format.

        Args:
            value (Color): The font color.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_FontColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_FontColor, self.Ptr, value.Ptr)

    @property
    def Underline(self)->'FontUnderlineType':
        """
        Gets or sets the underline type for the font in the conditional format.

        Returns:
            FontUnderlineType: The underline type.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_Underline.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_Underline.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_Underline, self.Ptr)
        objwraped = FontUnderlineType(ret)
        return objwraped

    @Underline.setter
    def Underline(self, value:'FontUnderlineType'):
        """
        Sets the underline type for the font in the conditional format.

        Args:
            value (FontUnderlineType): The underline type.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_Underline.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_Underline, self.Ptr, value.value)

    @property
    def IsStrikeThrough(self)->bool:
        """
        Gets or sets whether the font is striked through in the conditional format.

        Returns:
            bool: True if striked through; otherwise, False.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_IsStrikeThrough.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_IsStrikeThrough.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_IsStrikeThrough, self.Ptr)
        return ret

    @IsStrikeThrough.setter
    def IsStrikeThrough(self, value:bool):
        """
        Sets whether the font is striked through in the conditional format.

        Args:
            value (bool): True if striked through; otherwise, False.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_IsStrikeThrough.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_IsStrikeThrough, self.Ptr, value)

    @property
    def LeftBorderKnownColor(self)->'ExcelColors':
        """
        Gets or sets the known color of the left border in the conditional format.

        Returns:
            ExcelColors: The known color of the left border.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_LeftBorderKnownColor.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_LeftBorderKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_LeftBorderKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @LeftBorderKnownColor.setter
    def LeftBorderKnownColor(self, value:'ExcelColors'):
        """
        Sets the known color of the left border in the conditional format.

        Args:
            value (ExcelColors): The known color of the left border.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_LeftBorderKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_LeftBorderKnownColor, self.Ptr, value.value)

    @property
    def LeftBorderColor(self)->'Color':
        """
        Gets or sets the color of the left border in the conditional format.

        Returns:
            Color: The color of the left border.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_LeftBorderColor.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_LeftBorderColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_LeftBorderColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    @LeftBorderColor.setter
    def LeftBorderColor(self, value:'Color'):
        """
        Sets the color of the left border in the conditional format.

        Args:
            value (Color): The color of the left border.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_LeftBorderColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_LeftBorderColor, self.Ptr, value.Ptr)

    @property
    def LeftBorderStyle(self)->'LineStyleType':
        """
        Gets or sets the style of the left border in the conditional format.

        Returns:
            LineStyleType: The style of the left border.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_LeftBorderStyle.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_LeftBorderStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_LeftBorderStyle, self.Ptr)
        objwraped = LineStyleType(ret)
        return objwraped

    @LeftBorderStyle.setter
    def LeftBorderStyle(self, value:'LineStyleType'):
        """
        Sets the style of the left border in the conditional format.

        Args:
            value (LineStyleType): The style of the left border.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_LeftBorderStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_LeftBorderStyle, self.Ptr, value.value)

    @property
    def RightBorderKnownColor(self)->'ExcelColors':
        """
        Gets or sets the known color of the right border in the conditional format.

        Returns:
            ExcelColors: The known color of the right border.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_RightBorderKnownColor.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_RightBorderKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_RightBorderKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @RightBorderKnownColor.setter
    def RightBorderKnownColor(self, value:'ExcelColors'):
        """
        Sets the known color of the right border in the conditional format.

        Args:
            value (ExcelColors): The known color of the right border.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_RightBorderKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_RightBorderKnownColor, self.Ptr, value.value)

    @property
    def RightBorderColor(self)->'Color':
        """
        Gets or sets the color of the right border in the conditional format.

        Returns:
            Color: The color of the right border.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_RightBorderColor.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_RightBorderColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_RightBorderColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    @RightBorderColor.setter
    def RightBorderColor(self, value:'Color'):
        """
        Sets the color of the right border in the conditional format.

        Args:
            value (Color): The color of the right border.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_RightBorderColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_RightBorderColor, self.Ptr, value.Ptr)

    @property
    def RightBorderStyle(self)->'LineStyleType':
        """
        Gets or sets the style of the right border in the conditional format.

        Returns:
            LineStyleType: The style of the right border.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_RightBorderStyle.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_RightBorderStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_RightBorderStyle, self.Ptr)
        objwraped = LineStyleType(ret)
        return objwraped

    @RightBorderStyle.setter
    def RightBorderStyle(self, value:'LineStyleType'):
        """
        Sets the style of the right border in the conditional format.

        Args:
            value (LineStyleType): The style of the right border.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_RightBorderStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_RightBorderStyle, self.Ptr, value.value)

    @property
    def TopBorderKnownColor(self)->'ExcelColors':
        """
        Gets or sets the known color of the top border in the conditional format.

        Returns:
            ExcelColors: The known color of the top border.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_TopBorderKnownColor.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_TopBorderKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_TopBorderKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @TopBorderKnownColor.setter
    def TopBorderKnownColor(self, value:'ExcelColors'):
        """
        Sets the known color of the top border in the conditional format.

        Args:
            value (ExcelColors): The known color of the top border.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_TopBorderKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_TopBorderKnownColor, self.Ptr, value.value)

    @property
    def TopBorderColor(self)->'Color':
        """
        Gets or sets the color of the top border in the conditional format.

        Returns:
            Color: The color of the top border.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_TopBorderColor.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_TopBorderColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_TopBorderColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    @TopBorderColor.setter
    def TopBorderColor(self, value:'Color'):
        """
        Sets the color of the top border in the conditional format.

        Args:
            value (Color): The color of the top border.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_TopBorderColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_TopBorderColor, self.Ptr, value.Ptr)

    @property
    def TopBorderStyle(self)->'LineStyleType':
        """
        Gets or sets the style of the top border in the conditional format.

        Returns:
            LineStyleType: The style of the top border.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_TopBorderStyle.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_TopBorderStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_TopBorderStyle, self.Ptr)
        objwraped = LineStyleType(ret)
        return objwraped

    @TopBorderStyle.setter
    def TopBorderStyle(self, value:'LineStyleType'):
        """
        Sets the style of the top border in the conditional format.

        Args:
            value (LineStyleType): The style of the top border.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_TopBorderStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_TopBorderStyle, self.Ptr, value.value)

    @property
    def BottomBorderKnownColor(self)->'ExcelColors':
        """
        Gets or sets the known color of the bottom border in the conditional format.

        Returns:
            ExcelColors: The known color of the bottom border.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_BottomBorderKnownColor.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_BottomBorderKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_BottomBorderKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @BottomBorderKnownColor.setter
    def BottomBorderKnownColor(self, value:'ExcelColors'):
        """
        Sets the known color of the bottom border in the conditional format.

        Args:
            value (ExcelColors): The known color of the bottom border.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_BottomBorderKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_BottomBorderKnownColor, self.Ptr, value.value)

    @property
    def BottomBorderColor(self)->'Color':
        """
        Gets or sets the color of the bottom border in the conditional format.

        Returns:
            Color: The color of the bottom border.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_BottomBorderColor.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_BottomBorderColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_BottomBorderColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    @BottomBorderColor.setter
    def BottomBorderColor(self, value:'Color'):
        """
        Sets the color of the bottom border in the conditional format.

        Args:
            value (Color): The color of the bottom border.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_BottomBorderColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_BottomBorderColor, self.Ptr, value.Ptr)

    @property
    def BottomBorderStyle(self)->'LineStyleType':
        """
        Gets or sets the style of the bottom border in the conditional format.

        Returns:
            LineStyleType: The style of the bottom border.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_BottomBorderStyle.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_BottomBorderStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_BottomBorderStyle, self.Ptr)
        objwraped = LineStyleType(ret)
        return objwraped

    @BottomBorderStyle.setter
    def BottomBorderStyle(self, value:'LineStyleType'):
        """
        Sets the style of the bottom border in the conditional format.

        Args:
            value (LineStyleType): The style of the bottom border.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_BottomBorderStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_BottomBorderStyle, self.Ptr, value.value)

    @property
    def FirstFormula(self)->str:
        """
        Gets or sets the first formula for the conditional format.

        Returns:
            str: The first formula.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_FirstFormula.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_FirstFormula.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_FirstFormula, self.Ptr))
        return ret

    @FirstFormula.setter
    def FirstFormula(self, value:str):
        """
        Sets the first formula for the conditional format.

        Args:
            value (str): The first formula.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_FirstFormula.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_FirstFormula, self.Ptr, value)

    @property
    def FirstFormulaR1C1(self)->str:
        """
        Gets or sets the first formula in R1C1 notation for the conditional format.

        Returns:
            str: The first formula in R1C1 notation.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_FirstFormulaR1C1.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_FirstFormulaR1C1.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_FirstFormulaR1C1, self.Ptr))
        return ret

    @FirstFormulaR1C1.setter
    def FirstFormulaR1C1(self, value:str):
        """
        Sets the first formula in R1C1 notation for the conditional format.

        Args:
            value (str): The first formula in R1C1 notation.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_FirstFormulaR1C1.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_FirstFormulaR1C1, self.Ptr, value)

    @property
    def SecondFormulaR1C1(self)->str:
        """
        Gets or sets the second formula in R1C1 notation for the conditional format.

        Returns:
            str: The second formula in R1C1 notation.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_SecondFormulaR1C1.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_SecondFormulaR1C1.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_SecondFormulaR1C1, self.Ptr))
        return ret

    @SecondFormulaR1C1.setter
    def SecondFormulaR1C1(self, value:str):
        """
        Sets the second formula in R1C1 notation for the conditional format.

        Args:
            value (str): The second formula in R1C1 notation.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_SecondFormulaR1C1.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_SecondFormulaR1C1, self.Ptr, value)

    @property
    def SecondFormula(self)->str:
        """
        Gets or sets the second formula for the conditional format.

        Returns:
            str: The second formula.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_SecondFormula.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_SecondFormula.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_SecondFormula, self.Ptr))
        return ret

    @SecondFormula.setter
    def SecondFormula(self, value:str):
        """
        Sets the second formula for the conditional format.

        Args:
            value (str): The second formula.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_SecondFormula.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_SecondFormula, self.Ptr, value)

    @property
    def KnownColor(self)->'ExcelColors':
        """
        Gets or sets the known color for the conditional format.

        Returns:
            ExcelColors: The known color.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        """
        Sets the known color for the conditional format.

        Args:
            value (ExcelColors): The known color.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_KnownColor, self.Ptr, value.value)

    @property
    def Color(self)->'Color':
        """
        Gets or sets the color for the conditional format.

        Returns:
            Color: The color.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_Color.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    @Color.setter
    def Color(self, value:'Color'):
        """
        Sets the color for the conditional format.

        Args:
            value (Color): The color.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_Color, self.Ptr, value.Ptr)

    @property
    def BackKnownColor(self)->'ExcelColors':
        """
        Gets or sets the background known color for the conditional format.

        Returns:
            ExcelColors: The background known color.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_BackKnownColor.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_BackKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_BackKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @BackKnownColor.setter
    def BackKnownColor(self, value:'ExcelColors'):
        """
        Sets the background known color for the conditional format.

        Args:
            value (ExcelColors): The background known color.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_BackKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_BackKnownColor, self.Ptr, value.value)

    @property
    def BackColor(self)->'Color':
        """
        Gets or sets the background color for the conditional format.

        Returns:
            Color: The background color.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_BackColor.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_BackColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_BackColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    @BackColor.setter
    def BackColor(self, value:'Color'):
        """
        Sets the background color for the conditional format.

        Args:
            value (Color): The background color.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_BackColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_BackColor, self.Ptr, value.Ptr)

    @property
    def FillPattern(self)->'ExcelPatternType':
        """
        Gets or sets the fill pattern type.

        Returns:
            ExcelPatternType: The fill pattern type.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_FillPattern.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_FillPattern.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_FillPattern, self.Ptr)
        objwraped = ExcelPatternType(ret)
        return objwraped

    @FillPattern.setter
    def FillPattern(self, value:'ExcelPatternType'):
        """
        Sets the fill pattern type.

        Args:
            value (ExcelPatternType): The fill pattern type.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_FillPattern.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_FillPattern, self.Ptr, value.value)

    @property
    def IsSuperScript(self)->bool:
        """
        Gets or sets whether the font is superscript in the conditional format.

        Returns:
            bool: True if superscript; otherwise, False.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_IsSuperScript.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_IsSuperScript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_IsSuperScript, self.Ptr)
        return ret

    @IsSuperScript.setter
    def IsSuperScript(self, value:bool):
        """
        Sets whether the font is superscript in the conditional format.

        Args:
            value (bool): True if superscript; otherwise, False.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_IsSuperScript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_IsSuperScript, self.Ptr, value)

    @property
    def IsSubScript(self)->bool:
        """
        Gets or sets whether the font is subscript in the conditional format.

        Returns:
            bool: True if subscript; otherwise, False.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_IsSubScript.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_IsSubScript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_IsSubScript, self.Ptr)
        return ret

    @IsSubScript.setter
    def IsSubScript(self, value:bool):
        """
        Sets whether the font is subscript in the conditional format.

        Args:
            value (bool): True if subscript; otherwise, False.
        """
        GetDllLibXls().ConditionalFormatWrapper_set_IsSubScript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_IsSubScript, self.Ptr, value)

    @property
    def NumberFormat(self)->str:
        """

        """
        GetDllLibXls().ConditionalFormatWrapper_get_NumberFormat.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_NumberFormat.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_NumberFormat, self.Ptr))
        return ret

    @NumberFormat.setter
    def NumberFormat(self, value:str):
        GetDllLibXls().ConditionalFormatWrapper_set_NumberFormat.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_NumberFormat, self.Ptr, value)

    @property
    def ColorScale(self)->'ColorScale':
        """
        Gets the ColorScale object associated with the conditional format.

        Returns:
            ColorScale: The ColorScale object.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_ColorScale.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_ColorScale.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_ColorScale, self.Ptr)
        ret = None if intPtr==None else ColorScale(intPtr)
        return ret

    @property
    def DataBar(self)->'DataBar':
        """
        Gets the DataBar object associated with the conditional format.

        Returns:
            DataBar: The DataBar object.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_DataBar.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_DataBar.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_DataBar, self.Ptr)
        ret = None if intPtr==None else DataBar(intPtr)
        return ret

    @property
    def IconSet(self)->'IconSet':
        """
        Gets the IconSet object associated with the conditional format.

        Returns:
            IconSet: The IconSet object.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_IconSet.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_IconSet.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_IconSet, self.Ptr)
        ret = None if intPtr==None else IconSet(intPtr)
        return ret

    def BeginUpdate(self):
        """
        Begins batch update of the conditional format.
        """
        GetDllLibXls().ConditionalFormatWrapper_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """
        Ends batch update of the conditional format.
        """
        GetDllLibXls().ConditionalFormatWrapper_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_EndUpdate, self.Ptr)

    @dispatch
    def MakeFormula(self)->str:
        """
        Generates the formula for the conditional format.

        Returns:
            str: The generated formula.
        """
        GetDllLibXls().ConditionalFormatWrapper_MakeFormula.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_MakeFormula.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ConditionalFormatWrapper_MakeFormula, self.Ptr))
        return ret

    @dispatch
    def MakeFormula(self ,para:str)->str:
        """
        Generates the formula for the conditional format with a parameter.

        Args:
            para (str): The parameter for the formula.
        Returns:
            str: The generated formula.
        """
        
        GetDllLibXls().ConditionalFormatWrapper_MakeFormulaP.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_MakeFormulaP.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ConditionalFormatWrapper_MakeFormulaP, self.Ptr, para))
        return ret

    def SetTimePeriod(self ,timePeriod:'TimePeriodType'):
        """
        Sets the time period type for the conditional format.

        Args:
            timePeriod (TimePeriodType): The time period type.
        """
        enumtimePeriod:c_int = timePeriod.value

        GetDllLibXls().ConditionalFormatWrapper_SetTimePeriod.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_SetTimePeriod, self.Ptr, enumtimePeriod)

    @property
    def OColor(self)->'OColor':
        """
        Gets the conditional format color (read-only).

        Returns:
            OColor: The conditional format color.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_OColor.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_OColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_OColor, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret

    @property
    def BackColorObject(self)->'OColor':
        """
        Gets the conditional format background color (read-only).

        Returns:
            OColor: The background color.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_BackColorObject.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_BackColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_BackColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret

    @property
    def TopBorderColorObject(self)->'OColor':
        """
        Gets the conditional format top border color (read-only).

        Returns:
            OColor: The top border color.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_TopBorderColorObject.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_TopBorderColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_TopBorderColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret

    @property
    def BottomBorderColorObject(self)->'OColor':
        """
        Gets the conditional format bottom border color (read-only).

        Returns:
            OColor: The bottom border color.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_BottomBorderColorObject.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_BottomBorderColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_BottomBorderColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret

    @property
    def LeftBorderColorObject(self)->'OColor':
        """
        Gets the conditional format left border color (read-only).

        Returns:
            OColor: The left border color.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_LeftBorderColorObject.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_LeftBorderColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_LeftBorderColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret

    @property
    def RightBorderColorObject(self)->'OColor':
        """
        Gets the conditional format right border color (read-only).

        Returns:
            OColor: The right border color.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_RightBorderColorObject.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_RightBorderColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_RightBorderColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret

    @property
    def FontColorObject(self)->'OColor':
        """
        Gets the conditional format font color (read-only).

        Returns:
            OColor: The font color.
        """
        GetDllLibXls().ConditionalFormatWrapper_get_FontColorObject.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_FontColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_FontColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret

    @property
    def IsPatternStyleModified(self)->bool:
        """

        """
        GetDllLibXls().ConditionalFormatWrapper_get_IsPatternStyleModified.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_IsPatternStyleModified.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_IsPatternStyleModified, self.Ptr)
        return ret

    @IsPatternStyleModified.setter
    def IsPatternStyleModified(self, value:bool):
        GetDllLibXls().ConditionalFormatWrapper_set_IsPatternStyleModified.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_IsPatternStyleModified, self.Ptr, value)

    @property
    def IsBackgroundColorPresent(self)->bool:
        """

        """
        GetDllLibXls().ConditionalFormatWrapper_get_IsBackgroundColorPresent.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_IsBackgroundColorPresent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_IsBackgroundColorPresent, self.Ptr)
        return ret

    @IsBackgroundColorPresent.setter
    def IsBackgroundColorPresent(self, value:bool):
        GetDllLibXls().ConditionalFormatWrapper_set_IsBackgroundColorPresent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_IsBackgroundColorPresent, self.Ptr, value)

    @property
    def IsBorderFormatPresent(self)->bool:
        """

        """
        GetDllLibXls().ConditionalFormatWrapper_get_IsBorderFormatPresent.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_IsBorderFormatPresent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_IsBorderFormatPresent, self.Ptr)
        return ret

    @IsBorderFormatPresent.setter
    def IsBorderFormatPresent(self, value:bool):
        GetDllLibXls().ConditionalFormatWrapper_set_IsBorderFormatPresent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_IsBorderFormatPresent, self.Ptr, value)

    @property
    def IsBottomBorderModified(self)->bool:
        """

        """
        GetDllLibXls().ConditionalFormatWrapper_get_IsBottomBorderModified.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_IsBottomBorderModified.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_IsBottomBorderModified, self.Ptr)
        return ret

    @IsBottomBorderModified.setter
    def IsBottomBorderModified(self, value:bool):
        GetDllLibXls().ConditionalFormatWrapper_set_IsBottomBorderModified.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_IsBottomBorderModified, self.Ptr, value)

    @property
    def IsFontColorPresent(self)->bool:
        """

        """
        GetDllLibXls().ConditionalFormatWrapper_get_IsFontColorPresent.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_IsFontColorPresent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_IsFontColorPresent, self.Ptr)
        return ret

    @IsFontColorPresent.setter
    def IsFontColorPresent(self, value:bool):
        GetDllLibXls().ConditionalFormatWrapper_set_IsFontColorPresent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_IsFontColorPresent, self.Ptr, value)

    @property
    def IsFontFormatPresent(self)->bool:
        """

        """
        GetDllLibXls().ConditionalFormatWrapper_get_IsFontFormatPresent.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_IsFontFormatPresent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_IsFontFormatPresent, self.Ptr)
        return ret

    @IsFontFormatPresent.setter
    def IsFontFormatPresent(self, value:bool):
        GetDllLibXls().ConditionalFormatWrapper_set_IsFontFormatPresent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_IsFontFormatPresent, self.Ptr, value)

    @property
    def IsLeftBorderModified(self)->bool:
        """

        """
        GetDllLibXls().ConditionalFormatWrapper_get_IsLeftBorderModified.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_IsLeftBorderModified.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_IsLeftBorderModified, self.Ptr)
        return ret

    @IsLeftBorderModified.setter
    def IsLeftBorderModified(self, value:bool):
        GetDllLibXls().ConditionalFormatWrapper_set_IsLeftBorderModified.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_IsLeftBorderModified, self.Ptr, value)

    @property
    def IsPatternColorPresent(self)->bool:
        """
        Indicates whether pattern color .

        """
        GetDllLibXls().ConditionalFormatWrapper_get_IsPatternColorPresent.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_IsPatternColorPresent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_IsPatternColorPresent, self.Ptr)
        return ret

    @IsPatternColorPresent.setter
    def IsPatternColorPresent(self, value:bool):
        GetDllLibXls().ConditionalFormatWrapper_set_IsPatternColorPresent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_IsPatternColorPresent, self.Ptr, value)

    @property
    def IsPatternFormatPresent(self)->bool:
        """

        """
        GetDllLibXls().ConditionalFormatWrapper_get_IsPatternFormatPresent.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_IsPatternFormatPresent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_IsPatternFormatPresent, self.Ptr)
        return ret

    @IsPatternFormatPresent.setter
    def IsPatternFormatPresent(self, value:bool):
        GetDllLibXls().ConditionalFormatWrapper_set_IsPatternFormatPresent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_IsPatternFormatPresent, self.Ptr, value)

    @property
    def IsRightBorderModified(self)->bool:
        """

        """
        GetDllLibXls().ConditionalFormatWrapper_get_IsRightBorderModified.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_IsRightBorderModified.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_IsRightBorderModified, self.Ptr)
        return ret

    @IsRightBorderModified.setter
    def IsRightBorderModified(self, value:bool):
        GetDllLibXls().ConditionalFormatWrapper_set_IsRightBorderModified.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_IsRightBorderModified, self.Ptr, value)

    @property
    def IsTopBorderModified(self)->bool:
        """

        """
        GetDllLibXls().ConditionalFormatWrapper_get_IsTopBorderModified.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormatWrapper_get_IsTopBorderModified.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConditionalFormatWrapper_get_IsTopBorderModified, self.Ptr)
        return ret

    @IsTopBorderModified.setter
    def IsTopBorderModified(self, value:bool):
        GetDllLibXls().ConditionalFormatWrapper_set_IsTopBorderModified.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConditionalFormatWrapper_set_IsTopBorderModified, self.Ptr, value)

