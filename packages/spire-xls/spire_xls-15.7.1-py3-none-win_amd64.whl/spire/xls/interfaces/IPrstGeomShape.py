from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IPrstGeomShape (  IShape, IExcelApplication) :
    """Preset geometry shape interface for Excel.
    
    This interface represents a shape with preset geometry in an Excel worksheet.
    Preset geometry shapes are predefined shapes like rectangles, circles, arrows, stars, etc.
    This interface provides properties to control the shape type, text content, and text alignment.
    
    Inherits from:
        IShape: Base shape interface
        IExcelApplication: Excel application interface
    """
    @property
    @abc.abstractmethod
    def PrstShapeType(self)->'PrstGeomShapeType':
        """Gets the preset shape type.
        
        This property returns an enumeration value indicating the type of preset geometry
        shape, such as rectangle, circle, arrow, star, etc.
        
        Returns:
            PrstGeomShapeType: The preset geometry shape type.
        """
        pass


    @property
    @abc.abstractmethod
    def Text(self)->str:
        """Gets the text displayed in the shape.
        
        This property returns the text content that is displayed inside the shape.
        
        Returns:
            str: The text content of the shape.
        """
        pass


    @Text.setter
    @abc.abstractmethod
    def Text(self, value:str):
        """Sets the text displayed in the shape.
        
        This property sets the text content that is displayed inside the shape.
        
        Args:
            value (str): The new text content for the shape.
        """
        pass


#    @property
#
#    @abc.abstractmethod
#    def GeomPaths(self)->'CollectionExtended1':
#        """Gets the geometric paths that define the shape.
#        
#        This property returns a collection of geometric paths that define the
#        outline and structure of the shape.
#        
#        Returns:
#            CollectionExtended1: A collection of geometric paths.
#        """
#        pass
#


    @property
    @abc.abstractmethod
    def TextVerticalAlignment(self)->'ExcelVerticalAlignment':
        """Gets the vertical alignment of text within the shape.
        
        This property returns an enumeration value indicating how text is vertically
        aligned within the shape (top, middle, bottom, etc.).
        
        Returns:
            ExcelVerticalAlignment: The vertical alignment of text within the shape.
        """
        pass


    @TextVerticalAlignment.setter
    @abc.abstractmethod
    def TextVerticalAlignment(self, value:'ExcelVerticalAlignment'):
        """Sets the vertical alignment of text within the shape.
        
        This property sets how text is vertically aligned within the shape
        (top, middle, bottom, etc.).
        
        Args:
            value (ExcelVerticalAlignment): The vertical alignment to set for the text.
        """
        pass


