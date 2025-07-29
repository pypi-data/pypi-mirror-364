from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IXLSRanges (  IXLSRange) :
    """Excel ranges collection interface.
    
    This interface represents a collection of Excel ranges (IXLSRange objects).
    It provides functionality for managing multiple ranges, including removing ranges
    from the collection and accessing ranges by index.
    
    Inherits from:
        IXLSRange: Excel range interface
    """

    @abc.abstractmethod
    def Remove(self ,range:'IXLSRange'):
        """
        Removes range from the collection.

        Args:
            range (IXLSRange): Range to remove.
        """
        pass

    @abc.abstractmethod
    def get_Item(self ,index:int)->'IXLSRange':
        """
        Returns item by index from the collection.

        Returns:
            IXLSRange: The range item at the specified index.
        """
        pass


