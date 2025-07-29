from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class FontWrapper (  CommonWrapper, IInternalFont) :
    """Represents a wrapper for font operations in Excel.
    
    This class provides methods and properties for manipulating font attributes
    in Excel worksheets, including font style, color, size, and other formatting
    characteristics. It implements the IInternalFont interface and extends the
    CommonWrapper class to provide font-specific functionality.
    """
    @property

    def Parent(self)->'SpireObject':
        """Gets the parent object of this FontWrapper.
        
        Returns:
            SpireObject: The parent object that contains this font wrapper.
        """
        GetDllLibXls().FontWrapper_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().FontWrapper_get_Parent, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    def BeginUpdate(self):
        """Begins a batch update operation on the font properties.
        
        This method should be called before making multiple changes to font properties
        to improve performance by deferring the actual updates until EndUpdate is called.
        """
        GetDllLibXls().FontWrapper_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().FontWrapper_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """Ends a batch update operation and applies all pending changes to font properties.
        
        This method should be called after BeginUpdate to apply all the changes made
        to font properties in a single operation, improving performance.
        """
        GetDllLibXls().FontWrapper_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().FontWrapper_EndUpdate, self.Ptr)

#
#    def add_AfterChangeEvent(self ,value:'EventHandler'):
#        """
#
#        """
#        intPtrvalue:c_void_p = value.Ptr
#
#        GetDllLibXls().FontWrapper_add_AfterChangeEvent.argtypes=[c_void_p ,c_void_p]
#        CallCFunction(GetDllLibXls().FontWrapper_add_AfterChangeEvent, self.Ptr, intPtrvalue)


#
#    def remove_AfterChangeEvent(self ,value:'EventHandler'):
#        """
#
#        """
#        intPtrvalue:c_void_p = value.Ptr
#
#        GetDllLibXls().FontWrapper_remove_AfterChangeEvent.argtypes=[c_void_p ,c_void_p]
#        CallCFunction(GetDllLibXls().FontWrapper_remove_AfterChangeEvent, self.Ptr, intPtrvalue)


    @property
    def IsBold(self)->bool:
        """Gets or sets a value indicating whether the font is bold.
        
        Returns:
            bool: True if the font is bold; otherwise, False.
        """
        GetDllLibXls().FontWrapper_get_IsBold.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_IsBold.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FontWrapper_get_IsBold, self.Ptr)
        return ret

    @IsBold.setter
    def IsBold(self, value:bool):
        """Sets a value indicating whether the font is bold.
        
        Args:
            value (bool): True to set the font as bold; otherwise, False.
        """
        GetDllLibXls().FontWrapper_set_IsBold.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FontWrapper_set_IsBold, self.Ptr, value)

    @property

    def KnownColor(self)->'ExcelColors':
        """Gets or sets the predefined Excel color of the font.
        
        Returns:
            ExcelColors: An enumeration value representing the Excel color.
        """
        GetDllLibXls().FontWrapper_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().FontWrapper_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        """Sets the predefined Excel color of the font.
        
        Args:
            value (ExcelColors): An enumeration value representing the Excel color to set.
        """
        GetDllLibXls().FontWrapper_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().FontWrapper_set_KnownColor, self.Ptr, value.value)

    @property

    def Color(self)->'Color':
        """Gets or sets the primary color of the font.
        
        Returns:
            Color: A Color object representing the font color.
        """
        GetDllLibXls().FontWrapper_get_Color.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().FontWrapper_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        """Sets the primary color of the font.
        
        Args:
            value (Color): A Color object representing the font color to set.
        """
        GetDllLibXls().FontWrapper_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().FontWrapper_set_Color, self.Ptr, value.Ptr)


    def SetThemeColor(self ,type:'ThemeColorType',tint:float):
        """Sets a theme color for the font.
        
        Args:
            type (ThemeColorType): The type of theme color to set.
            tint (float): The tint value to apply to the theme color.
        """
        enumtype:c_int = type.value

        GetDllLibXls().FontWrapper_SetThemeColor.argtypes=[c_void_p ,c_int,c_double]
        CallCFunction(GetDllLibXls().FontWrapper_SetThemeColor, self.Ptr, enumtype,tint)

