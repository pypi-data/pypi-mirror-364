from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IDataValidation (  IExcelApplication, IOptimizedUpdate) :
    """Data validation interface.
    
    This interface provides functionality for creating and managing data validation rules
    in Excel cells. Data validation is used to restrict the type and values of data that
    users can enter into a cell and can provide input prompts and error messages.
    The interface includes functionality for setting validation conditions, comparison operators,
    error alerts, input messages, and more.
    
    Inherits from:
        IExcelApplication: Excel application interface
        IOptimizedUpdate: Optimized update interface
    """
    @property
    @abc.abstractmethod
    def InputTitle(self)->str:
        """
        Gets the input title for the data validation.

        Returns:
            str: The input title.
        """
        pass

    @InputTitle.setter
    @abc.abstractmethod
    def InputTitle(self, value:str):
        """
        Sets the input title for the data validation.

        Args:
            value (str): The input title to set.
        """
        pass

    @property
    @abc.abstractmethod
    def InputMessage(self)->str:
        """
        Gets the input message for the data validation.

        Returns:
            str: The input message.
        """
        pass

    @InputMessage.setter
    @abc.abstractmethod
    def InputMessage(self, value:str):
        """
        Sets the input message for the data validation.

        Args:
            value (str): The input message to set.
        """
        pass

    @property
    @abc.abstractmethod
    def ErrorTitle(self)->str:
        """
        Gets the error title for the data validation.

        Returns:
            str: The error title.
        """
        pass

    @ErrorTitle.setter
    @abc.abstractmethod
    def ErrorTitle(self, value:str):
        """
        Sets the error title for the data validation.

        Args:
            value (str): The error title to set.
        """
        pass

    @property
    @abc.abstractmethod
    def ErrorMessage(self)->str:
        """
        Gets the error message for the data validation.

        Returns:
            str: The error message.
        """
        pass

    @ErrorMessage.setter
    @abc.abstractmethod
    def ErrorMessage(self, value:str):
        """
        Sets the error message for the data validation.

        Args:
            value (str): The error message to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Formula1(self)->str:
        """
        Gets the first formula for the data validation.

        Returns:
            str: The first formula.
        """
        pass

    @Formula1.setter
    @abc.abstractmethod
    def Formula1(self, value:str):
        """
        Sets the first formula for the data validation.

        Args:
            value (str): The first formula to set.
        """
        pass

    @property
    @abc.abstractmethod
    def DateTime1(self)->'DateTime':
        """
        Gets the first date/time value for the data validation.

        Returns:
            DateTime: The first date/time value.
        """
        pass

    @DateTime1.setter
    @abc.abstractmethod
    def DateTime1(self, value:'DateTime'):
        """
        Sets the first date/time value for the data validation.

        Args:
            value (DateTime): The first date/time value to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Formula2(self)->str:
        """
        Gets the second formula for the data validation.

        Returns:
            str: The second formula.
        """
        pass

    @Formula2.setter
    @abc.abstractmethod
    def Formula2(self, value:str):
        """
        Sets the second formula for the data validation.

        Args:
            value (str): The second formula to set.
        """
        pass

    @property
    @abc.abstractmethod
    def DateTime2(self)->'DateTime':
        """
        Gets the second date/time value for the data validation.

        Returns:
            DateTime: The second date/time value.
        """
        pass

    @DateTime2.setter
    @abc.abstractmethod
    def DateTime2(self, value:'DateTime'):
        """
        Sets the second date/time value for the data validation.

        Args:
            value (DateTime): The second date/time value to set.
        """
        pass

    @property
    @abc.abstractmethod
    def AllowType(self)->'CellDataType':
        """
        Gets the allowed cell data type for the data validation.

        Returns:
            CellDataType: The allowed cell data type.
        """
        pass

    @AllowType.setter
    @abc.abstractmethod
    def AllowType(self, value:'CellDataType'):
        """
        Sets the allowed cell data type for the data validation.

        Args:
            value (CellDataType): The allowed cell data type to set.
        """
        pass

    @property
    @abc.abstractmethod
    def CompareOperator(self)->'ValidationComparisonOperator':
        """
        Gets the comparison operator for the data validation.

        Returns:
            ValidationComparisonOperator: The comparison operator.
        """
        pass

    @CompareOperator.setter
    @abc.abstractmethod
    def CompareOperator(self, value:'ValidationComparisonOperator'):
        """
        Sets the comparison operator for the data validation.

        Args:
            value (ValidationComparisonOperator): The comparison operator to set.
        """
        pass

    @property
    @abc.abstractmethod
    def IsListInFormula(self)->bool:
        """
        Gets whether the list is specified in the formula.

        Returns:
            bool: True if the list is in the formula, otherwise False.
        """
        pass

    @IsListInFormula.setter
    @abc.abstractmethod
    def IsListInFormula(self, value:bool):
        """
        Sets whether the list is specified in the formula.

        Args:
            value (bool): True if the list is in the formula, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def IgnoreBlank(self)->bool:
        """
        Gets whether blank values are ignored in the data validation.

        Returns:
            bool: True if blank values are ignored, otherwise False.
        """
        pass

    @IgnoreBlank.setter
    @abc.abstractmethod
    def IgnoreBlank(self, value:bool):
        """
        Sets whether blank values are ignored in the data validation.

        Args:
            value (bool): True if blank values are ignored, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def IsSuppressDropDownArrow(self)->bool:
        """
        Gets whether the drop-down arrow is suppressed.

        Returns:
            bool: True if the drop-down arrow is suppressed, otherwise False.
        """
        pass

    @IsSuppressDropDownArrow.setter
    @abc.abstractmethod
    def IsSuppressDropDownArrow(self, value:bool):
        """
        Sets whether the drop-down arrow is suppressed.

        Args:
            value (bool): True if the drop-down arrow is suppressed, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def ShowInput(self)->bool:
        """
        Gets whether the input message is shown.

        Returns:
            bool: True if the input message is shown, otherwise False.
        """
        pass

    @ShowInput.setter
    @abc.abstractmethod
    def ShowInput(self, value:bool):
        """
        Sets whether the input message is shown.

        Args:
            value (bool): True if the input message is shown, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def ShowError(self)->bool:
        """
        Gets whether the error message is shown.

        Returns:
            bool: True if the error message is shown, otherwise False.
        """
        pass

    @ShowError.setter
    @abc.abstractmethod
    def ShowError(self, value:bool):
        """
        Sets whether the error message is shown.

        Args:
            value (bool): True if the error message is shown, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def PromptBoxHPosition(self)->int:
        """
        Gets the horizontal position of the prompt box.

        Returns:
            int: The horizontal position.
        """
        pass

    @PromptBoxHPosition.setter
    @abc.abstractmethod
    def PromptBoxHPosition(self, value:int):
        """
        Sets the horizontal position of the prompt box.

        Args:
            value (int): The horizontal position to set.
        """
        pass

    @property
    @abc.abstractmethod
    def PromptBoxVPosition(self)->int:
        """
        Gets the vertical position of the prompt box.

        Returns:
            int: The vertical position.
        """
        pass

    @PromptBoxVPosition.setter
    @abc.abstractmethod
    def PromptBoxVPosition(self, value:int):
        """
        Sets the vertical position of the prompt box.

        Args:
            value (int): The vertical position to set.
        """
        pass

    @property
    @abc.abstractmethod
    def IsInputVisible(self)->bool:
        """
        Gets whether the input box is visible.

        Returns:
            bool: True if the input box is visible, otherwise False.
        """
        pass

    @IsInputVisible.setter
    @abc.abstractmethod
    def IsInputVisible(self, value:bool):
        """
        Sets whether the input box is visible.

        Args:
            value (bool): True if the input box is visible, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def IsInputPositionFixed(self)->bool:
        """
        Gets whether the input box position is fixed.

        Returns:
            bool: True if the input box position is fixed, otherwise False.
        """
        pass

    @IsInputPositionFixed.setter
    @abc.abstractmethod
    def IsInputPositionFixed(self, value:bool):
        """
        Sets whether the input box position is fixed.

        Args:
            value (bool): True if the input box position is fixed, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def AlertStyle(self)->'AlertStyleType':
        """
        Gets the alert style for the data validation.

        Returns:
            AlertStyleType: The alert style.
        """
        pass

    @AlertStyle.setter
    @abc.abstractmethod
    def AlertStyle(self, value:'AlertStyleType'):
        """
        Sets the alert style for the data validation.

        Args:
            value (AlertStyleType): The alert style to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Values(self)->List[str]:
        """
        Gets the list of values for the data validation.

        Returns:
            List[str]: The list of values.
        """
        pass

    @Values.setter
    @abc.abstractmethod
    def Values(self, value:List[str]):
        """
        Sets the list of values for the data validation.

        Args:
            value (List[str]): The list of values to set.
        """
        pass

    @property
    @abc.abstractmethod
    def DataRange(self)->'IXLSRange':
        """
        Gets the data range for the data validation.

        Returns:
            IXLSRange: The data range.
        """
        pass

    @DataRange.setter
    @abc.abstractmethod
    def DataRange(self, value:'IXLSRange'):
        """
        Sets the data range for the data validation.

        Args:
            value (IXLSRange): The data range to set.
        """
        pass


