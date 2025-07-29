from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class InteriorArrayWrapper (  XlsObject, IInterior) :
    """
    Wrapper class for an array of interior formatting objects.
    
    This class implements the IInterior interface and provides methods to manipulate
    the interior formatting properties of multiple Excel objects simultaneously.
    """
    @property

    def PatternKnownColor(self)->'ExcelColors':
        """
        Gets the known color of the pattern.
        
        Returns:
            ExcelColors: The pattern color as an ExcelColors enum value.
        """
        GetDllLibXls().InteriorArrayWrapper_get_PatternKnownColor.argtypes=[c_void_p]
        GetDllLibXls().InteriorArrayWrapper_get_PatternKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().InteriorArrayWrapper_get_PatternKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @PatternKnownColor.setter
    def PatternKnownColor(self, value:'ExcelColors'):
        """
        Sets the known color of the pattern.
        
        Args:
            value (ExcelColors): The pattern color as an ExcelColors enum value.
        """
        GetDllLibXls().InteriorArrayWrapper_set_PatternKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().InteriorArrayWrapper_set_PatternKnownColor, self.Ptr, value.value)

    @property

    def PatternColor(self)->'Color':
        """
        Gets the color of the pattern.
        
        Returns:
            Color: The pattern color object.
        """
        GetDllLibXls().InteriorArrayWrapper_get_PatternColor.argtypes=[c_void_p]
        GetDllLibXls().InteriorArrayWrapper_get_PatternColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().InteriorArrayWrapper_get_PatternColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @PatternColor.setter
    def PatternColor(self, value:'Color'):
        """
        Sets the color of the pattern.
        
        Args:
            value (Color): The pattern color object.
        """
        GetDllLibXls().InteriorArrayWrapper_set_PatternColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().InteriorArrayWrapper_set_PatternColor, self.Ptr, value.Ptr)

    @property

    def KnownColor(self)->'ExcelColors':
        """
        Gets the known color of the interior.
        
        Returns:
            ExcelColors: The interior color as an ExcelColors enum value.
        """
        GetDllLibXls().InteriorArrayWrapper_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().InteriorArrayWrapper_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().InteriorArrayWrapper_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        """
        Sets the known color of the interior.
        
        Args:
            value (ExcelColors): The interior color as an ExcelColors enum value.
        """
        GetDllLibXls().InteriorArrayWrapper_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().InteriorArrayWrapper_set_KnownColor, self.Ptr, value.value)

    @property

    def Color(self)->'Color':
        """
        Gets the color of the interior.
        
        Returns:
            Color: The interior color object.
        """
        GetDllLibXls().InteriorArrayWrapper_get_Color.argtypes=[c_void_p]
        GetDllLibXls().InteriorArrayWrapper_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().InteriorArrayWrapper_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        """
        Sets the color of the interior.
        
        Args:
            value (Color): The interior color object.
        """
        GetDllLibXls().InteriorArrayWrapper_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().InteriorArrayWrapper_set_Color, self.Ptr, value.Ptr)

    @property

    def Gradient(self)->'ExcelGradient':
        """
        Gets the gradient formatting of the interior.
        
        Returns:
            ExcelGradient: The gradient formatting object.
        """
        GetDllLibXls().InteriorArrayWrapper_get_Gradient.argtypes=[c_void_p]
        GetDllLibXls().InteriorArrayWrapper_get_Gradient.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().InteriorArrayWrapper_get_Gradient, self.Ptr)
        ret = None if intPtr==None else ExcelGradient(intPtr)
        return ret


    @property

    def FillPattern(self)->'ExcelPatternType':
        """
        Gets the fill pattern of the interior.
        
        Returns:
            ExcelPatternType: The fill pattern type.
        """
        GetDllLibXls().InteriorArrayWrapper_get_FillPattern.argtypes=[c_void_p]
        GetDllLibXls().InteriorArrayWrapper_get_FillPattern.restype=c_int
        ret = CallCFunction(GetDllLibXls().InteriorArrayWrapper_get_FillPattern, self.Ptr)
        objwraped = ExcelPatternType(ret)
        return objwraped

    @FillPattern.setter
    def FillPattern(self, value:'ExcelPatternType'):
        """
        Sets the fill pattern of the interior.
        
        Args:
            value (ExcelPatternType): The fill pattern type.
        """
        GetDllLibXls().InteriorArrayWrapper_set_FillPattern.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().InteriorArrayWrapper_set_FillPattern, self.Ptr, value.value)

    def BeginUpdate(self):
        """
        Begins a batch update operation on the interior array.
        
        This method should be called before making multiple changes to the interior properties.
        """
        GetDllLibXls().InteriorArrayWrapper_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().InteriorArrayWrapper_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """
        Ends a batch update operation on the interior array.
        
        This method should be called after making multiple changes to the interior properties.
        """
        GetDllLibXls().InteriorArrayWrapper_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().InteriorArrayWrapper_EndUpdate, self.Ptr)

