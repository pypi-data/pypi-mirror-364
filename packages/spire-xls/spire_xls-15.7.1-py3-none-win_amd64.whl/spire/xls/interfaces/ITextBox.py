from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ITextBox (  IExcelApplication) :
    """Interface for text box objects in Excel worksheets.
    
    This interface represents a text box in an Excel worksheet and provides properties
    to access and modify text box attributes such as alignment, text rotation, and content.
    """
    @property

    @abc.abstractmethod
    def HAlignment(self)->'CommentHAlignType':
        """Gets the horizontal alignment of text in the text box.
        
        Returns:
            CommentHAlignType: An enumeration value representing the horizontal alignment.
        """
        pass


    @HAlignment.setter
    @abc.abstractmethod
    def HAlignment(self, value:'CommentHAlignType'):
        """Sets the horizontal alignment of text in the text box.
        
        Args:
            value (CommentHAlignType): An enumeration value representing the horizontal alignment to set.
        """
        pass


    @property

    @abc.abstractmethod
    def VAlignment(self)->'CommentVAlignType':
        """Gets the vertical alignment of text in the text box.
        
        Returns:
            CommentVAlignType: An enumeration value representing the vertical alignment.
        """
        pass


    @VAlignment.setter
    @abc.abstractmethod
    def VAlignment(self, value:'CommentVAlignType'):
        """Sets the vertical alignment of text in the text box.
        
        Args:
            value (CommentVAlignType): An enumeration value representing the vertical alignment to set.
        """
        pass


    @property

    @abc.abstractmethod
    def TextRotation(self)->'TextRotationType':
        """Gets the rotation of text in the text box.
        
        Returns:
            TextRotationType: An enumeration value representing the text rotation.
        """
        pass


    @TextRotation.setter
    @abc.abstractmethod
    def TextRotation(self, value:'TextRotationType'):
        """Sets the rotation of text in the text box.
        
        Args:
            value (TextRotationType): An enumeration value representing the text rotation to set.
        """
        pass


    @property
    @abc.abstractmethod
    def IsTextLocked(self)->bool:
        """Gets whether the text in the text box is locked.
        
        Returns:
            bool: True if the text is locked; otherwise, False.
        """
        pass


    @IsTextLocked.setter
    @abc.abstractmethod
    def IsTextLocked(self, value:bool):
        """Sets whether the text in the text box is locked.
        
        Args:
            value (bool): True to lock the text; otherwise, False.
        """
        pass


    @property

    @abc.abstractmethod
    def RichText(self)->'IRichTextString':
        """Gets the rich text formatting of the text box content.
        
        Returns:
            IRichTextString: An object that represents the rich text formatting.
        """
        pass


    @property

    @abc.abstractmethod
    def Text(self)->str:
        """Gets the text content of the text box.
        
        Returns:
            str: The text content of the text box.
        """
        pass


    @Text.setter
    @abc.abstractmethod
    def Text(self, value:str):
        """Sets the text content of the text box.
        
        Args:
            value (str): The text content to set for the text box.
        """
        pass


