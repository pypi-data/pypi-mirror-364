from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IHyperLink (  IExcelApplication) :
    """
    Interface for hyperlink objects in Excel.
    
    This interface provides properties and methods to manipulate hyperlinks
    in Excel worksheets, including their addresses, display text, and tooltips.
    """
    @property
    @abc.abstractmethod
    def Address(self)->str:
        """
        Gets the address of the hyperlink.

        Returns:
            str: The address of the hyperlink.
        """
        pass

    @Address.setter
    @abc.abstractmethod
    def Address(self, value:str):
        """
        Sets the address of the hyperlink.

        Args:
            value (str): The address to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Name(self)->str:
        """
        Gets the name of the hyperlink.

        Returns:
            str: The name of the hyperlink.
        """
        pass

    @property
    @abc.abstractmethod
    def Range(self)->'IXLSRange':
        """
        Gets the range associated with the hyperlink.

        Returns:
            IXLSRange: The associated range.
        """
        pass

    @property
    @abc.abstractmethod
    def ScreenTip(self)->str:
        """
        Gets the screen tip of the hyperlink.

        Returns:
            str: The screen tip.
        """
        pass

    @ScreenTip.setter
    @abc.abstractmethod
    def ScreenTip(self, value:str):
        """
        Sets the screen tip of the hyperlink.

        Args:
            value (str): The screen tip to set.
        """
        pass

    @property
    @abc.abstractmethod
    def SubAddress(self)->str:
        """
        Gets the sub-address of the hyperlink.

        Returns:
            str: The sub-address.
        """
        pass

    @SubAddress.setter
    @abc.abstractmethod
    def SubAddress(self, value:str):
        """
        Sets the sub-address of the hyperlink.

        Args:
            value (str): The sub-address to set.
        """
        pass

    @property
    @abc.abstractmethod
    def TextToDisplay(self)->str:
        """
        Gets the text to display for the hyperlink.

        Returns:
            str: The text to display.
        """
        pass

    @TextToDisplay.setter
    @abc.abstractmethod
    def TextToDisplay(self, value:str):
        """
        Sets the text to display for the hyperlink.

        Args:
            value (str): The text to display.
        """
        pass

    @property
    @abc.abstractmethod
    def Type(self)->'HyperLinkType':
        """
        Gets the type of the hyperlink.

        Returns:
            HyperLinkType: The type of the hyperlink.
        """
        pass


