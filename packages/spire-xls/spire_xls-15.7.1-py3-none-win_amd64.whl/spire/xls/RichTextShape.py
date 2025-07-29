from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class RichTextShape (  SpireObject, IRichTextString) :
    """Represents rich text within a shape in Excel.
    
    This class implements the IRichTextString interface and provides functionality for 
    creating and manipulating text with different formatting applied to different parts
    when the text is contained within a shape (like a text box or comment).
    """
    @property

    def Text(self)->str:
        """Gets or sets the plain text content of the rich text shape.
        
        When setting this property, any existing formatting is preserved and applied
        to the new text content where applicable.
        
        Returns:
            str: The plain text content without formatting information.
        """
        GetDllLibXls().RichTextShape_get_Text.argtypes=[c_void_p]
        GetDllLibXls().RichTextShape_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().RichTextShape_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        GetDllLibXls().RichTextShape_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().RichTextShape_set_Text, self.Ptr, value)

    @property

    def RtfText(self)->str:
        """Gets the text content in Rich Text Format (RTF).
        
        This property returns the text with all formatting information encoded in RTF format,
        which can be used for interoperability with other applications that support RTF.
        
        Returns:
            str: The text content in RTF format.
        """
        GetDllLibXls().RichTextShape_get_RtfText.argtypes=[c_void_p]
        GetDllLibXls().RichTextShape_get_RtfText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().RichTextShape_get_RtfText, self.Ptr))
        return ret


    @property
    def IsFormatted(self)->bool:
        """Gets whether the rich text contains any formatting.
        
        Returns:
            bool: True if the text contains formatting (different fonts, colors, etc.);
                 otherwise, False.
        """
        GetDllLibXls().RichTextShape_get_IsFormatted.argtypes=[c_void_p]
        GetDllLibXls().RichTextShape_get_IsFormatted.restype=c_bool
        ret = CallCFunction(GetDllLibXls().RichTextShape_get_IsFormatted, self.Ptr)
        return ret

    @property

    def Parent(self)->'SpireObject':
        """Gets the parent shape object that contains this rich text.
        
        Returns:
            SpireObject: The parent shape object that contains this rich text.
        """
        GetDllLibXls().RichTextShape_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().RichTextShape_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RichTextShape_get_Parent, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def GetFont(self ,index:int)->'IFont':
        """Gets the font used at the specified character position in the text.
        
        Args:
            index (int): The zero-based character position in the text.
            
        Returns:
            IFont: The font object used at the specified position.
        """
        
        GetDllLibXls().RichTextShape_GetFont.argtypes=[c_void_p ,c_int]
        GetDllLibXls().RichTextShape_GetFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RichTextShape_GetFont, self.Ptr, index)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret



    def SetFont(self ,startIndex:int,endIndex:int,font:'IFont'):
        """Sets the font for a range of characters in the text.
        
        Args:
            startIndex (int): The zero-based starting character position.
            endIndex (int): The zero-based ending character position (inclusive).
            font (IFont): The font to apply to the specified range of characters.
        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RichTextShape_SetFont.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().RichTextShape_SetFont, self.Ptr, startIndex,endIndex,intPtrfont)

    def ClearFormatting(self):
        """Clears all formatting from the rich text.
        
        This method removes all formatting information while preserving the text content,
        resulting in plain text with default formatting.
        """
        GetDllLibXls().RichTextShape_ClearFormatting.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RichTextShape_ClearFormatting, self.Ptr)

    def Clear(self):
        """Clears both the text content and formatting.
        
        This method removes all text and formatting information, resulting in an empty
        rich text object.
        """
        GetDllLibXls().RichTextShape_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RichTextShape_Clear, self.Ptr)


    def Append(self ,text:str,font:'IFont'):
        """Appends text with the specified font to the end of the rich text.
        
        Args:
            text (str): The text to append.
            font (IFont): The font to apply to the appended text.
        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RichTextShape_Append.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().RichTextShape_Append, self.Ptr, text,intPtrfont)

    def BeginUpdate(self):
        """Begins a batch update operation on the rich text shape.
        
        This method marks the start of a series of changes to the rich text shape.
        Multiple changes can be made more efficiently by calling BeginUpdate
        before making the changes and EndUpdate after all changes are complete.
        """
        GetDllLibXls().RichTextShape_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RichTextShape_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """Ends a batch update operation on the rich text shape.
        
        This method should be called after BeginUpdate and all desired changes
        have been made. It applies all pending changes to the rich text shape.
        """
        GetDllLibXls().RichTextShape_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RichTextShape_EndUpdate, self.Ptr)

    @property

    def DefaultFont(self)->'XlsFont':
        """Gets the default font for this rich text shape.
        
        The default font is used for any portion of the text that doesn't have
        specific formatting applied.
        
        Returns:
            XlsFont: The default font object for the rich text shape.
        """
        GetDllLibXls().RichTextShape_get_DefaultFont.argtypes=[c_void_p]
        GetDllLibXls().RichTextShape_get_DefaultFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RichTextShape_get_DefaultFont, self.Ptr)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret


    @property
    def FormattingRunsCount(self)->int:
        """Gets the number of formatting runs in the rich text.
        
        A formatting run is a contiguous range of text that has the same formatting applied.
        
        Returns:
            int: The number of formatting runs in the rich text.
        """
        GetDllLibXls().RichTextShape_get_FormattingRunsCount.argtypes=[c_void_p]
        GetDllLibXls().RichTextShape_get_FormattingRunsCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().RichTextShape_get_FormattingRunsCount, self.Ptr)
        return ret


    def GetSpace(self ,FormattingRunsIndex:int)->int:
        """Gets the spacing value for the specified formatting run.
        
        Args:
            FormattingRunsIndex (int): The zero-based index of the formatting run.
            
        Returns:
            int: The spacing value for the specified formatting run.
        """
        
        GetDllLibXls().RichTextShape_GetSpace.argtypes=[c_void_p ,c_int]
        GetDllLibXls().RichTextShape_GetSpace.restype=c_int
        ret = CallCFunction(GetDllLibXls().RichTextShape_GetSpace, self.Ptr, FormattingRunsIndex)
        return ret


    def SetSpace(self ,FormattingRunsIndex:int,SpaceValue:int):
        """Sets the spacing value for the specified formatting run.
        
        Args:
            FormattingRunsIndex (int): The zero-based index of the formatting run.
            SpaceValue (int): The spacing value to set for the formatting run.
        """
        
        GetDllLibXls().RichTextShape_SetSpace.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().RichTextShape_SetSpace, self.Ptr, FormattingRunsIndex,SpaceValue)

