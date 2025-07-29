from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IShapeLineFormat (abc.ABC) :
    """Shape line formatting interface for Excel shapes.
    
    This interface provides properties and methods to control the line formatting
    of shapes in Excel, including line color, weight, style, dash style, arrow styles,
    and other line-related attributes. It allows detailed customization of line effects
    for shapes, charts, and other objects.
    """
    @property
    @abc.abstractmethod
    def Weight(self)->float:
        """Gets the weight (thickness) of the line.
        
        This property returns the weight (thickness) of the line in points.
        
        Returns:
            float: The weight of the line in points.
        """
        pass


    @Weight.setter
    @abc.abstractmethod
    def Weight(self, value:float):
        """Sets the weight (thickness) of the line.
        
        This property sets the weight (thickness) of the line in points.
        
        Args:
            value (float): The weight of the line in points.
        """
        pass


    @property
    @abc.abstractmethod
    def ForeColor(self)->'Color':
        """Gets the custom foreground color of the line.
        
        This property returns a Color object that defines a custom foreground color
        used for the line. This is applicable for solid lines and patterned lines.
        
        Returns:
            Color: A Color object representing the custom foreground color.
        """
        pass


    @ForeColor.setter
    @abc.abstractmethod
    def ForeColor(self, value:'Color'):
        """Sets the custom foreground color of the line.
        
        This property sets a Color object that defines a custom foreground color
        to use for the line. This is applicable for solid lines and patterned lines.
        
        Args:
            value (Color): A Color object representing the custom foreground color to set.
        """
        pass


    @property
    @abc.abstractmethod
    def BackColor(self)->'Color':
        """Gets the custom background color of the line.
        
        This property returns a Color object that defines a custom background color
        used for the line. This is primarily applicable for patterned lines.
        
        Returns:
            Color: A Color object representing the custom background color.
        """
        pass


    @BackColor.setter
    @abc.abstractmethod
    def BackColor(self, value:'Color'):
        """Sets the custom background color of the line.
        
        This property sets a Color object that defines a custom background color
        to use for the line. This is primarily applicable for patterned lines.
        
        Args:
            value (Color): A Color object representing the custom background color to set.
        """
        pass


    @property
    @abc.abstractmethod
    def ForeKnownColor(self)->'ExcelColors':
        """Gets the predefined foreground color of the line.
        
        This property returns an enumeration value that defines a predefined foreground color
        used for the line. This is applicable for solid lines and patterned lines.
        
        Returns:
            ExcelColors: An enumeration value representing the predefined foreground color.
        """
        pass


    @ForeKnownColor.setter
    @abc.abstractmethod
    def ForeKnownColor(self, value:'ExcelColors'):
        """Sets the predefined foreground color of the line.
        
        This property sets an enumeration value that defines a predefined foreground color
        to use for the line. This is applicable for solid lines and patterned lines.
        
        Args:
            value (ExcelColors): An enumeration value representing the predefined foreground color to set.
        """
        pass


    @property
    @abc.abstractmethod
    def BackKnownColor(self)->'ExcelColors':
        """Gets the predefined background color of the line.
        
        This property returns an enumeration value that defines a predefined background color
        used for the line. This is primarily applicable for patterned lines.
        
        Returns:
            ExcelColors: An enumeration value representing the predefined background color.
        """
        pass


    @BackKnownColor.setter
    @abc.abstractmethod
    def BackKnownColor(self, value:'ExcelColors'):
        """Sets the predefined background color of the line.
        
        This property sets an enumeration value that defines a predefined background color
        to use for the line. This is primarily applicable for patterned lines.
        
        Args:
            value (ExcelColors): An enumeration value representing the predefined background color to set.
        """
        pass


    @property
    @abc.abstractmethod
    def BeginArrowHeadStyle(self)->'ShapeArrowStyleType':
        """Gets the style of the arrowhead at the beginning of the line.
        
        This property returns an enumeration value that defines the style of the arrowhead
        at the beginning of the line, such as none, arrow, diamond, oval, etc.
        
        Returns:
            ShapeArrowStyleType: An enumeration value representing the beginning arrowhead style.
        """
        pass


    @BeginArrowHeadStyle.setter
    @abc.abstractmethod
    def BeginArrowHeadStyle(self, value:'ShapeArrowStyleType'):
        """Sets the style of the arrowhead at the beginning of the line.
        
        This property sets an enumeration value that defines the style of the arrowhead
        at the beginning of the line, such as none, arrow, diamond, oval, etc.
        
        Args:
            value (ShapeArrowStyleType): An enumeration value representing the beginning arrowhead style to set.
        """
        pass


    @property
    @abc.abstractmethod
    def EndArrowHeadStyle(self)->'ShapeArrowStyleType':
        """Gets the style of the arrowhead at the end of the line.
        
        This property returns an enumeration value that defines the style of the arrowhead
        at the end of the line, such as none, arrow, diamond, oval, etc.
        
        Returns:
            ShapeArrowStyleType: An enumeration value representing the end arrowhead style.
        """
        pass


    @EndArrowHeadStyle.setter
    @abc.abstractmethod
    def EndArrowHeadStyle(self, value:'ShapeArrowStyleType'):
        """Sets the style of the arrowhead at the end of the line.
        
        This property sets an enumeration value that defines the style of the arrowhead
        at the end of the line, such as none, arrow, diamond, oval, etc.
        
        Args:
            value (ShapeArrowStyleType): An enumeration value representing the end arrowhead style to set.
        """
        pass


    @property
    @abc.abstractmethod
    def BeginArrowheadLength(self)->'ShapeArrowLengthType':
        """Gets the length of the arrowhead at the beginning of the line.
        
        This property returns an enumeration value that defines the length of the arrowhead
        at the beginning of the line, such as short, medium, or long.
        
        Returns:
            ShapeArrowLengthType: An enumeration value representing the beginning arrowhead length.
        """
        pass


    @BeginArrowheadLength.setter
    @abc.abstractmethod
    def BeginArrowheadLength(self, value:'ShapeArrowLengthType'):
        """Sets the length of the arrowhead at the beginning of the line.
        
        This property sets an enumeration value that defines the length of the arrowhead
        at the beginning of the line, such as short, medium, or long.
        
        Args:
            value (ShapeArrowLengthType): An enumeration value representing the beginning arrowhead length to set.
        """
        pass


    @property
    @abc.abstractmethod
    def EndArrowheadLength(self)->'ShapeArrowLengthType':
        """Gets the length of the arrowhead at the end of the line.
        
        This property returns an enumeration value that defines the length of the arrowhead
        at the end of the line, such as short, medium, or long.
        
        Returns:
            ShapeArrowLengthType: An enumeration value representing the end arrowhead length.
        """
        pass


    @EndArrowheadLength.setter
    @abc.abstractmethod
    def EndArrowheadLength(self, value:'ShapeArrowLengthType'):
        """Sets the length of the arrowhead at the end of the line.
        
        This property sets an enumeration value that defines the length of the arrowhead
        at the end of the line, such as short, medium, or long.
        
        Args:
            value (ShapeArrowLengthType): An enumeration value representing the end arrowhead length to set.
        """
        pass


    @property
    @abc.abstractmethod
    def BeginArrowheadWidth(self)->'ShapeArrowWidthType':
        """Gets the width of the arrowhead at the beginning of the line.
        
        This property returns an enumeration value that defines the width of the arrowhead
        at the beginning of the line, such as narrow, medium, or wide.
        
        Returns:
            ShapeArrowWidthType: An enumeration value representing the beginning arrowhead width.
        """
        pass


    @BeginArrowheadWidth.setter
    @abc.abstractmethod
    def BeginArrowheadWidth(self, value:'ShapeArrowWidthType'):
        """Sets the width of the arrowhead at the beginning of the line.
        
        This property sets an enumeration value that defines the width of the arrowhead
        at the beginning of the line, such as narrow, medium, or wide.
        
        Args:
            value (ShapeArrowWidthType): An enumeration value representing the beginning arrowhead width to set.
        """
        pass


    @property
    @abc.abstractmethod
    def EndArrowheadWidth(self)->'ShapeArrowWidthType':
        """Gets the width of the arrowhead at the end of the line.
        
        This property returns an enumeration value that defines the width of the arrowhead
        at the end of the line, such as narrow, medium, or wide.
        
        Returns:
            ShapeArrowWidthType: An enumeration value representing the end arrowhead width.
        """
        pass


    @EndArrowheadWidth.setter
    @abc.abstractmethod
    def EndArrowheadWidth(self, value:'ShapeArrowWidthType'):
        """Sets the width of the arrowhead at the end of the line.
        
        This property sets an enumeration value that defines the width of the arrowhead
        at the end of the line, such as narrow, medium, or wide.
        
        Args:
            value (ShapeArrowWidthType): An enumeration value representing the end arrowhead width to set.
        """
        pass


    @property
    @abc.abstractmethod
    def DashStyle(self)->'ShapeDashLineStyleType':
        """Gets the dash style of the line.
        
        This property returns an enumeration value that defines the dash style of the line,
        such as solid, dash, dot, dash-dot, etc.
        
        Returns:
            ShapeDashLineStyleType: An enumeration value representing the dash style of the line.
        """
        pass


    @DashStyle.setter
    @abc.abstractmethod
    def DashStyle(self, value:'ShapeDashLineStyleType'):
        """Sets the dash style of the line.
        
        This property sets an enumeration value that defines the dash style of the line,
        such as solid, dash, dot, dash-dot, etc.
        
        Args:
            value (ShapeDashLineStyleType): An enumeration value representing the dash style to set.
        """
        pass


    @property
    @abc.abstractmethod
    def Style(self)->'ShapeLineStyleType':
        """Gets the line style.
        
        This property returns an enumeration value that defines the line style,
        such as single, double, thick-thin, etc.
        
        Returns:
            ShapeLineStyleType: An enumeration value representing the line style.
        """
        pass


    @Style.setter
    @abc.abstractmethod
    def Style(self, value:'ShapeLineStyleType'):
        """Sets the line style.
        
        This property sets an enumeration value that defines the line style,
        such as single, double, thick-thin, etc.
        
        Args:
            value (ShapeLineStyleType): An enumeration value representing the line style to set.
        """
        pass


    @property
    @abc.abstractmethod
    def Transparency(self)->float:
        """Gets the transparency of the line.
        
        This property returns the transparency value (from 0.0 to 1.0) for the line,
        where 0.0 is completely opaque and 1.0 is completely transparent.
        
        Returns:
            float: The transparency value (0.0-1.0).
        """
        pass


    @Transparency.setter
    @abc.abstractmethod
    def Transparency(self, value:float):
        """Sets the transparency of the line.
        
        This property sets the transparency value (from 0.0 to 1.0) for the line,
        where 0.0 is completely opaque and 1.0 is completely transparent.
        
        Args:
            value (float): The transparency value (0.0-1.0).
        """
        pass


    @property
    @abc.abstractmethod
    def Visible(self)->bool:
        """Gets whether the line is visible.
        
        When true, the line is visible. When false, the line is not visible.
        
        Returns:
            bool: True if the line is visible, otherwise False.
        """
        pass


    @Visible.setter
    @abc.abstractmethod
    def Visible(self, value:bool):
        """Sets whether the line is visible.
        
        When set to true, the line will be visible. When set to false, the line will not be visible.
        
        Args:
            value (bool): True to make the line visible, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def Pattern(self)->'GradientPatternType':
        """Gets the pattern type of the line.
        
        This property returns an enumeration value that defines the pattern type used
        for the line, such as horizontal lines, vertical lines, diagonal lines, dots, etc.
        This is applicable when the line has a pattern fill.
        
        Returns:
            GradientPatternType: An enumeration value representing the pattern type.
        """
        pass


    @Pattern.setter
    @abc.abstractmethod
    def Pattern(self, value:'GradientPatternType'):
        """Sets the pattern type of the line.
        
        This property sets an enumeration value that defines the pattern type to use
        for the line, such as horizontal lines, vertical lines, diagonal lines, dots, etc.
        This is applicable when the line has a pattern fill.
        
        Args:
            value (GradientPatternType): An enumeration value representing the pattern type to set.
        """
        pass


    @property
    @abc.abstractmethod
    def HasPattern(self)->bool:
        """Gets whether the line has a pattern.
        
        When true, the line has a pattern fill. When false, the line has a solid fill.
        
        Returns:
            bool: True if the line has a pattern, otherwise False.
        """
        pass


    @HasPattern.setter
    @abc.abstractmethod
    def HasPattern(self, value:bool):
        """Sets whether the line has a pattern.
        
        When set to true, the line will have a pattern fill. When set to false, the line will have a solid fill.
        
        Args:
            value (bool): True to apply a pattern to the line, otherwise False.
        """
        pass


