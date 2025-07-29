from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IColorScale (abc.ABC) :
    """Color scale interface.
    
    This interface provides functionality for creating and managing color scales in Excel
    conditional formatting. Color scales are visual tools that apply graduated colors to a
    range of cells based on their values. The interface allows setting the number of conditions
    for the color scale.
    """
#    @property
#
#    @abc.abstractmethod
#    def Criteria(self)->'IList1':
#        """
#
#        """
#        pass
#



    @abc.abstractmethod
    def SetConditionCount(self ,count:int):
        """
        Sets the number of conditions for the color scale.

        Args:
            count (int): The number of conditions to set.
        """
        pass


