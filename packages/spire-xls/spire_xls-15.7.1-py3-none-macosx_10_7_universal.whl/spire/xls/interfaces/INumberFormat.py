from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class INumberFormat (  IExcelApplication) :
    """
    
    """
    @property
    @abc.abstractmethod
    def Index(self)->int:
        """
        Gets the index of the number format.

        Returns:
            int: The index of the number format.
        """
        pass

    @property
    @abc.abstractmethod
    def FormatString(self)->str:
        """
        Gets the format string of the number format.

        Returns:
            str: The format string.
        """
        pass

    @property
    @abc.abstractmethod
    def FormatType(self)->'CellFormatType':
        """
        Gets the format type of the number format.

        Returns:
            CellFormatType: The format type.
        """
        pass

    @property
    @abc.abstractmethod
    def IsFraction(self)->bool:
        """
        Gets whether the number format is a fraction.

        Returns:
            bool: True if the format is a fraction, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def IsScientific(self)->bool:
        """
        Gets whether the number format is scientific.

        Returns:
            bool: True if the format is scientific, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def IsThousandSeparator(self)->bool:
        """
        Gets whether the number format uses a thousand separator.

        Returns:
            bool: True if a thousand separator is used, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def DecimalPlaces(self)->int:
        """
        Gets the number of decimal places in the number format.

        Returns:
            int: The number of decimal places.
        """
        pass


