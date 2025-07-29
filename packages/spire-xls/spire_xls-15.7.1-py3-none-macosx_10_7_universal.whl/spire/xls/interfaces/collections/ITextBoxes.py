from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ITextBoxes (abc.ABC) :
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
    def get_Item(self ,index:int)->ITextBoxLinkShape:
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
    def get_Item(self ,name:str)->ITextBoxLinkShape:
        """

        """
        pass



    @abc.abstractmethod
    def AddTextBox(self ,row:int,column:int,height:int,width:int)->'ITextBoxLinkShape':
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


