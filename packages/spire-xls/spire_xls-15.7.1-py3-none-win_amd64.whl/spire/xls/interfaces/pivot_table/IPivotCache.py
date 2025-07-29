from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IPivotCache (abc.ABC) :
    """
    Represents a single PivotCache object in a PivotTable collection.
    """
    @property
    @abc.abstractmethod
    def Index(self)->int:
        """
        Gets the index of the PivotCache in the collection.

        Returns:
            int: The index of the PivotCache.
        """
        pass


    @property

    @abc.abstractmethod
    def SourceType(self)->'DataSourceType':
        """
        Gets the type of the data source for the PivotCache.

        Returns:
            DataSourceType: The type of the data source.
        """
        pass


    @property

    @abc.abstractmethod
    def SourceRange(self)->'IXLSRange':
        """
        Gets the source range for the PivotCache.

        Returns:
            IXLSRange: The source range.
        """
        pass


