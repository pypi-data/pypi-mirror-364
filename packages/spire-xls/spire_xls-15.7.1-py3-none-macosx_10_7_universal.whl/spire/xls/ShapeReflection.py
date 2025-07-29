from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ShapeReflection (  XlsObject, IReflectionEffect, ICloneParent) :
    """Represents reflection effect settings for a shape in Excel.
    
    This class implements the IReflectionEffect and ICloneParent interfaces and provides
    functionality for configuring reflection effects applied to shapes in Excel worksheets.
    Reflection effects create a mirror image of the shape, simulating the appearance of
    the shape being reflected on a shiny surface.
    """

    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """Creates a copy of the reflection effect with the specified parent.
        
        Args:
            parent (SpireObject): The parent object for the cloned reflection effect.
            
        Returns:
            SpireObject: A new SpireObject that is a copy of this reflection effect.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().ShapeReflection_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().ShapeReflection_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ShapeReflection_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @property
    def Blur(self)->int:
        """Gets or sets the blur radius of the reflection.
        
        The blur radius determines how blurry or sharp the reflection appears.
        
        Returns:
            int: The blur radius of the reflection in points.
        """
        GetDllLibXls().ShapeReflection_get_Blur.argtypes=[c_void_p]
        GetDllLibXls().ShapeReflection_get_Blur.restype=c_int
        ret = CallCFunction(GetDllLibXls().ShapeReflection_get_Blur, self.Ptr)
        return ret

    @Blur.setter
    def Blur(self, value:int):
        GetDllLibXls().ShapeReflection_set_Blur.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ShapeReflection_set_Blur, self.Ptr, value)

    @property
    def Direction(self)->float:
        """Gets or sets the direction angle of the reflection.
        
        The direction angle determines the orientation of the reflection relative to the shape.
        
        Returns:
            float: The direction angle in degrees.
        """
        GetDllLibXls().ShapeReflection_get_Direction.argtypes=[c_void_p]
        GetDllLibXls().ShapeReflection_get_Direction.restype=c_double
        ret = CallCFunction(GetDllLibXls().ShapeReflection_get_Direction, self.Ptr)
        return ret

    @Direction.setter
    def Direction(self, value:float):
        GetDllLibXls().ShapeReflection_set_Direction.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().ShapeReflection_set_Direction, self.Ptr, value)

    @property
    def Distance(self)->int:
        """Gets or sets the distance of the reflection from the shape.
        
        The distance determines how far the reflection appears from the original shape.
        
        Returns:
            int: The distance of the reflection in points.
        """
        GetDllLibXls().ShapeReflection_get_Distance.argtypes=[c_void_p]
        GetDllLibXls().ShapeReflection_get_Distance.restype=c_int
        ret = CallCFunction(GetDllLibXls().ShapeReflection_get_Distance, self.Ptr)
        return ret

    @Distance.setter
    def Distance(self, value:int):
        GetDllLibXls().ShapeReflection_set_Distance.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ShapeReflection_set_Distance, self.Ptr, value)

    @property
    def FadeDirection(self)->float:
        """Gets or sets the fade direction angle of the reflection.
        
        The fade direction determines the direction in which the reflection gradually fades out.
        
        Returns:
            float: The fade direction angle in degrees.
        """
        GetDllLibXls().ShapeReflection_get_FadeDirection.argtypes=[c_void_p]
        GetDllLibXls().ShapeReflection_get_FadeDirection.restype=c_double
        ret = CallCFunction(GetDllLibXls().ShapeReflection_get_FadeDirection, self.Ptr)
        return ret

    @FadeDirection.setter
    def FadeDirection(self, value:float):
        GetDllLibXls().ShapeReflection_set_FadeDirection.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().ShapeReflection_set_FadeDirection, self.Ptr, value)

    @property
    def RotWithShape(self)->bool:
        """Gets or sets whether the reflection rotates with the shape.
        
        When set to True, the reflection will rotate along with the shape when the shape is rotated.
        
        Returns:
            bool: True if the reflection rotates with the shape; otherwise, False.
        """
        GetDllLibXls().ShapeReflection_get_RotWithShape.argtypes=[c_void_p]
        GetDllLibXls().ShapeReflection_get_RotWithShape.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ShapeReflection_get_RotWithShape, self.Ptr)
        return ret

    @RotWithShape.setter
    def RotWithShape(self, value:bool):
        GetDllLibXls().ShapeReflection_set_RotWithShape.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ShapeReflection_set_RotWithShape, self.Ptr, value)

    @property
    def Size(self)->int:
        """Gets or sets the size of the reflection as a percentage of the original shape.
        
        The size determines how large the reflection appears relative to the original shape.
        
        Returns:
            int: The size of the reflection as a percentage (0-100).
        """
        GetDllLibXls().ShapeReflection_get_Size.argtypes=[c_void_p]
        GetDllLibXls().ShapeReflection_get_Size.restype=c_int
        ret = CallCFunction(GetDllLibXls().ShapeReflection_get_Size, self.Ptr)
        return ret

    @Size.setter
    def Size(self, value:int):
        GetDllLibXls().ShapeReflection_set_Size.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ShapeReflection_set_Size, self.Ptr, value)

    @property
    def Transparency(self)->int:
        """Gets or sets the transparency level of the reflection.
        
        The transparency value ranges from 0 (fully opaque) to 100 (fully transparent).
        
        Returns:
            int: The transparency level as a percentage (0-100).
        """
        GetDllLibXls().ShapeReflection_get_Transparency.argtypes=[c_void_p]
        GetDllLibXls().ShapeReflection_get_Transparency.restype=c_int
        ret = CallCFunction(GetDllLibXls().ShapeReflection_get_Transparency, self.Ptr)
        return ret

    @Transparency.setter
    def Transparency(self, value:int):
        GetDllLibXls().ShapeReflection_set_Transparency.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ShapeReflection_set_Transparency, self.Ptr, value)

