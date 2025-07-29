from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IShadow (abc.ABC) :
    """Shadow effect interface for Excel elements.
    
    This interface provides properties and methods to control shadow effects applied
    to various elements in Excel, such as shapes, charts, and text. It allows configuration
    of shadow types (outer, inner, perspective), transparency, size, blur, angle, distance,
    color, and other properties that define the appearance of shadows.
    """
    @property
    @abc.abstractmethod
    def ShadowOuterType(self)->'XLSXChartShadowOuterType':
        """Gets the outer shadow type.
        
        This property returns an enumeration value that defines the type of outer shadow
        effect applied to the element, such as drop shadow, outer shadow variants, etc.
        
        Returns:
            XLSXChartShadowOuterType: The outer shadow type.
        """
        pass


    @ShadowOuterType.setter
    @abc.abstractmethod
    def ShadowOuterType(self, value:'XLSXChartShadowOuterType'):
        """Sets the outer shadow type.
        
        This property sets the type of outer shadow effect applied to the element,
        such as drop shadow, outer shadow variants, etc.
        
        Args:
            value (XLSXChartShadowOuterType): The outer shadow type to apply.
        """
        pass


    @property
    @abc.abstractmethod
    def ShadowInnerType(self)->'XLSXChartShadowInnerType':
        """Gets the inner shadow type.
        
        This property returns an enumeration value that defines the type of inner shadow
        effect applied to the element, creating shadow effects that appear inside the element's boundaries.
        
        Returns:
            XLSXChartShadowInnerType: The inner shadow type.
        """
        pass


    @ShadowInnerType.setter
    @abc.abstractmethod
    def ShadowInnerType(self, value:'XLSXChartShadowInnerType'):
        """Sets the inner shadow type.
        
        This property sets the type of inner shadow effect applied to the element,
        creating shadow effects that appear inside the element's boundaries.
        
        Args:
            value (XLSXChartShadowInnerType): The inner shadow type to apply.
        """
        pass


    @property
    @abc.abstractmethod
    def ShadowPrespectiveType(self)->'XLSXChartPrespectiveType':
        """Gets the perspective shadow type.
        
        This property returns an enumeration value that defines the perspective shadow
        effect applied to the element, creating three-dimensional shadow effects with
        perspective distortion.
        
        Returns:
            XLSXChartPrespectiveType: The perspective shadow type.
        """
        pass


    @ShadowPrespectiveType.setter
    @abc.abstractmethod
    def ShadowPrespectiveType(self, value:'XLSXChartPrespectiveType'):
        """Sets the perspective shadow type.
        
        This property sets the perspective shadow effect applied to the element,
        creating three-dimensional shadow effects with perspective distortion.
        
        Args:
            value (XLSXChartPrespectiveType): The perspective shadow type to apply.
        """
        pass


    @property
    @abc.abstractmethod
    def HasCustomStyle(self)->bool:
        """Gets whether the shadow has custom style settings.
        
        When true, the shadow uses custom style settings rather than preset styles.
        When false, the shadow uses a predefined style.
        
        Returns:
            bool: True if the shadow has custom style settings, otherwise False.
        """
        pass


    @HasCustomStyle.setter
    @abc.abstractmethod
    def HasCustomStyle(self, value:bool):
        """Sets whether the shadow has custom style settings.
        
        When set to true, the shadow will use custom style settings rather than preset styles.
        When set to false, the shadow will use a predefined style.
        
        Args:
            value (bool): True to use custom style settings, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def Transparency(self)->int:
        """Gets the transparency of the shadow as a percentage.
        
        This property returns the transparency level of the shadow, expressed as
        a percentage from 0 (completely opaque) to 100 (completely transparent).
        Higher values make the shadow more transparent.
        
        Returns:
            int: The transparency percentage (0-100).
        """
        pass


    @Transparency.setter
    @abc.abstractmethod
    def Transparency(self, value:int):
        """Sets the transparency of the shadow as a percentage.
        
        This property sets the transparency level of the shadow, expressed as
        a percentage from 0 (completely opaque) to 100 (completely transparent).
        Higher values make the shadow more transparent.
        
        Args:
            value (int): The transparency percentage (0-100).
        """
        pass


    @property
    @abc.abstractmethod
    def Size(self)->int:
        """Gets the size of the shadow as a percentage of the element.
        
        This property returns the size of the shadow relative to the original element,
        expressed as a percentage. A higher value creates a larger shadow.
        
        Returns:
            int: The size of the shadow as a percentage.
        """
        pass


    @Size.setter
    @abc.abstractmethod
    def Size(self, value:int):
        """Sets the size of the shadow as a percentage of the element.
        
        This property sets the size of the shadow relative to the original element,
        expressed as a percentage. A higher value creates a larger shadow.
        
        Args:
            value (int): The size of the shadow as a percentage.
        """
        pass


    @property
    @abc.abstractmethod
    def Blur(self)->int:
        """Gets the blur radius of the shadow.
        
        This property returns the blur radius of the shadow in points.
        Higher values create a more blurred, softer shadow effect.
        
        Returns:
            int: The blur radius in points.
        """
        pass


    @Blur.setter
    @abc.abstractmethod
    def Blur(self, value:int):
        """Sets the blur radius of the shadow.
        
        This property sets the blur radius of the shadow in points.
        Higher values create a more blurred, softer shadow effect.
        
        Args:
            value (int): The blur radius in points.
        """
        pass


    @property
    @abc.abstractmethod
    def Angle(self)->int:
        """Gets the angle of the shadow in degrees.
        
        This property returns the direction angle of the shadow in degrees,
        where 0 degrees typically represents a shadow directly to the right,
        with increasing values rotating counterclockwise.
        
        Returns:
            int: The angle in degrees.
        """
        pass


    @Angle.setter
    @abc.abstractmethod
    def Angle(self, value:int):
        """Sets the angle of the shadow in degrees.
        
        This property sets the direction angle of the shadow in degrees,
        where 0 degrees typically represents a shadow directly to the right,
        with increasing values rotating counterclockwise.
        
        Args:
            value (int): The angle in degrees.
        """
        pass


    @property
    @abc.abstractmethod
    def Distance(self)->int:
        """Gets the distance of the shadow from the element.
        
        This property returns the distance in points between the element and its shadow.
        Higher values create more separation between the element and its shadow.
        
        Returns:
            int: The distance in points.
        """
        pass


    @Distance.setter
    @abc.abstractmethod
    def Distance(self, value:int):
        """Sets the distance of the shadow from the element.
        
        This property sets the distance in points between the element and its shadow.
        Higher values create more separation between the element and its shadow.
        
        Args:
            value (int): The distance in points.
        """
        pass


    @property
    @abc.abstractmethod
    def Color(self)->'Color':
        """Gets the color of the shadow.
        
        This property returns the color used to render the shadow.
        
        Returns:
            Color: The color of the shadow.
        """
        pass


    @Color.setter
    @abc.abstractmethod
    def Color(self, value:'Color'):
        """Sets the color of the shadow.
        
        This property sets the color used to render the shadow.
        
        Args:
            value (Color): The color to use for the shadow.
        """
        pass


    @property
    @abc.abstractmethod
    def SoftEdge(self)->int:
        """Gets the soft edge radius of the shadow.
        
        This property returns the radius in points for the soft edge effect applied to the shadow.
        Soft edges create a gradual transition between the shadow and the background.
        A value of 0 means no soft edge effect is applied.
        
        Returns:
            int: The soft edge radius in points.
        """
        pass


    @SoftEdge.setter
    @abc.abstractmethod
    def SoftEdge(self, value:int):
        """Sets the soft edge radius of the shadow.
        
        This property sets the radius in points for the soft edge effect applied to the shadow.
        Soft edges create a gradual transition between the shadow and the background.
        A value of 0 means no soft edge effect is applied.
        
        Args:
            value (int): The soft edge radius in points.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def CustomShadowStyles(self, iOuter:XLSXChartShadowOuterType, iTransparency:int, iSize:int, iBlur:int, iAngle:int, iDistance:int, iCustomShadowStyle:bool):
        """Customizes the outer shadow style with specific parameters.
        
        This method sets up a custom outer shadow with the specified parameters.
        
        Args:
            iOuter (XLSXChartShadowOuterType): The type of outer shadow.
            iTransparency (int): The transparency percentage (0-100).
            iSize (int): The size of the shadow as a percentage.
            iBlur (int): The blur radius in points.
            iAngle (int): The angle in degrees.
            iDistance (int): The distance in points.
            iCustomShadowStyle (bool): Whether to use custom shadow style.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def CustomShadowStyles(self, iInner:XLSXChartShadowInnerType, iTransparency:int, iBlur:int, iAngle:int, iDistance:int, iCustomShadowStyle:bool):
        """Customizes the inner shadow style with specific parameters.
        
        This method sets up a custom inner shadow with the specified parameters.
        
        Args:
            iInner (XLSXChartShadowInnerType): The type of inner shadow.
            iTransparency (int): The transparency percentage (0-100).
            iBlur (int): The blur radius in points.
            iAngle (int): The angle in degrees.
            iDistance (int): The distance in points.
            iCustomShadowStyle (bool): Whether to use custom shadow style.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def CustomShadowStyles(self, iPerspective:XLSXChartPrespectiveType, iTransparency:int, iSize:int, iBlur:int, iAngle:int, iDistance:int, iCustomShadowStyle:bool):
        """Customizes the perspective shadow style with specific parameters.
        
        This method sets up a custom perspective shadow with the specified parameters.
        
        Args:
            iPerspective (XLSXChartPrespectiveType): The type of perspective shadow.
            iTransparency (int): The transparency percentage (0-100).
            iSize (int): The size of the shadow as a percentage.
            iBlur (int): The blur radius in points.
            iAngle (int): The angle in degrees.
            iDistance (int): The distance in points.
            iCustomShadowStyle (bool): Whether to use custom shadow style.
        """
        pass


