from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class LOGFONT (SpireObject) :
    """Represents a logical font structure that defines the attributes of a font.
    
    This class encapsulates the properties of a font, including its height, width, weight,
    orientation, and other characteristics. It is used to specify the visual attributes
    of text in Excel worksheets and charts.
    """
    def lfHeight(self)->int:
        """Gets the height of the font in logical units.
        
        A positive value specifies the cell height of the font. A negative value specifies
        the character height of the font.
        
        Returns:
            int: The height of the font.
        """
        GetDllLibXls().LOGFONT_lfHeight.argtypes=[c_void_p]
        GetDllLibXls().LOGFONT_lfHeight.restype=c_int
        ret = CallCFunction(GetDllLibXls().LOGFONT_lfHeight, self.Ptr)
        return ret

    def lfWidth(self)->int:
        """Gets the average width of characters in the font.
        
        Returns:
            int: The average width of characters in the font.
        """
        GetDllLibXls().LOGFONT_lfWidth.argtypes=[c_void_p]
        GetDllLibXls().LOGFONT_lfWidth.restype=c_int
        ret = CallCFunction(GetDllLibXls().LOGFONT_lfWidth, self.Ptr)
        return ret

    def lfEscapement(self)->int:
        """Gets the angle, in tenths of degrees, between the baseline of a font and the x-axis.
        
        Returns:
            int: The angle of escapement for the font.
        """
        GetDllLibXls().LOGFONT_lfEscapement.argtypes=[c_void_p]
        GetDllLibXls().LOGFONT_lfEscapement.restype=c_int
        ret = CallCFunction(GetDllLibXls().LOGFONT_lfEscapement, self.Ptr)
        return ret

    def lfOrientation(self)->int:
        """Gets the angle, in tenths of degrees, between each character's baseline and the x-axis.
        
        Returns:
            int: The orientation angle of the font.
        """
        GetDllLibXls().LOGFONT_lfOrientation.argtypes=[c_void_p]
        GetDllLibXls().LOGFONT_lfOrientation.restype=c_int
        ret = CallCFunction(GetDllLibXls().LOGFONT_lfOrientation, self.Ptr)
        return ret

    def lfWeight(self)->int:
        """Gets the weight of the font in the range 0 through 1000.
        
        Common values are:
        - 400: Normal
        - 700: Bold
        
        Returns:
            int: The weight of the font.
        """
        GetDllLibXls().LOGFONT_lfWeight.argtypes=[c_void_p]
        GetDllLibXls().LOGFONT_lfWeight.restype=c_int
        ret = CallCFunction(GetDllLibXls().LOGFONT_lfWeight, self.Ptr)
        return ret

    def lfItalic(self)->int:
        """Gets a value indicating whether the font is italic.
        
        Returns:
            int: Nonzero if the font is italic; otherwise, 0.
        """
        GetDllLibXls().LOGFONT_lfItalic.argtypes=[c_void_p]
        GetDllLibXls().LOGFONT_lfItalic.restype=c_int
        ret = CallCFunction(GetDllLibXls().LOGFONT_lfItalic, self.Ptr)
        return ret

    def lfUnderline(self)->int:
        """Gets a value indicating whether the font is underlined.
        
        Returns:
            int: Nonzero if the font is underlined; otherwise, 0.
        """
        GetDllLibXls().LOGFONT_lfUnderline.argtypes=[c_void_p]
        GetDllLibXls().LOGFONT_lfUnderline.restype=c_int
        ret = CallCFunction(GetDllLibXls().LOGFONT_lfUnderline, self.Ptr)
        return ret

    def lfStrikeOut(self)->int:
        """Gets a value indicating whether the font has a strikeout.
        
        Returns:
            int: Nonzero if the font has a strikeout; otherwise, 0.
        """
        GetDllLibXls().LOGFONT_lfStrikeOut.argtypes=[c_void_p]
        GetDllLibXls().LOGFONT_lfStrikeOut.restype=c_int
        ret = CallCFunction(GetDllLibXls().LOGFONT_lfStrikeOut, self.Ptr)
        return ret

    def lfCharSet(self)->int:
        """Gets the character set of the font.
        
        Returns:
            int: The character set identifier.
        """
        GetDllLibXls().LOGFONT_lfCharSet.argtypes=[c_void_p]
        GetDllLibXls().LOGFONT_lfCharSet.restype=c_int
        ret = CallCFunction(GetDllLibXls().LOGFONT_lfCharSet, self.Ptr)
        return ret

    def lfOutPrecision(self)->int:
        """Gets the output precision for the font.
        
        The output precision defines how closely the output must match the requested font's height,
        width, character orientation, escapement, pitch, and font type.
        
        Returns:
            int: The output precision value.
        """
        GetDllLibXls().LOGFONT_lfOutPrecision.argtypes=[c_void_p]
        GetDllLibXls().LOGFONT_lfOutPrecision.restype=c_int
        ret = CallCFunction(GetDllLibXls().LOGFONT_lfOutPrecision, self.Ptr)
        return ret

    def lfClipPrecision(self)->int:
        """Gets the clipping precision for the font.
        
        The clipping precision defines how to clip characters that are partially outside the clipping region.
        
        Returns:
            int: The clipping precision value.
        """
        GetDllLibXls().LOGFONT_lfClipPrecision.argtypes=[c_void_p]
        GetDllLibXls().LOGFONT_lfClipPrecision.restype=c_int
        ret = CallCFunction(GetDllLibXls().LOGFONT_lfClipPrecision, self.Ptr)
        return ret

    def lfQuality(self)->int:
        """Gets the output quality for the font.
        
        The output quality defines how carefully the graphics device interface (GDI) 
        must draw the output to match the characteristics of the selected font.
        
        Returns:
            int: The output quality value.
        """
        GetDllLibXls().LOGFONT_lfQuality.argtypes=[c_void_p]
        GetDllLibXls().LOGFONT_lfQuality.restype=c_int
        ret = CallCFunction(GetDllLibXls().LOGFONT_lfQuality, self.Ptr)
        return ret

    def lfPitchAndFamily(self)->int:
        """Gets the pitch and family of the font.
        
        The low-order bit specifies the pitch of the font, and the high-order bit specifies the font family.
        
        Returns:
            int: The pitch and family value.
        """
        GetDllLibXls().LOGFONT_lfPitchAndFamily.argtypes=[c_void_p]
        GetDllLibXls().LOGFONT_lfPitchAndFamily.restype=c_int
        ret = CallCFunction(GetDllLibXls().LOGFONT_lfPitchAndFamily, self.Ptr)
        return ret


    def lfFaceName(self)->str:
        """Gets the typeface name of the font.
        
        Returns:
            str: The typeface name of the font.
        """
        GetDllLibXls().LOGFONT_lfFaceName.argtypes=[c_void_p]
        GetDllLibXls().LOGFONT_lfFaceName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().LOGFONT_lfFaceName, self.Ptr))
        return ret


