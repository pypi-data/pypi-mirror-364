from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class RTFCommentArray (  XlsObject, IRichTextString, IOptimizedUpdate) :
    """Represents an array of rich text comments in Excel.
    
    This class implements the IRichTextString and IOptimizedUpdate interfaces and provides
    functionality for managing arrays of rich text comments in Excel worksheets.
    It allows for formatting and manipulating the text content of multiple comments.
    """

    def GetFont(self ,iPosition:int)->'IFont':
        """Gets the font used at the specified character position in the comment text.
        
        Args:
            iPosition (int): The zero-based character position in the text.
            
        Returns:
            IFont: The font object used at the specified position.
        """
        
        GetDllLibXls().RTFCommentArray_GetFont.argtypes=[c_void_p ,c_int]
        GetDllLibXls().RTFCommentArray_GetFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RTFCommentArray_GetFont, self.Ptr, iPosition)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret



    def SetFont(self ,iStartPos:int,iEndPos:int,font:'IFont'):
        """Sets the font for a range of characters in the comment text.
        
        Args:
            iStartPos (int): The zero-based starting character position.
            iEndPos (int): The zero-based ending character position (inclusive).
            font (IFont): The font to apply to the specified range of characters.
        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RTFCommentArray_SetFont.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().RTFCommentArray_SetFont, self.Ptr, iStartPos,iEndPos,intPtrfont)

    def ClearFormatting(self):
        """Clears all formatting from the comment text.
        
        This method removes all formatting information while preserving the text content,
        resulting in plain text with default formatting.
        """
        GetDllLibXls().RTFCommentArray_ClearFormatting.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RTFCommentArray_ClearFormatting, self.Ptr)


    def Append(self ,text:str,font:'IFont'):
        """Appends text with the specified font to the end of the comment text.
        
        Args:
            text (str): The text to append.
            font (IFont): The font to apply to the appended text.
        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RTFCommentArray_Append.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().RTFCommentArray_Append, self.Ptr, text,intPtrfont)

    def Clear(self):
        """Clears both the text content and formatting of the comments.
        
        This method removes all text and formatting information, resulting in empty
        comment text.
        """
        GetDllLibXls().RTFCommentArray_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RTFCommentArray_Clear, self.Ptr)

    @property

    def Text(self)->str:
        """Gets or sets the plain text content of the comment.
        
        When setting this property, any existing formatting is preserved and applied
        to the new text content where applicable.
        
        Returns:
            str: The plain text content without formatting information.
        """
        GetDllLibXls().RTFCommentArray_get_Text.argtypes=[c_void_p]
        GetDllLibXls().RTFCommentArray_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().RTFCommentArray_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        GetDllLibXls().RTFCommentArray_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().RTFCommentArray_set_Text, self.Ptr, value)

    @property

    def RtfText(self)->str:
        """Gets the text content in Rich Text Format (RTF).
        
        This property returns the text with all formatting information encoded in RTF format,
        which can be used for interoperability with other applications that support RTF.
        
        Returns:
            str: The text content in RTF format.
        """
        GetDllLibXls().RTFCommentArray_get_RtfText.argtypes=[c_void_p]
        GetDllLibXls().RTFCommentArray_get_RtfText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().RTFCommentArray_get_RtfText, self.Ptr))
        return ret


    @property
    def IsFormatted(self)->bool:
        """Gets whether the comment text contains any formatting.
        
        Returns:
            bool: True if the text contains formatting (different fonts, colors, etc.);
                 otherwise, False.
        """
        GetDllLibXls().RTFCommentArray_get_IsFormatted.argtypes=[c_void_p]
        GetDllLibXls().RTFCommentArray_get_IsFormatted.restype=c_bool
        ret = CallCFunction(GetDllLibXls().RTFCommentArray_get_IsFormatted, self.Ptr)
        return ret

    def BeginUpdate(self):
        """Begins a batch update operation on the comment array.
        
        This method marks the start of a series of changes to the comment array.
        Multiple changes can be made more efficiently by calling BeginUpdate
        before making the changes and EndUpdate after all changes are complete.
        """
        GetDllLibXls().RTFCommentArray_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RTFCommentArray_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """Ends a batch update operation on the comment array.
        
        This method should be called after BeginUpdate and all desired changes
        have been made. It applies all pending changes to the comment array.
        """
        GetDllLibXls().RTFCommentArray_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RTFCommentArray_EndUpdate, self.Ptr)

