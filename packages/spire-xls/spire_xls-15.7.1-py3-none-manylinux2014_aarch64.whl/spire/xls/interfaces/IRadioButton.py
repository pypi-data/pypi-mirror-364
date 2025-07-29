from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IRadioButton (  IShape, IExcelApplication) :
    """Radio button control interface for Excel.
    
    This interface represents a radio button form control in an Excel worksheet.
    Radio buttons are used to present a set of mutually exclusive options, where
    only one option can be selected at a time. This interface provides properties
    to control the appearance and behavior of radio buttons.
    
    Inherits from:
        IShape: Base shape interface
        IExcelApplication: Excel application interface
    """
    @property
    @abc.abstractmethod
    def CheckState(self)->'CheckState':
        """Gets the check state of the radio button.
        
        This property returns an enumeration value indicating whether the radio button
        is checked, unchecked, or in a mixed state.
        
        Returns:
            CheckState: The current check state of the radio button.
        """
        pass


    @CheckState.setter
    @abc.abstractmethod
    def CheckState(self, value:'CheckState'):
        """Sets the check state of the radio button.
        
        This property sets whether the radio button is checked, unchecked, or in a mixed state.
        Note that setting one radio button in a group to checked will automatically
        uncheck other radio buttons in the same group.
        
        Args:
            value (CheckState): The check state to set for the radio button.
        """
        pass


    @property
    @abc.abstractmethod
    def IsFirstButton(self)->bool:
        """Gets whether this radio button is the first button in its group.
        
        Radio buttons are organized in groups where only one can be selected at a time.
        This property returns whether this radio button is the first one in its group.
        
        Returns:
            bool: True if this is the first radio button in the group, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def Display3DShading(self)->bool:
        """Gets whether the radio button displays with a 3D shading effect.
        
        This property returns whether the radio button has a three-dimensional
        shading effect applied to its appearance.
        
        Returns:
            bool: True if the radio button displays with 3D shading, otherwise False.
        """
        pass


    @Display3DShading.setter
    @abc.abstractmethod
    def Display3DShading(self, value:bool):
        """Sets whether the radio button displays with a 3D shading effect.
        
        This property sets whether the radio button has a three-dimensional
        shading effect applied to its appearance.
        
        Args:
            value (bool): True to display the radio button with 3D shading, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def Line(self)->'IShapeLineFormat':
        """Gets the line formatting for the radio button's border.
        
        This property returns an interface that provides access to line formatting properties
        such as color, style, weight, etc. for the border of the radio button.
        
        Returns:
            IShapeLineFormat: An interface for accessing and modifying the line formatting.
        """
        pass


    @property
    @abc.abstractmethod
    def Text(self)->str:
        """Gets the text label displayed next to the radio button.
        
        This property returns the text that appears as a label for the radio button.
        
        Returns:
            str: The text label of the radio button.
        """
        pass


    @Text.setter
    @abc.abstractmethod
    def Text(self, value:str):
        """Sets the text label displayed next to the radio button.
        
        This property sets the text that appears as a label for the radio button.
        
        Args:
            value (str): The new text label for the radio button.
        """
        pass


    @property
    @abc.abstractmethod
    def IsTextLocked(self)->bool:
        """Gets whether the text label of the radio button is locked for editing.
        
        When true, the text label cannot be edited by the user in Excel.
        When false, the user can edit the text label.
        
        Returns:
            bool: True if the text label is locked, otherwise False.
        """
        pass


    @IsTextLocked.setter
    @abc.abstractmethod
    def IsTextLocked(self, value:bool):
        """Sets whether the text label of the radio button is locked for editing.
        
        When set to true, the text label cannot be edited by the user in Excel.
        When set to false, the user can edit the text label.
        
        Args:
            value (bool): True to lock the text label, otherwise False.
        """
        pass


