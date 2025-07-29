from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IExtendIndex (abc.ABC) :
    """Interface for accessing extended format index.
    
    This interface provides functionality to access the extended format index,
    which is typically used to reference specific formatting in a spreadsheet.
    """
    @property
    @abc.abstractmethod
    def ExtendedFormatIndex(self)->int:
        """
        Gets the extended format index.

        Returns:
            int: The extended format index.
        """
        pass


