from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ShapeGlow (  XlsObject, IGlow, ICloneParent) :
    """Represents glow effect settings for a shape in Excel.
    
    This class implements the IGlow and ICloneParent interfaces and provides functionality
    for configuring glow effects applied to shapes in Excel worksheets. Glow effects add
    a colored, blurred outline around the shape to create a glowing appearance.
    """
    @property
    def SoftEdge(self)->int:
        """Gets or sets the radius of the soft edge effect for the glow.
        
        The soft edge radius determines how far the glow extends from the shape's edge.
        
        Returns:
            int: The radius of the soft edge effect in points.
        """
        GetDllLibXls().ShapeGlow_get_SoftEdge.argtypes=[c_void_p]
        GetDllLibXls().ShapeGlow_get_SoftEdge.restype=c_int
        ret = CallCFunction(GetDllLibXls().ShapeGlow_get_SoftEdge, self.Ptr)
        return ret

    @SoftEdge.setter
    def SoftEdge(self, value:int):
        GetDllLibXls().ShapeGlow_set_SoftEdge.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ShapeGlow_set_SoftEdge, self.Ptr, value)

    @property
    def Transparency(self)->int:
        """Gets or sets the transparency level of the glow effect.
        
        The transparency value ranges from 0 (fully opaque) to 100 (fully transparent).
        
        Returns:
            int: The transparency level as a percentage (0-100).
        """
        GetDllLibXls().ShapeGlow_get_Transparency.argtypes=[c_void_p]
        GetDllLibXls().ShapeGlow_get_Transparency.restype=c_int
        ret = CallCFunction(GetDllLibXls().ShapeGlow_get_Transparency, self.Ptr)
        return ret

    @Transparency.setter
    def Transparency(self, value:int):
        GetDllLibXls().ShapeGlow_set_Transparency.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ShapeGlow_set_Transparency, self.Ptr, value)

    @property
    def Radius(self)->int:
        """Gets or sets the radius of the glow effect.
        
        The radius determines the overall size of the glow around the shape.
        
        Returns:
            int: The radius of the glow effect in points.
        """
        GetDllLibXls().ShapeGlow_get_Radius.argtypes=[c_void_p]
        GetDllLibXls().ShapeGlow_get_Radius.restype=c_int
        ret = CallCFunction(GetDllLibXls().ShapeGlow_get_Radius, self.Ptr)
        return ret

    @Radius.setter
    def Radius(self, value:int):
        GetDllLibXls().ShapeGlow_set_Radius.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ShapeGlow_set_Radius, self.Ptr, value)

    @property

    def Color(self)->'Color':
        """Gets or sets the color of the glow effect.
        
        Returns:
            Color: The color object representing the glow color.
        """
        GetDllLibXls().ShapeGlow_get_Color.argtypes=[c_void_p]
        GetDllLibXls().ShapeGlow_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ShapeGlow_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        GetDllLibXls().ShapeGlow_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ShapeGlow_set_Color, self.Ptr, value.Ptr)


    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """Creates a copy of the glow effect with the specified parent.
        
        Args:
            parent (SpireObject): The parent object for the cloned glow effect.
            
        Returns:
            SpireObject: A new SpireObject that is a copy of this glow effect.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().ShapeGlow_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().ShapeGlow_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ShapeGlow_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


