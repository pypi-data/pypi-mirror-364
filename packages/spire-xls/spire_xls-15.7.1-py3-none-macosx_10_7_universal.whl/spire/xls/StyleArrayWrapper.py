from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class StyleArrayWrapper (  XlsObject, IStyle, IExtendIndex) :
    """Represents a wrapper for cell style arrays in Excel.
    
    This class implements the IStyle and IExtendIndex interfaces and provides functionality
    for managing cell formatting styles including borders, fill patterns, fonts, alignment,
    number formats, and protection settings. It allows batch updates to style properties
    through BeginUpdate and EndUpdate methods.
    """
    @property
    def IsModified(self)->bool:
        """Gets whether the style has been modified since it was created or last saved.
        
        Returns:
            bool: True if the style has been modified; otherwise, False.
        """
        GetDllLibXls().StyleArrayWrapper_get_IsModified.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_IsModified.restype=c_bool
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_IsModified, self.Ptr)
        return ret

    @property

    def Borders(self)->'IBorders':
        """Gets the borders collection for the style.
        
        Returns:
            IBorders: The collection of borders for the style.
        """
        GetDllLibXls().StyleArrayWrapper_get_Borders.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_Borders.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_Borders, self.Ptr)
        ret = None if intPtr==None else XlsBordersCollection(intPtr)
        return ret


    @property
    def BuiltIn(self)->bool:
        """Gets whether the style is a built-in style.
        
        Returns:
            bool: True if the style is a built-in style; otherwise, False.
        """
        GetDllLibXls().StyleArrayWrapper_get_BuiltIn.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_BuiltIn.restype=c_bool
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_BuiltIn, self.Ptr)
        return ret

    @property

    def FillPattern(self)->'ExcelPatternType':
        """Gets or sets the fill pattern type for the style.
        
        Returns:
            ExcelPatternType: The fill pattern type.
        """
        GetDllLibXls().StyleArrayWrapper_get_FillPattern.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_FillPattern.restype=c_int
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_FillPattern, self.Ptr)
        objwraped = ExcelPatternType(ret)
        return objwraped

    @FillPattern.setter
    def FillPattern(self, value:'ExcelPatternType'):
        GetDllLibXls().StyleArrayWrapper_set_FillPattern.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_FillPattern, self.Ptr, value.value)

    @property

    def FillBackground(self)->'ExcelColors':
        """Gets or sets the background color for the fill pattern.
        
        Returns:
            ExcelColors: The background color as an Excel color.
        """
        GetDllLibXls().StyleArrayWrapper_get_FillBackground.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_FillBackground.restype=c_int
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_FillBackground, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @FillBackground.setter
    def FillBackground(self, value:'ExcelColors'):
        GetDllLibXls().StyleArrayWrapper_set_FillBackground.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_FillBackground, self.Ptr, value.value)

    @property

    def FillBackgroundRGB(self)->'Color':
        """

        """
        GetDllLibXls().StyleArrayWrapper_get_FillBackgroundRGB.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_FillBackgroundRGB.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_FillBackgroundRGB, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @FillBackgroundRGB.setter
    def FillBackgroundRGB(self, value:'Color'):
        GetDllLibXls().StyleArrayWrapper_set_FillBackgroundRGB.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_FillBackgroundRGB, self.Ptr, value.Ptr)

    @property

    def FillForeground(self)->'ExcelColors':
        """

        """
        GetDllLibXls().StyleArrayWrapper_get_FillForeground.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_FillForeground.restype=c_int
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_FillForeground, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @FillForeground.setter
    def FillForeground(self, value:'ExcelColors'):
        GetDllLibXls().StyleArrayWrapper_set_FillForeground.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_FillForeground, self.Ptr, value.value)

    @property

    def FillForegroundRGB(self)->'Color':
        """

        """
        GetDllLibXls().StyleArrayWrapper_get_FillForegroundRGB.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_FillForegroundRGB.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_FillForegroundRGB, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @FillForegroundRGB.setter
    def FillForegroundRGB(self, value:'Color'):
        GetDllLibXls().StyleArrayWrapper_set_FillForegroundRGB.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_FillForegroundRGB, self.Ptr, value.Ptr)

    @property

    def Font(self)->'IFont':
        """Gets the font object for the style.
        
        Returns:
            IFont: The font object.
        """
        GetDllLibXls().StyleArrayWrapper_get_Font.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_Font.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_Font, self.Ptr)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret


    @property
    def FormulaHidden(self)->bool:
        """Gets or sets whether formulas are hidden when the worksheet is protected.
        
        Returns:
            bool: True if formulas are hidden; otherwise, False.
        """
        GetDllLibXls().StyleArrayWrapper_get_FormulaHidden.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_FormulaHidden.restype=c_bool
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_FormulaHidden, self.Ptr)
        return ret

    @FormulaHidden.setter
    def FormulaHidden(self, value:bool):
        GetDllLibXls().StyleArrayWrapper_set_FormulaHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_FormulaHidden, self.Ptr, value)

    @property

    def HorizontalAlignment(self)->'HorizontalAlignType':
        """Gets or sets the horizontal alignment for the style.
        
        Returns:
            HorizontalAlignType: The horizontal alignment type.
        """
        GetDllLibXls().StyleArrayWrapper_get_HorizontalAlignment.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_HorizontalAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_HorizontalAlignment, self.Ptr)
        objwraped = HorizontalAlignType(ret)
        return objwraped

    @HorizontalAlignment.setter
    def HorizontalAlignment(self, value:'HorizontalAlignType'):
        GetDllLibXls().StyleArrayWrapper_set_HorizontalAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_HorizontalAlignment, self.Ptr, value.value)

    @property
    def IncludeAlignment(self)->bool:
        """Gets or sets whether alignment settings are included in the style.
        
        Returns:
            bool: True if alignment settings are included; otherwise, False.
        """
        GetDllLibXls().StyleArrayWrapper_get_IncludeAlignment.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_IncludeAlignment.restype=c_bool
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_IncludeAlignment, self.Ptr)
        return ret

    @IncludeAlignment.setter
    def IncludeAlignment(self, value:bool):
        GetDllLibXls().StyleArrayWrapper_set_IncludeAlignment.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_IncludeAlignment, self.Ptr, value)

    @property
    def IncludeBorder(self)->bool:
        """Gets or sets whether border settings are included in the style.
        
        Returns:
            bool: True if border settings are included; otherwise, False.
        """
        GetDllLibXls().StyleArrayWrapper_get_IncludeBorder.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_IncludeBorder.restype=c_bool
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_IncludeBorder, self.Ptr)
        return ret

    @IncludeBorder.setter
    def IncludeBorder(self, value:bool):
        GetDllLibXls().StyleArrayWrapper_set_IncludeBorder.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_IncludeBorder, self.Ptr, value)

    @property
    def IncludeFont(self)->bool:
        """Gets or sets whether font settings are included in the style.
        
        Returns:
            bool: True if font settings are included; otherwise, False.
        """
        GetDllLibXls().StyleArrayWrapper_get_IncludeFont.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_IncludeFont.restype=c_bool
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_IncludeFont, self.Ptr)
        return ret

    @IncludeFont.setter
    def IncludeFont(self, value:bool):
        GetDllLibXls().StyleArrayWrapper_set_IncludeFont.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_IncludeFont, self.Ptr, value)

    @property
    def IncludeNumberFormat(self)->bool:
        """Gets or sets whether number format settings are included in the style.
        
        Returns:
            bool: True if number format settings are included; otherwise, False.
        """
        GetDllLibXls().StyleArrayWrapper_get_IncludeNumberFormat.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_IncludeNumberFormat.restype=c_bool
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_IncludeNumberFormat, self.Ptr)
        return ret

    @IncludeNumberFormat.setter
    def IncludeNumberFormat(self, value:bool):
        GetDllLibXls().StyleArrayWrapper_set_IncludeNumberFormat.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_IncludeNumberFormat, self.Ptr, value)

    @property
    def IncludePatterns(self)->bool:
        """Gets or sets whether pattern settings are included in the style.
        
        Returns:
            bool: True if pattern settings are included; otherwise, False.
        """
        GetDllLibXls().StyleArrayWrapper_get_IncludePatterns.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_IncludePatterns.restype=c_bool
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_IncludePatterns, self.Ptr)
        return ret

    @IncludePatterns.setter
    def IncludePatterns(self, value:bool):
        GetDllLibXls().StyleArrayWrapper_set_IncludePatterns.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_IncludePatterns, self.Ptr, value)

    @property
    def IncludeProtection(self)->bool:
        """Gets or sets whether protection settings are included in the style.
        
        Returns:
            bool: True if protection settings are included; otherwise, False.
        """
        GetDllLibXls().StyleArrayWrapper_get_IncludeProtection.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_IncludeProtection.restype=c_bool
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_IncludeProtection, self.Ptr)
        return ret

    @IncludeProtection.setter
    def IncludeProtection(self, value:bool):
        GetDllLibXls().StyleArrayWrapper_set_IncludeProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_IncludeProtection, self.Ptr, value)

    @property
    def IndentLevel(self)->int:
        """Gets or sets the indent level for the style.
        
        Returns:
            int: The indent level value.
        """
        GetDllLibXls().StyleArrayWrapper_get_IndentLevel.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_IndentLevel.restype=c_int
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_IndentLevel, self.Ptr)
        return ret

    @IndentLevel.setter
    def IndentLevel(self, value:int):
        GetDllLibXls().StyleArrayWrapper_set_IndentLevel.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_IndentLevel, self.Ptr, value)

    @property
    def IsInitialized(self)->bool:
        """Gets whether the style has been initialized.
        
        Returns:
            bool: True if the style has been initialized; otherwise, False.
        """
        GetDllLibXls().StyleArrayWrapper_get_IsInitialized.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_IsInitialized.restype=c_bool
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_IsInitialized, self.Ptr)
        return ret

    @property
    def Locked(self)->bool:
        """Gets or sets whether the cells using this style are locked.
        
        When a worksheet is protected, locked cells cannot be modified by the user.
        
        Returns:
            bool: True if cells are locked; otherwise, False.
        """
        GetDllLibXls().StyleArrayWrapper_get_Locked.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_Locked.restype=c_bool
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_Locked, self.Ptr)
        return ret

    @Locked.setter
    def Locked(self, value:bool):
        GetDllLibXls().StyleArrayWrapper_set_Locked.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_Locked, self.Ptr, value)

    @property

    def Name(self)->str:
        """Gets the name of the style.
        
        Returns:
            str: The name of the style.
        """
        GetDllLibXls().StyleArrayWrapper_get_Name.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().StyleArrayWrapper_get_Name, self.Ptr))
        return ret


    @property

    def NumberFormat(self)->str:
        """Gets or sets the number format string for the style.
        
        The format string follows Excel's number format syntax.
        
        Returns:
            str: The number format string.
        """
        GetDllLibXls().StyleArrayWrapper_get_NumberFormat.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_NumberFormat.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().StyleArrayWrapper_get_NumberFormat, self.Ptr))
        return ret


    @NumberFormat.setter
    def NumberFormat(self, value:str):
        GetDllLibXls().StyleArrayWrapper_set_NumberFormat.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_NumberFormat, self.Ptr, value)

    @property
    def NumberFormatIndex(self)->int:
        """Gets or sets the index of the number format.
        
        Returns:
            int: The index of the number format.
        """
        GetDllLibXls().StyleArrayWrapper_get_NumberFormatIndex.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_NumberFormatIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_NumberFormatIndex, self.Ptr)
        return ret

    @NumberFormatIndex.setter
    def NumberFormatIndex(self, value:int):
        GetDllLibXls().StyleArrayWrapper_set_NumberFormatIndex.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_NumberFormatIndex, self.Ptr, value)

    @property

    def NumberFormatSettings(self)->'INumberFormat':
        """Gets the number format settings object for the style.
        
        Returns:
            INumberFormat: The number format settings object.
        """
        GetDllLibXls().StyleArrayWrapper_get_NumberFormatSettings.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_NumberFormatSettings.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_NumberFormatSettings, self.Ptr)
        ret = None if intPtr==None else INumberFormat(intPtr)
        return ret


    @property
    def Rotation(self)->int:
        """Gets or sets the text rotation angle for the style.
        
        Returns:
            int: The text rotation angle in degrees.
        """
        GetDllLibXls().StyleArrayWrapper_get_Rotation.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_Rotation.restype=c_int
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_Rotation, self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:int):
        GetDllLibXls().StyleArrayWrapper_set_Rotation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_Rotation, self.Ptr, value)

    @property
    def ShrinkToFit(self)->bool:
        """Gets or sets whether text automatically shrinks to fit in the available column width.
        
        Returns:
            bool: True if text shrinks to fit; otherwise, False.
        """
        GetDllLibXls().StyleArrayWrapper_get_ShrinkToFit.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_ShrinkToFit.restype=c_bool
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_ShrinkToFit, self.Ptr)
        return ret

    @ShrinkToFit.setter
    def ShrinkToFit(self, value:bool):
        GetDllLibXls().StyleArrayWrapper_set_ShrinkToFit.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_ShrinkToFit, self.Ptr, value)

    @property

    def VerticalAlignment(self)->'VerticalAlignType':
        """Gets or sets the vertical alignment for the style.
        
        Returns:
            VerticalAlignType: The vertical alignment type.
        """
        GetDllLibXls().StyleArrayWrapper_get_VerticalAlignment.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_VerticalAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_VerticalAlignment, self.Ptr)
        objwraped = VerticalAlignType(ret)
        return objwraped

    @VerticalAlignment.setter
    def VerticalAlignment(self, value:'VerticalAlignType'):
        GetDllLibXls().StyleArrayWrapper_set_VerticalAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_VerticalAlignment, self.Ptr, value.value)

    @property
    def WrapText(self)->bool:
        """Gets or sets whether text is wrapped within the cell.
        
        Returns:
            bool: True if text wrapping is enabled; otherwise, False.
        """
        GetDllLibXls().StyleArrayWrapper_get_WrapText.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_WrapText.restype=c_bool
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_WrapText, self.Ptr)
        return ret

    @WrapText.setter
    def WrapText(self, value:bool):
        GetDllLibXls().StyleArrayWrapper_set_WrapText.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_WrapText, self.Ptr, value)

    @property

    def ReadingOrder(self)->'ReadingOrderType':
        """Gets or sets the reading order for the style.
        
        Returns:
            ReadingOrderType: The reading order type (left-to-right, right-to-left, or context).
        """
        GetDllLibXls().StyleArrayWrapper_get_ReadingOrder.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_ReadingOrder.restype=c_int
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_ReadingOrder, self.Ptr)
        objwraped = ReadingOrderType(ret)
        return objwraped

    @ReadingOrder.setter
    def ReadingOrder(self, value:'ReadingOrderType'):
        GetDllLibXls().StyleArrayWrapper_set_ReadingOrder.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_ReadingOrder, self.Ptr, value.value)

    @property
    def IsFirstSymbolApostrophe(self)->bool:
        """Gets or sets whether the first character in the cell is an apostrophe.
        
        In Excel, an apostrophe at the beginning of a cell's text forces the cell to be treated as text,
        even if it contains what would otherwise be interpreted as a number or formula.
        
        Returns:
            bool: True if the first character is an apostrophe; otherwise, False.
        """
        GetDllLibXls().StyleArrayWrapper_get_IsFirstSymbolApostrophe.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_IsFirstSymbolApostrophe.restype=c_bool
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_IsFirstSymbolApostrophe, self.Ptr)
        return ret

    @IsFirstSymbolApostrophe.setter
    def IsFirstSymbolApostrophe(self, value:bool):
        GetDllLibXls().StyleArrayWrapper_set_IsFirstSymbolApostrophe.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_IsFirstSymbolApostrophe, self.Ptr, value)

    @property

    def PatternKnownColor(self)->'ExcelColors':
        """Gets or sets the pattern color using Excel's predefined color palette.
        
        Returns:
            ExcelColors: The pattern color from Excel's color palette.
        """
        GetDllLibXls().StyleArrayWrapper_get_PatternKnownColor.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_PatternKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_PatternKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @PatternKnownColor.setter
    def PatternKnownColor(self, value:'ExcelColors'):
        GetDllLibXls().StyleArrayWrapper_set_PatternKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_PatternKnownColor, self.Ptr, value.value)

    @property

    def PatternColor(self)->'Color':
        """Gets or sets the pattern color for the style.
        
        Returns:
            Color: The pattern color object.
        """
        GetDllLibXls().StyleArrayWrapper_get_PatternColor.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_PatternColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_PatternColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @PatternColor.setter
    def PatternColor(self, value:'Color'):
        GetDllLibXls().StyleArrayWrapper_set_PatternColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_PatternColor, self.Ptr, value.Ptr)

    @property

    def KnownColor(self)->'ExcelColors':
        """Gets or sets the cell color using Excel's predefined color palette.
        
        Returns:
            ExcelColors: The cell color from Excel's color palette.
        """
        GetDllLibXls().StyleArrayWrapper_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        GetDllLibXls().StyleArrayWrapper_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_KnownColor, self.Ptr, value.value)

    @property

    def Color(self)->'Color':
        """Gets or sets the cell color for the style.
        
        Returns:
            Color: The cell color object.
        """
        GetDllLibXls().StyleArrayWrapper_get_Color.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        GetDllLibXls().StyleArrayWrapper_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_Color, self.Ptr, value.Ptr)

    @property

    def Interior(self)->'IInterior':
        """Gets the interior object for the style.
        
        The interior object contains properties for formatting the inside of a cell or range.
        
        Returns:
            IInterior: The interior object.
        """
        GetDllLibXls().StyleArrayWrapper_get_Interior.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_Interior.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_Interior, self.Ptr)
        ret = None if intPtr==None else ExcelInterior(intPtr)
        return ret



    def SetThemeColor(self ,type:'ThemeColorType',tint:float):
        """Sets a theme color for the style.
        
        Args:
            type (ThemeColorType): The theme color type.
            tint (float): The tint value to apply to the theme color (-1.0 to 1.0).
        """
        enumtype:c_int = type.value

        GetDllLibXls().StyleArrayWrapper_SetThemeColor.argtypes=[c_void_p ,c_int,c_double]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_SetThemeColor, self.Ptr, enumtype,tint)

