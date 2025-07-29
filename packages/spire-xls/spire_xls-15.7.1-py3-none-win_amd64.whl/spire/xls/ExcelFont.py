from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ExcelFont (  SpireObject, IFont) :
    """Represents a font in an Excel workbook.
    
    This class encapsulates the properties and methods for managing font formatting in Excel,
    including font name, size, style (bold, italic, etc.), color, and other attributes.
    It implements the IFont interface to provide standard font manipulation functionality.
    """
    @property
    def IsItalic(self)->bool:
        """Gets or sets whether the font style is italic.
        
        Returns:
            bool: True if the font style is italic; otherwise, False.
        """
        GetDllLibXls().ExcelFont_get_IsItalic.argtypes=[c_void_p]
        GetDllLibXls().ExcelFont_get_IsItalic.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExcelFont_get_IsItalic, self.Ptr)
        return ret

    @IsItalic.setter
    def IsItalic(self, value:bool):
        GetDllLibXls().ExcelFont_set_IsItalic.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExcelFont_set_IsItalic, self.Ptr, value)

    @property

    def KnownColor(self)->'ExcelColors':
        """Gets or sets the primary Excel color of the font using predefined Excel colors.
        
        Returns:
            ExcelColors: An enumeration value representing the predefined Excel color.
        """
        GetDllLibXls().ExcelFont_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().ExcelFont_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelFont_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        GetDllLibXls().ExcelFont_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelFont_set_KnownColor, self.Ptr, value.value)

    @property

    def Color(self)->'Color':
        """Gets or sets the primary color of the font using RGB values.
        
        Returns:
            Color: A Color object representing the RGB color of the font.
        """
        GetDllLibXls().ExcelFont_get_Color.argtypes=[c_void_p]
        GetDllLibXls().ExcelFont_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelFont_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        GetDllLibXls().ExcelFont_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ExcelFont_set_Color, self.Ptr, value.Ptr)


    def SetThemeColor(self ,type:'ThemeColorType',tint:float):
        """Sets the theme color for the font.
        
        Args:
            type (ThemeColorType): The theme color type to apply.
            tint (float): The tint value to apply to the theme color, between -1.0 and 1.0.
                          Positive values lighten the color, negative values darken it.
        """
        enumtype:c_int = type.value

        GetDllLibXls().ExcelFont_SetThemeColor.argtypes=[c_void_p ,c_int,c_double]
        CallCFunction(GetDllLibXls().ExcelFont_SetThemeColor, self.Ptr, enumtype,tint)

