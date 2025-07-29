from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IGeomPathShape (  IPrstGeomShape, IShape, IExcelApplication) :
    """
    Interface for geometric path shape objects in Excel.
    
    This interface extends IPrstGeomShape, IShape, and IExcelApplication to provide
    functionality for shapes that are defined by geometric paths.
    """

    @abc.abstractmethod
    def AddPath(self)->'IGeomPathInfo':
        """
        Adds a new geometric path info to the shape.

        Returns:
            IGeomPathInfo: The added geometric path info.
        """
        pass

    @abc.abstractmethod
    def get_Item(self ,index:int)->'IGeomPathInfo':
        """
        Gets the geometric path info by index.

        Args:
            index (int): The index of the geometric path info.

        Returns:
            IGeomPathInfo: The geometric path info at the specified index.
        """
        pass


