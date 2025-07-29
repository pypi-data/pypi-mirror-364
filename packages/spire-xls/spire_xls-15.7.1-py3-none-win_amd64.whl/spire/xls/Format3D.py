from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class Format3D (  XlsObject, IFormat3D, ICloneParent) :
    """Represents 3D formatting for Excel objects.
    
    This class provides properties and methods to manipulate 3D formatting effects
    for Excel objects such as shapes, charts, and other elements. It allows control
    over bevels, lighting, materials, extrusion, and contours to create sophisticated
    3D visual effects.
    """
    @property

    def BevelTopType(self)->'XLSXChartBevelType':
        """Gets the bevel type for the top surface of the 3D object.
        
        Returns:
            XLSXChartBevelType: An enumeration value representing the bevel type for the top surface.
        """
        GetDllLibXls().Format3D_get_BevelTopType.argtypes=[c_void_p]
        GetDllLibXls().Format3D_get_BevelTopType.restype=c_int
        ret = CallCFunction(GetDllLibXls().Format3D_get_BevelTopType, self.Ptr)
        objwraped = XLSXChartBevelType(ret)
        return objwraped

    @BevelTopType.setter
    def BevelTopType(self, value:'XLSXChartBevelType'):
        """Sets the bevel type for the top surface of the 3D object.
        
        Args:
            value (XLSXChartBevelType): An enumeration value representing the bevel type for the top surface.
        """
        GetDllLibXls().Format3D_set_BevelTopType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().Format3D_set_BevelTopType, self.Ptr, value.value)

    @property

    def BevelBottomType(self)->'XLSXChartBevelType':
        """Gets the bevel type for the bottom surface of the 3D object.
        
        Returns:
            XLSXChartBevelType: An enumeration value representing the bevel type for the bottom surface.
        """
        GetDllLibXls().Format3D_get_BevelBottomType.argtypes=[c_void_p]
        GetDllLibXls().Format3D_get_BevelBottomType.restype=c_int
        ret = CallCFunction(GetDllLibXls().Format3D_get_BevelBottomType, self.Ptr)
        objwraped = XLSXChartBevelType(ret)
        return objwraped

    @BevelBottomType.setter
    def BevelBottomType(self, value:'XLSXChartBevelType'):
        """Sets the bevel type for the bottom surface of the 3D object.
        
        Args:
            value (XLSXChartBevelType): An enumeration value representing the bevel type for the bottom surface.
        """
        GetDllLibXls().Format3D_set_BevelBottomType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().Format3D_set_BevelBottomType, self.Ptr, value.value)

    @property

    def MaterialType(self)->'XLSXChartMaterialType':
        """Gets the material type of the 3D object.
        
        Returns:
            XLSXChartMaterialType: An enumeration value representing the material type.
        """
        GetDllLibXls().Format3D_get_MaterialType.argtypes=[c_void_p]
        GetDllLibXls().Format3D_get_MaterialType.restype=c_int
        ret = CallCFunction(GetDllLibXls().Format3D_get_MaterialType, self.Ptr)
        objwraped = XLSXChartMaterialType(ret)
        return objwraped

    @MaterialType.setter
    def MaterialType(self, value:'XLSXChartMaterialType'):
        """Sets the material type of the 3D object.
        
        Args:
            value (XLSXChartMaterialType): An enumeration value representing the material type.
        """
        GetDllLibXls().Format3D_set_MaterialType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().Format3D_set_MaterialType, self.Ptr, value.value)

    @property

    def LightingType(self)->'XLSXChartLightingType':
        """Gets the lighting type applied to the 3D object.
        
        Returns:
            XLSXChartLightingType: An enumeration value representing the lighting type.
        """
        GetDllLibXls().Format3D_get_LightingType.argtypes=[c_void_p]
        GetDllLibXls().Format3D_get_LightingType.restype=c_int
        ret = CallCFunction(GetDllLibXls().Format3D_get_LightingType, self.Ptr)
        objwraped = XLSXChartLightingType(ret)
        return objwraped

    @LightingType.setter
    def LightingType(self, value:'XLSXChartLightingType'):
        """Sets the lighting type applied to the 3D object.
        
        Args:
            value (XLSXChartLightingType): An enumeration value representing the lighting type.
        """
        GetDllLibXls().Format3D_set_LightingType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().Format3D_set_LightingType, self.Ptr, value.value)

    @property
    def BevelTopWidth(self)->float:
        """Gets the width of the top bevel in points.
        
        Returns:
            float: The width of the top bevel in points.
        """
        GetDllLibXls().Format3D_get_BevelTopWidth.argtypes=[c_void_p]
        GetDllLibXls().Format3D_get_BevelTopWidth.restype=c_double
        ret = CallCFunction(GetDllLibXls().Format3D_get_BevelTopWidth, self.Ptr)
        return ret

    @BevelTopWidth.setter
    def BevelTopWidth(self, value:float):
        """Sets the width of the top bevel in points.
        
        Args:
            value (float): The width of the top bevel in points.
        """
        GetDllLibXls().Format3D_set_BevelTopWidth.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().Format3D_set_BevelTopWidth, self.Ptr, value)

    @property
    def BevelTopHeight(self)->float:
        """Gets the height of the top bevel in points.
        
        Returns:
            float: The height of the top bevel in points.
        """
        GetDllLibXls().Format3D_get_BevelTopHeight.argtypes=[c_void_p]
        GetDllLibXls().Format3D_get_BevelTopHeight.restype=c_double
        ret = CallCFunction(GetDllLibXls().Format3D_get_BevelTopHeight, self.Ptr)
        return ret

    @BevelTopHeight.setter
    def BevelTopHeight(self, value:float):
        """Sets the height of the top bevel in points.
        
        Args:
            value (float): The height of the top bevel in points.
        """
        GetDllLibXls().Format3D_set_BevelTopHeight.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().Format3D_set_BevelTopHeight, self.Ptr, value)

    @property
    def BevelBottomWidth(self)->float:
        """Gets the width of the bottom bevel in points.
        
        Returns:
            float: The width of the bottom bevel in points.
        """
        GetDllLibXls().Format3D_get_BevelBottomWidth.argtypes=[c_void_p]
        GetDllLibXls().Format3D_get_BevelBottomWidth.restype=c_double
        ret = CallCFunction(GetDllLibXls().Format3D_get_BevelBottomWidth, self.Ptr)
        return ret

    @BevelBottomWidth.setter
    def BevelBottomWidth(self, value:float):
        """Sets the width of the bottom bevel in points.
        
        Args:
            value (float): The width of the bottom bevel in points.
        """
        GetDllLibXls().Format3D_set_BevelBottomWidth.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().Format3D_set_BevelBottomWidth, self.Ptr, value)

    @property
    def BevelBottomHeight(self)->float:
        """Gets the height of the bottom bevel in points.
        
        Returns:
            float: The height of the bottom bevel in points.
        """
        GetDllLibXls().Format3D_get_BevelBottomHeight.argtypes=[c_void_p]
        GetDllLibXls().Format3D_get_BevelBottomHeight.restype=c_double
        ret = CallCFunction(GetDllLibXls().Format3D_get_BevelBottomHeight, self.Ptr)
        return ret

    @BevelBottomHeight.setter
    def BevelBottomHeight(self, value:float):
        """Sets the height of the bottom bevel in points.
        
        Args:
            value (float): The height of the bottom bevel in points.
        """
        GetDllLibXls().Format3D_set_BevelBottomHeight.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().Format3D_set_BevelBottomHeight, self.Ptr, value)

    @property
    def ExtrusionHeight(self)->float:
        """Gets the extrusion height of the 3D object in points.
        
        Returns:
            float: The extrusion height in points.
        """
        GetDllLibXls().Format3D_get_ExtrusionHeight.argtypes=[c_void_p]
        GetDllLibXls().Format3D_get_ExtrusionHeight.restype=c_double
        ret = CallCFunction(GetDllLibXls().Format3D_get_ExtrusionHeight, self.Ptr)
        return ret

    @ExtrusionHeight.setter
    def ExtrusionHeight(self, value:float):
        """Sets the extrusion height of the 3D object in points.
        
        Args:
            value (float): The extrusion height in points.
        """
        GetDllLibXls().Format3D_set_ExtrusionHeight.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().Format3D_set_ExtrusionHeight, self.Ptr, value)

    @property

    def ExtrusionColor(self)->'Color':
        """Gets the color of the extrusion effect.
        
        Returns:
            Color: A Color object representing the extrusion color.
        """
        GetDllLibXls().Format3D_get_ExtrusionColor.argtypes=[c_void_p]
        GetDllLibXls().Format3D_get_ExtrusionColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Format3D_get_ExtrusionColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @ExtrusionColor.setter
    def ExtrusionColor(self, value:'Color'):
        """Sets the color of the extrusion effect.
        
        Args:
            value (Color): A Color object representing the extrusion color.
        """
        GetDllLibXls().Format3D_set_ExtrusionColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().Format3D_set_ExtrusionColor, self.Ptr, value.Ptr)

    @property
    def ContourWidth(self)->float:
        """Gets the width of the contour effect in points.
        
        Returns:
            float: The contour width in points.
        """
        GetDllLibXls().Format3D_get_ContourWidth.argtypes=[c_void_p]
        GetDllLibXls().Format3D_get_ContourWidth.restype=c_double
        ret = CallCFunction(GetDllLibXls().Format3D_get_ContourWidth, self.Ptr)
        return ret

    @ContourWidth.setter
    def ContourWidth(self, value:float):
        """Sets the width of the contour effect in points.
        
        Args:
            value (float): The contour width in points.
        """
        GetDllLibXls().Format3D_set_ContourWidth.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().Format3D_set_ContourWidth, self.Ptr, value)

    @property

    def ContourColor(self)->'Color':
        """Gets the color of the contour effect.
        
        Returns:
            Color: A Color object representing the contour color.
        """
        GetDllLibXls().Format3D_get_ContourColor.argtypes=[c_void_p]
        GetDllLibXls().Format3D_get_ContourColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Format3D_get_ContourColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @ContourColor.setter
    def ContourColor(self, value:'Color'):
        """Sets the color of the contour effect.
        
        Args:
            value (Color): A Color object representing the contour color.
        """
        GetDllLibXls().Format3D_set_ContourColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().Format3D_set_ContourColor, self.Ptr, value.Ptr)

    @property
    def LightingAngle(self)->float:
        """Gets the angle of the lighting effect in degrees.
        
        Returns:
            float: The lighting angle in degrees.
        """
        GetDllLibXls().Format3D_get_LightingAngle.argtypes=[c_void_p]
        GetDllLibXls().Format3D_get_LightingAngle.restype=c_double
        ret = CallCFunction(GetDllLibXls().Format3D_get_LightingAngle, self.Ptr)
        return ret

    @LightingAngle.setter
    def LightingAngle(self, value:float):
        """Sets the angle of the lighting effect in degrees.
        
        Args:
            value (float): The lighting angle in degrees.
        """
        GetDllLibXls().Format3D_set_LightingAngle.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().Format3D_set_LightingAngle, self.Ptr, value)


    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """Creates a clone of this Format3D object.
        
        Args:
            parent (SpireObject): The parent object for the cloned Format3D object.
            
        Returns:
            SpireObject: A new Format3D object that is a copy of this instance.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().Format3D_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().Format3D_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Format3D_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