#
#    def GetThemeColor(self ,type:'ThemeColorType&',tint:'Double&')->bool:
#        """
#
#        """
#        intPtrtype:c_void_p = type.Ptr
#        intPtrtint:c_void_p = tint.Ptr
#
#        GetDllLibXls().ExcelFont_GetThemeColor.argtypes=[c_void_p ,c_void_p,c_void_p]
#        GetDllLibXls().ExcelFont_GetThemeColor.restype=c_bool
#        ret = CallCFunction(GetDllLibXls().ExcelFont_GetThemeColor, self.Ptr, intPtrtype,intPtrtint)
#        return ret


    @property
    def IsBold(self)->bool:
        """
        True if the font is bold.

        """
        GetDllLibXls().ExcelFont_get_IsBold.argtypes=[c_void_p]
        GetDllLibXls().ExcelFont_get_IsBold.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExcelFont_get_IsBold, self.Ptr)
        return ret

    @IsBold.setter
    def IsBold(self, value:bool):
        GetDllLibXls().ExcelFont_set_IsBold.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExcelFont_set_IsBold, self.Ptr, value)

    @property

    def FontName(self)->str:
        """
        Returns or sets the font name. Read / write string.

        """
        GetDllLibXls().ExcelFont_get_FontName.argtypes=[c_void_p]
        GetDllLibXls().ExcelFont_get_FontName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ExcelFont_get_FontName, self.Ptr))
        return ret


    @FontName.setter
    def FontName(self, value:str):
        GetDllLibXls().ExcelFont_set_FontName.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ExcelFont_set_FontName, self.Ptr, value)

    @property
    def Size(self)->float:
        """
        Returns or sets the size of the font. Read / write integer.

        """
        GetDllLibXls().ExcelFont_get_Size.argtypes=[c_void_p]
        GetDllLibXls().ExcelFont_get_Size.restype=c_double
        ret = CallCFunction(GetDllLibXls().ExcelFont_get_Size, self.Ptr)
        return ret

    @Size.setter
    def Size(self, value:float):
        GetDllLibXls().ExcelFont_set_Size.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().ExcelFont_set_Size, self.Ptr, value)

    @property
    def IsStrikethrough(self)->bool:
        """
        True if the font is struck through with a horizontal line. Read / write Boolean

        """
        GetDllLibXls().ExcelFont_get_IsStrikethrough.argtypes=[c_void_p]
        GetDllLibXls().ExcelFont_get_IsStrikethrough.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExcelFont_get_IsStrikethrough, self.Ptr)
        return ret

    @IsStrikethrough.setter
    def IsStrikethrough(self, value:bool):
        GetDllLibXls().ExcelFont_set_IsStrikethrough.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExcelFont_set_IsStrikethrough, self.Ptr, value)

    @property

    def StrikethroughType(self)->str:
        """

        """
        GetDllLibXls().ExcelFont_get_StrikethroughType.argtypes=[c_void_p]
        GetDllLibXls().ExcelFont_get_StrikethroughType.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ExcelFont_get_StrikethroughType, self.Ptr))
        return ret


    @StrikethroughType.setter
    def StrikethroughType(self, value:str):
        GetDllLibXls().ExcelFont_set_StrikethroughType.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ExcelFont_set_StrikethroughType, self.Ptr, value)

    @property
    def IsSubscript(self)->bool:
        """
        True if the font is formatted as subscript. False by default. Read / write Boolean.

        """
        GetDllLibXls().ExcelFont_get_IsSubscript.argtypes=[c_void_p]
        GetDllLibXls().ExcelFont_get_IsSubscript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExcelFont_get_IsSubscript, self.Ptr)
        return ret

    @IsSubscript.setter
    def IsSubscript(self, value:bool):
        GetDllLibXls().ExcelFont_set_IsSubscript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExcelFont_set_IsSubscript, self.Ptr, value)

    @property
    def IsSuperscript(self)->bool:
        """
        True if the font is formatted as superscript. False by default. Read/write Boolean

        """
        GetDllLibXls().ExcelFont_get_IsSuperscript.argtypes=[c_void_p]
        GetDllLibXls().ExcelFont_get_IsSuperscript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExcelFont_get_IsSuperscript, self.Ptr)
        return ret

    @IsSuperscript.setter
    def IsSuperscript(self, value:bool):
        GetDllLibXls().ExcelFont_set_IsSuperscript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExcelFont_set_IsSuperscript, self.Ptr, value)

    @property
    def IsAutoColor(self)->bool:
        """Gets whether the font color is automatically selected.
        
        When True, Excel automatically determines the font color based on the background
        or other contextual factors.
        
        Returns:
            bool: True if the font color is automatically selected; otherwise, False.
        """
        GetDllLibXls().ExcelFont_get_IsAutoColor.argtypes=[c_void_p]
        GetDllLibXls().ExcelFont_get_IsAutoColor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExcelFont_get_IsAutoColor, self.Ptr)
        return ret

    @property

    def Underline(self)->'FontUnderlineType':
        """Gets or sets the type of underline applied to the font.
        
        This property allows for different underline styles such as single, double,
        accounting, etc.
        
        Returns:
            FontUnderlineType: An enumeration value representing the underline type.
        """
        GetDllLibXls().ExcelFont_get_Underline.argtypes=[c_void_p]
        GetDllLibXls().ExcelFont_get_Underline.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelFont_get_Underline, self.Ptr)
        objwraped = FontUnderlineType(ret)
        return objwraped

    @Underline.setter
    def Underline(self, value:'FontUnderlineType'):
        GetDllLibXls().ExcelFont_set_Underline.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelFont_set_Underline, self.Ptr, value.value)

    @property

    def VerticalAlignment(self)->'FontVertialAlignmentType':
        """Gets or sets the vertical alignment of the font.
        
        This property controls whether text appears as normal, subscript, or superscript.
        
        Returns:
            FontVertialAlignmentType: An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().ExcelFont_get_VerticalAlignment.argtypes=[c_void_p]
        GetDllLibXls().ExcelFont_get_VerticalAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelFont_get_VerticalAlignment, self.Ptr)
        objwraped = FontVertialAlignmentType(ret)
        return objwraped

    @VerticalAlignment.setter
    def VerticalAlignment(self, value:'FontVertialAlignmentType'):
        GetDllLibXls().ExcelFont_set_VerticalAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelFont_set_VerticalAlignment, self.Ptr, value.value)


    def GenerateNativeFont(self)->'Font':
        """Generates a system font object based on this Excel font.
        
        This method creates a Font object that can be used with the system's drawing
        functions, representing the same visual attributes as this Excel font.
        
        Returns:
            Font: A system Font object with the same properties as this Excel font.
        """
        GetDllLibXls().ExcelFont_GenerateNativeFont.argtypes=[c_void_p]
        GetDllLibXls().ExcelFont_GenerateNativeFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelFont_GenerateNativeFont, self.Ptr)
        ret = None if intPtr==None else Font(intPtr)
        return ret


    @property

    def Parent(self)->'SpireObject':
        """Gets the parent object of this font.
        
        The parent object is typically the cell, range, or style that contains this font.
        
        Returns:
            SpireObject: The parent object that contains this font.
        """
        GetDllLibXls().ExcelFont_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().ExcelFont_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelFont_get_Parent, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    def BeginUpdate(self):
        """Begins a batch update operation on the font.
        
        This method marks the start of a series of changes to the font properties.
        Multiple property changes can be made more efficiently by calling BeginUpdate
        before making the changes and EndUpdate after all changes are complete.
        """
        GetDllLibXls().ExcelFont_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().ExcelFont_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """Ends a batch update operation on the font.
        
        This method should be called after BeginUpdate and all desired property
        changes have been made. It applies all pending changes to the font properties.
        """
        GetDllLibXls().ExcelFont_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().ExcelFont_EndUpdate, self.Ptr)

