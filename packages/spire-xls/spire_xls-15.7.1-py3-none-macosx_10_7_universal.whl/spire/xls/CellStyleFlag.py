from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class CellStyleFlag (SpireObject) :
    """Represents flags that control which aspects of a cell style are applied.
    
    This class provides a set of boolean properties that determine which formatting
    elements of a cell style should be applied when copying styles between cells or
    when applying styles to ranges. Each property corresponds to a specific formatting
    aspect such as borders, font properties, alignment, etc.
    """
    @property
    def All(self)->bool:
        """Gets or sets whether all style elements should be applied.
        
        When set to True, all formatting elements of the style will be applied.
        When set to False, only the specifically enabled elements will be applied.
        
        Returns:
            bool: True if all style elements should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_All.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_All.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_All, self.Ptr)
        return ret

    @All.setter
    def All(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_All.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_All, self.Ptr, value)

    @property
    def Borders(self)->bool:
        """Gets or sets whether all border style elements should be applied.
        
        When set to True, all border formatting (left, right, top, bottom, and diagonal borders)
        will be applied.
        
        Returns:
            bool: True if all border style elements should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_Borders.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_Borders.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_Borders, self.Ptr)
        return ret

    @Borders.setter
    def Borders(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_Borders.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_Borders, self.Ptr, value)

    @property
    def LeftBorder(self)->bool:
        """Gets or sets whether the left border style should be applied.
        
        When set to True, the left border formatting (style, color, etc.) will be applied.
        
        Returns:
            bool: True if the left border style should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_LeftBorder.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_LeftBorder.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_LeftBorder, self.Ptr)
        return ret

    @LeftBorder.setter
    def LeftBorder(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_LeftBorder.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_LeftBorder, self.Ptr, value)

    @property
    def RightBorder(self)->bool:
        """Gets or sets whether the right border style should be applied.
        
        When set to True, the right border formatting (style, color, etc.) will be applied.
        
        Returns:
            bool: True if the right border style should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_RightBorder.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_RightBorder.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_RightBorder, self.Ptr)
        return ret

    @RightBorder.setter
    def RightBorder(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_RightBorder.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_RightBorder, self.Ptr, value)

    @property
    def TopBorder(self)->bool:
        """Gets or sets whether the top border style should be applied.
        
        When set to True, the top border formatting (style, color, etc.) will be applied.
        
        Returns:
            bool: True if the top border style should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_TopBorder.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_TopBorder.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_TopBorder, self.Ptr)
        return ret

    @TopBorder.setter
    def TopBorder(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_TopBorder.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_TopBorder, self.Ptr, value)

    @property
    def BottomBorder(self)->bool:
        """Gets or sets whether the bottom border style should be applied.
        
        When set to True, the bottom border formatting (style, color, etc.) will be applied.
        
        Returns:
            bool: True if the bottom border style should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_BottomBorder.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_BottomBorder.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_BottomBorder, self.Ptr)
        return ret

    @BottomBorder.setter
    def BottomBorder(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_BottomBorder.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_BottomBorder, self.Ptr, value)

    @property
    def DiagonalDownBorder(self)->bool:
        """Gets or sets whether the diagonal down border style should be applied.
        
        When set to True, the diagonal down border formatting (style, color, etc.) will be applied.
        Diagonal down borders run from the top-left to the bottom-right of a cell.
        
        Returns:
            bool: True if the diagonal down border style should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_DiagonalDownBorder.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_DiagonalDownBorder.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_DiagonalDownBorder, self.Ptr)
        return ret

    @DiagonalDownBorder.setter
    def DiagonalDownBorder(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_DiagonalDownBorder.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_DiagonalDownBorder, self.Ptr, value)

    @property
    def DiagonalUpBorder(self)->bool:
        """Gets or sets whether the diagonal up border style should be applied.
        
        When set to True, the diagonal up border formatting (style, color, etc.) will be applied.
        Diagonal up borders run from the bottom-left to the top-right of a cell.
        
        Returns:
            bool: True if the diagonal up border style should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_DiagonalUpBorder.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_DiagonalUpBorder.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_DiagonalUpBorder, self.Ptr)
        return ret

    @DiagonalUpBorder.setter
    def DiagonalUpBorder(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_DiagonalUpBorder.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_DiagonalUpBorder, self.Ptr, value)

    @property
    def Font(self)->bool:
        """Gets or sets whether all font style elements should be applied.
        
        When set to True, all font formatting (size, name, color, bold, italic, etc.)
        will be applied.
        
        Returns:
            bool: True if all font style elements should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_Font.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_Font.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_Font, self.Ptr)
        return ret

    @Font.setter
    def Font(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_Font.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_Font, self.Ptr, value)

    @property
    def FontSize(self)->bool:
        """Gets or sets whether the font size should be applied.
        
        When set to True, the font size formatting will be applied.
        
        Returns:
            bool: True if the font size should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_FontSize.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_FontSize.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_FontSize, self.Ptr)
        return ret

    @FontSize.setter
    def FontSize(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_FontSize.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_FontSize, self.Ptr, value)

    @property
    def FontName(self)->bool:
        """Gets or sets whether the font name should be applied.
        
        When set to True, the font name (typeface) formatting will be applied.
        
        Returns:
            bool: True if the font name should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_FontName.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_FontName.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_FontName, self.Ptr)
        return ret

    @FontName.setter
    def FontName(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_FontName.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_FontName, self.Ptr, value)

    @property
    def FontColor(self)->bool:
        """Gets or sets whether the font color should be applied.
        
        When set to True, the font color formatting will be applied.
        
        Returns:
            bool: True if the font color should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_FontColor.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_FontColor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_FontColor, self.Ptr)
        return ret

    @FontColor.setter
    def FontColor(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_FontColor.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_FontColor, self.Ptr, value)

    @property
    def FontBold(self)->bool:
        """Gets or sets whether the font bold style should be applied.
        
        When set to True, the bold formatting of the font will be applied.
        
        Returns:
            bool: True if the font bold style should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_FontBold.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_FontBold.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_FontBold, self.Ptr)
        return ret

    @FontBold.setter
    def FontBold(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_FontBold.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_FontBold, self.Ptr, value)

    @property
    def FontItalic(self)->bool:
        """Gets or sets whether the font italic style should be applied.
        
        When set to True, the italic formatting of the font will be applied.
        
        Returns:
            bool: True if the font italic style should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_FontItalic.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_FontItalic.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_FontItalic, self.Ptr)
        return ret

    @FontItalic.setter
    def FontItalic(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_FontItalic.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_FontItalic, self.Ptr, value)

    @property
    def FontUnderline(self)->bool:
        """Gets or sets whether the font underline style should be applied.
        
        When set to True, the underline formatting of the font will be applied.
        
        Returns:
            bool: True if the font underline style should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_FontUnderline.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_FontUnderline.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_FontUnderline, self.Ptr)
        return ret

    @FontUnderline.setter
    def FontUnderline(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_FontUnderline.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_FontUnderline, self.Ptr, value)

    @property
    def FontStrike(self)->bool:
        """Gets or sets whether the font strikethrough style should be applied.
        
        When set to True, the strikethrough formatting of the font will be applied.
        
        Returns:
            bool: True if the font strikethrough style should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_FontStrike.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_FontStrike.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_FontStrike, self.Ptr)
        return ret

    @FontStrike.setter
    def FontStrike(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_FontStrike.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_FontStrike, self.Ptr, value)

    @property
    def FontScript(self)->bool:
        """Gets or sets whether the font script style should be applied.
        
        When set to True, the script formatting (superscript or subscript) of the font will be applied.
        
        Returns:
            bool: True if the font script style should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_FontScript.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_FontScript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_FontScript, self.Ptr)
        return ret

    @FontScript.setter
    def FontScript(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_FontScript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_FontScript, self.Ptr, value)

    @property
    def NumberFormat(self)->bool:
        """Gets or sets whether the number format should be applied.
        
        When set to True, the number format (such as currency, date, percentage, etc.) will be applied.
        
        Returns:
            bool: True if the number format should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_NumberFormat.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_NumberFormat.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_NumberFormat, self.Ptr)
        return ret

    @NumberFormat.setter
    def NumberFormat(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_NumberFormat.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_NumberFormat, self.Ptr, value)

    @property
    def HorizontalAlignment(self)->bool:
        """Gets or sets whether the horizontal alignment should be applied.
        
        When set to True, the horizontal alignment formatting (left, center, right, etc.) will be applied.
        
        Returns:
            bool: True if the horizontal alignment should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_HorizontalAlignment.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_HorizontalAlignment.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_HorizontalAlignment, self.Ptr)
        return ret

    @HorizontalAlignment.setter
    def HorizontalAlignment(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_HorizontalAlignment.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_HorizontalAlignment, self.Ptr, value)

    @property
    def VerticalAlignment(self)->bool:
        """Gets or sets whether the vertical alignment should be applied.
        
        When set to True, the vertical alignment formatting (top, middle, bottom, etc.) will be applied.
        
        Returns:
            bool: True if the vertical alignment should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_VerticalAlignment.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_VerticalAlignment.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_VerticalAlignment, self.Ptr)
        return ret

    @VerticalAlignment.setter
    def VerticalAlignment(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_VerticalAlignment.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_VerticalAlignment, self.Ptr, value)

    @property
    def Indent(self)->bool:
        """Gets or sets whether the text indentation should be applied.
        
        When set to True, the text indentation level formatting will be applied.
        
        Returns:
            bool: True if the text indentation should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_Indent.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_Indent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_Indent, self.Ptr)
        return ret

    @Indent.setter
    def Indent(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_Indent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_Indent, self.Ptr, value)

    @property
    def Rotation(self)->bool:
        """Gets or sets whether the text rotation should be applied.
        
        When set to True, the text rotation formatting (angle of text) will be applied.
        
        Returns:
            bool: True if the text rotation should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_Rotation.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_Rotation.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_Rotation, self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_Rotation.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_Rotation, self.Ptr, value)

    @property
    def WrapText(self)->bool:
        """Gets or sets whether the text wrapping should be applied.
        
        When set to True, the text wrapping formatting (whether text wraps within the cell) will be applied.
        
        Returns:
            bool: True if the text wrapping should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_WrapText.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_WrapText.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_WrapText, self.Ptr)
        return ret

    @WrapText.setter
    def WrapText(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_WrapText.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_WrapText, self.Ptr, value)

    @property
    def ShrinkToFit(self)->bool:
        """Gets or sets whether the shrink to fit formatting should be applied.
        
        When set to True, the shrink to fit formatting (whether text should be shrunk to fit in the cell) will be applied.
        
        Returns:
            bool: True if the shrink to fit formatting should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_ShrinkToFit.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_ShrinkToFit.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_ShrinkToFit, self.Ptr)
        return ret

    @ShrinkToFit.setter
    def ShrinkToFit(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_ShrinkToFit.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_ShrinkToFit, self.Ptr, value)

    @property
    def TextDirection(self)->bool:
        """Gets or sets whether the text direction should be applied.
        
        When set to True, the text direction formatting (left-to-right or right-to-left) will be applied.
        
        Returns:
            bool: True if the text direction should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_TextDirection.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_TextDirection.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_TextDirection, self.Ptr)
        return ret

    @TextDirection.setter
    def TextDirection(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_TextDirection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_TextDirection, self.Ptr, value)

    @property
    def CellShading(self)->bool:
        """Gets or sets whether the cell shading should be applied.
        
        When set to True, the cell shading formatting (background color and pattern) will be applied.
        
        Returns:
            bool: True if the cell shading should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_CellShading.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_CellShading.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_CellShading, self.Ptr)
        return ret

    @CellShading.setter
    def CellShading(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_CellShading.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_CellShading, self.Ptr, value)

    @property
    def Locked(self)->bool:
        """Gets or sets whether the cell locking should be applied.
        
        When set to True, the cell locking formatting (whether the cell is locked when the sheet is protected)
        will be applied.
        
        Returns:
            bool: True if the cell locking should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_Locked.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_Locked.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_Locked, self.Ptr)
        return ret

    @Locked.setter
    def Locked(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_Locked.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_Locked, self.Ptr, value)

    @property
    def HideFormula(self)->bool:
        """Gets or sets whether the formula hiding should be applied.
        
        When set to True, the formula hiding formatting (whether formulas are hidden when the sheet is protected)
        will be applied.
        
        Returns:
            bool: True if the formula hiding should be applied; otherwise, False.
        """
        GetDllLibXls().CellStyleFlag_get_HideFormula.argtypes=[c_void_p]
        GetDllLibXls().CellStyleFlag_get_HideFormula.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CellStyleFlag_get_HideFormula, self.Ptr)
        return ret

    @HideFormula.setter
    def HideFormula(self, value:bool):
        GetDllLibXls().CellStyleFlag_set_HideFormula.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CellStyleFlag_set_HideFormula, self.Ptr, value)

