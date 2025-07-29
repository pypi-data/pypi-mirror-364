from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IPivotCalculatedFields (abc.ABC) :
    """
    Represents a collection of calculated fields in a PivotTable.
    """
    @property
    @abc.abstractmethod
    def Count(self)->int:
        """
        Gets the number of calculated fields in the collection.

        Returns:
            int: The number of calculated fields.
        """
        pass


    @dispatch

    @abc.abstractmethod
    def get_Item(self ,index:int)->IPivotField:
        """
        Gets the calculated field at the specified index.

        Args:
            index (int): The index of the calculated field to retrieve.
        Returns:
            IPivotField: The calculated field at the specified index.
        """
        pass


    @dispatch

    @abc.abstractmethod
    def get_Item(self ,name:str)->IPivotField:
        """
        Gets the calculated field with the specified name.

        Args:
            name (str): The name of the calculated field to retrieve.
        Returns:
            IPivotField: The calculated field with the specified name.
        """
        pass



    @abc.abstractmethod
    def Add(self ,name:str,formula:str)->'IPivotField':
        """
        Adds a new calculated field to the collection.

        Args:
            name (str): The name of the new calculated field.
            formula (str): The formula for the calculated field.
        Returns:
            IPivotField: The newly added calculated field.
        """
        pass


