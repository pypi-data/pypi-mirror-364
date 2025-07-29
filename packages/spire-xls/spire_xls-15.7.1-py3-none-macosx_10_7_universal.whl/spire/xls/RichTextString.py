from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class RichTextString (  CommonWrapper, IRichTextString, IExcelApplication) :
    """Represents a base class for rich text strings in Excel.
    
    This class implements the IRichTextString and IExcelApplication interfaces and serves
    as a base class for other rich text implementations. It provides core functionality
    for creating and manipulating text with different formatting applied to different parts.
    """
    @property

    def Parent(self)->'SpireObject':
        """Gets the parent object that contains this rich text string.
        
        Returns:
            SpireObject: The parent object that contains this rich text string.
        """
        GetDllLibXls().RichTextString_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().RichTextString_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RichTextString_get_Parent, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def GetFont(self ,index:int)->'IFont':
        """Gets the font used at the specified character position in the text.
        
        Args:
            index (int): The zero-based character position in the text.
            
        Returns:
            IFont: The font object used at the specified position.
        """
        
        GetDllLibXls().RichTextString_GetFont.argtypes=[c_void_p ,c_int]
        GetDllLibXls().RichTextString_GetFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RichTextString_GetFont, self.Ptr, index)
        ret = None if intPtr==None else FontWrapper(intPtr)
        return ret



    def SetFont(self ,startIndex:int,endIndex:int,font:'IFont'):
        """Sets the font for a range of characters in the text.
        
        Args:
            startIndex (int): The zero-based starting character position.
            endIndex (int): The zero-based ending character position (inclusive).
            font (IFont): The font to apply to the specified range of characters.
        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RichTextString_SetFont.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().RichTextString_SetFont, self.Ptr, startIndex,endIndex,intPtrfont)

    def ClearFormatting(self):
        """Clears all formatting from the rich text.
        
        This method removes all formatting information while preserving the text content,
        resulting in plain text with default formatting.
        """
        GetDllLibXls().RichTextString_ClearFormatting.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RichTextString_ClearFormatting, self.Ptr)

    def Clear(self):
        """Clears both the text content and formatting.
        
        This method removes all text and formatting information, resulting in an empty
        rich text string.
        """
        GetDllLibXls().RichTextString_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RichTextString_Clear, self.Ptr)


    def Append(self ,text:str,font:'IFont'):
        """Appends text with the specified font to the end of the rich text.
        
        Args:
            text (str): The text to append.
            font (IFont): The font to apply to the appended text.
        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RichTextString_Append.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().RichTextString_Append, self.Ptr, text,intPtrfont)

    @property

    def Text(self)->str:
        """Gets or sets the plain text content of the rich text string.
        
        When setting this property, any existing formatting is preserved and applied
        to the new text content where applicable.
        
        Returns:
            str: The plain text content without formatting information.
        """
        GetDllLibXls().RichTextString_get_Text.argtypes=[c_void_p]
        GetDllLibXls().RichTextString_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().RichTextString_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        GetDllLibXls().RichTextString_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().RichTextString_set_Text, self.Ptr, value)

    @property

    def RtfText(self)->str:
        """Gets the text content in Rich Text Format (RTF).
        
        This property returns the text with all formatting information encoded in RTF format,
        which can be used for interoperability with other applications that support RTF.
        
        Returns:
            str: The text content in RTF format.
        """
        GetDllLibXls().RichTextString_get_RtfText.argtypes=[c_void_p]
        GetDllLibXls().RichTextString_get_RtfText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().RichTextString_get_RtfText, self.Ptr))
        return ret


    @property
    def IsFormatted(self)->bool:
        """Gets whether the rich text contains any formatting.
        
        Returns:
            bool: True if the text contains formatting (different fonts, colors, etc.);
                 otherwise, False.
        """
        GetDllLibXls().RichTextString_get_IsFormatted.argtypes=[c_void_p]
        GetDllLibXls().RichTextString_get_IsFormatted.restype=c_bool
        ret = CallCFunction(GetDllLibXls().RichTextString_get_IsFormatted, self.Ptr)
        return ret

    @property

    def DefaultFont(self)->'XlsFont':
        """Gets the default font for this rich text string.
        
        The default font is used for any portion of the text that doesn't have
        specific formatting applied.
        
        Returns:
            XlsFont: The default font object for the rich text string.
        """
        GetDllLibXls().RichTextString_get_DefaultFont.argtypes=[c_void_p]
        GetDllLibXls().RichTextString_get_DefaultFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RichTextString_get_DefaultFont, self.Ptr)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret


