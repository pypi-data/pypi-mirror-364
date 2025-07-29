from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IMigrantRange (  IXLSRange) :
    """
    Interface for a range that can be relocated within a worksheet.
    
    This interface extends IXLSRange and provides functionality to reset
    the position of a range by changing its row and column coordinates.
    """

    @abc.abstractmethod
    def ResetRowColumn(self ,iRow:int,iColumn:int):
        """
        Resets the row and column of the migrant range.

        Args:
            iRow (int): The row index to reset.
            iColumn (int): The column index to reset.
        """
        pass


