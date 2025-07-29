from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IVPageBreaks (  abc.ABC) :
    """Collection of vertical page breaks in a worksheet.
    
    This interface represents a collection of vertical page breaks in an Excel worksheet.
    It provides access to the count of vertical page breaks and methods to manage them.
    """
    @property
    @abc.abstractmethod
    def Count(self)->int:
        """Gets the number of vertical page breaks in the collection.
        
        Returns:
            int: The number of vertical page breaks.
        """
        pass


    #@property

    #@abc.abstractmethod
    #def Parent(self)->'SpireObject':
    #    """Gets the parent object of the vertical page breaks collection.
    #    
    #    Returns:
    #        SpireObject: The parent object that contains this collection.
    #    """
    #    pass


