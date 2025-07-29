from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ExcelInterior (  SpireObject, IInterior) :
    """Used to get or set interior settings for Excel cells and shapes.
    
    This class encapsulates the properties and methods for managing the interior formatting
    of cells and shapes in Excel, including background colors, patterns, and gradient effects.
    It implements the IInterior interface to provide standard interior formatting functionality.
    """
    @property

    def PatternKnownColor(self)->'ExcelColors':
        """Gets or sets the pattern color using predefined Excel colors.
        
        This property determines the color of the pattern applied to the cell or shape interior.
        
        Returns:
            ExcelColors: An enumeration value representing the predefined Excel color for the pattern.
        """
        GetDllLibXls().ExcelInterior_get_PatternKnownColor.argtypes=[c_void_p]
        GetDllLibXls().ExcelInterior_get_PatternKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelInterior_get_PatternKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @PatternKnownColor.setter
    def PatternKnownColor(self, value:'ExcelColors'):
        GetDllLibXls().ExcelInterior_set_PatternKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelInterior_set_PatternKnownColor, self.Ptr, value.value)

    @property

    def PatternColor(self)->'Color':
        """Gets or sets the pattern color using RGB values.
        
        This property determines the color of the pattern applied to the cell or shape interior.
        
        Returns:
            Color: A Color object representing the RGB color of the pattern.
        """
        GetDllLibXls().ExcelInterior_get_PatternColor.argtypes=[c_void_p]
        GetDllLibXls().ExcelInterior_get_PatternColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelInterior_get_PatternColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @PatternColor.setter
    def PatternColor(self, value:'Color'):
        GetDllLibXls().ExcelInterior_set_PatternColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ExcelInterior_set_PatternColor, self.Ptr, value.Ptr)

    @property

    def KnownColor(self)->'ExcelColors':
        """Gets or sets the background color using predefined Excel colors.
        
        This property determines the background color of the cell or shape interior.
        
        Returns:
            ExcelColors: An enumeration value representing the predefined Excel color for the background.
        """
        GetDllLibXls().ExcelInterior_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().ExcelInterior_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelInterior_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        GetDllLibXls().ExcelInterior_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelInterior_set_KnownColor, self.Ptr, value.value)

    @property

    def Color(self)->'Color':
        """Gets or sets the background color using RGB values.
        
        This property determines the background color of the cell or shape interior.
        
        Returns:
            Color: A Color object representing the RGB color of the background.
        """
        GetDllLibXls().ExcelInterior_get_Color.argtypes=[c_void_p]
        GetDllLibXls().ExcelInterior_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelInterior_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        GetDllLibXls().ExcelInterior_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ExcelInterior_set_Color, self.Ptr, value.Ptr)

    @property

    def Gradient(self)->'ExcelGradient':
        """Gets the gradient object for this interior.
        
        The gradient object contains properties for configuring gradient fill effects,
        including colors, style, and variants.
        
        Returns:
            ExcelGradient: The gradient object for this interior.
        """
        GetDllLibXls().ExcelInterior_get_Gradient.argtypes=[c_void_p]
        GetDllLibXls().ExcelInterior_get_Gradient.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelInterior_get_Gradient, self.Ptr)
        ret = None if intPtr==None else ExcelGradient(intPtr)
        return ret


    @property

    def FillPattern(self)->'ExcelPatternType':
        """Gets or sets the fill pattern for the interior.
        
        This property determines the pattern used to fill the cell or shape interior,
        such as solid, dotted, striped, etc.
        
        Returns:
            ExcelPatternType: An enumeration value representing the fill pattern type.
        """
        GetDllLibXls().ExcelInterior_get_FillPattern.argtypes=[c_void_p]
        GetDllLibXls().ExcelInterior_get_FillPattern.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelInterior_get_FillPattern, self.Ptr)
        objwraped = ExcelPatternType(ret)
        return objwraped

    @FillPattern.setter
    def FillPattern(self, value:'ExcelPatternType'):
        GetDllLibXls().ExcelInterior_set_FillPattern.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelInterior_set_FillPattern, self.Ptr, value.value)


    def m_interior(self)->'IInterior':
        """Gets the internal IInterior interface implementation.
        
        This method is primarily used internally to access the underlying interior object.
        
        Returns:
            IInterior: The internal IInterior interface implementation.
        """
        GetDllLibXls().ExcelInterior_m_interior.argtypes=[c_void_p]
        GetDllLibXls().ExcelInterior_m_interior.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelInterior_m_interior, self.Ptr)
        ret = None if intPtr==None else ExcelInterior(intPtr)
        return ret


