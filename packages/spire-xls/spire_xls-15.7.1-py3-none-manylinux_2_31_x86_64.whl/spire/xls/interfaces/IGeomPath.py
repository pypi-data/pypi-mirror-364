from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IGeomPath (abc.ABC) :
    """
    Interface for geometric path objects in Excel.
    
    This interface represents a geometric path that can be used to define
    custom shapes in Excel. It serves as a base interface for more specific
    geometric path implementations.
    """
#    @property
#
#    @abc.abstractmethod
#    def SegmentPaths(self)->'CollectionExtended1':
#        """
#
#        """
#        pass
#


