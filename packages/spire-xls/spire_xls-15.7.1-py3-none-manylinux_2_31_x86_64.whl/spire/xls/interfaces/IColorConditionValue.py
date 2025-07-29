from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IColorConditionValue (  IConditionValue) :
    """Color condition value interface.
    
    This interface extends the condition value interface to include color formatting
    capabilities. It is used in conditional formatting rules that apply color-based
    formatting, such as color scales and icon sets, allowing the specification of
    colors to be applied when conditions are met.
    
    Inherits from:
        IConditionValue: Condition value interface
    """
    @property

    @abc.abstractmethod
    def FormatColor(self)->'Color':
        """
        Gets the format color for the condition value.

        Returns:
            Color: The format color.
        """
        pass


    @FormatColor.setter
    @abc.abstractmethod
    def FormatColor(self, value:'Color'):
        """
        Sets the format color for the condition value.

        Args:
            value (Color): The format color to set.
        """
        pass


