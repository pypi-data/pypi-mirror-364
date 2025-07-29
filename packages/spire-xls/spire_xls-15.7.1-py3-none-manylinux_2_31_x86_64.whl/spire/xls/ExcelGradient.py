from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ExcelGradient (  SpireObject, IGradient) :
    """Represents a gradient fill effect in Excel.
    
    This class encapsulates the properties and methods for managing gradient fill effects
    in Excel shapes, cells, and other objects. It provides functionality to set gradient colors,
    styles, and variants, supporting both two-color and preset gradients.
    """
    @property

    def BackColor(self)->'Color':
        """Gets or sets the ending color of the gradient.
        
        Returns:
            Color: A Color object representing the ending color of the gradient.
        """
        GetDllLibXls().ExcelGradient_get_BackColor.argtypes=[c_void_p]
        GetDllLibXls().ExcelGradient_get_BackColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelGradient_get_BackColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @BackColor.setter
    def BackColor(self, value:'Color'):
        GetDllLibXls().ExcelGradient_set_BackColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ExcelGradient_set_BackColor, self.Ptr, value.Ptr)

    @property

    def BackColorObject(self)->'OColor':
        """Gets the ending color object of the gradient.
        
        Returns:
            OColor: An OColor object representing the ending color of the gradient.
        """
        GetDllLibXls().ExcelGradient_get_BackColorObject.argtypes=[c_void_p]
        GetDllLibXls().ExcelGradient_get_BackColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelGradient_get_BackColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def BackKnownColor(self)->'ExcelColors':
        """Gets or sets the ending color of the gradient using predefined Excel colors.
        
        Returns:
            ExcelColors: An enumeration value representing the predefined Excel color.
        """
        GetDllLibXls().ExcelGradient_get_BackKnownColor.argtypes=[c_void_p]
        GetDllLibXls().ExcelGradient_get_BackKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelGradient_get_BackKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @BackKnownColor.setter
    def BackKnownColor(self, value:'ExcelColors'):
        GetDllLibXls().ExcelGradient_set_BackKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelGradient_set_BackKnownColor, self.Ptr, value.value)

    @property

    def ForeColor(self)->'Color':
        """Gets or sets the starting color of the gradient.
        
        Returns:
            Color: A Color object representing the starting color of the gradient.
        """
        GetDllLibXls().ExcelGradient_get_ForeColor.argtypes=[c_void_p]
        GetDllLibXls().ExcelGradient_get_ForeColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelGradient_get_ForeColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @ForeColor.setter
    def ForeColor(self, value:'Color'):
        GetDllLibXls().ExcelGradient_set_ForeColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ExcelGradient_set_ForeColor, self.Ptr, value.Ptr)

    @property

    def ForeKnownColor(self)->'ExcelColors':
        """Gets or sets the starting color of the gradient using predefined Excel colors.
        
        Returns:
            ExcelColors: An enumeration value representing the predefined Excel color.
        """
        GetDllLibXls().ExcelGradient_get_ForeKnownColor.argtypes=[c_void_p]
        GetDllLibXls().ExcelGradient_get_ForeKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelGradient_get_ForeKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @ForeKnownColor.setter
    def ForeKnownColor(self, value:'ExcelColors'):
        GetDllLibXls().ExcelGradient_set_ForeKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelGradient_set_ForeKnownColor, self.Ptr, value.value)

    @property

    def ForeColorObject(self)->'OColor':
        """Gets the starting color object of the gradient.
        
        Returns:
            OColor: An OColor object representing the starting color of the gradient.
        """
        GetDllLibXls().ExcelGradient_get_ForeColorObject.argtypes=[c_void_p]
        GetDllLibXls().ExcelGradient_get_ForeColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelGradient_get_ForeColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def GradientStyle(self)->'GradientStyleType':
        """Gets or sets the style of the gradient.
        
        The gradient style determines the direction and pattern of the gradient fill,
        such as horizontal, vertical, diagonal, or radial.
        
        Returns:
            GradientStyleType: An enumeration value representing the gradient style.
        """
        GetDllLibXls().ExcelGradient_get_GradientStyle.argtypes=[c_void_p]
        GetDllLibXls().ExcelGradient_get_GradientStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelGradient_get_GradientStyle, self.Ptr)
        objwraped = GradientStyleType(ret)
        return objwraped

    @GradientStyle.setter
    def GradientStyle(self, value:'GradientStyleType'):
        GetDllLibXls().ExcelGradient_set_GradientStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelGradient_set_GradientStyle, self.Ptr, value.value)

    @property

    def GradientVariant(self)->'GradientVariantsType':
        """Gets or sets the variant of the gradient.
        
        The gradient variant determines the intensity and distribution of colors in the gradient,
        such as the number of color bands or the smoothness of the transition.
        
        Returns:
            GradientVariantsType: An enumeration value representing the gradient variant.
        """
        GetDllLibXls().ExcelGradient_get_GradientVariant.argtypes=[c_void_p]
        GetDllLibXls().ExcelGradient_get_GradientVariant.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelGradient_get_GradientVariant, self.Ptr)
        objwraped = GradientVariantsType(ret)
        return objwraped

    @GradientVariant.setter
    def GradientVariant(self, value:'GradientVariantsType'):
        GetDllLibXls().ExcelGradient_set_GradientVariant.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelGradient_set_GradientVariant, self.Ptr, value.value)


    def CompareTo(self ,gradient:'IGradient')->int:
        """Compares this gradient with another gradient object.
        
        This method compares the current gradient with the specified gradient object
        and returns an integer that indicates their relative position in the sort order.
        
        Args:
            gradient (IGradient): The gradient to compare with this instance.
            
        Returns:
            int: A value that indicates the relative order of the objects being compared.
                 Less than zero: This instance precedes the specified object in the sort order.
                 Zero: This instance occurs in the same position in the sort order as the specified object.
                 Greater than zero: This instance follows the specified object in the sort order.
        """
        intPtrgradient:c_void_p = gradient.Ptr

        GetDllLibXls().ExcelGradient_CompareTo.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().ExcelGradient_CompareTo.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelGradient_CompareTo, self.Ptr, intPtrgradient)
        return ret

    @dispatch
    def TwoColorGradient(self):
        """Creates a two-color gradient with default style and variant.
        
        This method configures the gradient to use two colors (the fore color and back color)
        with default gradient style and variant settings.
        """
        GetDllLibXls().ExcelGradient_TwoColorGradient.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().ExcelGradient_TwoColorGradient, self.Ptr)

    @dispatch

    def TwoColorGradient(self ,style:GradientStyleType,variant:GradientVariantsType):
        """Creates a two-color gradient with the specified style and variant.
        
        This method configures the gradient to use two colors (the fore color and back color)
        with the specified gradient style and variant settings.
        
        Args:
            style (GradientStyleType): The style of the gradient (horizontal, vertical, diagonal, etc.).
            variant (GradientVariantsType): The variant of the gradient determining color distribution.
        """
        enumstyle:c_int = style.value
        enumvariant:c_int = variant.value

        GetDllLibXls().ExcelGradient_TwoColorGradientSV.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().ExcelGradient_TwoColorGradientSV, self.Ptr, enumstyle,enumvariant)

