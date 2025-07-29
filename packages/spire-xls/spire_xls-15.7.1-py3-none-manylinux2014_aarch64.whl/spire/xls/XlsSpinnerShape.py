from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsSpinnerShape (  XlsShape, ISpinnerShape) :
    """Represents a spinner control in an Excel worksheet.
    
    This class provides properties and methods for manipulating spinner controls,
    including value ranges and appearance.
    """
    @property
    def Display3DShading(self)->bool:
        """Gets or sets whether the spinner displays with 3D shading.
        
        Returns:
            bool: True if the spinner has 3D shading; otherwise, False.
        """
        GetDllLibXls().XlsSpinnerShape_get_Display3DShading.argtypes=[c_void_p]
        GetDllLibXls().XlsSpinnerShape_get_Display3DShading.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsSpinnerShape_get_Display3DShading, self.Ptr)
        return ret

    @Display3DShading.setter
    def Display3DShading(self, value:bool):
        """Sets whether the spinner displays with 3D shading.
        
        Args:
            value (bool): True to display with 3D shading; False for flat appearance.
        """
        GetDllLibXls().XlsSpinnerShape_set_Display3DShading.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsSpinnerShape_set_Display3DShading, self.Ptr, value)

    @property
    def CurrentValue(self)->int:
        """Gets or sets the current value of the spinner.
        
        The value must be between Min and Max properties.
        
        Returns:
            int: The current value of the spinner.
        """
        GetDllLibXls().XlsSpinnerShape_get_CurrentValue.argtypes=[c_void_p]
        GetDllLibXls().XlsSpinnerShape_get_CurrentValue.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsSpinnerShape_get_CurrentValue, self.Ptr)
        return ret

    @CurrentValue.setter
    def CurrentValue(self, value:int):
        """Sets the current value of the spinner.
        
        Args:
            value (int): The current value to set for the spinner. Must be between Min and Max.
        """
        GetDllLibXls().XlsSpinnerShape_set_CurrentValue.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsSpinnerShape_set_CurrentValue, self.Ptr, value)

    @property
    def Min(self)->int:
        """Gets or sets the minimum value of the spinner.
        
        Returns:
            int: The minimum value of the spinner.
        """
        GetDllLibXls().XlsSpinnerShape_get_Min.argtypes=[c_void_p]
        GetDllLibXls().XlsSpinnerShape_get_Min.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsSpinnerShape_get_Min, self.Ptr)
        return ret

    @Min.setter
    def Min(self, value:int):
        """Sets the minimum value of the spinner.
        
        Args:
            value (int): The minimum value to set for the spinner.
        """
        GetDllLibXls().XlsSpinnerShape_set_Min.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsSpinnerShape_set_Min, self.Ptr, value)

    @property
    def Max(self)->int:
        """Gets or sets the maximum value of the spinner.
        
        Returns:
            int: The maximum value of the spinner.
        """
        GetDllLibXls().XlsSpinnerShape_get_Max.argtypes=[c_void_p]
        GetDllLibXls().XlsSpinnerShape_get_Max.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsSpinnerShape_get_Max, self.Ptr)
        return ret

    @Max.setter
    def Max(self, value:int):
        """Sets the maximum value of the spinner.
        
        Args:
            value (int): The maximum value to set for the spinner.
        """
        GetDllLibXls().XlsSpinnerShape_set_Max.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsSpinnerShape_set_Max, self.Ptr, value)

    @property
    def IncrementalChange(self)->int:
        """Gets or sets the increment value for the spinner.
        
        This is the value that changes when the user clicks on the spinner arrows.
        
        Returns:
            int: The increment value for the spinner.
        """
        GetDllLibXls().XlsSpinnerShape_get_IncrementalChange.argtypes=[c_void_p]
        GetDllLibXls().XlsSpinnerShape_get_IncrementalChange.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsSpinnerShape_get_IncrementalChange, self.Ptr)
        return ret

    @IncrementalChange.setter
    def IncrementalChange(self, value:int):
        """Sets the increment value for the spinner.
        
        Args:
            value (int): The increment value to set for the spinner.
        """
        GetDllLibXls().XlsSpinnerShape_set_IncrementalChange.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsSpinnerShape_set_IncrementalChange, self.Ptr, value)

    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets the shape type of the spinner.
        
        Returns:
            ExcelShapeType: An enumeration value representing the shape type.
        """
        GetDllLibXls().XlsSpinnerShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsSpinnerShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsSpinnerShape_get_ShapeType, self.Ptr)
        objwraped = ExcelShapeType(ret)
        return objwraped

#
#    def Clone(self ,parent:'SpireObject',hashNewNames:'Dictionary2',dicFontIndexes:'Dictionary2',addToCollections:bool)->'IShape':
#        """
#
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrhashNewNames:c_void_p = hashNewNames.Ptr
#        intPtrdicFontIndexes:c_void_p = dicFontIndexes.Ptr
#
#        GetDllLibXls().XlsSpinnerShape_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsSpinnerShape_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsSpinnerShape_Clone, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollections)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


