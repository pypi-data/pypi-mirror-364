from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsGradient (  XlsObject, IGradient) :
    """Represents a gradient fill in an Excel worksheet.
    
    This class provides properties and methods for manipulating gradient fills in Excel,
    including gradient colors, styles, and variants. It extends XlsObject and
    implements the IGradient interface.
    """
    @property

    def BackColorObject(self)->'OColor':
        """Gets the Office color object for the background color of the gradient.
        
        Returns:
            OColor: An Office color object representing the background color.
        """
        GetDllLibXls().XlsGradient_get_BackColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsGradient_get_BackColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsGradient_get_BackColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def ForeColorObject(self)->'OColor':
        """Gets the Office color object for the foreground color of the gradient.
        
        Returns:
            OColor: An Office color object representing the foreground color.
        """
        GetDllLibXls().XlsGradient_get_ForeColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsGradient_get_ForeColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsGradient_get_ForeColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def BackColor(self)->'Color':
        """Gets or sets the background color of the gradient.
        
        Returns:
            Color: A Color object representing the background color.
        """
        GetDllLibXls().XlsGradient_get_BackColor.argtypes=[c_void_p]
        GetDllLibXls().XlsGradient_get_BackColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsGradient_get_BackColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @BackColor.setter
    def BackColor(self, value:'Color'):
        """Sets the background color of the gradient.
        
        Args:
            value (Color): A Color object representing the background color.
        """
        GetDllLibXls().XlsGradient_set_BackColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsGradient_set_BackColor, self.Ptr, value.Ptr)

    @property

    def ForeColor(self)->'Color':
        """Gets or sets the foreground color of the gradient.
        
        Returns:
            Color: A Color object representing the foreground color.
        """
        GetDllLibXls().XlsGradient_get_ForeColor.argtypes=[c_void_p]
        GetDllLibXls().XlsGradient_get_ForeColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsGradient_get_ForeColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @ForeColor.setter
    def ForeColor(self, value:'Color'):
        """Sets the foreground color of the gradient.
        
        Args:
            value (Color): A Color object representing the foreground color.
        """
        GetDllLibXls().XlsGradient_set_ForeColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsGradient_set_ForeColor, self.Ptr, value.Ptr)

    @property

    def BackKnownColor(self)->'ExcelColors':
        """Gets or sets a predefined Excel color for the background of the gradient.
        
        Returns:
            ExcelColors: An enumeration value representing the Excel color.
        """
        GetDllLibXls().XlsGradient_get_BackKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsGradient_get_BackKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsGradient_get_BackKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @BackKnownColor.setter
    def BackKnownColor(self, value:'ExcelColors'):
        """Sets a predefined Excel color for the background of the gradient.
        
        Args:
            value (ExcelColors): An enumeration value representing the Excel color.
        """
        GetDllLibXls().XlsGradient_set_BackKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsGradient_set_BackKnownColor, self.Ptr, value.value)

    @property

    def ForeKnownColor(self)->'ExcelColors':
        """Gets or sets a predefined Excel color for the foreground of the gradient.
        
        Returns:
            ExcelColors: An enumeration value representing the Excel color.
        """
        GetDllLibXls().XlsGradient_get_ForeKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsGradient_get_ForeKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsGradient_get_ForeKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @ForeKnownColor.setter
    def ForeKnownColor(self, value:'ExcelColors'):
        """Sets a predefined Excel color for the foreground of the gradient.
        
        Args:
            value (ExcelColors): An enumeration value representing the Excel color.
        """
        GetDllLibXls().XlsGradient_set_ForeKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsGradient_set_ForeKnownColor, self.Ptr, value.value)

    @property

    def GradientStyle(self)->'GradientStyleType':
        """Gets or sets the style of the gradient.
        
        Returns:
            GradientStyleType: An enumeration value representing the gradient style.
        """
        GetDllLibXls().XlsGradient_get_GradientStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsGradient_get_GradientStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsGradient_get_GradientStyle, self.Ptr)
        objwraped = GradientStyleType(ret)
        return objwraped

    @GradientStyle.setter
    def GradientStyle(self, value:'GradientStyleType'):
        """Sets the style of the gradient.
        
        Args:
            value (GradientStyleType): An enumeration value representing the gradient style.
        """
        GetDllLibXls().XlsGradient_set_GradientStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsGradient_set_GradientStyle, self.Ptr, value.value)

    @property

    def GradientVariant(self)->'GradientVariantsType':
        """Gets or sets the variant of the gradient.
        
        Returns:
            GradientVariantsType: An enumeration value representing the gradient variant.
        """
        GetDllLibXls().XlsGradient_get_GradientVariant.argtypes=[c_void_p]
        GetDllLibXls().XlsGradient_get_GradientVariant.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsGradient_get_GradientVariant, self.Ptr)
        objwraped = GradientVariantsType(ret)
        return objwraped

    @GradientVariant.setter
    def GradientVariant(self, value:'GradientVariantsType'):
        """Sets the variant of the gradient.
        
        Args:
            value (GradientVariantsType): An enumeration value representing the gradient variant.
        """
        GetDllLibXls().XlsGradient_set_GradientVariant.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsGradient_set_GradientVariant, self.Ptr, value.value)


    def CompareTo(self ,twin:'IGradient')->int:
        """Compares the current gradient with another gradient.
        
        Args:
            twin (IGradient): The gradient to compare with the current gradient.
            
        Returns:
            int: A value that indicates the relative order of the objects being compared.
                 Less than zero: This gradient precedes twin in the sort order.
                 Zero: This gradient occurs in the same position in the sort order as twin.
                 Greater than zero: This gradient follows twin in the sort order.
        """
        intPtrtwin:c_void_p = twin.Ptr

        GetDllLibXls().XlsGradient_CompareTo.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsGradient_CompareTo.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsGradient_CompareTo, self.Ptr, intPtrtwin)
        return ret

    @dispatch
    def TwoColorGradient(self):
        """Creates a two-color gradient with default settings.
        
        This method sets up a two-color gradient using the current foreground and background colors
        with default style and variant settings.
        """
        GetDllLibXls().XlsGradient_TwoColorGradient.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsGradient_TwoColorGradient, self.Ptr)

    @dispatch

    def TwoColorGradient(self ,style:GradientStyleType):
        """Creates a two-color gradient with the specified style.
        
        Args:
            style (GradientStyleType): The style to use for the gradient.
        """
        enumstyle:c_int = style.value

        GetDllLibXls().XlsGradient_TwoColorGradientS.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsGradient_TwoColorGradientS, self.Ptr, enumstyle)

    @dispatch

    def TwoColorGradient(self ,style:GradientStyleType,variant:GradientVariantsType):
        """Creates a two-color gradient with the specified style and variant.
        
        Args:
            style (GradientStyleType): The style to use for the gradient.
            variant (GradientVariantsType): The variant to use for the gradient.
        """
        enumstyle:c_int = style.value
        enumvariant:c_int = variant.value

        GetDllLibXls().XlsGradient_TwoColorGradientSV.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsGradient_TwoColorGradientSV, self.Ptr, enumstyle,enumvariant)

