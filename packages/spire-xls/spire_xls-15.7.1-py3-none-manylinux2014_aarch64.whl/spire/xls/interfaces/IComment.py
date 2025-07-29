from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IComment (  ITextBoxShape, ITextBox, IShape) :
    """Comment interface.
    
    This interface provides functionality for creating and managing comments in Excel worksheets.
    Comments are notes or explanations that can be attached to cells to provide additional
    information. The interface allows setting the author, visibility, position, and auto-sizing
    properties of comments.
    
    Inherits from:
        ITextBoxShape: Text box shape interface
        ITextBox: Text box interface
        IShape: Shape interface
    """
    @property
    @abc.abstractmethod
    def Author(self)->str:
        """
        Gets the author of the comment.

        Returns:
            str: The author name.
        """
        pass

    @Author.setter
    @abc.abstractmethod
    def Author(self, value:str):
        """
        Sets the author of the comment.

        Args:
            value (str): The author name.
        """
        pass

    @property
    @abc.abstractmethod
    def IsVisible(self)->bool:
        """
        Gets whether the comment is visible.

        Returns:
            bool: True if visible, otherwise False.
        """
        pass

    @IsVisible.setter
    @abc.abstractmethod
    def IsVisible(self, value:bool):
        """
        Sets whether the comment is visible.

        Args:
            value (bool): True to make visible, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def Row(self)->int:
        """
        Gets the row index of the comment.

        Returns:
            int: The row index.
        """
        pass

    @property
    @abc.abstractmethod
    def Column(self)->int:
        """
        Gets the column index of the comment.

        Returns:
            int: The column index.
        """
        pass

    @property
    @abc.abstractmethod
    def AutoSize(self)->bool:
        """
        Gets whether the comment is auto-sized.

        Returns:
            bool: True if auto-sized, otherwise False.
        """
        pass

    @AutoSize.setter
    @abc.abstractmethod
    def AutoSize(self, value:bool):
        """
        Sets whether the comment is auto-sized.

        Args:
            value (bool): True to auto-size, otherwise False.
        """
        pass


