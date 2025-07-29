from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class FontArrayWrapper (  XlsObject, IFont, IOptimizedUpdate) :
    """Represents a wrapper for font arrays in Excel.
    
    This class provides access to font properties for multiple cells or ranges,
    allowing batch operations on font attributes such as style, color, size, etc.
    It implements the IFont interface for font manipulation and IOptimizedUpdate
    for performance optimization when making multiple changes.
    """
    @property
    def IsItalic(self)->bool:
        """Gets a value indicating whether the font is italic.
        
        Returns:
            bool: True if the font is italic; otherwise, False.
        """
        GetDllLibXls().FontArrayWrapper_get_IsItalic.argtypes=[c_void_p]
        GetDllLibXls().FontArrayWrapper_get_IsItalic.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FontArrayWrapper_get_IsItalic, self.Ptr)
        return ret

    @IsItalic.setter
    def IsItalic(self, value:bool):
        """Sets a value indicating whether the font is italic.
        
        Args:
            value (bool): True to set the font as italic; otherwise, False.
        """
        GetDllLibXls().FontArrayWrapper_set_IsItalic.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FontArrayWrapper_set_IsItalic, self.Ptr, value)

    @property

    def KnownColor(self)->'ExcelColors':
        """Gets the predefined Excel color of the font.
        
        Returns:
            ExcelColors: An enumeration value representing the Excel color.
        """
        GetDllLibXls().FontArrayWrapper_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().FontArrayWrapper_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().FontArrayWrapper_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        """Sets the predefined Excel color of the font.
        
        Args:
            value (ExcelColors): An enumeration value representing the Excel color to set.
        """
        GetDllLibXls().FontArrayWrapper_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().FontArrayWrapper_set_KnownColor, self.Ptr, value.value)

    @property

    def Color(self)->'Color':
        """Gets the color of the font.
        
        Returns:
            Color: A Color object representing the font color.
        """
        GetDllLibXls().FontArrayWrapper_get_Color.argtypes=[c_void_p]
        GetDllLibXls().FontArrayWrapper_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().FontArrayWrapper_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        """Sets the color of the font.
        
        Args:
            value (Color): A Color object representing the font color to set.
        """
        GetDllLibXls().FontArrayWrapper_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().FontArrayWrapper_set_Color, self.Ptr, value.Ptr)


    def SetThemeColor(self ,type:'ThemeColorType',tint:float):
        """Sets a theme color for the font.
        
        Args:
            type (ThemeColorType): The type of theme color to set.
            tint (float): The tint value to apply to the theme color.
        """
        enumtype:c_int = type.value

        GetDllLibXls().FontArrayWrapper_SetThemeColor.argtypes=[c_void_p ,c_int,c_double]
        CallCFunction(GetDllLibXls().FontArrayWrapper_SetThemeColor, self.Ptr, enumtype,tint)