#
#    def GetThemeColor(self ,type:'ThemeColorType&',tint:'Double&')->bool:
#        """
#
#        """
#        intPtrtype:c_void_p = type.Ptr
#        intPtrtint:c_void_p = tint.Ptr
#
#        GetDllLibXls().StyleArrayWrapper_GetThemeColor.argtypes=[c_void_p ,c_void_p,c_void_p]
#        GetDllLibXls().StyleArrayWrapper_GetThemeColor.restype=c_bool
#        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_GetThemeColor, self.Ptr, intPtrtype,intPtrtint)
#        return ret


    @property
    def JustifyLast(self)->bool:
        """Gets or sets whether the last line of text is justified.
        
        Returns:
            bool: True if the last line is justified; otherwise, False.
        """
        GetDllLibXls().StyleArrayWrapper_get_JustifyLast.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_JustifyLast.restype=c_bool
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_JustifyLast, self.Ptr)
        return ret

    @JustifyLast.setter
    def JustifyLast(self, value:bool):
        GetDllLibXls().StyleArrayWrapper_set_JustifyLast.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_JustifyLast, self.Ptr, value)

    @property

    def NumberFormatLocal(self)->str:
        """Gets or sets the number format string in the user's local language.
        
        Returns:
            str: The localized number format string.
        """
        GetDllLibXls().StyleArrayWrapper_get_NumberFormatLocal.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_NumberFormatLocal.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().StyleArrayWrapper_get_NumberFormatLocal, self.Ptr))
        return ret


    @NumberFormatLocal.setter
    def NumberFormatLocal(self, value:str):
        GetDllLibXls().StyleArrayWrapper_set_NumberFormatLocal.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_set_NumberFormatLocal, self.Ptr, value)

    @property
    def ExtendedFormatIndex(self)->int:
        """Gets the extended format index for the style.
        
        Returns:
            int: The extended format index.
        """
        GetDllLibXls().StyleArrayWrapper_get_ExtendedFormatIndex.argtypes=[c_void_p]
        GetDllLibXls().StyleArrayWrapper_get_ExtendedFormatIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().StyleArrayWrapper_get_ExtendedFormatIndex, self.Ptr)
        return ret

    def BeginUpdate(self):
        """Begins a batch update operation on the style.
        
        This method marks the start of a series of changes to the style properties.
        For better performance, multiple property changes should be made between
        BeginUpdate and EndUpdate calls.
        """
        GetDllLibXls().StyleArrayWrapper_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """Ends a batch update operation on the style.
        
        This method applies all pending changes to the style properties that were
        made since the last BeginUpdate call.
        """
        GetDllLibXls().StyleArrayWrapper_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().StyleArrayWrapper_EndUpdate, self.Ptr)

