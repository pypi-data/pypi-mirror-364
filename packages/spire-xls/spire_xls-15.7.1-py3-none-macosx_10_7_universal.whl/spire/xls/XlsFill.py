from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsFill (SpireObject) :
    """Represents a fill formatting in an Excel worksheet.
    
    This class provides properties and methods for manipulating fill formatting in Excel,
    including patterns, colors, and gradient effects. It extends SpireObject and can be used
    to create and modify cell and shape fills.
    """
    @property

    def OColor(self)->'OColor':
        """Gets the Office color of the fill.
        
        Returns:
            OColor: An object representing the Office color of the fill.
        """
        GetDllLibXls().XlsFill_get_OColor.argtypes=[c_void_p]
        GetDllLibXls().XlsFill_get_OColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsFill_get_OColor, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def PatternColorObject(self)->'OColor':
        """Gets the pattern color object of the fill.
        
        Returns:
            OColor: An object representing the pattern color of the fill.
        """
        GetDllLibXls().XlsFill_get_PatternColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsFill_get_PatternColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsFill_get_PatternColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def Pattern(self)->'ExcelPatternType':
        """Gets or sets the pattern type of the fill.
        
        Returns:
            ExcelPatternType: An enumeration value representing the pattern type.
        """
        GetDllLibXls().XlsFill_get_Pattern.argtypes=[c_void_p]
        GetDllLibXls().XlsFill_get_Pattern.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsFill_get_Pattern, self.Ptr)
        objwraped = ExcelPatternType(ret)
        return objwraped

    @Pattern.setter
    def Pattern(self, value:'ExcelPatternType'):
        """Sets the pattern type of the fill.
        
        Args:
            value (ExcelPatternType): An enumeration value representing the pattern type.
        """
        GetDllLibXls().XlsFill_set_Pattern.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsFill_set_Pattern, self.Ptr, value.value)

    @property

    def GradientStyle(self)->'GradientStyleType':
        """Gets or sets the gradient style of the fill.
        
        Returns:
            GradientStyleType: An enumeration value representing the gradient style.
        """
        GetDllLibXls().XlsFill_get_GradientStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsFill_get_GradientStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsFill_get_GradientStyle, self.Ptr)
        objwraped = GradientStyleType(ret)
        return objwraped

    @GradientStyle.setter
    def GradientStyle(self, value:'GradientStyleType'):
        """Sets the gradient style of the fill.
        
        Args:
            value (GradientStyleType): An enumeration value representing the gradient style.
        """
        GetDllLibXls().XlsFill_set_GradientStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsFill_set_GradientStyle, self.Ptr, value.value)

    @property

    def GradientVariant(self)->'GradientVariantsType':
        """Gets or sets the gradient variant of the fill.
        
        Returns:
            GradientVariantsType: An enumeration value representing the gradient variant.
        """
        GetDllLibXls().XlsFill_get_GradientVariant.argtypes=[c_void_p]
        GetDllLibXls().XlsFill_get_GradientVariant.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsFill_get_GradientVariant, self.Ptr)
        objwraped = GradientVariantsType(ret)
        return objwraped

    @GradientVariant.setter
    def GradientVariant(self, value:'GradientVariantsType'):
        """Sets the gradient variant of the fill.
        
        Args:
            value (GradientVariantsType): An enumeration value representing the gradient variant.
        """
        GetDllLibXls().XlsFill_set_GradientVariant.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsFill_set_GradientVariant, self.Ptr, value.value)

    @property

    def FillType(self)->'ShapeFillType':
        """Gets or sets the type of the fill.
        
        Returns:
            ShapeFillType: An enumeration value representing the fill type.
        """
        GetDllLibXls().XlsFill_get_FillType.argtypes=[c_void_p]
        GetDllLibXls().XlsFill_get_FillType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsFill_get_FillType, self.Ptr)
        objwraped = ShapeFillType(ret)
        return objwraped

    @FillType.setter
    def FillType(self, value:'ShapeFillType'):
        """Sets the type of the fill.
        
        Args:
            value (ShapeFillType): An enumeration value representing the fill type.
        """
        GetDllLibXls().XlsFill_set_FillType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsFill_set_FillType, self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """Determines whether the specified object is equal to the current fill.
        
        Args:
            obj (SpireObject): The object to compare with the current fill.
            
        Returns:
            bool: True if the specified object is equal to the current fill; otherwise, False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibXls().XlsFill_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsFill_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsFill_Equals, self.Ptr, intPtrobj)
        return ret

    def GetHashCode(self)->int:
        """Gets the hash code for the current fill.
        
        Returns:
            int: A hash code for the current fill.
        """
        GetDllLibXls().XlsFill_GetHashCode.argtypes=[c_void_p]
        GetDllLibXls().XlsFill_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsFill_GetHashCode, self.Ptr)
        return ret


    def Clone(self)->'XlsFill':
        """Creates a clone of this fill.
        
        Returns:
            XlsFill: A new instance of the fill with the same formatting.
        """
        GetDllLibXls().XlsFill_Clone.argtypes=[c_void_p]
        GetDllLibXls().XlsFill_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsFill_Clone, self.Ptr)
        ret = None if intPtr==None else XlsFill(intPtr)
        return ret


