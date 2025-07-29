from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ILabelShape (  IShape, IExcelApplication) :
    """
    Interface for label shape objects in Excel.
    
    This interface provides properties and methods to manipulate label shapes
    in Excel worksheets, which are shapes that display text.
    """
    @property
    @abc.abstractmethod
    def Text(self)->str:
        """
        Gets the text of the label shape.

        Returns:
            str: The text of the label shape.
        """
        pass

    @Text.setter
    @abc.abstractmethod
    def Text(self, value:str):
        """
        Sets the text of the label shape.

        Args:
            value (str): The text to set.
        """
        pass

    @property
    @abc.abstractmethod
    def IsTextLocked(self)->bool:
        """
        Gets whether the text of the label shape is locked.

        Returns:
            bool: True if the text is locked, otherwise False.
        """
        pass

    @IsTextLocked.setter
    @abc.abstractmethod
    def IsTextLocked(self, value:bool):
        """
        Sets whether the text of the label shape is locked.

        Args:
            value (bool): True to lock the text, otherwise False.
        """
        pass


