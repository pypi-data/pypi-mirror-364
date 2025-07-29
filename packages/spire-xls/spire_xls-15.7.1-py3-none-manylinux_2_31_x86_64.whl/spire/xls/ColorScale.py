from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ColorScale (SpireObject) :
    """Represents a color scale conditional formatting rule in an Excel worksheet.
    
    This class provides properties and methods for configuring color scale conditional formatting,
    which changes the color of a cell based on its value relative to other values in the selected range.
    It allows for defining color gradients with minimum, midpoint, and maximum values and colors.
    """

    @property

    def MaxColor(self)->'Color':
        """
        Get or set the max value object's corresponding color.

        """
        GetDllLibXls().ColorScale_get_MaxColor.argtypes=[c_void_p]
        GetDllLibXls().ColorScale_get_MaxColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ColorScale_get_MaxColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @MaxColor.setter
    def MaxColor(self, value:'Color'):
        GetDllLibXls().ColorScale_set_MaxColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ColorScale_set_MaxColor, self.Ptr, value.Ptr)

    @property

    def MidColor(self)->'Color':
        """
        Get or set the mid value object's corresponding color.

        """
        GetDllLibXls().ColorScale_get_MidColor.argtypes=[c_void_p]
        GetDllLibXls().ColorScale_get_MidColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ColorScale_get_MidColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @MidColor.setter
    def MidColor(self, value:'Color'):
        GetDllLibXls().ColorScale_set_MidColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ColorScale_set_MidColor, self.Ptr, value.Ptr)

    @property

    def MinColor(self)->'Color':
        """
        Get or set the min value object's corresponding color.

        """
        GetDllLibXls().ColorScale_get_MinColor.argtypes=[c_void_p]
        GetDllLibXls().ColorScale_get_MinColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ColorScale_get_MinColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @MinColor.setter
    def MinColor(self, value:'Color'):
        GetDllLibXls().ColorScale_set_MinColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ColorScale_set_MinColor, self.Ptr, value.Ptr)

    @property

    def MaxValue(self)->'IConditionValue':
        """
        Get or set this ColorScale's max value object.

        """
        GetDllLibXls().ColorScale_get_MaxValue.argtypes=[c_void_p]
        GetDllLibXls().ColorScale_get_MaxValue.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ColorScale_get_MaxValue, self.Ptr)
        ret = None if intPtr==None else XlsConditionValue(intPtr)
        return ret


    @property

    def MidValue(self)->'IConditionValue':
        """
        Get or set this ColorScale's mid value object.

        """
        GetDllLibXls().ColorScale_get_MidValue.argtypes=[c_void_p]
        GetDllLibXls().ColorScale_get_MidValue.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ColorScale_get_MidValue, self.Ptr)
        ret = None if intPtr==None else XlsConditionValue(intPtr)
        return ret


    @property

    def MinValue(self)->'IConditionValue':
        """
        Get or set this ColorScale's min value object.

        """
        GetDllLibXls().ColorScale_get_MinValue.argtypes=[c_void_p]
        GetDllLibXls().ColorScale_get_MinValue.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ColorScale_get_MinValue, self.Ptr)
        ret = None if intPtr==None else XlsConditionValue(intPtr)
        return ret


    @dispatch

    def AddCriteria(self ,item:ColorConditionValue):
        """Adds a color condition value to the color scale.
        
        This method adds a predefined color condition value to the color scale,
        which includes a condition type, value, and color.
        
        Args:
            item (ColorConditionValue): The color condition value to add.
        """
        intPtritem:c_void_p = item.Ptr

        GetDllLibXls().ColorScale_AddCriteria.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().ColorScale_AddCriteria, self.Ptr, intPtritem)

    @dispatch

    def AddCriteria(self ,type:ConditionValueType,value:SpireObject,color:Color):
        """Adds a color condition to the color scale with the specified type, value, and color.
        
        This method creates and adds a new color condition to the color scale
        using the provided condition type, value object, and color.
        
        Args:
            type (ConditionValueType): The type of condition value (e.g., minimum, percent, formula).
            value (SpireObject): The value object that defines the condition threshold.
            color (Color): The color to apply when the condition is met.
        """
        enumtype:c_int = type.value
        intPtrvalue:c_void_p = value.Ptr
        intPtrcolor:c_void_p = color.Ptr

        GetDllLibXls().ColorScale_AddCriteriaTVC.argtypes=[c_void_p ,c_int,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().ColorScale_AddCriteriaTVC, self.Ptr, enumtype,intPtrvalue,intPtrcolor)


    def SetConditionCount(self ,count:int):
        """
        Sets number of objects in the collection.

        Args:
            count: 

        """
        
        GetDllLibXls().ColorScale_SetConditionCount.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().ColorScale_SetConditionCount, self.Ptr, count)

