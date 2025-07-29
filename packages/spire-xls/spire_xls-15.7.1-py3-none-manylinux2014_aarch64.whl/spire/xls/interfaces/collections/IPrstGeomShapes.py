from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IPrstGeomShapes (abc.ABC) :
    """

    """
    @property
    @abc.abstractmethod
    def Count(self)->int:
        """

        """
        pass


    @dispatch

    @abc.abstractmethod
    def get_Item(self ,index:int)->IPrstGeomShape:
        """
        Returns single item from the collection.

        Args:
            index: Item's index to get.

        Returns:
            Single item from the collection.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def get_Item(self ,name:str)->IPrstGeomShape:
        """

        """
        pass



    @abc.abstractmethod
    def AddPrstGeomShape(self ,row:int,column:int,height:int,width:int,shapeType:'PrstGeomShapeType')->'IPrstGeomShape':
        """
        Adds new item to the collection.

        Args:
            row: One-based row index of the top-left corner of the new item.
            column: One-based column index of the top-left corner of the new item.
            height: Height in pixels of the new item.
            width: Width in pixels of the new item.

        Returns:
            Newly added item.

        """
        pass



    @abc.abstractmethod
    def AddNotPrimitiveShape(self ,row:int,column:int,width:int,height:int)->'IGeomPathShape':
        """

        """
        pass


    @dispatch

    @abc.abstractmethod
    def get_Item(self ,shapeType:PrstGeomShapeType)->List[IPrstGeomShape]:
        """

        """
        pass



