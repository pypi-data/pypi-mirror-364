from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class INamedObject (abc.ABC) :
    """
    Interface for objects that have a name property.
    
    This interface provides access to the name property of Excel objects
    that can be identified by a name.
    """
    @property
    @abc.abstractmethod
    def Name(self)->str:
        """
        Gets the name of the object.

        Returns:
            str: The name of the object.
        """
        pass


