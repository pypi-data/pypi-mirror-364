from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IStyle (  IExtendedFormat, IExcelApplication, IOptimizedUpdate) :
    """Interface for Excel cell styles.
    
    This interface represents a style in an Excel workbook and provides properties
    to access and modify style attributes such as name, built-in status, and interior formatting.
    """
    @property
    @abc.abstractmethod
    def BuiltIn(self)->bool:
        """Gets whether the style is a built-in Excel style.
        
        Returns:
            bool: True if the style is built-in; otherwise, False.
        """
        pass


    @property

    @abc.abstractmethod
    def Name(self)->str:
        """Gets the name of the style.
        
        Returns:
            str: The name of the style.
        """
        pass


    @property
    @abc.abstractmethod
    def IsInitialized(self)->bool:
        """Gets whether the style has been initialized.
        
        Returns:
            bool: True if the style has been initialized; otherwise, False.
        """
        pass


    @property

    @abc.abstractmethod
    def Interior(self)->'IInterior':
        """Gets the interior formatting of the style.
        
        Returns:
            IInterior: An object that represents the interior formatting of the style.
        """
        pass


