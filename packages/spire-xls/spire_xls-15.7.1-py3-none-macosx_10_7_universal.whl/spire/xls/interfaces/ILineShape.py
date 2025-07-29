from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ILineShape (  IPrstGeomShape) :
    """
    Interface for line shape objects in Excel.
    
    This interface provides properties and methods to manipulate line shapes
    in Excel worksheets, including their appearance and formatting.
    """
    @property
    @abc.abstractmethod
    def Color(self)->'Color':
        """
        Gets the line color.

        Returns:
            Color: The line color.
        """
        pass

    @Color.setter
    @abc.abstractmethod
    def Color(self, value:'Color'):
        """
        Sets the line color.

        Args:
            value (Color): The line color to set.
        """
        pass

    @property
    @abc.abstractmethod
    def BeginArrowHeadStyle(self)->'ShapeArrowStyleType':
        """
        Gets the begin arrow head style.

        Returns:
            ShapeArrowStyleType: The begin arrow head style.
        """
        pass

    @BeginArrowHeadStyle.setter
    @abc.abstractmethod
    def BeginArrowHeadStyle(self, value:'ShapeArrowStyleType'):
        """
        Sets the begin arrow head style.

        Args:
            value (ShapeArrowStyleType): The begin arrow head style to set.
        """
        pass

    @property
    @abc.abstractmethod
    def BeginArrowheadLength(self)->'ShapeArrowLengthType':
        """
        Gets the begin arrow head length.

        Returns:
            ShapeArrowLengthType: The begin arrow head length.
        """
        pass

    @BeginArrowheadLength.setter
    @abc.abstractmethod
    def BeginArrowheadLength(self, value:'ShapeArrowLengthType'):
        """
        Sets the begin arrow head length.

        Args:
            value (ShapeArrowLengthType): The begin arrow head length to set.
        """
        pass

    @property
    @abc.abstractmethod
    def BeginArrowheadWidth(self)->'ShapeArrowWidthType':
        """
        Gets the begin arrow head width.

        Returns:
            ShapeArrowWidthType: The begin arrow head width.
        """
        pass

    @BeginArrowheadWidth.setter
    @abc.abstractmethod
    def BeginArrowheadWidth(self, value:'ShapeArrowWidthType'):
        """
        Sets the begin arrow head width.

        Args:
            value (ShapeArrowWidthType): The begin arrow head width to set.
        """
        pass

    @property
    @abc.abstractmethod
    def EndArrowHeadStyle(self)->'ShapeArrowStyleType':
        """
        Gets the end arrow head style.

        Returns:
            ShapeArrowStyleType: The end arrow head style.
        """
        pass

    @EndArrowHeadStyle.setter
    @abc.abstractmethod
    def EndArrowHeadStyle(self, value:'ShapeArrowStyleType'):
        """
        Sets the end arrow head style.

        Args:
            value (ShapeArrowStyleType): The end arrow head style to set.
        """
        pass

    @property
    @abc.abstractmethod
    def EndArrowheadLength(self)->'ShapeArrowLengthType':
        """
        Gets the end arrow head length.

        Returns:
            ShapeArrowLengthType: The end arrow head length.
        """
        pass

    @EndArrowheadLength.setter
    @abc.abstractmethod
    def EndArrowheadLength(self, value:'ShapeArrowLengthType'):
        """
        Sets the end arrow head length.

        Args:
            value (ShapeArrowLengthType): The end arrow head length to set.
        """
        pass

    @property
    @abc.abstractmethod
    def EndArrowheadWidth(self)->'ShapeArrowWidthType':
        """
        Gets the end arrow head width.

        Returns:
            ShapeArrowWidthType: The end arrow head width.
        """
        pass

    @EndArrowheadWidth.setter
    @abc.abstractmethod
    def EndArrowheadWidth(self, value:'ShapeArrowWidthType'):
        """
        Sets the end arrow head width.

        Args:
            value (ShapeArrowWidthType): The end arrow head width to set.
        """
        pass

    @property
    @abc.abstractmethod
    def DashStyle(self)->'ShapeDashLineStyleType':
        """
        Gets the dash style of the line.

        Returns:
            ShapeDashLineStyleType: The dash style.
        """
        pass

    @DashStyle.setter
    @abc.abstractmethod
    def DashStyle(self, value:'ShapeDashLineStyleType'):
        """
        Sets the dash style of the line.

        Args:
            value (ShapeDashLineStyleType): The dash style to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Style(self)->'ShapeLineStyleType':
        """
        Gets the line style.

        Returns:
            ShapeLineStyleType: The line style.
        """
        pass

    @Style.setter
    @abc.abstractmethod
    def Style(self, value:'ShapeLineStyleType'):
        """
        Sets the line style.

        Args:
            value (ShapeLineStyleType): The line style to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Transparency(self)->float:
        """
        Gets the transparency value (0-1).

        Returns:
            float: The transparency value.
        """
        pass

    @Transparency.setter
    @abc.abstractmethod
    def Transparency(self, value:float):
        """
        Sets the transparency value (0-1).

        Args:
            value (float): The transparency value to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Weight(self)->float:
        """
        Gets the weight (thickness) of the line.
        
        Returns:
            float: The line weight.
        """
        pass

    @Weight.setter
    @abc.abstractmethod
    def Weight(self, value:float):
        """
        Sets the weight (thickness) of the line.
        
        Args:
            value (float): The line weight to set.
        """
        pass

    @property
    @abc.abstractmethod
    def MiddleOffsetPercent(self)->float:
        """
        Gets the middle offset percent of the line.
        
        When middle point is located behind the start point, value is less than 0.
        When middle point is located at the start point, value is 0.
        When middle point is located at the end point, value is 1.
        When middle point is located behind the end point, value is greater than 1.
        
        Returns:
            float: The middle offset percent value.
        """
        pass

    @MiddleOffsetPercent.setter
    @abc.abstractmethod
    def MiddleOffsetPercent(self, value:float):
        """
        Sets the middle offset percent of the line.
        
        When middle point is located behind the start point, value is less than 0.
        When middle point is located at the start point, value is 0.
        When middle point is located at the end point, value is 1.
        When middle point is located behind the end point, value is greater than 1.
        
        Args:
            value (float): The middle offset percent value to set.
        """
        pass

    @property
    @abc.abstractmethod
    def LineShapeType(self)->'LineShapeType':
        """
        Gets the line shape type.
        
        Returns:
            LineShapeType: The line shape type.
        """
        pass

    @property
    @abc.abstractmethod
    def Rotation(self)->int:
        """
        Gets the rotation angle of the line shape in degrees.
        
        Returns:
            int: The rotation angle in degrees.
        """
        pass

    @Rotation.setter
    @abc.abstractmethod
    def Rotation(self, value:int):
        """
        Sets the rotation angle of the line shape in degrees.
        
        Args:
            value (int): The rotation angle in degrees to set.
        """
        pass

    @property
    @abc.abstractmethod
    def HyLink(self)->'IHyperLink':
        """
        Gets the hyperlink associated with the line shape.
        
        Returns:
            IHyperLink: The hyperlink object.
        """
        pass


