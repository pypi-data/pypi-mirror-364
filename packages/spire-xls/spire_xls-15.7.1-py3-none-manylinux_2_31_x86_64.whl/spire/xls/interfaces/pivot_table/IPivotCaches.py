from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IPivotCaches (abc.ABC) :
    """
    Represents a collection of PivotCache objects in a PivotTable.
    """
    @property
    @abc.abstractmethod
    def Count(self)->int:
        """
        Gets the number of PivotCache objects in the collection.

        Returns:
            int: The number of PivotCache objects.
        """
        pass



    @abc.abstractmethod
    def get_Item(self ,index:int)->'IPivotCache':
        """
        Gets the PivotCache at the specified index.

        Args:
            index (int): The index of the PivotCache to retrieve.
        Returns:
            IPivotCache: The PivotCache object at the specified index.
        """
        pass



    @abc.abstractmethod
    def Add(self ,range:'CellRange')->'PivotCache':
        """
        Adds a new PivotCache to the collection based on the specified range.

        Args:
            range (CellRange): The cell range to use as the data source.
        Returns:
            PivotCache: The newly added PivotCache object.
        """
        pass


