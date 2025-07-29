from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class OColor (SpireObject) :
    """
    This object used to store, convert colors.

    """
    @property
    def Value(self)->int:
        """
        Returns color value (it can be index, rgb color, etc.)

        """
        GetDllLibXls().OColor_get_Value.argtypes=[c_void_p]
        GetDllLibXls().OColor_get_Value.restype=c_int
        ret = CallCFunction(GetDllLibXls().OColor_get_Value, self.Ptr)
        return ret

    @property
    def Tint(self)->float:
        """
        Gets or sets Tint.

        """
        GetDllLibXls().OColor_get_Tint.argtypes=[c_void_p]
        GetDllLibXls().OColor_get_Tint.restype=c_double
        ret = CallCFunction(GetDllLibXls().OColor_get_Tint, self.Ptr)
        return ret

    @Tint.setter
    def Tint(self, value:float):
        GetDllLibXls().OColor_set_Tint.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().OColor_set_Tint, self.Ptr, value)

    @property

    def ColorType(self)->'ColorType':
        """
        Returns type of the stored color.

        """
        GetDllLibXls().OColor_get_ColorType.argtypes=[c_void_p]
        GetDllLibXls().OColor_get_ColorType.restype=c_int
        ret = CallCFunction(GetDllLibXls().OColor_get_ColorType, self.Ptr)
        objwraped = ColorType(ret)
        return objwraped

    def GetHashCode(self)->int:
        """
        Returns the hash code for this instance.

        Returns:
            A 32-bit signed integer hash code.

        """
        GetDllLibXls().OColor_GetHashCode.argtypes=[c_void_p]
        GetDllLibXls().OColor_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibXls().OColor_GetHashCode, self.Ptr)
        return ret

    @dispatch

    def SetTheme(self ,themeIndex:int,book:IWorkbook):
        """Sets the color to a theme color.
        
        This method sets the color to a predefined theme color from the workbook's theme.
        
        Args:
            themeIndex (int): The index of the theme color.
            book (IWorkbook): The workbook containing the theme colors.
        """
        intPtrbook:c_void_p = book.Ptr

        GetDllLibXls().OColor_SetTheme.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibXls().OColor_SetTheme, self.Ptr, themeIndex,intPtrbook)

    @dispatch

    def SetTheme(self ,themeIndex:int,book:IWorkbook,dTintValue:float):
        """Sets the color to a theme color with a specified tint value.
        
        This method sets the color to a predefined theme color from the workbook's theme
        and applies the specified tint value to lighten or darken the color.
        
        Args:
            themeIndex (int): The index of the theme color.
            book (IWorkbook): The workbook containing the theme colors.
            dTintValue (float): The tint value to apply to the theme color. 
                               Positive values lighten the color, negative values darken it.
                               Value should be between -1.0 and 1.0.
        """
        intPtrbook:c_void_p = book.Ptr

        GetDllLibXls().OColor_SetThemeTBD.argtypes=[c_void_p ,c_int,c_void_p,c_double]
        CallCFunction(GetDllLibXls().OColor_SetThemeTBD, self.Ptr, themeIndex,intPtrbook,dTintValue)

#
#    def GetThemeColor(self ,themeIndex:'Int32&',tint:'Double&')->bool:
#        """
#
#        """
#        intPtrthemeIndex:c_void_p = themeIndex.Ptr
#        intPtrtint:c_void_p = tint.Ptr
#
#        GetDllLibXls().OColor_GetThemeColor.argtypes=[c_void_p ,c_void_p,c_void_p]
#        GetDllLibXls().OColor_GetThemeColor.restype=c_bool
#        ret = CallCFunction(GetDllLibXls().OColor_GetThemeColor, self.Ptr, intPtrthemeIndex,intPtrtint)
#        return ret



    def SetRGB(self ,rgb:'Color',book:'IWorkbook',dTintValue:float):
        """Sets the color to an RGB color with a specified tint value.
        
        This method sets the color to the specified RGB color and applies the
        specified tint value to lighten or darken the color.
        
        Args:
            rgb (Color): The RGB color to set.
            book (IWorkbook): The workbook context for the color.
            dTintValue (float): The tint value to apply to the color.
                               Positive values lighten the color, negative values darken it.
                               Value should be between -1.0 and 1.0.
        """
        intPtrrgb:c_void_p = rgb.Ptr
        intPtrbook:c_void_p = book.Ptr

        GetDllLibXls().OColor_SetRGB.argtypes=[c_void_p ,c_void_p,c_void_p,c_double]
        CallCFunction(GetDllLibXls().OColor_SetRGB, self.Ptr, intPtrrgb,intPtrbook,dTintValue)


    def SetKnownColor(self ,value:'ExcelColors'):
        """
        Sets known color.

        Args:
            value: Excel color to set.

        """
        enumvalue:c_int = value.value

        GetDllLibXls().OColor_SetKnownColor.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().OColor_SetKnownColor, self.Ptr, enumvalue)


    def GetKnownColor(self ,book:'Workbook')->'ExcelColors':
        """Gets the Excel known color equivalent of this color.
        
        This method attempts to match this color to one of the predefined Excel colors.
        
        Args:
            book (Workbook): The workbook context for the color.
            
        Returns:
            ExcelColors: An enumeration value representing the Excel known color.
        """
        intPtrbook:c_void_p = book.Ptr

        GetDllLibXls().OColor_GetKnownColor.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().OColor_GetKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().OColor_GetKnownColor, self.Ptr, intPtrbook)
        objwraped = ExcelColors(ret)
        return objwraped

    def Dispose(self):
        """Releases all resources used by the OColor object.
        
        This method performs necessary cleanup operations and should be called
        when the object is no longer needed.
        """
        GetDllLibXls().OColor_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().OColor_Dispose, self.Ptr)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified Object is equal to the current Object.

        Args:
            obj: The Object to compare with the current Object.

        Returns:
            true if the specified Object is equal to the current Object; otherwise, false.

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibXls().OColor_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().OColor_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibXls().OColor_Equals, self.Ptr, intPtrobj)
        return ret

