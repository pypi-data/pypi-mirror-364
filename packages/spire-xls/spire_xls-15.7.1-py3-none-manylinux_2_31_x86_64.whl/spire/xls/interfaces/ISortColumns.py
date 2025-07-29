from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ISortColumns (  SpireObject) :
    """Collection of sort columns for Excel sorting operations.
    
    This interface represents a collection of sort columns and provides methods
    to add, remove, and access sort columns in a sort operation. It allows configuring
    multi-column sort operations with different sort criteria for each column.
    """
    @property
    @abc.abstractmethod
    def Count(self)->int:
        """Gets the number of sort columns in the collection.
        
        This property returns the count of sort columns currently in the collection.
        
        Returns:
            int: The number of sort columns.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def Add(self, key:int, sortComparsionType:SortComparsionType, orderBy:OrderBy)->ISortColumn:
        """Adds a new sort column with specified comparison type and order.
        
        This method adds a new sort column to the collection with the specified key,
        comparison type, and sort order.
        
        Args:
            key (int): The column index to sort by.
            sortComparsionType (SortComparsionType): The comparison type to use for sorting.
            orderBy (OrderBy): The sort order (ascending or descending).
            
        Returns:
            ISortColumn: The newly created sort column object.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def Add(self, key:int, orderBy:OrderBy)->ISortColumn:
        """Adds a new sort column with default comparison type and specified order.
        
        This method adds a new sort column to the collection with the specified key
        and sort order, using the default comparison type.
        
        Args:
            key (int): The column index to sort by.
            orderBy (OrderBy): The sort order (ascending or descending).
            
        Returns:
            ISortColumn: The newly created sort column object.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def Remove(self, key:int):
        """Removes a sort column by its key (column index).
        
        This method removes the sort column with the specified key from the collection.
        
        Args:
            key (int): The column index of the sort column to remove.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def Remove(self, sortField:ISortColumn):
        """Removes a specific sort column object.
        
        This method removes the specified sort column object from the collection.
        
        Args:
            sortField (ISortColumn): The sort column object to remove.
        """
        pass


    @abc.abstractmethod
    def get_Item(self, index:int)->'ISortColumn':
        """Gets the sort column at the specified index.
        
        This method returns the sort column at the specified position in the collection.
        
        Args:
            index (int): The zero-based index of the sort column to retrieve.
            
        Returns:
            ISortColumn: The sort column at the specified index.
        """
        pass


