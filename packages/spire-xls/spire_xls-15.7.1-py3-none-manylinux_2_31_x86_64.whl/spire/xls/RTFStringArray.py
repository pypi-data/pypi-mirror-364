from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class RTFStringArray (  XlsObject, IRichTextString, IOptimizedUpdate) :
    """Represents an array of rich text strings in Excel.
    
    This class implements the IRichTextString and IOptimizedUpdate interfaces and provides
    functionality for managing arrays of rich text strings in Excel worksheets.
    It allows for formatting and manipulating the text content of multiple text strings.
    """

    def GetFont(self ,iPosition:int)->'IFont':
        """Gets the font used at the specified character position in the text.
        
        Args:
            iPosition (int): The zero-based character position in the text.
            
        Returns:
            IFont: The font object used at the specified position.
        """
        
        GetDllLibXls().RTFStringArray_GetFont.argtypes=[c_void_p ,c_int]
        GetDllLibXls().RTFStringArray_GetFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RTFStringArray_GetFont, self.Ptr, iPosition)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret



    def SetFont(self ,iStartPos:int,iEndPos:int,font:'IFont'):
        """Sets the font for a range of characters in the text.
        
        Args:
            iStartPos (int): The zero-based starting character position.
            iEndPos (int): The zero-based ending character position (inclusive).
            font (IFont): The font to apply to the specified range of characters.
        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RTFStringArray_SetFont.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().RTFStringArray_SetFont, self.Ptr, iStartPos,iEndPos,intPtrfont)

    def ClearFormatting(self):
        """Clears all formatting from the text strings.
        
        This method removes all formatting information while preserving the text content,
        resulting in plain text with default formatting.
        """
        GetDllLibXls().RTFStringArray_ClearFormatting.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RTFStringArray_ClearFormatting, self.Ptr)


    def Append(self ,text:str,font:'IFont'):
        """Appends text with the specified font to the end of the text string array.
        
        Args:
            text (str): The text to append.
            font (IFont): The font to apply to the appended text.
        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RTFStringArray_Append.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().RTFStringArray_Append, self.Ptr, text,intPtrfont)

    @property

    def Text(self)->str:
        """Gets or sets the plain text content of the string array.
        
        When setting this property, any existing formatting is preserved and applied
        to the new text content where applicable.
        
        Returns:
            str: The plain text content without formatting information.
        """
        GetDllLibXls().RTFStringArray_get_Text.argtypes=[c_void_p]
        GetDllLibXls().RTFStringArray_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().RTFStringArray_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        GetDllLibXls().RTFStringArray_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().RTFStringArray_set_Text, self.Ptr, value)

    @property

    def RtfText(self)->str:
        """Gets the text content in Rich Text Format (RTF).
        
        This property returns the text with all formatting information encoded in RTF format,
        which can be used for interoperability with other applications that support RTF.
        
        Returns:
            str: The text content in RTF format.
        """
        GetDllLibXls().RTFStringArray_get_RtfText.argtypes=[c_void_p]
        GetDllLibXls().RTFStringArray_get_RtfText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().RTFStringArray_get_RtfText, self.Ptr))
        return ret


    @property
    def IsFormatted(self)->bool:
        """Gets whether the text strings contain any formatting.
        
        Returns:
            bool: True if the text contains formatting (different fonts, colors, etc.);
                 otherwise, False.
        """
        GetDllLibXls().RTFStringArray_get_IsFormatted.argtypes=[c_void_p]
        GetDllLibXls().RTFStringArray_get_IsFormatted.restype=c_bool
        ret = CallCFunction(GetDllLibXls().RTFStringArray_get_IsFormatted, self.Ptr)
        return ret

    def Clear(self):
        """Clears both the text content and formatting of the string array.
        
        This method removes all text and formatting information, resulting in empty
        text strings.
        """
        GetDllLibXls().RTFStringArray_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RTFStringArray_Clear, self.Ptr)

    def BeginUpdate(self):
        """Begins a batch update operation on the string array.
        
        This method marks the start of a series of changes to the string array.
        Multiple changes can be made more efficiently by calling BeginUpdate
        before making the changes and EndUpdate after all changes are complete.
        """
        GetDllLibXls().RTFStringArray_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RTFStringArray_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """Ends a batch update operation on the string array.
        
        This method should be called after BeginUpdate and all desired changes
        have been made. It applies all pending changes to the string array.
        """
        GetDllLibXls().RTFStringArray_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RTFStringArray_EndUpdate, self.Ptr)