#
#    def GetThemeColor(self ,type:'ThemeColorType&',tint:'Double&')->bool:
#        """
#
#        """
#        intPtrtype:c_void_p = type.Ptr
#        intPtrtint:c_void_p = tint.Ptr
#
#        GetDllLibXls().FontArrayWrapper_GetThemeColor.argtypes=[c_void_p ,c_void_p,c_void_p]
#        GetDllLibXls().FontArrayWrapper_GetThemeColor.restype=c_bool
#        ret = CallCFunction(GetDllLibXls().FontArrayWrapper_GetThemeColor, self.Ptr, intPtrtype,intPtrtint)
#        return ret


    @property
    def IsBold(self)->bool:
        """Gets a value indicating whether the font is bold.
        
        Returns:
            bool: True if the font is bold; otherwise, False.
        """
        GetDllLibXls().FontArrayWrapper_get_IsBold.argtypes=[c_void_p]
        GetDllLibXls().FontArrayWrapper_get_IsBold.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FontArrayWrapper_get_IsBold, self.Ptr)
        return ret

    @IsBold.setter
    def IsBold(self, value:bool):
        """Sets a value indicating whether the font is bold.
        
        Args:
            value (bool): True to set the font as bold; otherwise, False.
        """
        GetDllLibXls().FontArrayWrapper_set_IsBold.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FontArrayWrapper_set_IsBold, self.Ptr, value)

    @property
    def Size(self)->float:
        """Gets the size of the font in points.
        
        Returns:
            float: The font size in points.
        """
        GetDllLibXls().FontArrayWrapper_get_Size.argtypes=[c_void_p]
        GetDllLibXls().FontArrayWrapper_get_Size.restype=c_double
        ret = CallCFunction(GetDllLibXls().FontArrayWrapper_get_Size, self.Ptr)
        return ret

    @Size.setter
    def Size(self, value:float):
        """Sets the size of the font in points.
        
        Args:
            value (float): The font size in points to set.
        """
        GetDllLibXls().FontArrayWrapper_set_Size.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().FontArrayWrapper_set_Size, self.Ptr, value)

    @property
    def IsStrikethrough(self)->bool:
        """Gets a value indicating whether the font has a strikethrough.
        
        Returns:
            bool: True if the font has a strikethrough; otherwise, False.
        """
        GetDllLibXls().FontArrayWrapper_get_IsStrikethrough.argtypes=[c_void_p]
        GetDllLibXls().FontArrayWrapper_get_IsStrikethrough.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FontArrayWrapper_get_IsStrikethrough, self.Ptr)
        return ret

    @IsStrikethrough.setter
    def IsStrikethrough(self, value:bool):
        """Sets a value indicating whether the font has a strikethrough.
        
        Args:
            value (bool): True to apply strikethrough to the font; otherwise, False.
        """
        GetDllLibXls().FontArrayWrapper_set_IsStrikethrough.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FontArrayWrapper_set_IsStrikethrough, self.Ptr, value)

    @property

    def StrikethroughType(self)->str:
        """Gets the type of strikethrough applied to the font.
        
        Returns:
            str: A string representing the type of strikethrough.
        """
        GetDllLibXls().FontArrayWrapper_get_StrikethroughType.argtypes=[c_void_p]
        GetDllLibXls().FontArrayWrapper_get_StrikethroughType.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().FontArrayWrapper_get_StrikethroughType, self.Ptr))
        return ret


    @StrikethroughType.setter
    def StrikethroughType(self, value:str):
        """Sets the type of strikethrough applied to the font.
        
        Args:
            value (str): A string representing the type of strikethrough to apply.
        """
        GetDllLibXls().FontArrayWrapper_set_StrikethroughType.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().FontArrayWrapper_set_StrikethroughType, self.Ptr, value)

    @property
    def IsSubscript(self)->bool:
        """Gets a value indicating whether the font is subscript.
        
        Returns:
            bool: True if the font is subscript; otherwise, False.
        """
        GetDllLibXls().FontArrayWrapper_get_IsSubscript.argtypes=[c_void_p]
        GetDllLibXls().FontArrayWrapper_get_IsSubscript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FontArrayWrapper_get_IsSubscript, self.Ptr)
        return ret

    @IsSubscript.setter
    def IsSubscript(self, value:bool):
        """Sets a value indicating whether the font is subscript.
        
        Args:
            value (bool): True to set the font as subscript; otherwise, False.
        """
        GetDllLibXls().FontArrayWrapper_set_IsSubscript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FontArrayWrapper_set_IsSubscript, self.Ptr, value)

    @property
    def IsSuperscript(self)->bool:
        """Gets a value indicating whether the font is superscript.
        
        Returns:
            bool: True if the font is superscript; otherwise, False.
        """
        GetDllLibXls().FontArrayWrapper_get_IsSuperscript.argtypes=[c_void_p]
        GetDllLibXls().FontArrayWrapper_get_IsSuperscript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FontArrayWrapper_get_IsSuperscript, self.Ptr)
        return ret

    @IsSuperscript.setter
    def IsSuperscript(self, value:bool):
        """Sets a value indicating whether the font is superscript.
        
        Args:
            value (bool): True to set the font as superscript; otherwise, False.
        """
        GetDllLibXls().FontArrayWrapper_set_IsSuperscript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FontArrayWrapper_set_IsSuperscript, self.Ptr, value)

    @property

    def Underline(self)->'FontUnderlineType':
        """Gets the type of underline applied to the font.
        
        Returns:
            FontUnderlineType: An enumeration value representing the underline type.
        """
        GetDllLibXls().FontArrayWrapper_get_Underline.argtypes=[c_void_p]
        GetDllLibXls().FontArrayWrapper_get_Underline.restype=c_int
        ret = CallCFunction(GetDllLibXls().FontArrayWrapper_get_Underline, self.Ptr)
        objwraped = FontUnderlineType(ret)
        return objwraped

    @Underline.setter
    def Underline(self, value:'FontUnderlineType'):
        """Sets the type of underline applied to the font.
        
        Args:
            value (FontUnderlineType): An enumeration value representing the underline type to apply.
        """
        GetDllLibXls().FontArrayWrapper_set_Underline.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().FontArrayWrapper_set_Underline, self.Ptr, value.value)

    @property

    def FontName(self)->str:
        """Gets the name of the font.
        
        Returns:
            str: The name of the font.
        """
        GetDllLibXls().FontArrayWrapper_get_FontName.argtypes=[c_void_p]
        GetDllLibXls().FontArrayWrapper_get_FontName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().FontArrayWrapper_get_FontName, self.Ptr))
        return ret


    @FontName.setter
    def FontName(self, value:str):
        """Sets the name of the font.
        
        Args:
            value (str): The name of the font to set.
        """
        GetDllLibXls().FontArrayWrapper_set_FontName.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().FontArrayWrapper_set_FontName, self.Ptr, value)

    @property

    def VerticalAlignment(self)->'FontVertialAlignmentType':
        """Gets the vertical alignment of the font.
        
        Returns:
            FontVertialAlignmentType: An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().FontArrayWrapper_get_VerticalAlignment.argtypes=[c_void_p]
        GetDllLibXls().FontArrayWrapper_get_VerticalAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().FontArrayWrapper_get_VerticalAlignment, self.Ptr)
        objwraped = FontVertialAlignmentType(ret)
        return objwraped

    @VerticalAlignment.setter
    def VerticalAlignment(self, value:'FontVertialAlignmentType'):
        """Sets the vertical alignment of the font.
        
        Args:
            value (FontVertialAlignmentType): An enumeration value representing the vertical alignment to set.
        """
        GetDllLibXls().FontArrayWrapper_set_VerticalAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().FontArrayWrapper_set_VerticalAlignment, self.Ptr, value.value)


    def GenerateNativeFont(self)->'Font':
        """Generates a native Font object from this FontArrayWrapper.
        
        Returns:
            Font: A Font object representing the font settings in this wrapper.
        """
        GetDllLibXls().FontArrayWrapper_GenerateNativeFont.argtypes=[c_void_p]
        GetDllLibXls().FontArrayWrapper_GenerateNativeFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().FontArrayWrapper_GenerateNativeFont, self.Ptr)
        ret = None if intPtr==None else Font(intPtr)
        return ret


    @property
    def IsAutoColor(self)->bool:
        """Gets a value indicating whether the font color is set to automatic.
        
        Returns:
            bool: True if the font color is automatic; otherwise, False.
        """
        GetDllLibXls().FontArrayWrapper_get_IsAutoColor.argtypes=[c_void_p]
        GetDllLibXls().FontArrayWrapper_get_IsAutoColor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FontArrayWrapper_get_IsAutoColor, self.Ptr)
        return ret

    def BeginUpdate(self):
        """Begins a batch update operation on the font properties.
        
        This method should be called before making multiple changes to font properties
        to improve performance by deferring the actual updates until EndUpdate is called.
        """
        GetDllLibXls().FontArrayWrapper_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().FontArrayWrapper_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """Ends a batch update operation and applies all pending changes to font properties.
        
        This method should be called after BeginUpdate to apply all the changes made
        to font properties in a single operation, improving performance.
        """
        GetDllLibXls().FontArrayWrapper_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().FontArrayWrapper_EndUpdate, self.Ptr)

