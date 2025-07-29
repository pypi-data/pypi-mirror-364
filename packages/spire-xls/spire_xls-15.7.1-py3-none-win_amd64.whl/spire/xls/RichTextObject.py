from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class RichTextObject (  SpireObject, IRichTextString) :
    """Represents a rich text object that can contain text with multiple formatting runs.
    
    This class implements the IRichTextString interface and provides functionality for 
    creating and manipulating text with different formatting applied to different parts.
    Rich text objects can be used in cell values, comments, and other text containers in Excel.
    """

    def GetFont(self ,position:int)->'XlsFont':
        """Gets the font used at the specified character position in the text.
        
        Args:
            position (int): The zero-based character position in the text.
            
        Returns:
            XlsFont: The font object used at the specified position.
        """
        
        GetDllLibXls().RichTextObject_GetFont.argtypes=[c_void_p ,c_int]
        GetDllLibXls().RichTextObject_GetFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RichTextObject_GetFont, self.Ptr, position)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret



    def SetFont(self ,startPos:int,endPos:int,font:'IFont'):
        """Sets the font for a range of characters in the text.
        
        Args:
            startPos (int): The zero-based starting character position.
            endPos (int): The zero-based ending character position (inclusive).
            font (IFont): The font to apply to the specified range of characters.
        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RichTextObject_SetFont.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().RichTextObject_SetFont, self.Ptr, startPos,endPos,intPtrfont)

    def ClearFormatting(self):
        """Clears all formatting from the rich text.
        
        This method removes all formatting information while preserving the text content,
        resulting in plain text with default formatting.
        """
        GetDllLibXls().RichTextObject_ClearFormatting.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RichTextObject_ClearFormatting, self.Ptr)

    def Clear(self):
        """Clears both the text content and formatting.
        
        This method removes all text and formatting information, resulting in an empty
        rich text object.
        """
        GetDllLibXls().RichTextObject_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RichTextObject_Clear, self.Ptr)

    @property

    def Text(self)->str:
        """Gets or sets the plain text content of the rich text object.
        
        When setting this property, any existing formatting is preserved and applied
        to the new text content where applicable.
        
        Returns:
            str: The plain text content without formatting information.
        """
        GetDllLibXls().RichTextObject_get_Text.argtypes=[c_void_p]
        GetDllLibXls().RichTextObject_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().RichTextObject_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        GetDllLibXls().RichTextObject_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().RichTextObject_set_Text, self.Ptr, value)

    @property

    def RtfText(self)->str:
        """Gets the text content in Rich Text Format (RTF).
        
        This property returns the text with all formatting information encoded in RTF format,
        which can be used for interoperability with other applications that support RTF.
        
        Returns:
            str: The text content in RTF format.
        """
        GetDllLibXls().RichTextObject_get_RtfText.argtypes=[c_void_p]
        GetDllLibXls().RichTextObject_get_RtfText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().RichTextObject_get_RtfText, self.Ptr))
        return ret


    @property
    def IsFormatted(self)->bool:
        """Gets whether the rich text contains any formatting.
        
        Returns:
            bool: True if the text contains formatting (different fonts, colors, etc.);
                 otherwise, False.
        """
        GetDllLibXls().RichTextObject_get_IsFormatted.argtypes=[c_void_p]
        GetDllLibXls().RichTextObject_get_IsFormatted.restype=c_bool
        ret = CallCFunction(GetDllLibXls().RichTextObject_get_IsFormatted, self.Ptr)
        return ret

    @property

    def Parent(self)->'SpireObject':
        """Gets the parent object that contains this rich text object.
        
        Returns:
            SpireObject: The parent object that contains this rich text object.
        """
        GetDllLibXls().RichTextObject_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().RichTextObject_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RichTextObject_get_Parent, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    def BeginUpdate(self):
        """Begins a batch update operation on the rich text object.
        
        This method marks the start of a series of changes to the rich text object.
        Multiple changes can be made more efficiently by calling BeginUpdate
        before making the changes and EndUpdate after all changes are complete.
        """
        GetDllLibXls().RichTextObject_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RichTextObject_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """Ends a batch update operation on the rich text object.
        
        This method should be called after BeginUpdate and all desired changes
        have been made. It applies all pending changes to the rich text object.
        """
        GetDllLibXls().RichTextObject_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RichTextObject_EndUpdate, self.Ptr)


    def Append(self ,text:str,font:'IFont'):
        """Appends text with the specified font to the end of the rich text.
        
        Args:
            text (str): The text to append.
            font (IFont): The font to apply to the appended text.
        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RichTextObject_Append.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().RichTextObject_Append, self.Ptr, text,intPtrfont)

