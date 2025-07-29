from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsScrollBarShape (  XlsShape, IScrollBarShape) :
    """Represents a scroll bar control in an Excel worksheet.
    
    This class provides properties and methods for manipulating scroll bar controls,
    including value ranges, appearance, and orientation.
    """
    @property
    def Display3DShading(self)->bool:
        """Gets or sets whether the scroll bar displays with 3D shading.
        
        Returns:
            bool: True if the scroll bar has 3D shading; otherwise, False.
        """
        GetDllLibXls().XlsScrollBarShape_get_Display3DShading.argtypes=[c_void_p]
        GetDllLibXls().XlsScrollBarShape_get_Display3DShading.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsScrollBarShape_get_Display3DShading, self.Ptr)
        return ret

    @Display3DShading.setter
    def Display3DShading(self, value:bool):
        """Sets whether the scroll bar displays with 3D shading.
        
        Args:
            value (bool): True to display with 3D shading; False for flat appearance.
        """
        GetDllLibXls().XlsScrollBarShape_set_Display3DShading.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsScrollBarShape_set_Display3DShading, self.Ptr, value)

    @property
    def CurrentValue(self)->int:
        """Gets or sets the current value of the scroll bar.
        
        The value must be between Min and Max properties.
        
        Returns:
            int: The current value of the scroll bar.
        """
        GetDllLibXls().XlsScrollBarShape_get_CurrentValue.argtypes=[c_void_p]
        GetDllLibXls().XlsScrollBarShape_get_CurrentValue.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsScrollBarShape_get_CurrentValue, self.Ptr)
        return ret

    @CurrentValue.setter
    def CurrentValue(self, value:int):
        """Sets the current value of the scroll bar.
        
        Args:
            value (int): The current value to set for the scroll bar. Must be between Min and Max.
        """
        GetDllLibXls().XlsScrollBarShape_set_CurrentValue.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsScrollBarShape_set_CurrentValue, self.Ptr, value)

    @property
    def Min(self)->int:
        """Gets or sets the minimum value of the scroll bar.
        
        Returns:
            int: The minimum value of the scroll bar.
        """
        GetDllLibXls().XlsScrollBarShape_get_Min.argtypes=[c_void_p]
        GetDllLibXls().XlsScrollBarShape_get_Min.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsScrollBarShape_get_Min, self.Ptr)
        return ret

    @Min.setter
    def Min(self, value:int):
        """Sets the minimum value of the scroll bar.
        
        Args:
            value (int): The minimum value to set for the scroll bar.
        """
        GetDllLibXls().XlsScrollBarShape_set_Min.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsScrollBarShape_set_Min, self.Ptr, value)

    @property
    def Max(self)->int:
        """Gets or sets the maximum value of the scroll bar.
        
        Returns:
            int: The maximum value of the scroll bar.
        """
        GetDllLibXls().XlsScrollBarShape_get_Max.argtypes=[c_void_p]
        GetDllLibXls().XlsScrollBarShape_get_Max.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsScrollBarShape_get_Max, self.Ptr)
        return ret

    @Max.setter
    def Max(self, value:int):
        """Sets the maximum value of the scroll bar.
        
        Args:
            value (int): The maximum value to set for the scroll bar.
        """
        GetDllLibXls().XlsScrollBarShape_set_Max.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsScrollBarShape_set_Max, self.Ptr, value)

    @property
    def IncrementalChange(self)->int:
        """Gets or sets the small change value for the scroll bar.
        
        This is the value that changes when the user clicks on the scroll arrows.
        
        Returns:
            int: The small change value for the scroll bar.
        """
        GetDllLibXls().XlsScrollBarShape_get_IncrementalChange.argtypes=[c_void_p]
        GetDllLibXls().XlsScrollBarShape_get_IncrementalChange.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsScrollBarShape_get_IncrementalChange, self.Ptr)
        return ret

    @IncrementalChange.setter
    def IncrementalChange(self, value:int):
        """Sets the small change value for the scroll bar.
        
        Args:
            value (int): The small change value to set for the scroll bar.
        """
        GetDllLibXls().XlsScrollBarShape_set_IncrementalChange.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsScrollBarShape_set_IncrementalChange, self.Ptr, value)

    @property
    def PageChange(self)->int:
        """Gets or sets the large change value for the scroll bar.
        
        This is the value that changes when the user clicks on the scroll bar area
        between the thumb and the arrows.
        
        Returns:
            int: The large change value for the scroll bar.
        """
        GetDllLibXls().XlsScrollBarShape_get_PageChange.argtypes=[c_void_p]
        GetDllLibXls().XlsScrollBarShape_get_PageChange.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsScrollBarShape_get_PageChange, self.Ptr)
        return ret

    @PageChange.setter
    def PageChange(self, value:int):
        """Sets the large change value for the scroll bar.
        
        Args:
            value (int): The large change value to set for the scroll bar.
        """
        GetDllLibXls().XlsScrollBarShape_set_PageChange.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsScrollBarShape_set_PageChange, self.Ptr, value)

    @property
    def IsHorizontal(self)->bool:
        """Gets or sets whether the scroll bar is horizontal.
        
        Returns:
            bool: True if the scroll bar is horizontal; False if it is vertical.
        """
        GetDllLibXls().XlsScrollBarShape_get_IsHorizontal.argtypes=[c_void_p]
        GetDllLibXls().XlsScrollBarShape_get_IsHorizontal.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsScrollBarShape_get_IsHorizontal, self.Ptr)
        return ret

    @IsHorizontal.setter
    def IsHorizontal(self, value:bool):
        """Sets whether the scroll bar is horizontal.
        
        Args:
            value (bool): True to make the scroll bar horizontal; False to make it vertical.
        """
        GetDllLibXls().XlsScrollBarShape_set_IsHorizontal.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsScrollBarShape_set_IsHorizontal, self.Ptr, value)

    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets the shape type of the scroll bar.
        
        Returns:
            ExcelShapeType: An enumeration value representing the shape type.
        """
        GetDllLibXls().XlsScrollBarShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsScrollBarShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsScrollBarShape_get_ShapeType, self.Ptr)
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
#        GetDllLibXls().XlsScrollBarShape_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsScrollBarShape_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsScrollBarShape_Clone, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollections)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


