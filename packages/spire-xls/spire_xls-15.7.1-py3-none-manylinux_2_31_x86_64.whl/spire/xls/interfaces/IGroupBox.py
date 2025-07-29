from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IGroupBox (  IShape, IExcelApplication) :
    """
    Interface for group box shape objects in Excel.
    
    This interface provides properties and methods to manipulate group box shapes
    in Excel worksheets, which are container controls that can group related controls.
    """
    @property
    @abc.abstractmethod
    def Display3DShading(self)->bool:
        """
        Gets whether the group box displays 3D shading.

        Returns:
            bool: True if 3D shading is displayed, otherwise False.
        """
        pass

    @Display3DShading.setter
    @abc.abstractmethod
    def Display3DShading(self, value:bool):
        """
        Sets whether the group box displays 3D shading.

        Args:
            value (bool): True to display 3D shading, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def Text(self)->str:
        """
        Gets the text of the group box.

        Returns:
            str: The text of the group box.
        """
        pass

    @Text.setter
    @abc.abstractmethod
    def Text(self, value:str):
        """
        Sets the text of the group box.

        Args:
            value (str): The text to set.
        """
        pass

    @property
    @abc.abstractmethod
    def IsTextLocked(self)->bool:
        """
        Gets whether the text of the group box is locked.

        Returns:
            bool: True if the text is locked, otherwise False.
        """
        pass

    @IsTextLocked.setter
    @abc.abstractmethod
    def IsTextLocked(self, value:bool):
        """
        Sets whether the text of the group box is locked.

        Args:
            value (bool): True to lock the text, otherwise False.
        """
        pass


