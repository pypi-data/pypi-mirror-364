from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IReflectionEffect (abc.ABC) :
    """Reflection effect interface for Excel shapes.
    
    This interface provides properties to control the reflection effect applied to shapes
    in an Excel worksheet. Reflection effects add a mirror image below or at an angle from
    the original shape, creating a professional visual appearance. The interface allows
    configuring various aspects of the reflection such as blur, direction, distance,
    transparency, and size.
    """
    @property
    @abc.abstractmethod
    def Blur(self)->int:
        """Gets the blur radius of the reflection effect.
        
        This property returns the blur radius of the reflection effect in points.
        Higher values create a more blurred, softer reflection.
        
        Returns:
            int: The blur radius of the reflection in points.
        """
        pass


    @Blur.setter
    @abc.abstractmethod
    def Blur(self, value:int):
        """Sets the blur radius of the reflection effect.
        
        This property sets the blur radius of the reflection effect in points.
        Higher values create a more blurred, softer reflection.
        
        Args:
            value (int): The blur radius of the reflection in points.
        """
        pass


    @property
    @abc.abstractmethod
    def Direction(self)->float:
        """Gets the direction of the reflection effect in degrees.
        
        This property returns the angle in degrees at which the reflection appears
        relative to the shape. The default is typically 0 degrees (directly below).
        
        Returns:
            float: The direction angle in degrees.
        """
        pass


    @Direction.setter
    @abc.abstractmethod
    def Direction(self, value:float):
        """Sets the direction of the reflection effect in degrees.
        
        This property sets the angle in degrees at which the reflection appears
        relative to the shape. The default is typically 0 degrees (directly below).
        
        Args:
            value (float): The direction angle in degrees.
        """
        pass


    @property
    @abc.abstractmethod
    def Distance(self)->int:
        """Gets the distance of the reflection from the shape.
        
        This property returns the distance in points between the shape and its reflection.
        Higher values create more separation between the shape and its reflection.
        
        Returns:
            int: The distance in points.
        """
        pass


    @Distance.setter
    @abc.abstractmethod
    def Distance(self, value:int):
        """Sets the distance of the reflection from the shape.
        
        This property sets the distance in points between the shape and its reflection.
        Higher values create more separation between the shape and its reflection.
        
        Args:
            value (int): The distance in points.
        """
        pass


    @property
    @abc.abstractmethod
    def FadeDirection(self)->float:
        """Gets the fade direction of the reflection in degrees.
        
        This property returns the direction in which the reflection fades out.
        The angle is measured in degrees, with 0 degrees typically representing fading away
        from the shape.
        
        Returns:
            float: The fade direction angle in degrees.
        """
        pass


    @FadeDirection.setter
    @abc.abstractmethod
    def FadeDirection(self, value:float):
        """Sets the fade direction of the reflection in degrees.
        
        This property sets the direction in which the reflection fades out.
        The angle is measured in degrees, with 0 degrees typically representing fading away
        from the shape.
        
        Args:
            value (float): The fade direction angle in degrees.
        """
        pass


    @property
    @abc.abstractmethod
    def RotWithShape(self)->bool:
        """Gets whether the reflection rotates when the shape is rotated.
        
        When true, the reflection rotates along with the shape when the shape is rotated.
        When false, the reflection maintains its original orientation regardless of the shape's rotation.
        
        Returns:
            bool: True if the reflection rotates with the shape, otherwise False.
        """
        pass


    @RotWithShape.setter
    @abc.abstractmethod
    def RotWithShape(self, value:bool):
        """Sets whether the reflection rotates when the shape is rotated.
        
        When set to true, the reflection will rotate along with the shape when the shape is rotated.
        When set to false, the reflection will maintain its original orientation regardless of the shape's rotation.
        
        Args:
            value (bool): True to make the reflection rotate with the shape, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def Size(self)->int:
        """Gets the size of the reflection as a percentage of the shape.
        
        This property returns the size of the reflection relative to the original shape,
        expressed as a percentage. A value of 100 means the reflection is the same size as the shape.
        
        Returns:
            int: The size of the reflection as a percentage.
        """
        pass


    @Size.setter
    @abc.abstractmethod
    def Size(self, value:int):
        """Sets the size of the reflection as a percentage of the shape.
        
        This property sets the size of the reflection relative to the original shape,
        expressed as a percentage. A value of 100 means the reflection is the same size as the shape.
        
        Args:
            value (int): The size of the reflection as a percentage.
        """
        pass


    @property
    @abc.abstractmethod
    def Transparency(self)->int:
        """Gets the transparency of the reflection as a percentage.
        
        This property returns the transparency level of the reflection, expressed as
        a percentage from 0 (completely opaque) to 100 (completely transparent).
        Higher values make the reflection more transparent.
        
        Returns:
            int: The transparency percentage (0-100).
        """
        pass


    @Transparency.setter
    @abc.abstractmethod
    def Transparency(self, value:int):
        """Sets the transparency of the reflection as a percentage.
        
        This property sets the transparency level of the reflection, expressed as
        a percentage from 0 (completely opaque) to 100 (completely transparent).
        Higher values make the reflection more transparent.
        
        Args:
            value (int): The transparency percentage (0-100).
        """
        pass


