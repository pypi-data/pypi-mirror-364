from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IDataBar (abc.ABC) :
    """Data bar interface.
    
    This interface provides functionality for creating and managing data bars in Excel
    conditional formatting. Data bars are visual tools that display colored bars in cells
    to represent the relative magnitude of cell values. The interface allows setting minimum
    and maximum points, color, percentage ranges, and whether to show the cell value.
    """
    @property
    @abc.abstractmethod
    def MinPoint(self)->'IConditionValue':
        """
        Gets the minimum point condition value for the data bar.

        Returns:
            IConditionValue: The minimum point condition value.
        """
        pass

    @property
    @abc.abstractmethod
    def MaxPoint(self)->'IConditionValue':
        """
        Gets the maximum point condition value for the data bar.

        Returns:
            IConditionValue: The maximum point condition value.
        """
        pass

    @property
    @abc.abstractmethod
    def BarColor(self)->'Color':
        """
        Gets the color of the data bar.

        Returns:
            Color: The color of the data bar.
        """
        pass

    @BarColor.setter
    @abc.abstractmethod
    def BarColor(self, value:'Color'):
        """
        Sets the color of the data bar.

        Args:
            value (Color): The color to set.
        """
        pass

    @property
    @abc.abstractmethod
    def PercentMax(self)->int:
        """
        Gets the maximum percentage for the data bar.

        Returns:
            int: The maximum percentage.
        """
        pass

    @PercentMax.setter
    @abc.abstractmethod
    def PercentMax(self, value:int):
        """
        Sets the maximum percentage for the data bar.

        Args:
            value (int): The maximum percentage to set.
        """
        pass

    @property
    @abc.abstractmethod
    def PercentMin(self)->int:
        """
        Gets the minimum percentage for the data bar.

        Returns:
            int: The minimum percentage.
        """
        pass

    @PercentMin.setter
    @abc.abstractmethod
    def PercentMin(self, value:int):
        """
        Sets the minimum percentage for the data bar.

        Args:
            value (int): The minimum percentage to set.
        """
        pass

    @property
    @abc.abstractmethod
    def ShowValue(self)->bool:
        """
        Gets whether the value is shown in the data bar.

        Returns:
            bool: True if the value is shown, otherwise False.
        """
        pass

    @ShowValue.setter
    @abc.abstractmethod
    def ShowValue(self, value:bool):
        """
        Sets whether the value is shown in the data bar.

        Args:
            value (bool): True to show the value, otherwise False.
        """
        pass


