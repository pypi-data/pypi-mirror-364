from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class GradientArrayWrapper (  XlsObject, IGradient) :
    """Represents a wrapper for gradient arrays in Excel.
    
    This class provides methods and properties for manipulating gradient effects
    in Excel, including two-color gradients with various styles and variants.
    It implements the IGradient interface to enable gradient formatting for
    cell backgrounds and other elements.
    """
    @property

    def BackColorObject(self)->'OColor':
        """Gets the background color object of the gradient.
        
        Returns:
            OColor: An OColor object representing the background color.
        """
        GetDllLibXls().GradientArrayWrapper_get_BackColorObject.argtypes=[c_void_p]
        GetDllLibXls().GradientArrayWrapper_get_BackColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().GradientArrayWrapper_get_BackColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def BackColor(self)->'Color':
        """Gets or sets the background color of the gradient.
        
        Returns:
            Color: A Color object representing the background color.
        """
        GetDllLibXls().GradientArrayWrapper_get_BackColor.argtypes=[c_void_p]
        GetDllLibXls().GradientArrayWrapper_get_BackColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().GradientArrayWrapper_get_BackColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @BackColor.setter
    def BackColor(self, value:'Color'):
        """Sets the background color of the gradient.
        
        Args:
            value (Color): A Color object representing the background color to set.
        """
        GetDllLibXls().GradientArrayWrapper_set_BackColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().GradientArrayWrapper_set_BackColor, self.Ptr, value.Ptr)

    @property

    def BackKnownColor(self)->'ExcelColors':
        """Gets or sets the predefined Excel color for the gradient background.
        
        Returns:
            ExcelColors: An enumeration value representing the Excel color.
        """
        GetDllLibXls().GradientArrayWrapper_get_BackKnownColor.argtypes=[c_void_p]
        GetDllLibXls().GradientArrayWrapper_get_BackKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().GradientArrayWrapper_get_BackKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @BackKnownColor.setter
    def BackKnownColor(self, value:'ExcelColors'):
        """Sets the predefined Excel color for the gradient background.
        
        Args:
            value (ExcelColors): An enumeration value representing the Excel color to set.
        """
        GetDllLibXls().GradientArrayWrapper_set_BackKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().GradientArrayWrapper_set_BackKnownColor, self.Ptr, value.value)

    @property

    def ForeColorObject(self)->'OColor':
        """Gets the foreground color object of the gradient.
        
        Returns:
            OColor: An OColor object representing the foreground color.
        """
        GetDllLibXls().GradientArrayWrapper_get_ForeColorObject.argtypes=[c_void_p]
        GetDllLibXls().GradientArrayWrapper_get_ForeColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().GradientArrayWrapper_get_ForeColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def ForeColor(self)->'Color':
        """Gets or sets the foreground color of the gradient.
        
        Returns:
            Color: A Color object representing the foreground color.
        """
        GetDllLibXls().GradientArrayWrapper_get_ForeColor.argtypes=[c_void_p]
        GetDllLibXls().GradientArrayWrapper_get_ForeColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().GradientArrayWrapper_get_ForeColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @ForeColor.setter
    def ForeColor(self, value:'Color'):
        """Sets the foreground color of the gradient.
        
        Args:
            value (Color): A Color object representing the foreground color to set.
        """
        GetDllLibXls().GradientArrayWrapper_set_ForeColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().GradientArrayWrapper_set_ForeColor, self.Ptr, value.Ptr)

    @property

    def ForeKnownColor(self)->'ExcelColors':
        """Gets or sets the predefined Excel color for the gradient foreground.
        
        Returns:
            ExcelColors: An enumeration value representing the Excel color.
        """
        GetDllLibXls().GradientArrayWrapper_get_ForeKnownColor.argtypes=[c_void_p]
        GetDllLibXls().GradientArrayWrapper_get_ForeKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().GradientArrayWrapper_get_ForeKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @ForeKnownColor.setter
    def ForeKnownColor(self, value:'ExcelColors'):
        """Sets the predefined Excel color for the gradient foreground.
        
        Args:
            value (ExcelColors): An enumeration value representing the Excel color to set.
        """
        GetDllLibXls().GradientArrayWrapper_set_ForeKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().GradientArrayWrapper_set_ForeKnownColor, self.Ptr, value.value)

    @property

    def GradientStyle(self)->'GradientStyleType':
        """Gets or sets the style of the gradient.
        
        Returns:
            GradientStyleType: An enumeration value representing the gradient style.
        """
        GetDllLibXls().GradientArrayWrapper_get_GradientStyle.argtypes=[c_void_p]
        GetDllLibXls().GradientArrayWrapper_get_GradientStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().GradientArrayWrapper_get_GradientStyle, self.Ptr)
        objwraped = GradientStyleType(ret)
        return objwraped

    @GradientStyle.setter
    def GradientStyle(self, value:'GradientStyleType'):
        """Sets the style of the gradient.
        
        Args:
            value (GradientStyleType): An enumeration value representing the gradient style to set.
        """
        GetDllLibXls().GradientArrayWrapper_set_GradientStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().GradientArrayWrapper_set_GradientStyle, self.Ptr, value.value)

    @property

    def GradientVariant(self)->'GradientVariantsType':
        """Gets or sets the variant of the gradient.
        
        Returns:
            GradientVariantsType: An enumeration value representing the gradient variant.
        """
        GetDllLibXls().GradientArrayWrapper_get_GradientVariant.argtypes=[c_void_p]
        GetDllLibXls().GradientArrayWrapper_get_GradientVariant.restype=c_int
        ret = CallCFunction(GetDllLibXls().GradientArrayWrapper_get_GradientVariant, self.Ptr)
        objwraped = GradientVariantsType(ret)
        return objwraped

    @GradientVariant.setter
    def GradientVariant(self, value:'GradientVariantsType'):
        """Sets the variant of the gradient.
        
        Args:
            value (GradientVariantsType): An enumeration value representing the gradient variant to set.
        """
        GetDllLibXls().GradientArrayWrapper_set_GradientVariant.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().GradientArrayWrapper_set_GradientVariant, self.Ptr, value.value)


    def CompareTo(self ,gradient:'IGradient')->int:
        """Compares this gradient with another gradient.
        
        Args:
            gradient (IGradient): The gradient to compare with.
            
        Returns:
            int: A value that indicates the relative order of the objects being compared.
        """
        intPtrgradient:c_void_p = gradient.Ptr

        GetDllLibXls().GradientArrayWrapper_CompareTo.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().GradientArrayWrapper_CompareTo.restype=c_int
        ret = CallCFunction(GetDllLibXls().GradientArrayWrapper_CompareTo, self.Ptr, intPtrgradient)
        return ret

    @dispatch
    def TwoColorGradient(self):
        """Creates a two-color gradient with default style and variant.
        
        This method sets up a two-color gradient using the current foreground and
        background colors with default style and variant settings.
        """
        GetDllLibXls().GradientArrayWrapper_TwoColorGradient.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().GradientArrayWrapper_TwoColorGradient, self.Ptr)

    @dispatch

    def TwoColorGradient(self ,style:GradientStyleType,variant:GradientVariantsType):
        """Creates a two-color gradient with specified style and variant.
        
        Args:
            style (GradientStyleType): The style of the gradient.
            variant (GradientVariantsType): The variant of the gradient.
        """
        enumstyle:c_int = style.value
        enumvariant:c_int = variant.value

        GetDllLibXls().GradientArrayWrapper_TwoColorGradientSV.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().GradientArrayWrapper_TwoColorGradientSV, self.Ptr, enumstyle,enumvariant)

    def BeginUpdate(self):
        """Begins a batch update operation on the gradient properties.
        
        This method should be called before making multiple changes to gradient properties
        to improve performance by deferring the actual updates until EndUpdate is called.
        """
        GetDllLibXls().GradientArrayWrapper_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().GradientArrayWrapper_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """Ends a batch update operation and applies all pending changes to gradient properties.
        
        This method should be called after BeginUpdate to apply all the changes made
        to gradient properties in a single operation, improving performance.
        """
        GetDllLibXls().GradientArrayWrapper_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().GradientArrayWrapper_EndUpdate, self.Ptr)

