from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IConditionalFormats (  IExcelApplication) :
    """Conditional formats collection interface.
    
    This interface represents a collection of conditional formatting rules in Excel.
    Conditional formatting allows cells to be formatted based on their values or other
    conditions. The interface provides methods for adding, accessing, and removing
    conditional formatting rules.
    
    Inherits from:
        IExcelApplication: Excel application interface
    """
    @property
    @abc.abstractmethod
    def Count(self)->int:
        """Gets the number of conditional formats in the collection.
        
        Returns:
            int: The number of conditional formats.
        """
        pass



    @abc.abstractmethod
    def get_Item(self ,index:int)->'IConditionalFormat':
        """Gets a conditional format by index.
        
        Args:
            index (int): The zero-based index of the conditional format to retrieve.
            
        Returns:
            IConditionalFormat: The conditional format at the specified index.
        """
        pass



    @abc.abstractmethod
    def AddCondition(self)->'IConditionalFormat':
        """Adds a new conditional format to the collection.
        
        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        pass



    @abc.abstractmethod
    def RemoveAt(self ,index:int):
        """Removes a conditional format at the specified index.
        
        Args:
            index (int): The zero-based index of the conditional format to remove.
        """
        pass


