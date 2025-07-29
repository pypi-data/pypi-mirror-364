from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ISortedRule (abc.ABC) :
    """Interface for defining sorting rules in Excel worksheets.
    
    This abstract class provides methods for sorting Excel ranges based on different
    data types and criteria.
    """
    @property

    @abc.abstractmethod
    def Range(self)->'IXLSRange':
        """Gets the Excel range to which the sorting rule applies.
        
        Returns:
            IXLSRange: The Excel range object associated with this sorting rule.
        """
        pass


    @Range.setter
    @abc.abstractmethod
    def Range(self, value:'IXLSRange'):
        """Sets the Excel range to which the sorting rule applies.
        
        Args:
            value (IXLSRange): The Excel range object to associate with this sorting rule.
        """
        pass



    @abc.abstractmethod
    def SortInt(self ,left:int,right:int,columnIndex:int):
        """Sorts integer values in ascending order within the specified range.
        
        Args:
            left (int): The left boundary index of the range to sort.
            right (int): The right boundary index of the range to sort.
            columnIndex (int): The index of the column to sort by.
        """
        pass



    @abc.abstractmethod
    def SortFloat(self ,left:int,right:int,columnIndex:int):
        """Sorts floating-point values in ascending order within the specified range.
        
        Args:
            left (int): The left boundary index of the range to sort.
            right (int): The right boundary index of the range to sort.
            columnIndex (int): The index of the column to sort by.
        """
        pass



    @abc.abstractmethod
    def SortDate(self ,left:int,right:int,columnIndex:int):
        """Sorts date values in ascending order within the specified range.
        
        Args:
            left (int): The left boundary index of the range to sort.
            right (int): The right boundary index of the range to sort.
            columnIndex (int): The index of the column to sort by.
        """
        pass



    @abc.abstractmethod
    def SortString(self ,left:int,right:int,columnIndex:int):
        """Sorts string values in ascending order within the specified range.
        
        Args:
            left (int): The left boundary index of the range to sort.
            right (int): The right boundary index of the range to sort.
            columnIndex (int): The index of the column to sort by.
        """
        pass



    @abc.abstractmethod
    def SortOnTypes(self ,left:int,right:int,columnIndex:int):
        """Sorts values based on their data types within the specified range.
        
        Args:
            left (int): The left boundary index of the range to sort.
            right (int): The right boundary index of the range to sort.
            columnIndex (int): The index of the column to sort by.
        """
        pass



    @abc.abstractmethod
    def SortIntDesc(self ,left:int,right:int,columnIndex:int):
        """Sorts integer values in descending order within the specified range.
        
        Args:
            left (int): The left boundary index of the range to sort.
            right (int): The right boundary index of the range to sort.
            columnIndex (int): The index of the column to sort by.
        """
        pass



    @abc.abstractmethod
    def SortFloatDesc(self ,left:int,right:int,columnIndex:int):
        """Sorts floating-point values in descending order within the specified range.
        
        Args:
            left (int): The left boundary index of the range to sort.
            right (int): The right boundary index of the range to sort.
            columnIndex (int): The index of the column to sort by.
        """
        pass



    @abc.abstractmethod
    def SortDateDesc(self ,left:int,right:int,columnIndex:int):
        """Sorts date values in descending order within the specified range.
        
        Args:
            left (int): The left boundary index of the range to sort.
            right (int): The right boundary index of the range to sort.
            columnIndex (int): The index of the column to sort by.
        """
        pass



    @abc.abstractmethod
    def SortStringDesc(self ,left:int,right:int,columnIndex:int):
        """Sorts string values in descending order within the specified range.
        
        Args:
            left (int): The left boundary index of the range to sort.
            right (int): The right boundary index of the range to sort.
            columnIndex (int): The index of the column to sort by.
        """
        pass


