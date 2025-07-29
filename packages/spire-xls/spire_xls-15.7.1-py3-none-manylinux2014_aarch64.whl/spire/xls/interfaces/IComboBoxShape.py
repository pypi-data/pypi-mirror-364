from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IComboBoxShape (  IShape, IExcelApplication) :
    """Combo box shape interface.
    
    This interface provides functionality for creating and managing combo box controls
    in Excel worksheets. A combo box allows users to select a value from a predefined list.
    The interface provides functionality for setting the list fill range, selected index,
    dropdown lines, 3D shading effects, and retrieving the selected value.
    
    Inherits from:
        IShape: Shape interface
        IExcelApplication: Excel application interface
    """
    @property
    @abc.abstractmethod
    def ListFillRange(self)->'IXLSRange':
        """
        Gets the range used to fill the combo box list.

        Returns:
            IXLSRange: The range used to fill the list.
        """
        pass

    @ListFillRange.setter
    @abc.abstractmethod
    def ListFillRange(self, value:'IXLSRange'):
        """
        Sets the range used to fill the combo box list.

        Args:
            value (IXLSRange): The range to set.
        """
        pass

    @property
    @abc.abstractmethod
    def SelectedIndex(self)->int:
        """
        Gets the selected index of the combo box.

        Returns:
            int: The selected index.
        """
        pass

    @SelectedIndex.setter
    @abc.abstractmethod
    def SelectedIndex(self, value:int):
        """
        Sets the selected index of the combo box.

        Args:
            value (int): The selected index to set.
        """
        pass

    @property
    @abc.abstractmethod
    def DropDownLines(self)->int:
        """
        Gets the number of lines displayed in the drop-down list.

        Returns:
            int: The number of lines.
        """
        pass

    @DropDownLines.setter
    @abc.abstractmethod
    def DropDownLines(self, value:int):
        """
        Sets the number of lines displayed in the drop-down list.

        Args:
            value (int): The number of lines to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Display3DShading(self)->bool:
        """
        Gets whether the combo box displays 3D shading.

        Returns:
            bool: True if 3D shading is displayed, otherwise False.
        """
        pass

    @Display3DShading.setter
    @abc.abstractmethod
    def Display3DShading(self, value:bool):
        """
        Sets whether the combo box displays 3D shading.

        Args:
            value (bool): True to display 3D shading, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def SelectedValue(self)->str:
        """
        Gets the selected value of the combo box.

        Returns:
            str: The selected value.
        """
        pass


