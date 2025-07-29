from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IMarkersDesigner (abc.ABC) :
    """
    Represents a designer for markers.
    """
    @dispatch
    @abc.abstractmethod
    def ApplyMarkers(self):
        """
        Applies markers to the designer.
        """
        pass

    @dispatch
    @abc.abstractmethod
    def ApplyMarkers(self ,action:UnknownVariableAction):
        """
        Applies markers to the designer with a specified action for unknown variables.

        Args:
            action (UnknownVariableAction): The action for unknown variables.
        """
        pass

    @abc.abstractmethod
    def AddVariable(self ,strName:str,variable:'SpireObject',rowCount:int):
        """
        Adds a variable to the designer.

        Args:
            strName (str): The name of the variable.
            variable (SpireObject): The variable object.
            rowCount (int): The row count for the variable.
        """
        pass

    @abc.abstractmethod
    def RemoveVariable(self ,strName:str):
        """
        Removes a variable from the designer.

        Args:
            strName (str): The name of the variable to remove.
        """
        pass

    @abc.abstractmethod
    def ContainsVariable(self ,strName:str)->bool:
        """
        Checks if the designer contains a variable with the specified name.

        Args:
            strName (str): The name of the variable to check.

        Returns:
            bool: True if the variable exists, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def MarkerPrefix(self)->str:
        """
        Gets the marker prefix.

        Returns:
            str: The marker prefix.
        """
        pass

    @MarkerPrefix.setter
    @abc.abstractmethod
    def MarkerPrefix(self, value:str):
        """
        Sets the marker prefix.

        Args:
            value (str): The marker prefix to set.
        """
        pass

    @property
    @abc.abstractmethod
    def ArgumentSeparator(self)->int:
        """
        Gets the argument separator.

        Returns:
            int: The argument separator.
        """
        pass

    @ArgumentSeparator.setter
    @abc.abstractmethod
    def ArgumentSeparator(self, value:int):
        """
        Sets the argument separator.

        Args:
            value (int): The argument separator to set.
        """
        pass

    @property
    @abc.abstractmethod
    def IsDetectDataTypes(self)->bool:
        """
        Gets whether data types are detected automatically.

        Returns:
            bool: True if data types are detected, otherwise False.
        """
        pass

    @IsDetectDataTypes.setter
    @abc.abstractmethod
    def IsDetectDataTypes(self, value:bool):
        """
        Sets whether data types are detected automatically.

        Args:
            value (bool): True to detect data types, otherwise False.
        """
        pass