#
#    def GetThemeColor(self ,type:'ThemeColorType&',tint:'Double&')->bool:
#        """
#
#        """
#        intPtrtype:c_void_p = type.Ptr
#        intPtrtint:c_void_p = tint.Ptr
#
#        GetDllLibXls().FontWrapper_GetThemeColor.argtypes=[c_void_p ,c_void_p,c_void_p]
#        GetDllLibXls().FontWrapper_GetThemeColor.restype=c_bool
#        ret = CallCFunction(GetDllLibXls().FontWrapper_GetThemeColor, self.Ptr, intPtrtype,intPtrtint)
#        return ret


    @property
    def IsItalic(self)->bool:
        """Gets or sets a value indicating whether the font style is italic.
        
        Returns:
            bool: True if the font is italic; otherwise, False.
        """
        GetDllLibXls().FontWrapper_get_IsItalic.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_IsItalic.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FontWrapper_get_IsItalic, self.Ptr)
        return ret

    @IsItalic.setter
    def IsItalic(self, value:bool):
        """Sets a value indicating whether the font style is italic.
        
        Args:
            value (bool): True to set the font as italic; otherwise, False.
        """
        GetDllLibXls().FontWrapper_set_IsItalic.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FontWrapper_set_IsItalic, self.Ptr, value)

    @property
    def MacOSOutlineFont(self)->bool:
        """Gets or sets a value indicating whether the font is an outline font.
        
        Returns:
            bool: True if the font is an outline font; otherwise, False.
        """
        GetDllLibXls().FontWrapper_get_MacOSOutlineFont.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_MacOSOutlineFont.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FontWrapper_get_MacOSOutlineFont, self.Ptr)
        return ret

    @MacOSOutlineFont.setter
    def MacOSOutlineFont(self, value:bool):
        """Sets a value indicating whether the font is an outline font.
        
        Args:
            value (bool): True to set the font as an outline font; otherwise, False.
        """
        GetDllLibXls().FontWrapper_set_MacOSOutlineFont.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FontWrapper_set_MacOSOutlineFont, self.Ptr, value)

    @property
    def MacOSShadow(self)->bool:
        """Gets or sets a value indicating whether the font is a shadow font or if the object has a shadow.
        
        Returns:
            bool: True if the font is a shadow font or the object has a shadow; otherwise, False.
        """
        GetDllLibXls().FontWrapper_get_MacOSShadow.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_MacOSShadow.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FontWrapper_get_MacOSShadow, self.Ptr)
        return ret

    @MacOSShadow.setter
    def MacOSShadow(self, value:bool):
        """Sets a value indicating whether the font is a shadow font or if the object has a shadow.
        
        Args:
            value (bool): True to set the font as a shadow font or give the object a shadow; otherwise, False.
        """
        GetDllLibXls().FontWrapper_set_MacOSShadow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FontWrapper_set_MacOSShadow, self.Ptr, value)

    @property
    def Size(self)->float:
        """Gets or sets the size of the font in points.
        
        Returns:
            float: The font size in points.
        """
        GetDllLibXls().FontWrapper_get_Size.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_Size.restype=c_double
        ret = CallCFunction(GetDllLibXls().FontWrapper_get_Size, self.Ptr)
        return ret

    @Size.setter
    def Size(self, value:float):
        """Sets the size of the font in points.
        
        Args:
            value (float): The font size in points to set.
        """
        GetDllLibXls().FontWrapper_set_Size.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().FontWrapper_set_Size, self.Ptr, value)

    @property
    def IsStrikethrough(self)->bool:
        """Gets or sets a value indicating whether the font is struck through with a horizontal line.
        
        Returns:
            bool: True if the font has a strikethrough; otherwise, False.
        """
        GetDllLibXls().FontWrapper_get_IsStrikethrough.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_IsStrikethrough.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FontWrapper_get_IsStrikethrough, self.Ptr)
        return ret

    @IsStrikethrough.setter
    def IsStrikethrough(self, value:bool):
        """Sets a value indicating whether the font is struck through with a horizontal line.
        
        Args:
            value (bool): True to apply strikethrough to the font; otherwise, False.
        """
        GetDllLibXls().FontWrapper_set_IsStrikethrough.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FontWrapper_set_IsStrikethrough, self.Ptr, value)

    @property

    def StrikethroughType(self)->str:
        """Gets the type of strikethrough applied to the font.
        
        Returns:
            str: A string representing the type of strikethrough.
        """
        GetDllLibXls().FontWrapper_get_StrikethroughType.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_StrikethroughType.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().FontWrapper_get_StrikethroughType, self.Ptr))
        return ret


    @StrikethroughType.setter
    def StrikethroughType(self, value:str):
        """Sets the type of strikethrough applied to the font.
        
        Args:
            value (str): A string representing the type of strikethrough to apply.
        """
        GetDllLibXls().FontWrapper_set_StrikethroughType.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().FontWrapper_set_StrikethroughType, self.Ptr, value)

    @property
    def IsSubscript(self)->bool:
        """Gets or sets a value indicating whether the font is formatted as subscript.
        
        Returns:
            bool: True if the font is subscript; otherwise, False.
        """
        GetDllLibXls().FontWrapper_get_IsSubscript.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_IsSubscript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FontWrapper_get_IsSubscript, self.Ptr)
        return ret

    @IsSubscript.setter
    def IsSubscript(self, value:bool):
        """Sets a value indicating whether the font is formatted as subscript.
        
        Args:
            value (bool): True to set the font as subscript; otherwise, False.
        """
        GetDllLibXls().FontWrapper_set_IsSubscript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FontWrapper_set_IsSubscript, self.Ptr, value)

    @property
    def IsSuperscript(self)->bool:
        """Gets or sets a value indicating whether the font is formatted as superscript.
        
        Returns:
            bool: True if the font is superscript; otherwise, False.
        """
        GetDllLibXls().FontWrapper_get_IsSuperscript.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_IsSuperscript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FontWrapper_get_IsSuperscript, self.Ptr)
        return ret

    @IsSuperscript.setter
    def IsSuperscript(self, value:bool):
        """Sets a value indicating whether the font is formatted as superscript.
        
        Args:
            value (bool): True to set the font as superscript; otherwise, False.
        """
        GetDllLibXls().FontWrapper_set_IsSuperscript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FontWrapper_set_IsSuperscript, self.Ptr, value)

    @property

    def Underline(self)->'FontUnderlineType':
        """Gets or sets the type of underline applied to the font.
        
        Returns:
            FontUnderlineType: An enumeration value representing the underline type.
        """
        GetDllLibXls().FontWrapper_get_Underline.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_Underline.restype=c_int
        ret = CallCFunction(GetDllLibXls().FontWrapper_get_Underline, self.Ptr)
        objwraped = FontUnderlineType(ret)
        return objwraped

    @Underline.setter
    def Underline(self, value:'FontUnderlineType'):
        """Sets the type of underline applied to the font.
        
        Args:
            value (FontUnderlineType): An enumeration value representing the underline type to apply.
        """
        GetDllLibXls().FontWrapper_set_Underline.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().FontWrapper_set_Underline, self.Ptr, value.value)

    @property

    def FontName(self)->str:
        """Gets or sets the name of the font.
        
        Returns:
            str: The name of the font.
        """
        GetDllLibXls().FontWrapper_get_FontName.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_FontName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().FontWrapper_get_FontName, self.Ptr))
        return ret


    @FontName.setter
    def FontName(self, value:str):
        """Sets the name of the font.
        
        Args:
            value (str): The name of the font to set.
        """
        GetDllLibXls().FontWrapper_set_FontName.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().FontWrapper_set_FontName, self.Ptr, value)

    @property

    def VerticalAlignment(self)->'FontVertialAlignmentType':
        """Gets the vertical alignment of the font.
        
        Returns:
            FontVertialAlignmentType: An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().FontWrapper_get_VerticalAlignment.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_VerticalAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().FontWrapper_get_VerticalAlignment, self.Ptr)
        objwraped = FontVertialAlignmentType(ret)
        return objwraped

    @VerticalAlignment.setter
    def VerticalAlignment(self, value:'FontVertialAlignmentType'):
        """Sets the vertical alignment of the font.
        
        Args:
            value (FontVertialAlignmentType): An enumeration value representing the vertical alignment to set.
        """
        GetDllLibXls().FontWrapper_set_VerticalAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().FontWrapper_set_VerticalAlignment, self.Ptr, value.value)


    def GenerateNativeFont(self)->'Font':
        """Generates a native Font object from this FontWrapper.
        
        Returns:
            Font: A Font object representing the font settings in this wrapper.
        """
        GetDllLibXls().FontWrapper_GenerateNativeFont.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_GenerateNativeFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().FontWrapper_GenerateNativeFont, self.Ptr)
        ret = None if intPtr==None else Font(intPtr)
        return ret


    @property
    def IsAutoColor(self)->bool:
        """Gets a value indicating whether the font color is set to automatic.
        
        Returns:
            bool: True if the font color is automatic; otherwise, False.
        """
        GetDllLibXls().FontWrapper_get_IsAutoColor.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_IsAutoColor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FontWrapper_get_IsAutoColor, self.Ptr)
        return ret

    @property
    def Index(self)->int:
        """Gets the index of the font in the collection.
        
        Returns:
            int: The index of the font.
        """
        GetDllLibXls().FontWrapper_get_Index.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_Index.restype=c_int
        ret = CallCFunction(GetDllLibXls().FontWrapper_get_Index, self.Ptr)
        return ret

    @property

    def Font(self)->'XlsFont':
        """Gets the internal XlsFont object.
        
        Returns:
            XlsFont: The internal font object.
        """
        GetDllLibXls().FontWrapper_get_Font.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_Font.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().FontWrapper_get_Font, self.Ptr)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret


    @property
    def FontIndex(self)->int:
        """Gets the index of the font in the fonts collection.
        
        Returns:
            int: The index of the font.
        """
        GetDllLibXls().FontWrapper_get_FontIndex.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_FontIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().FontWrapper_get_FontIndex, self.Ptr)
        return ret

    @property
    def IsReadOnly(self)->bool:
        """Gets or sets a value indicating whether the font is read-only.
        
        Returns:
            bool: True if the font is read-only; otherwise, False.
        """
        GetDllLibXls().FontWrapper_get_IsReadOnly.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_IsReadOnly.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FontWrapper_get_IsReadOnly, self.Ptr)
        return ret

    @IsReadOnly.setter
    def IsReadOnly(self, value:bool):
        """Sets a value indicating whether the font is read-only.
        
        Args:
            value (bool): True to set the font as read-only; otherwise, False.
        """
        GetDllLibXls().FontWrapper_set_IsReadOnly.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FontWrapper_set_IsReadOnly, self.Ptr, value)

    @property

    def Workbook(self)->'XlsWorkbook':
        """Gets the workbook that contains this font.
        
        Returns:
            XlsWorkbook: The parent workbook object.
        """
        GetDllLibXls().FontWrapper_get_Workbook.argtypes=[c_void_p]
        GetDllLibXls().FontWrapper_get_Workbook.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().FontWrapper_get_Workbook, self.Ptr)
        ret = None if intPtr==None else XlsWorkbook(intPtr)
        return ret


    def ColorObjectUpdate(self):
        """Updates the color object associated with this font.
        
        This method refreshes the color properties of the font after changes.
        """
        GetDllLibXls().FontWrapper_ColorObjectUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().FontWrapper_ColorObjectUpdate, self.Ptr)


    def Clone(self ,book:'XlsWorkbook',parent:'SpireObject',dicFontIndexes:'IDictionary')->'FontWrapper':
        """Creates a clone of this FontWrapper object.
        
        Args:
            book (XlsWorkbook): The workbook for the cloned font.
            parent (SpireObject): The parent object for the cloned font.
            dicFontIndexes (IDictionary): A dictionary mapping font indexes.
            
        Returns:
            FontWrapper: A new FontWrapper object that is a copy of this instance.
        """
        intPtrbook:c_void_p = book.Ptr
        intPtrparent:c_void_p = parent.Ptr
        intPtrdicFontIndexes:c_void_p = dicFontIndexes.Ptr

        GetDllLibXls().FontWrapper_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p]
        GetDllLibXls().FontWrapper_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().FontWrapper_Clone, self.Ptr, intPtrbook,intPtrparent,intPtrdicFontIndexes)
        ret = None if intPtr==None else FontWrapper(intPtr)
        return ret


