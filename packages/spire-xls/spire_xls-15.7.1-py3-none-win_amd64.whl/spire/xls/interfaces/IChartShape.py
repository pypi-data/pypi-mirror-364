from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartShape (  IShape, IExcelApplication, IChart) :
    """

    """
    @property
    @abc.abstractmethod
    def TopRow(self)->int:
        """
        Top row of the chart in the worksheet.

        """
        pass


    @TopRow.setter
    @abc.abstractmethod
    def TopRow(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def BottomRow(self)->int:
        """
        Bottom row of the chart in the worksheet.

        """
        pass


    @BottomRow.setter
    @abc.abstractmethod
    def BottomRow(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def LeftColumn(self)->int:
        """
        Left column of the chart in the worksheet.

        """
        pass


    @LeftColumn.setter
    @abc.abstractmethod
    def LeftColumn(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def RightColumn(self)->int:
        """
        Right column of the chart in the worksheet.

        """
        pass


    @RightColumn.setter
    @abc.abstractmethod
    def RightColumn(self, value:int):
        """

        """
        pass


