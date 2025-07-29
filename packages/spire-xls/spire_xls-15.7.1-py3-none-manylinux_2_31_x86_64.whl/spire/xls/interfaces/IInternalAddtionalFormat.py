from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IInternalAddtionalFormat (  IExtendedFormat, IExcelApplication) :
    """
    Interface for internal additional formatting in Excel.
    
    This interface extends IExtendedFormat and IExcelApplication to provide
    access to additional formatting properties used internally by Excel,
    particularly for border styles and colors.
    """
    @property
    @abc.abstractmethod
    def BottomBorderColor(self)->'OColor':
        """
        Gets the bottom border color.

        Returns:
            OColor: The bottom border color.
        """
        pass

    @property
    @abc.abstractmethod
    def TopBorderColor(self)->'OColor':
        """
        Gets the top border color.

        Returns:
            OColor: The top border color.
        """
        pass

    @property
    @abc.abstractmethod
    def LeftBorderColor(self)->'OColor':
        """
        Gets the left border color.

        Returns:
            OColor: The left border color.
        """
        pass

    @property
    @abc.abstractmethod
    def RightBorderColor(self)->'OColor':
        """
        Gets the right border color.

        Returns:
            OColor: The right border color.
        """
        pass

    @property
    @abc.abstractmethod
    def DiagonalBorderColor(self)->'OColor':
        """
        Gets the diagonal border color.

        Returns:
            OColor: The diagonal border color.
        """
        pass

    @property
    @abc.abstractmethod
    def LeftBorderLineStyle(self)->'LineStyleType':
        """
        Gets the left border line style.

        Returns:
            LineStyleType: The left border line style.
        """
        pass

    @LeftBorderLineStyle.setter
    @abc.abstractmethod
    def LeftBorderLineStyle(self, value:'LineStyleType'):
        """
        Sets the left border line style.

        Args:
            value (LineStyleType): The left border line style to set.
        """
        pass

    @property
    @abc.abstractmethod
    def RightBorderLineStyle(self)->'LineStyleType':
        """
        Gets the right border line style.

        Returns:
            LineStyleType: The right border line style.
        """
        pass

    @RightBorderLineStyle.setter
    @abc.abstractmethod
    def RightBorderLineStyle(self, value:'LineStyleType'):
        """
        Sets the right border line style.

        Args:
            value (LineStyleType): The right border line style to set.
        """
        pass

    @property
    @abc.abstractmethod
    def TopBorderLineStyle(self)->'LineStyleType':
        """
        Gets the top border line style.

        Returns:
            LineStyleType: The top border line style.
        """
        pass

    @TopBorderLineStyle.setter
    @abc.abstractmethod
    def TopBorderLineStyle(self, value:'LineStyleType'):
        """
        Sets the top border line style.

        Args:
            value (LineStyleType): The top border line style to set.
        """
        pass

    @property
    @abc.abstractmethod
    def BottomBorderLineStyle(self)->'LineStyleType':
        """
        Gets the bottom border line style.

        Returns:
            LineStyleType: The bottom border line style.
        """
        pass

    @BottomBorderLineStyle.setter
    @abc.abstractmethod
    def BottomBorderLineStyle(self, value:'LineStyleType'):
        """
        Sets the bottom border line style.

        Args:
            value (LineStyleType): The bottom border line style to set.
        """
        pass

    @property
    @abc.abstractmethod
    def DiagonalUpBorderLineStyle(self)->'LineStyleType':
        """
        Gets the diagonal up border line style.

        Returns:
            LineStyleType: The diagonal up border line style.
        """
        pass

    @DiagonalUpBorderLineStyle.setter
    @abc.abstractmethod
    def DiagonalUpBorderLineStyle(self, value:'LineStyleType'):
        """
        Sets the diagonal up border line style.

        Args:
            value (LineStyleType): The diagonal up border line style to set.
        """
        pass

    @property
    @abc.abstractmethod
    def DiagonalDownBorderLineStyle(self)->'LineStyleType':
        """
        Gets the diagonal down border line style.

        Returns:
            LineStyleType: The diagonal down border line style.
        """
        pass

    @DiagonalDownBorderLineStyle.setter
    @abc.abstractmethod
    def DiagonalDownBorderLineStyle(self, value:'LineStyleType'):
        """
        Sets the diagonal down border line style.

        Args:
            value (LineStyleType): The diagonal down border line style to set.
        """
        pass

    @property
    @abc.abstractmethod
    def DiagonalUpVisible(self)->bool:
        """
        Gets whether the diagonal up border is visible.

        Returns:
            bool: True if visible, otherwise False.
        """
        pass

    @DiagonalUpVisible.setter
    @abc.abstractmethod
    def DiagonalUpVisible(self, value:bool):
        """
        Sets whether the diagonal up border is visible.

        Args:
            value (bool): True to set visible, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def DiagonalDownVisible(self)->bool:
        """
        Gets whether the diagonal down border is visible.

        Returns:
            bool: True if visible, otherwise False.
        """
        pass

    @DiagonalDownVisible.setter
    @abc.abstractmethod
    def DiagonalDownVisible(self, value:bool):
        """
        Sets whether the diagonal down border is visible.

        Args:
            value (bool): True to set visible, otherwise False.
        """
        pass

    @abc.abstractmethod
    def BeginUpdate(self):
        """
        Begins a batch update operation on the format.
        
        This method should be called before making multiple changes to the format properties.
        """
        pass

    @abc.abstractmethod
    def EndUpdate(self):
        """
        Ends a batch update operation on the format.
        
        This method should be called after making multiple changes to apply all changes at once.
        """
        pass

    @property
    @abc.abstractmethod
    def Workbook(self)->'XlsWorkbook':
        """
        Gets the workbook associated with this format.
        
        Returns:
            XlsWorkbook: The workbook object.
        """
        pass


