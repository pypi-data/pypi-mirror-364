from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IConditionValue (abc.ABC) :
    """Condition value interface.
    
    This interface provides functionality for defining and managing condition values used in Excel
    conditional formatting rules. Condition values specify the criteria that determine when a
    formatting rule should be applied. The interface allows setting the condition type, value,
    and comparison operators.
    """
    @property
    @abc.abstractmethod
    def Type(self)->'ConditionValueType':
        """
        Gets the type of the condition value.

        Returns:
            ConditionValueType: The type of the condition value.
        """
        pass

    @Type.setter
    @abc.abstractmethod
    def Type(self, value:'ConditionValueType'):
        """
        Sets the type of the condition value.

        Args:
            value (ConditionValueType): The type to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Value(self)->'SpireObject':
        """
        Gets the value of the condition.

        Returns:
            SpireObject: The value of the condition.
        """
        pass

    @Value.setter
    @abc.abstractmethod
    def Value(self, value:'SpireObject'):
        """
        Sets the value of the condition.

        Args:
            value (SpireObject): The value to set.
        """
        pass

    @property
    @abc.abstractmethod
    def IsGTE(self)->bool:
        """
        Gets whether the condition is greater than or equal to.

        Returns:
            bool: True if greater than or equal to, otherwise False.
        """
        pass

    @IsGTE.setter
    @abc.abstractmethod
    def IsGTE(self, value:bool):
        """
        Sets whether the condition is greater than or equal to.

        Args:
            value (bool): True if greater than or equal to, otherwise False.
        """
        pass


