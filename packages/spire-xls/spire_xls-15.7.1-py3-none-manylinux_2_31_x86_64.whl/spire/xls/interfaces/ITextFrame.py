from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ITextFrame (abc.ABC) :
    """Interface for text frames in Excel shapes.
    
    This interface represents a text frame that contains text in a shape
    and provides properties to control text layout, auto-sizing, and margins.
    """
    @property
    @abc.abstractmethod
    def AutoSize(self)->bool:
        """Gets whether the text frame is automatically sized to fit its content.
        
        Returns:
            bool: True if the text frame is automatically sized; otherwise, False.
        """
        pass


    @AutoSize.setter
    @abc.abstractmethod
    def AutoSize(self, value:bool):
        """Sets whether the text frame is automatically sized to fit its content.
        
        Args:
            value (bool): True to automatically size the text frame; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsAutoMargin(self)->bool:
        """Gets whether margins are automatically calculated for the text frame.
        
        Returns:
            bool: True if margins are automatically calculated; otherwise, False.
        """
        pass


    @IsAutoMargin.setter
    @abc.abstractmethod
    def IsAutoMargin(self, value:bool):
        """Sets whether margins are automatically calculated for the text frame.
        
        Args:
            value (bool): True to automatically calculate margins; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def LeftMarginPt(self)->float:
        """Gets the left margin of the text frame in points.
        
        Returns:
            float: The left margin size in points.
        """
        pass


    @LeftMarginPt.setter
    @abc.abstractmethod
    def LeftMarginPt(self, value:float):
        """Sets the left margin of the text frame in points.
        
        Args:
            value (float): The left margin size in points to set.
        """
        pass


    @property
    @abc.abstractmethod
    def RightMarginPt(self)->float:
        """Gets the right margin of the text frame in points.
        
        Returns:
            float: The right margin size in points.
        """
        pass


    @RightMarginPt.setter
    @abc.abstractmethod
    def RightMarginPt(self, value:float):
        """Sets the right margin of the text frame in points.
        
        Args:
            value (float): The right margin size in points to set.
        """
        pass


    @property
    @abc.abstractmethod
    def TopMarginPt(self)->float:
        """Gets the top margin of the text frame in points.
        
        Returns:
            float: The top margin size in points.
        """
        pass


    @TopMarginPt.setter
    @abc.abstractmethod
    def TopMarginPt(self, value:float):
        """Sets the top margin of the text frame in points.
        
        Args:
            value (float): The top margin size in points to set.
        """
        pass


    @property
    @abc.abstractmethod
    def BottomMarginPt(self)->float:
        """Gets the bottom margin of the text frame in points.
        
        Returns:
            float: The bottom margin size in points.
        """
        pass


    @BottomMarginPt.setter
    @abc.abstractmethod
    def BottomMarginPt(self, value:float):
        """Sets the bottom margin of the text frame in points.
        
        Args:
            value (float): The bottom margin size in points to set.
        """
        pass


