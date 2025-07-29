from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IOvalShape (  IPrstGeomShape) :
    """
    Interface for oval shape objects in Excel.
    
    This interface provides properties and methods to manipulate oval shapes in Excel worksheets.
    """
    @property

    @abc.abstractmethod
    def Line(self)->'IShapeLineFormat':
        """
        Gets the line format of the oval shape.
        
        Returns:
            IShapeLineFormat: The line format object.
        """
        pass


    @property
    @abc.abstractmethod
    def Rotation(self)->int:
        """
        Gets the rotation angle of the oval shape.
        
        Returns:
            int: The rotation angle in degrees.
        """
        pass


    @Rotation.setter
    @abc.abstractmethod
    def Rotation(self, value:int):
        """
        Sets the rotation angle of the oval shape.
        
        Args:
            value (int): The rotation angle in degrees.
        """
        pass


    @property

    @abc.abstractmethod
    def HyLink(self)->'IHyperLink':
        """
        Gets the hyperlink associated with the oval shape.
        
        Returns:
            IHyperLink: The hyperlink object.
        """
        pass


    @property

    @abc.abstractmethod
    def HAlignment(self)->'CommentHAlignType':
        """
        Gets the horizontal alignment of text in the oval shape.
        
        Returns:
            CommentHAlignType: The horizontal alignment type.
        """
        pass


    @HAlignment.setter
    @abc.abstractmethod
    def HAlignment(self, value:'CommentHAlignType'):
        """
        Sets the horizontal alignment of text in the oval shape.
        
        Args:
            value (CommentHAlignType): The horizontal alignment type.
        """
        pass


    @property

    @abc.abstractmethod
    def VAlignment(self)->'CommentVAlignType':
        """
        Gets the vertical alignment of text in the oval shape.
        
        Returns:
            CommentVAlignType: The vertical alignment type.
        """
        pass


    @VAlignment.setter
    @abc.abstractmethod
    def VAlignment(self, value:'CommentVAlignType'):
        """
        Sets the vertical alignment of text in the oval shape.
        
        Args:
            value (CommentVAlignType): The vertical alignment type.
        """
        pass


    @property

    @abc.abstractmethod
    def TextRotation(self)->'TextRotationType':
        """
        Gets the text rotation type for the oval shape.
        
        Returns:
            TextRotationType: The text rotation type.
        """
        pass


    @TextRotation.setter
    @abc.abstractmethod
    def TextRotation(self, value:'TextRotationType'):
        """
        Sets the text rotation type for the oval shape.
        
        Args:
            value (TextRotationType): The text rotation type.
        """
        pass


    @property
    @abc.abstractmethod
    def IsTextLocked(self)->bool:
        """
        Gets whether the text in the oval shape is locked.
        
        Returns:
            bool: True if the text is locked, otherwise False.
        """
        pass


    @IsTextLocked.setter
    @abc.abstractmethod
    def IsTextLocked(self, value:bool):
        """
        Sets whether the text in the oval shape is locked.
        
        Args:
            value (bool): True to lock the text, otherwise False.
        """
        pass


    @property

    @abc.abstractmethod
    def RichText(self)->'IRichTextString':
        """
        Gets the rich text string for the oval shape.
        
        Returns:
            IRichTextString: The rich text string object.
        """
        pass


    @property

    @abc.abstractmethod
    def Text(self)->str:
        """
        Gets the text content of the oval shape.
        
        Returns:
            str: The text content.
        """
        pass


    @Text.setter
    @abc.abstractmethod
    def Text(self, value:str):
        """
        Sets the text content of the oval shape.
        
        Args:
            value (str): The text content.
        """
        pass


