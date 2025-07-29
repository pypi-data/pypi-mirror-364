from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IErrorIndicator (abc.ABC) :
    """Error indicator interface.
    
    This interface provides functionality for managing error indicators in Excel,
    allowing setting and getting error ignore options. Error indicators are typically
    used to identify and handle potential errors or warnings in Excel worksheets.
    """
    @property
    @abc.abstractmethod
    def IgnoreOptions(self)->'IgnoreErrorType':
        """
        Gets the ignore error options for the indicator.

        Returns:
            IgnoreErrorType: The ignore error options.
        """
        pass

    @IgnoreOptions.setter
    @abc.abstractmethod
    def IgnoreOptions(self, value:'IgnoreErrorType'):
        """
        Sets the ignore error options for the indicator.

        Args:
            value (IgnoreErrorType): The ignore error options to set.
        """
        pass


