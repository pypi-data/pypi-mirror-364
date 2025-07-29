from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class RichText (  RichTextObject) :
    """

    """
    @dispatch
    def __init__(self, obj:SpireObject):
        GetDllLibXls().RichText_Create.argtypes=[c_void_p]
        GetDllLibXls().RichText_Create.restype = c_void_p
        intPtr = CallCFunction(GetDllLibXls().RichText_Create, obj.Ptr)
        super(RichText, self).__init__(intPtr)

    def GetFont(self ,position:int)->'ExcelFont':
        """
        Returns font for character at specified position.

        Args:
            Position: Position

        """
        
        GetDllLibXls().RichText_GetFont.argtypes=[c_void_p ,c_int]
        GetDllLibXls().RichText_GetFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RichText_GetFont, self.Ptr, position)
        ret = None if intPtr==None else ExcelFont(intPtr)
        return ret



    def SetFont(self ,startPos:int,endPos:int,font:'ExcelFont'):
        """
        Sets font for specified range of characters.

        Args:
            startPos: Position of first character.
            endPos: Position of last character.
            font: Font to set.

        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RichText_SetFont.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().RichText_SetFont, self.Ptr, startPos,endPos,intPtrfont)

