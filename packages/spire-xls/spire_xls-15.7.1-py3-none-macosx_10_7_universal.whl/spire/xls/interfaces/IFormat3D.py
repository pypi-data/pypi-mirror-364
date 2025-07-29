from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IFormat3D (abc.ABC) :
    """3D formatting interface.
    
    This interface provides functionality for managing 3D formatting effects in Excel charts
    and shapes. It allows customization of 3D properties such as bevel types, material types,
    lighting effects, and dimensions for creating professional-looking 3D visualizations.
    """
    @property

    @abc.abstractmethod
    def BevelTopType(self)->'XLSXChartBevelType':
        """Gets the bevel type for the top face of a 3D shape.
        
        Returns:
            XLSXChartBevelType: The bevel type for the top face.
        """
        pass


    @BevelTopType.setter
    @abc.abstractmethod
    def BevelTopType(self, value:'XLSXChartBevelType'):
        """Sets the bevel type for the top face of a 3D shape.
        
        Args:
            value (XLSXChartBevelType): The bevel type to set for the top face.
        """
        pass


    @property

    @abc.abstractmethod
    def BevelBottomType(self)->'XLSXChartBevelType':
        """Gets the bevel type for the bottom face of a 3D shape.
        
        Returns:
            XLSXChartBevelType: The bevel type for the bottom face.
        """
        pass


    @BevelBottomType.setter
    @abc.abstractmethod
    def BevelBottomType(self, value:'XLSXChartBevelType'):
        """Sets the bevel type for the bottom face of a 3D shape.
        
        Args:
            value (XLSXChartBevelType): The bevel type to set for the bottom face.
        """
        pass


    @property

    @abc.abstractmethod
    def MaterialType(self)->'XLSXChartMaterialType':
        """Gets the material type for the 3D shape.
        
        Returns:
            XLSXChartMaterialType: The material type for the 3D shape.
        """
        pass


    @MaterialType.setter
    @abc.abstractmethod
    def MaterialType(self, value:'XLSXChartMaterialType'):
        """Sets the material type for the 3D shape.
        
        Args:
            value (XLSXChartMaterialType): The material type to set for the 3D shape.
        """
        pass


    @property

    @abc.abstractmethod
    def LightingType(self)->'XLSXChartLightingType':
        """Gets the lighting type for the 3D shape.
        
        Returns:
            XLSXChartLightingType: The lighting type for the 3D shape.
        """
        pass


    @LightingType.setter
    @abc.abstractmethod
    def LightingType(self, value:'XLSXChartLightingType'):
        """Sets the lighting type for the 3D shape.
        
        Args:
            value (XLSXChartLightingType): The lighting type to set for the 3D shape.
        """
        pass


    @property
    @abc.abstractmethod
    def BevelTopWidth(self)->float:
        """Gets the width of the top bevel.
        
        Returns:
            float: The width of the top bevel in points.
        """
        pass


    @BevelTopWidth.setter
    @abc.abstractmethod
    def BevelTopWidth(self, value:float):
        """Sets the width of the top bevel.
        
        Args:
            value (float): The width of the top bevel in points.
        """
        pass


    @property
    @abc.abstractmethod
    def BevelTopHeight(self)->float:
        """Gets the height of the top bevel.
        
        Returns:
            float: The height of the top bevel in points.
        """
        pass


    @BevelTopHeight.setter
    @abc.abstractmethod
    def BevelTopHeight(self, value:float):
        """Sets the height of the top bevel.
        
        Args:
            value (float): The height of the top bevel in points.
        """
        pass


    @property
    @abc.abstractmethod
    def BevelBottomWidth(self)->float:
        """Gets the width of the bottom bevel.
        
        Returns:
            float: The width of the bottom bevel in points.
        """
        pass


    @BevelBottomWidth.setter
    @abc.abstractmethod
    def BevelBottomWidth(self, value:float):
        """Sets the width of the bottom bevel.
        
        Args:
            value (float): The width of the bottom bevel in points.
        """
        pass


    @property
    @abc.abstractmethod
    def BevelBottomHeight(self)->float:
        """Gets the height of the bottom bevel.
        
        Returns:
            float: The height of the bottom bevel in points.
        """
        pass


    @BevelBottomHeight.setter
    @abc.abstractmethod
    def BevelBottomHeight(self, value:float):
        """Sets the height of the bottom bevel.
        
        Args:
            value (float): The height of the bottom bevel in points.
        """
        pass


    @property
    @abc.abstractmethod
    def ContourWidth(self)->float:
        """Gets the width of the contour.
        
        Returns:
            float: The width of the contour in points.
        """
        pass


    @ContourWidth.setter
    @abc.abstractmethod
    def ContourWidth(self, value:float):
        """Sets the width of the contour.
        
        Args:
            value (float): The width of the contour in points.
        """
        pass


    @property
    @abc.abstractmethod
    def ExtrusionHeight(self)->float:
        """Gets the height of the extrusion effect.
        
        Returns:
            float: The height of the extrusion in points.
        """
        pass


    @ExtrusionHeight.setter
    @abc.abstractmethod
    def ExtrusionHeight(self, value:float):
        """Sets the height of the extrusion effect.
        
        Args:
            value (float): The height of the extrusion in points.
        """
        pass


    @property

    @abc.abstractmethod
    def ContourColor(self)->'Color':
        """Gets the color of the contour.
        
        Returns:
            Color: The color of the contour.
        """
        pass


    @ContourColor.setter
    @abc.abstractmethod
    def ContourColor(self, value:'Color'):
        """Sets the color of the contour.
        
        Args:
            value (Color): The color to set for the contour.
        """
        pass


    @property

    @abc.abstractmethod
    def ExtrusionColor(self)->'Color':
        """Gets the color of the extrusion.
        
        Returns:
            Color: The color of the extrusion.
        """
        pass


    @ExtrusionColor.setter
    @abc.abstractmethod
    def ExtrusionColor(self, value:'Color'):
        """Sets the color of the extrusion.
        
        Args:
            value (Color): The color to set for the extrusion.
        """
        pass


    @property
    @abc.abstractmethod
    def LightingAngle(self)->float:
        """Gets the angle of the lighting effect.
        
        Returns:
            float: The angle of the lighting effect in degrees.
        """
        pass


    @LightingAngle.setter
    @abc.abstractmethod
    def LightingAngle(self, value:float):
        """Sets the angle of the lighting effect.
        
        Args:
            value (float): The angle of the lighting effect in degrees.
        """
        pass


