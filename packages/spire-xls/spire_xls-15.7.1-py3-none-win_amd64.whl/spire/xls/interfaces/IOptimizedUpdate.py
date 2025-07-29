from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IOptimizedUpdate (abc.ABC) :
    """
    Interface for objects that support optimized batch updates.
    
    This interface provides methods to begin and end batch update operations,
    which can improve performance when making multiple changes to an object.
    """
    @abc.abstractmethod
    def BeginUpdate(self):
        """
        Begins a batch update operation.
        
        Call this method before making multiple changes to the object to improve performance.
        """
        pass


    @abc.abstractmethod
    def EndUpdate(self):
        """
        Ends a batch update operation.
        
        Call this method after making multiple changes to apply all changes at once.
        """
        pass


