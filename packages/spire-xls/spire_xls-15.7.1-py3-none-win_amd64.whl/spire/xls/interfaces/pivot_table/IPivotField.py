from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IPivotField (abc.ABC) :
    """
    Represents a field in a PivotTable.
    """

    @abc.abstractmethod
    def AddLabelFilter(self ,type:'PivotLabelFilterType',value1:'SpireObject',value2:'SpireObject'):
        """
        Add label filter for pivot field, only for row and column field.

        Args:
            type: Filter type.
            value1: First filter value.
            value2: Second filter value, only for Between and NotBetween type.

        """
        pass



    @abc.abstractmethod
    def AddValueFilter(self ,type:'PivotValueFilterType',dataField:'IPivotDataField',value1:'SpireObject',value2:'SpireObject'):
        """
        Add value filter for pivot field, only for row and column field.

        Args:
            type: Filter type.
            dataField: Filter data field.
            value1: First filter value.
            value2: Second filter value, only for Between and NotBetween type.

        """
        pass
    @dispatch

    @abc.abstractmethod
    def CreateGroup(self ,startValue:float,endValue:float,intervalValue:float):
        """
        Create group for current field.

        Args:
            startValue: The start number value
            endValue: The end number value
            intervalValue: The interval number value

        """
        pass

    @property

    @abc.abstractmethod
    def CustomName(self)->str:
        """
        Gets or sets the custom name of the pivot field.

        Returns:
            str: The custom name of the pivot field.
        """
        pass

    @CustomName.setter
    @abc.abstractmethod
    def CustomName(self, value:str):
        """
        Sets the custom name of the pivot field.

        Args:
            value (str): The new custom name.
        """
        pass

    @property

    @abc.abstractmethod
    def Name(self)->str:
        """
        Gets the name of the pivot field.

        Returns:
            str: The name of the pivot field.
        """
        pass


    @property

    @abc.abstractmethod
    def Axis(self)->'AxisTypes':
        """
        Gets or sets the axis type of the pivot field.

        Returns:
            AxisTypes: The axis type.
        """
        pass


    @Axis.setter
    @abc.abstractmethod
    def Axis(self, value:'AxisTypes'):
        """
        Sets the axis type of the pivot field.

        Args:
            value (AxisTypes): The axis type to set.
        """
        pass


    @property

    @abc.abstractmethod
    def NumberFormat(self)->str:
        """
        Gets or sets the number format of the pivot field.

        Returns:
            str: The number format string.
        """
        pass


    @NumberFormat.setter
    @abc.abstractmethod
    def NumberFormat(self, value:str):
        """
        Sets the number format of the pivot field.

        Args:
            value (str): The number format string.
        """
        pass


    @property

    @abc.abstractmethod
    def Subtotals(self)->'SubtotalTypes':
        """
        Gets or sets the subtotal types for the pivot field.

        Returns:
            SubtotalTypes: The subtotal types.
        """
        pass


    @Subtotals.setter
    @abc.abstractmethod
    def Subtotals(self, value:'SubtotalTypes'):
        """
        Sets the subtotal types for the pivot field.

        Args:
            value (SubtotalTypes): The subtotal types to set.
        """
        pass


    @property
    @abc.abstractmethod
    def CanDragToRow(self)->bool:
        """
        Indicates whether the field can be dragged to the row area.

        Returns:
            bool: True if the field can be dragged to the row area; otherwise, False.
        """
        pass


    @CanDragToRow.setter
    @abc.abstractmethod
    def CanDragToRow(self, value:bool):
        """
        Sets whether the field can be dragged to the row area.

        Args:
            value (bool): True if the field can be dragged to the row area; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def CanDragToColumn(self)->bool:
        """
        Indicates whether the field can be dragged to the column area.

        Returns:
            bool: True if the field can be dragged to the column area; otherwise, False.
        """
        pass


    @CanDragToColumn.setter
    @abc.abstractmethod
    def CanDragToColumn(self, value:bool):
        """
        Sets whether the field can be dragged to the column area.

        Args:
            value (bool): True if the field can be dragged to the column area; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def CanDragToPage(self)->bool:
        """
        Indicates whether the field can be dragged to the page area.

        Returns:
            bool: True if the field can be dragged to the page area; otherwise, False.
        """
        pass


    @CanDragToPage.setter
    @abc.abstractmethod
    def CanDragToPage(self, value:bool):
        """
        Sets whether the field can be dragged to the page area.

        Args:
            value (bool): True if the field can be dragged to the page area; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def CanDragOff(self)->bool:
        """
        Indicates whether the field can be dragged off the PivotTable.

        Returns:
            bool: True if the field can be dragged off; otherwise, False.
        """
        pass


    @CanDragOff.setter
    @abc.abstractmethod
    def CanDragOff(self, value:bool):
        """
        Sets whether the field can be dragged off the PivotTable.

        Args:
            value (bool): True if the field can be dragged off; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def ShowBlankRow(self)->bool:
        """
        Indicates whether a blank row is shown for the field.

        Returns:
            bool: True if a blank row is shown; otherwise, False.
        """
        pass


    @ShowBlankRow.setter
    @abc.abstractmethod
    def ShowBlankRow(self, value:bool):
        """
        Sets whether a blank row is shown for the field.

        Args:
            value (bool): True to show a blank row; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def CanDragToData(self)->bool:
        """
        Indicates whether the field can be dragged to the data area.

        Returns:
            bool: True if the field can be dragged to the data area; otherwise, False.
        """
        pass


    @CanDragToData.setter
    @abc.abstractmethod
    def CanDragToData(self, value:bool):
        """
        Sets whether the field can be dragged to the data area.

        Args:
            value (bool): True if the field can be dragged to the data area; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsFormulaField(self)->bool:
        """
        Indicates whether the field is a formula field.

        Returns:
            bool: True if the field is a formula field; otherwise, False.
        """
        pass


    @property

    @abc.abstractmethod
    def Formula(self)->str:
        """
        Gets or sets the formula of the field.

        Returns:
            str: The formula string.
        """
        pass


    @Formula.setter
    @abc.abstractmethod
    def Formula(self, value:str):
        """
        Sets the formula of the field.

        Args:
            value (str): The formula string.
        """
        pass


    @property
    @abc.abstractmethod
    def RepeatItemLabels(self)->bool:
        """
        Indicates whether item labels are repeated for the field.

        Returns:
            bool: True if item labels are repeated; otherwise, False.
        """
        pass


    @RepeatItemLabels.setter
    @abc.abstractmethod
    def RepeatItemLabels(self, value:bool):
        """
        Sets whether item labels are repeated for the field.

        Args:
            value (bool): True to repeat item labels; otherwise, False.
        """
        pass


