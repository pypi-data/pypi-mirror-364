from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IPictureShape (  IShape, IExcelApplication) :
    """Picture shape interface for Excel.
    
    This interface represents a picture or image shape in an Excel worksheet.
    It provides properties and methods to manipulate the picture's appearance,
    including file information, color settings, fill and line formatting.
    
    Inherits from:
        IShape: Base shape interface
        IExcelApplication: Excel application interface
    """
    @property
    @abc.abstractmethod
    def FileName(self)->str:
        """Gets the filename of the picture.
        
        Returns:
            str: The filename of the picture, including path information if available.
        """
        pass


    @property
    @abc.abstractmethod
    def Picture(self)->'Stream':
        """Gets the picture data as a stream.
        
        Returns:
            Stream: A stream containing the binary data of the picture.
        """
        pass


    @property
    @abc.abstractmethod
    def ColorFrom(self)->'Color':
        """Gets the starting color for gradient effects applied to the picture.
        
        Returns:
            Color: The starting color of the gradient effect.
        """
        pass


    @ColorFrom.setter
    @abc.abstractmethod
    def ColorFrom(self, value:'Color'):
        """Sets the starting color for gradient effects applied to the picture.
        
        Args:
            value (Color): The starting color to be used for gradient effects.
        """
        pass


    @property
    @abc.abstractmethod
    def ColorTo(self)->'Color':
        """Gets the ending color for gradient effects applied to the picture.
        
        Returns:
            Color: The ending color of the gradient effect.
        """
        pass


    @ColorTo.setter
    @abc.abstractmethod
    def ColorTo(self, value:'Color'):
        """Sets the ending color for gradient effects applied to the picture.
        
        Args:
            value (Color): The ending color to be used for gradient effects.
        """
        pass


    @property
    @abc.abstractmethod
    def Fill(self)->'IShapeFill':
        """Gets the fill formatting properties for the picture shape.
        
        Returns:
            IShapeFill: An interface for accessing and modifying the fill formatting.
        """
        pass


    @property
    @abc.abstractmethod
    def Line(self)->'IShapeLineFormat':
        """Gets the line formatting properties for the picture shape border.
        
        Returns:
            IShapeLineFormat: An interface for accessing and modifying the line formatting.
        """
        pass


    @abc.abstractmethod
    def Remove(self, removeImage:bool):
        """Removes the picture shape from the worksheet.
        
        Args:
            removeImage (bool): When True, removes the image data as well as the shape;
                               when False, removes only the shape container while preserving the image data.
        """
        pass


