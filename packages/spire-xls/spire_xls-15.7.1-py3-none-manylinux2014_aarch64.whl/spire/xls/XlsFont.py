from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsFont (  XlsObject, IFont, IOptimizedUpdate, ICloneParent) :
    """Represents a font in an Excel worksheet.
    
    This class provides properties and methods for manipulating fonts in Excel,
    including font style, size, color, and other formatting options. It extends XlsObject and
    implements the IFont, IOptimizedUpdate, and ICloneParent interfaces.
    """

    def Clone(self ,parent:'SpireObject')->'XlsFont':
        """Creates a clone of this font.
        
        Args:
            parent (SpireObject): The parent object for the cloned font.
            
        Returns:
            XlsFont: A new instance of the font with the same formatting.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsFont_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsFont_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsFont_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret



    def CompareTo(self ,obj:'SpireObject')->int:
        """Compares the current font with another object.
        
        Args:
            obj (SpireObject): The object to compare with the current font.
            
        Returns:
            int: A value that indicates the relative order of the objects being compared.
                 Less than zero: This font precedes obj in the sort order.
                 Zero: This font occurs in the same position in the sort order as obj.
                 Greater than zero: This font follows obj in the sort order.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibXls().XlsFont_CompareTo.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsFont_CompareTo.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsFont_CompareTo, self.Ptr, intPtrobj)
        return ret

    @property
    def IsAutoColor(self)->bool:
        """Gets whether the font color is automatically determined.
        
        Returns:
            bool: True if the font color is automatically determined; otherwise, False.
        """
        GetDllLibXls().XlsFont_get_IsAutoColor.argtypes=[c_void_p]
        GetDllLibXls().XlsFont_get_IsAutoColor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsFont_get_IsAutoColor, self.Ptr)
        return ret

    @property
    def IsBold(self)->bool:
        """Gets or sets whether the font is bold.
        
        Returns:
            bool: True if the font is bold; otherwise, False.
        """
        GetDllLibXls().XlsFont_get_IsBold.argtypes=[c_void_p]
        GetDllLibXls().XlsFont_get_IsBold.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsFont_get_IsBold, self.Ptr)
        return ret

    @IsBold.setter
    def IsBold(self, value:bool):
        """Sets whether the font is bold.
        
        Args:
            value (bool): True to make the font bold; otherwise, False.
        """
        GetDllLibXls().XlsFont_set_IsBold.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsFont_set_IsBold, self.Ptr, value)

    @property

    def OColor(self)->'OColor':
        """Gets the Office color of the font.
        
        Returns:
            OColor: An object representing the Office color of the font.
        """
        GetDllLibXls().XlsFont_get_OColor.argtypes=[c_void_p]
        GetDllLibXls().XlsFont_get_OColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsFont_get_OColor, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def KnownColor(self)->'ExcelColors':
        """Gets or sets a predefined Excel color for the font.
        
        Returns:
            ExcelColors: An enumeration value representing the Excel color.
        """
        GetDllLibXls().XlsFont_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsFont_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsFont_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        """Sets a predefined Excel color for the font.
        
        Args:
            value (ExcelColors): An enumeration value representing the Excel color.
        """
        GetDllLibXls().XlsFont_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsFont_set_KnownColor, self.Ptr, value.value)

    @property

    def Color(self)->'Color':
        """Gets or sets the color of the font.
        
        Returns:
            Color: A Color object representing the font color.
        """
        GetDllLibXls().XlsFont_get_Color.argtypes=[c_void_p]
        GetDllLibXls().XlsFont_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsFont_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        """Sets the color of the font.
        
        Args:
            value (Color): A Color object representing the font color.
        """
        GetDllLibXls().XlsFont_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsFont_set_Color, self.Ptr, value.Ptr)


    def SetThemeColor(self ,type:'ThemeColorType',tint:float):
        """Sets a theme color for the font.
        
        Args:
            type (ThemeColorType): The theme color type to set.
            tint (float): The tint value to apply to the theme color.
        """
        enumtype:c_int = type.value

        GetDllLibXls().XlsFont_SetThemeColor.argtypes=[c_void_p ,c_int,c_double]
        CallCFunction(GetDllLibXls().XlsFont_SetThemeColor, self.Ptr, enumtype,tint)

