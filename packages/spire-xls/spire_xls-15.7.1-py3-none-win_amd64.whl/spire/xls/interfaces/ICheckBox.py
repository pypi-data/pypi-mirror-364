from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ICheckBox (  IShape, IExcelApplication) :
    """Checkbox interface.
    
    This interface provides functionality for creating and managing checkbox form controls
    in Excel worksheets. Checkboxes allow users to make binary choices (checked or unchecked)
    and can be linked to cell values. The interface provides methods to set the check state,
    appearance properties like 3D shading, text display, and line formatting.
    
    Inherits from:
        IShape: Shape interface
        IExcelApplication: Excel application interface
    """
    @property
    @abc.abstractmethod
    def CheckState(self)->'CheckState':
        """
        Gets the check state of the checkbox.

        Returns:
            CheckState: The check state of the checkbox.
        """
        pass

    @CheckState.setter
    @abc.abstractmethod
    def CheckState(self, value:'CheckState'):
        """
        Sets the check state of the checkbox.

        Args:
            value (CheckState): The check state to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Line(self)->'IShapeLineFormat':
        """
        Gets the line format of the checkbox.

        Returns:
            IShapeLineFormat: The line format object.
        """
        pass

    @property
    @abc.abstractmethod
    def Text(self)->str:
        """
        Gets the text of the checkbox.

        Returns:
            str: The text of the checkbox.
        """
        pass

    @Text.setter
    @abc.abstractmethod
    def Text(self, value:str):
        """
        Sets the text of the checkbox.

        Args:
            value (str): The text to set.
        """
        pass

    @property
    @abc.abstractmethod
    def IsTextLocked(self)->bool:
        """
        Gets whether the text of the checkbox is locked.

        Returns:
            bool: True if the text is locked, otherwise False.
        """
        pass

    @IsTextLocked.setter
    @abc.abstractmethod
    def IsTextLocked(self, value:bool):
        """
        Sets whether the text of the checkbox is locked.

        Args:
            value (bool): True to lock the text, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def Display3DShading(self)->bool:
        """
        Gets whether the checkbox displays 3D shading.

        Returns:
            bool: True if 3D shading is displayed, otherwise False.
        """
        pass

    @Display3DShading.setter
    @abc.abstractmethod
    def Display3DShading(self, value:bool):
        """
        Sets whether the checkbox displays 3D shading.

        Args:
            value (bool): True to display 3D shading, otherwise False.
        """
        pass


