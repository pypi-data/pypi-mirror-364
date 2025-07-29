from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IRectangleShape (  ITextBox, IPrstGeomShape) :
    """Rectangle shape interface for Excel.
    
    This interface represents a rectangle shape in an Excel worksheet.
    It provides properties to control the rectangle type, rotation, line formatting,
    and hyperlink settings. Rectangle shapes can be used for highlighting areas,
    creating containers, or adding decorative elements to a worksheet.
    
    Inherits from:
        ITextBox: Text box interface for handling text within the shape
        IPrstGeomShape: Preset geometry shape interface
    """
    @property
    @abc.abstractmethod
    def RectShapeType(self)->'RectangleShapeType':
        """Gets the rectangle shape type.
        
        This property returns an enumeration value indicating the specific type of
        rectangle shape, such as standard rectangle, rounded rectangle, snip corner, etc.
        
        Returns:
            RectangleShapeType: The type of the rectangle shape.
        """
        pass


    @property
    @abc.abstractmethod
    def Rotation(self)->int:
        """Gets the rotation angle of the rectangle shape in degrees.
        
        This property returns the rotation angle of the rectangle shape in degrees,
        where 0 represents no rotation and positive values represent clockwise rotation.
        
        Returns:
            int: The rotation angle in degrees.
        """
        pass


    @Rotation.setter
    @abc.abstractmethod
    def Rotation(self, value:int):
        """Sets the rotation angle of the rectangle shape in degrees.
        
        This property sets the rotation angle of the rectangle shape in degrees,
        where 0 represents no rotation and positive values represent clockwise rotation.
        
        Args:
            value (int): The rotation angle in degrees.
        """
        pass


    @property
    @abc.abstractmethod
    def Line(self)->'IShapeLineFormat':
        """Gets the line formatting for the rectangle's border.
        
        This property returns an interface that provides access to line formatting properties
        such as color, style, weight, etc. for the border of the rectangle shape.
        
        Returns:
            IShapeLineFormat: An interface for accessing and modifying the line formatting.
        """
        pass


    @property
    @abc.abstractmethod
    def HyLink(self)->'IHyperLink':
        """Gets the hyperlink associated with the rectangle shape.
        
        This property returns an interface that provides access to the hyperlink properties
        of the rectangle shape, allowing the shape to act as a clickable link.
        
        Returns:
            IHyperLink: An interface for accessing and modifying the hyperlink properties.
        """
        pass


