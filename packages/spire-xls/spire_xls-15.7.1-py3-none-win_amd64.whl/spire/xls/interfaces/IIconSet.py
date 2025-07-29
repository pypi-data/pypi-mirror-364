from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IIconSet (abc.ABC) :
    """
    Interface for icon set conditional formatting in Excel.
    
    This interface provides properties and methods to manipulate icon set conditional
    formatting, which displays icons in cells based on their values.
    """
#    @property
#    @abc.abstractmethod
#    def IconCriteria(self)->'IList1':
#        """
#        Gets the icon criteria for the icon set.
#
#        Returns:
#            IList1: The icon criteria collection.
#        """
#        pass
#
    @property
    @abc.abstractmethod
    def IconSet(self)->'IconSetType':
        """
        Gets the icon set type.

        Returns:
            IconSetType: The icon set type.
        """
        pass

    @IconSet.setter
    @abc.abstractmethod
    def IconSet(self, value:'IconSetType'):
        """
        Sets the icon set type.

        Args:
            value (IconSetType): The icon set type to set.
        """
        pass

    @property
    @abc.abstractmethod
    def PercentileValues(self)->bool:
        """
        Gets whether percentile values are used.

        Returns:
            bool: True if percentile values are used, otherwise False.
        """
        pass

    @PercentileValues.setter
    @abc.abstractmethod
    def PercentileValues(self, value:bool):
        """
        Sets whether percentile values are used.

        Args:
            value (bool): True to use percentile values, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def IsReverseOrder(self)->bool:
        """
        Gets whether the icon set is in reverse order.

        Returns:
            bool: True if in reverse order, otherwise False.
        """
        pass

    @IsReverseOrder.setter
    @abc.abstractmethod
    def IsReverseOrder(self, value:bool):
        """
        Sets whether the icon set is in reverse order.

        Args:
            value (bool): True for reverse order, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def ShowIconOnly(self)->bool:
        """
        Gets whether only the icon is shown.

        Returns:
            bool: True if only the icon is shown, otherwise False.
        """
        pass

    @ShowIconOnly.setter
    @abc.abstractmethod
    def ShowIconOnly(self, value:bool):
        """
        Sets whether only the icon is shown.

        Args:
            value (bool): True to show only the icon, otherwise False.
        """
        pass


