from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IArcShape (  ITextBox, IPrstGeomShape) :
    """Arc shape interface.
    
    This interface provides functionality for creating and managing arc shapes in Excel worksheets.
    Arc shapes are curved line segments that can be customized with various properties such as
    rotation angle, line formatting, arrow styles, and colors. The interface allows detailed
    control over the appearance of arcs, including arrow heads at the beginning and end of the arc.
    
    Inherits from:
        ITextBox: Text box interface
        IPrstGeomShape: Preset geometry shape interface
    """
    @property
    @abc.abstractmethod
    def Line(self)->'IShapeLineFormat':
        """
        Gets the line format of the arc shape.

        Returns:
            IShapeLineFormat: The line format object.
        """
        pass

    @property
    @abc.abstractmethod
    def Rotation(self)->int:
        """
        Gets the rotation angle of the arc shape.

        Returns:
            int: The rotation angle in degrees.
        """
        pass

    @Rotation.setter
    @abc.abstractmethod
    def Rotation(self, value:int):
        """
        Sets the rotation angle of the arc shape.

        Args:
            value (int): The rotation angle in degrees.
        """
        pass

    @property
    @abc.abstractmethod
    def Color(self)->'Color':
        """
        Gets the line color of the arc shape.

        Returns:
            Color: The color object.
        """
        pass

    @Color.setter
    @abc.abstractmethod
    def Color(self, value:'Color'):
        """
        Sets the line color of the arc shape.

        Args:
            value (Color): The color object.
        """
        pass

    @property
    @abc.abstractmethod
    def BeginArrowHeadStyle(self)->'ShapeArrowStyleType':
        """
        Gets the begin arrow head style of the arc shape.

        Returns:
            ShapeArrowStyleType: The arrow head style type.
        """
        pass

    @BeginArrowHeadStyle.setter
    @abc.abstractmethod
    def BeginArrowHeadStyle(self, value:'ShapeArrowStyleType'):
        """
        Sets the begin arrow head style of the arc shape.

        Args:
            value (ShapeArrowStyleType): The arrow head style type.
        """
        pass

    @property
    @abc.abstractmethod
    def BeginArrowheadLength(self)->'ShapeArrowLengthType':
        """
        Gets the begin arrow head length of the arc shape.

        Returns:
            ShapeArrowLengthType: The arrow head length type.
        """
        pass

    @BeginArrowheadLength.setter
    @abc.abstractmethod
    def BeginArrowheadLength(self, value:'ShapeArrowLengthType'):
        """
        Sets the begin arrow head length of the arc shape.

        Args:
            value (ShapeArrowLengthType): The arrow head length type.
        """
        pass

    @property
    @abc.abstractmethod
    def BeginArrowheadWidth(self)->'ShapeArrowWidthType':
        """
        Gets the begin arrow head width of the arc shape.

        Returns:
            ShapeArrowWidthType: The arrow head width type.
        """
        pass

    @BeginArrowheadWidth.setter
    @abc.abstractmethod
    def BeginArrowheadWidth(self, value:'ShapeArrowWidthType'):
        """
        Sets the begin arrow head width of the arc shape.

        Args:
            value (ShapeArrowWidthType): The arrow head width type.
        """
        pass

    @property
    @abc.abstractmethod
    def EndArrowHeadStyle(self)->'ShapeArrowStyleType':
        """
        Gets the end arrow head style of the arc shape.

        Returns:
            ShapeArrowStyleType: The arrow head style type.
        """
        pass

    @EndArrowHeadStyle.setter
    @abc.abstractmethod
    def EndArrowHeadStyle(self, value:'ShapeArrowStyleType'):
        """
        Sets the end arrow head style of the arc shape.

        Args:
            value (ShapeArrowStyleType): The arrow head style type.
        """
        pass

    @property
    @abc.abstractmethod
    def EndArrowheadLength(self)->'ShapeArrowLengthType':
        """
        Gets the end arrow head length of the arc shape.

        Returns:
            ShapeArrowLengthType: The arrow head length type.
        """
        pass

    @EndArrowheadLength.setter
    @abc.abstractmethod
    def EndArrowheadLength(self, value:'ShapeArrowLengthType'):
        """
        Sets the end arrow head length of the arc shape.

        Args:
            value (ShapeArrowLengthType): The arrow head length type.
        """
        pass

    @property
    @abc.abstractmethod
    def EndArrowheadWidth(self)->'ShapeArrowWidthType':
        """
        Gets the end arrow head width of the arc shape.

        Returns:
            ShapeArrowWidthType: The arrow head width type.
        """
        pass

    @EndArrowheadWidth.setter
    @abc.abstractmethod
    def EndArrowheadWidth(self, value:'ShapeArrowWidthType'):
        """
        Sets the end arrow head width of the arc shape.

        Args:
            value (ShapeArrowWidthType): The arrow head width type.
        """
        pass

    @property
    @abc.abstractmethod
    def DashStyle(self)->'ShapeDashLineStyleType':
        """
        Gets the dash style of the arc shape.

        Returns:
            ShapeDashLineStyleType: The dash line style type.
        """
        pass

    @DashStyle.setter
    @abc.abstractmethod
    def DashStyle(self, value:'ShapeDashLineStyleType'):
        """
        Sets the dash style of the arc shape.

        Args:
            value (ShapeDashLineStyleType): The dash line style type.
        """
        pass

    @property
    @abc.abstractmethod
    def Style(self)->'ShapeLineStyleType':
        """
        Gets the line style of the arc shape.

        Returns:
            ShapeLineStyleType: The line style type.
        """
        pass

    @Style.setter
    @abc.abstractmethod
    def Style(self, value:'ShapeLineStyleType'):
        """
        Sets the line style of the arc shape.

        Args:
            value (ShapeLineStyleType): The line style type.
        """
        pass

    @property
    @abc.abstractmethod
    def Weight(self)->float:
        """
        Gets the line weight of the arc shape.

        Returns:
            float: The line weight.
        """
        pass

    @Weight.setter
    @abc.abstractmethod
    def Weight(self, value:float):
        """
        Sets the line weight of the arc shape.

        Args:
            value (float): The line weight.
        """
        pass

    @property
    @abc.abstractmethod
    def HyLink(self)->'IHyperLink':
        """
        Gets the hyperlink associated with the arc shape.

        Returns:
            IHyperLink: The hyperlink object.
        """
        pass


