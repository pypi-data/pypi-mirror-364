from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ISortColumn (abc.ABC) :
    """Sort column interface for Excel sorting operations.
    
    This interface represents a column in a sort operation and provides properties
    to configure how the column should be sorted, including the sort key, comparison type,
    sort order, and color-based sorting options.
    """
    @property
    @abc.abstractmethod
    def Key(self)->int:
        """Gets the key (column index) to sort by.
        
        This property returns the index of the column to sort by.
        
        Returns:
            int: The column index to sort by.
        """
        pass


    @Key.setter
    @abc.abstractmethod
    def Key(self, value:int):
        """Sets the key (column index) to sort by.
        
        This property sets the index of the column to sort by.
        
        Args:
            value (int): The column index to sort by.
        """
        pass


    @property
    @abc.abstractmethod
    def ComparsionType(self)->'SortComparsionType':
        """Gets the comparison type used for sorting.
        
        This property returns an enumeration value that defines how values in the column
        should be compared during sorting, such as by values, by cell color, by font color, etc.
        
        Returns:
            SortComparsionType: An enumeration value representing the comparison type.
        """
        pass


    @ComparsionType.setter
    @abc.abstractmethod
    def ComparsionType(self, value:'SortComparsionType'):
        """Sets the comparison type used for sorting.
        
        This property sets an enumeration value that defines how values in the column
        should be compared during sorting, such as by values, by cell color, by font color, etc.
        
        Args:
            value (SortComparsionType): An enumeration value representing the comparison type to set.
        """
        pass


    @property
    @abc.abstractmethod
    def Order(self)->'OrderBy':
        """Gets the sort order.
        
        This property returns an enumeration value that defines the sort order,
        such as ascending or descending.
        
        Returns:
            OrderBy: An enumeration value representing the sort order.
        """
        pass


    @Order.setter
    @abc.abstractmethod
    def Order(self, value:'OrderBy'):
        """Sets the sort order.
        
        This property sets an enumeration value that defines the sort order,
        such as ascending or descending.
        
        Args:
            value (OrderBy): An enumeration value representing the sort order to set.
        """
        pass


    @property
    @abc.abstractmethod
    def Color(self)->'Color':
        """Gets the color used for color-based sorting.
        
        This property returns a Color object that defines the color to sort by
        when using color-based sorting (e.g., when ComparsionType is set to sort by cell color or font color).
        
        Returns:
            Color: A Color object representing the color to sort by.
        """
        pass


    @Color.setter
    @abc.abstractmethod
    def Color(self, value:'Color'):
        """Sets the color used for color-based sorting.
        
        This property sets a Color object that defines the color to sort by
        when using color-based sorting (e.g., when ComparsionType is set to sort by cell color or font color).
        
        Args:
            value (Color): A Color object representing the color to sort by.
        """
        pass


    @abc.abstractmethod
    def SetLevel(self, priority:int):
        """Sets the priority level of this sort column.
        
        This method sets the priority level of this sort column in a multi-column sort operation.
        Lower priority values indicate higher precedence in the sort order.
        
        Args:
            priority (int): The priority level to set for this sort column.
        """
        pass


