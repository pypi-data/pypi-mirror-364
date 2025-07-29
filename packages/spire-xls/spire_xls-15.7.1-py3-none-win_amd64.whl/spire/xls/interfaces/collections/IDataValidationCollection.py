from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IDataValidationCollection (abc.ABC) :
    """

    """
    @property
    @abc.abstractmethod
    def IsPromptBoxPositionFixed(self)->bool:
        """
        Indicates whehter prompt box has fixed position..

        """
        pass


    @property
    @abc.abstractmethod
    def IsPromptBoxVisible(self)->bool:
        """
        Indicates whehter prompt box is visible..

        """
        pass


    @property

    @abc.abstractmethod
    def ParentTable(self)->'IDataValidationTable':
        """

        """
        pass


    @property
    @abc.abstractmethod
    def PromptBoxHPosition(self)->int:
        """
        Vertical position of the prompt box.

        """
        pass


    @PromptBoxHPosition.setter
    @abc.abstractmethod
    def PromptBoxHPosition(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def PromptBoxVPosition(self)->int:
        """
        Vertical position of the prompt box.

        """
        pass


    @PromptBoxVPosition.setter
    @abc.abstractmethod
    def PromptBoxVPosition(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def ShapesCount(self)->int:
        """

        """
        pass



    @abc.abstractmethod
    def get_Item(self ,index:int)->'IDataValidation':
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Workbook(self)->'Workbook':
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Worksheet(self)->'Worksheet':
        """

        """
        pass


#
#    @abc.abstractmethod
#    def Remove(self ,rectangles:'Rectangle[]'):
#        """
#
#        """
#        pass
#