#
#    def GetThemeColor(self ,type:'ThemeColorType&',tint:'Double&')->bool:
#        """
#
#        """
#        intPtrtype:c_void_p = type.Ptr
#        intPtrtint:c_void_p = tint.Ptr
#
#        GetDllLibXls().XlsFont_GetThemeColor.argtypes=[c_void_p ,c_void_p,c_void_p]
#        GetDllLibXls().XlsFont_GetThemeColor.restype=c_bool
#        ret = CallCFunction(GetDllLibXls().XlsFont_GetThemeColor, self.Ptr, intPtrtype,intPtrtint)
#        return ret


    @property
    def IsItalic(self)->bool:
        """Gets or sets whether the font is italic.
        
        Returns:
            bool: True if the font is italic; otherwise, False.
        """
        GetDllLibXls().XlsFont_get_IsItalic.argtypes=[c_void_p]
        GetDllLibXls().XlsFont_get_IsItalic.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsFont_get_IsItalic, self.Ptr)
        return ret

    @IsItalic.setter
    def IsItalic(self, value:bool):
        """Sets whether the font is italic.
        
        Args:
            value (bool): True to make the font italic; otherwise, False.
        """
        GetDllLibXls().XlsFont_set_IsItalic.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsFont_set_IsItalic, self.Ptr, value)

    @property
    def Size(self)->float:
        """Gets or sets the size of the font in points.
        
        Returns:
            float: The size of the font in points.
        """
        GetDllLibXls().XlsFont_get_Size.argtypes=[c_void_p]
        GetDllLibXls().XlsFont_get_Size.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsFont_get_Size, self.Ptr)
        return ret

    @Size.setter
    def Size(self, value:float):
        """Sets the size of the font in points.
        
        Args:
            value (float): The size of the font in points.
        """
        GetDllLibXls().XlsFont_set_Size.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsFont_set_Size, self.Ptr, value)

    @property
    def IsStrikethrough(self)->bool:
        """Gets or sets whether the font has a strikethrough.
        
        Returns:
            bool: True if the font has a strikethrough; otherwise, False.
        """
        GetDllLibXls().XlsFont_get_IsStrikethrough.argtypes=[c_void_p]
        GetDllLibXls().XlsFont_get_IsStrikethrough.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsFont_get_IsStrikethrough, self.Ptr)
        return ret

    @IsStrikethrough.setter
    def IsStrikethrough(self, value:bool):
        """Sets whether the font has a strikethrough.
        
        Args:
            value (bool): True to apply a strikethrough to the font; otherwise, False.
        """
        GetDllLibXls().XlsFont_set_IsStrikethrough.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsFont_set_IsStrikethrough, self.Ptr, value)

    @property
    def IsSubscript(self)->bool:
        """Gets or sets whether the font is subscript.
        
        Returns:
            bool: True if the font is subscript; otherwise, False.
        """
        GetDllLibXls().XlsFont_get_IsSubscript.argtypes=[c_void_p]
        GetDllLibXls().XlsFont_get_IsSubscript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsFont_get_IsSubscript, self.Ptr)
        return ret

    @IsSubscript.setter
    def IsSubscript(self, value:bool):
        """Sets whether the font is subscript.
        
        Args:
            value (bool): True to make the font subscript; otherwise, False.
        """
        GetDllLibXls().XlsFont_set_IsSubscript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsFont_set_IsSubscript, self.Ptr, value)

    @property

    def StrikethroughType(self)->str:
        """Gets or sets the type of strikethrough for the font.
        
        Returns:
            str: The type of strikethrough for the font.
        """
        GetDllLibXls().XlsFont_get_StrikethroughType.argtypes=[c_void_p]
        GetDllLibXls().XlsFont_get_StrikethroughType.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsFont_get_StrikethroughType, self.Ptr))
        return ret


    @StrikethroughType.setter
    def StrikethroughType(self, value:str):
        """Sets the type of strikethrough for the font.
        
        Args:
            value (str): The type of strikethrough for the font.
        """
        GetDllLibXls().XlsFont_set_StrikethroughType.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsFont_set_StrikethroughType, self.Ptr, value)

    @property
    def IsSuperscript(self)->bool:
        """Gets or sets whether the font is superscript.
        
        Returns:
            bool: True if the font is superscript; otherwise, False.
        """
        GetDllLibXls().XlsFont_get_IsSuperscript.argtypes=[c_void_p]
        GetDllLibXls().XlsFont_get_IsSuperscript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsFont_get_IsSuperscript, self.Ptr)
        return ret

    @IsSuperscript.setter
    def IsSuperscript(self, value:bool):
        """Sets whether the font is superscript.
        
        Args:
            value (bool): True to make the font superscript; otherwise, False.
        """
        GetDllLibXls().XlsFont_set_IsSuperscript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsFont_set_IsSuperscript, self.Ptr, value)

    @property

    def Underline(self)->'FontUnderlineType':
        """Gets or sets the type of underline for the font.
        
        Returns:
            FontUnderlineType: An enumeration value representing the underline type.
        """
        GetDllLibXls().XlsFont_get_Underline.argtypes=[c_void_p]
        GetDllLibXls().XlsFont_get_Underline.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsFont_get_Underline, self.Ptr)
        objwraped = FontUnderlineType(ret)
        return objwraped

    @Underline.setter
    def Underline(self, value:'FontUnderlineType'):
        """Sets the type of underline for the font.
        
        Args:
            value (FontUnderlineType): An enumeration value representing the underline type.
        """
        GetDllLibXls().XlsFont_set_Underline.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsFont_set_Underline, self.Ptr, value.value)

    @property

    def FontName(self)->str:
        """Gets or sets the name of the font.
        
        Returns:
            str: The name of the font.
        """
        GetDllLibXls().XlsFont_get_FontName.argtypes=[c_void_p]
        GetDllLibXls().XlsFont_get_FontName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsFont_get_FontName, self.Ptr))
        return ret


    @FontName.setter
    def FontName(self, value:str):
        """Sets the name of the font.
        
        Args:
            value (str): The name of the font.
        """
        GetDllLibXls().XlsFont_set_FontName.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsFont_set_FontName, self.Ptr, value)

    @property

    def VerticalAlignment(self)->'FontVertialAlignmentType':
        """Gets or sets the vertical alignment of the font.
        
        Returns:
            FontVertialAlignmentType: An enumeration value representing the vertical alignment type.
        """
        GetDllLibXls().XlsFont_get_VerticalAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsFont_get_VerticalAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsFont_get_VerticalAlignment, self.Ptr)
        objwraped = FontVertialAlignmentType(ret)
        return objwraped

    @VerticalAlignment.setter
    def VerticalAlignment(self, value:'FontVertialAlignmentType'):
        """Sets the vertical alignment of the font.
        
        Args:
            value (FontVertialAlignmentType): An enumeration value representing the vertical alignment type.
        """
        GetDllLibXls().XlsFont_set_VerticalAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsFont_set_VerticalAlignment, self.Ptr, value.value)

    @property

    def Scheme(self)->str:
        """Gets or sets the font scheme.
        
        Returns:
            str: The font scheme.
        """
        GetDllLibXls().XlsFont_get_Scheme.argtypes=[c_void_p]
        GetDllLibXls().XlsFont_get_Scheme.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsFont_get_Scheme, self.Ptr))
        return ret


    @Scheme.setter
    def Scheme(self, value:str):
        """Sets the font scheme.
        
        Args:
            value (str): The font scheme to set.
        """
        GetDllLibXls().XlsFont_set_Scheme.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsFont_set_Scheme, self.Ptr, value)

    @dispatch

    def GenerateNativeFont(self)->Font:
        """Generates a native Font object from this XlsFont.
        
        Returns:
            Font: A native Font object with the properties of this XlsFont.
        """
        GetDllLibXls().XlsFont_GenerateNativeFont.argtypes=[c_void_p]
        GetDllLibXls().XlsFont_GenerateNativeFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsFont_GenerateNativeFont, self.Ptr)
        ret = None if intPtr==None else Font(intPtr)
        return ret


    @dispatch

    def GenerateNativeFont(self ,size:float)->Font:
        """Generates a native Font object from this XlsFont with a specified size.
        
        Args:
            size (float): The size of the font in points.
            
        Returns:
            Font: A native Font object with the properties of this XlsFont and the specified size.
        """
        
        GetDllLibXls().XlsFont_GenerateNativeFontS.argtypes=[c_void_p ,c_float]
        GetDllLibXls().XlsFont_GenerateNativeFontS.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsFont_GenerateNativeFontS, self.Ptr, size)
        ret = None if intPtr==None else Font(intPtr)
        return ret


    def BeginUpdate(self):
        """Begins a series of operations that modify the font.
        
        This method should be called before making multiple changes to the font
        to improve performance.
        """
        GetDllLibXls().XlsFont_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsFont_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """Ends a series of operations that modify the font.
        
        This method should be called after making multiple changes to the font
        to apply the changes and improve performance.
        """
        GetDllLibXls().XlsFont_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsFont_EndUpdate, self.Ptr)

    @property

    def Font(self)->'XlsFont':
        """Gets the font object.
        
        Returns:
            XlsFont: The font object.
        """
        GetDllLibXls().XlsFont_get_Font.argtypes=[c_void_p]
        GetDllLibXls().XlsFont_get_Font.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsFont_get_Font, self.Ptr)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret



    def MeasureString(self ,strValue:str)->'SizeF':
        """Measures the size of a string when drawn with this font.
        
        Args:
            strValue (str): The string to measure.
            
        Returns:
            SizeF: The size of the string in the current font.
        """
        
        GetDllLibXls().XlsFont_MeasureString.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsFont_MeasureString.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsFont_MeasureString, self.Ptr, strValue)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


