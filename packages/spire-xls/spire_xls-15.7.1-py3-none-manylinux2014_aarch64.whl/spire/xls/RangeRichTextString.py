from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class RangeRichTextString (  RichTextString) :
    """Represents a rich text string in a cell range.
    
    This class inherits from RichTextString and provides functionality for working with
    formatted text in Excel cell ranges. Rich text strings can contain multiple text runs
    with different formatting applied to different parts of the text.
    """
    def Dispose(self):
        """Releases all resources used by the RangeRichTextString object.
        
        This method performs necessary cleanup operations and should be called
        when the object is no longer needed.
        """
        GetDllLibXls().RangeRichTextString_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RangeRichTextString_Dispose, self.Ptr)

    @property
    def Index(self)->int:
        """Gets the index of this rich text string in the collection.
        
        Returns:
            int: The zero-based index of the rich text string.
        """
        GetDllLibXls().RangeRichTextString_get_Index.argtypes=[c_void_p]
        GetDllLibXls().RangeRichTextString_get_Index.restype=c_int
        ret = CallCFunction(GetDllLibXls().RangeRichTextString_get_Index, self.Ptr)
        return ret

    @property

    def DefaultFont(self)->'XlsFont':
        """Gets the default font for this rich text string.
        
        The default font is used for any portion of the text that doesn't have
        specific formatting applied.
        
        Returns:
            XlsFont: The default font object for the rich text string.
        """
        GetDllLibXls().RangeRichTextString_get_DefaultFont.argtypes=[c_void_p]
        GetDllLibXls().RangeRichTextString_get_DefaultFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangeRichTextString_get_DefaultFont, self.Ptr)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret


