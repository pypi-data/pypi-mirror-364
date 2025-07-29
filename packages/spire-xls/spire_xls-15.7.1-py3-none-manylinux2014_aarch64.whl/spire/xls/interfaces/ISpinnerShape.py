from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ISpinnerShape (  IShape, IExcelApplication) :
    """Interface for spinner control shapes in Excel worksheets.
    
    This interface represents a spinner control shape that allows users to 
    increment or decrement numeric values within a specified range.
    """
    @property
    @abc.abstractmethod
    def Display3DShading(self)->bool:
        """Gets whether 3D shading is displayed for the spinner.
        
        Returns:
            bool: True if 3D shading is displayed; otherwise, False.
        """
        pass


    @Display3DShading.setter
    @abc.abstractmethod
    def Display3DShading(self, value:bool):
        """Sets whether 3D shading is displayed for the spinner.
        
        Args:
            value (bool): True to display 3D shading; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def CurrentValue(self)->int:
        """Gets the current value of the spinner.
        
        Returns:
            int: The current value of the spinner.
        """
        pass


    @CurrentValue.setter
    @abc.abstractmethod
    def CurrentValue(self, value:int):
        """Sets the current value of the spinner.
        
        Args:
            value (int): The value to set for the spinner.
        """
        pass


    @property
    @abc.abstractmethod
    def Min(self)->int:
        """Gets the minimum value allowed for the spinner.
        
        Returns:
            int: The minimum value of the spinner.
        """
        pass


    @Min.setter
    @abc.abstractmethod
    def Min(self, value:int):
        """Sets the minimum value allowed for the spinner.
        
        Args:
            value (int): The minimum value to set for the spinner.
        """
        pass


    @property
    @abc.abstractmethod
    def Max(self)->int:
        """Gets the maximum value allowed for the spinner.
        
        Returns:
            int: The maximum value of the spinner.
        """
        pass


    @Max.setter
    @abc.abstractmethod
    def Max(self, value:int):
        """Sets the maximum value allowed for the spinner.
        
        Args:
            value (int): The maximum value to set for the spinner.
        """
        pass


    @property
    @abc.abstractmethod
    def IncrementalChange(self)->int:
        """Gets the amount to change the spinner value with each increment.
        
        Returns:
            int: The incremental change value.
        """
        pass


    @IncrementalChange.setter
    @abc.abstractmethod
    def IncrementalChange(self, value:int):
        """Sets the amount to change the spinner value with each increment.
        
        Args:
            value (int): The incremental change value to set.
        """
        pass


