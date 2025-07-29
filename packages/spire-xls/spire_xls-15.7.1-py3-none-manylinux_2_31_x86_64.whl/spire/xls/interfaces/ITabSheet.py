from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ITabSheet (  IExcelApplication) :
    """Interface for Excel worksheet tabs.
    
    This interface represents a worksheet tab in an Excel workbook and provides properties
    and methods to access and modify tab attributes such as color, name, visibility, and protection.
    """
    @property

    @abc.abstractmethod
    def TabKnownColor(self)->'ExcelColors':
        """Gets the predefined color of the worksheet tab.
        
        Returns:
            ExcelColors: An enumeration value representing the predefined color of the tab.
        """
        pass


    @TabKnownColor.setter
    @abc.abstractmethod
    def TabKnownColor(self, value:'ExcelColors'):
        """Sets the predefined color of the worksheet tab.
        
        Args:
            value (ExcelColors): An enumeration value representing the predefined color to set.
        """
        pass


    @property

    @abc.abstractmethod
    def TabColor(self)->'Color':
        """Gets the custom color of the worksheet tab.
        
        Returns:
            Color: A Color object representing the custom color of the tab.
        """
        pass


    @TabColor.setter
    @abc.abstractmethod
    def TabColor(self, value:'Color'):
        """Sets the custom color of the worksheet tab.
        
        Args:
            value (Color): A Color object representing the custom color to set.
        """
        pass


    @property

    @abc.abstractmethod
    def Pictures(self)->'IPictures':
        """Gets the collection of pictures in the worksheet.
        
        Returns:
            IPictures: A collection of picture objects in the worksheet.
        """
        pass


    @property

    @abc.abstractmethod
    def Workbook(self)->'IWorkbook':
        """Gets the parent workbook of the worksheet.
        
        Returns:
            IWorkbook: The parent workbook object.
        """
        pass


    @property
    @abc.abstractmethod
    def IsRightToLeft(self)->bool:
        """Gets whether the worksheet is displayed from right to left.
        
        Returns:
            bool: True if the worksheet is displayed from right to left; otherwise, False.
        """
        pass


    @IsRightToLeft.setter
    @abc.abstractmethod
    def IsRightToLeft(self, value:bool):
        """Sets whether the worksheet is displayed from right to left.
        
        Args:
            value (bool): True to display the worksheet from right to left; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsSelected(self)->bool:
        """Gets whether the worksheet is selected.
        
        Returns:
            bool: True if the worksheet is selected; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def TabIndex(self)->int:
        """Gets the index of the worksheet tab.
        
        Returns:
            int: The zero-based index of the worksheet tab.
        """
        pass


    @property

    @abc.abstractmethod
    def Name(self)->str:
        """Gets the name of the worksheet.
        
        Returns:
            str: The name of the worksheet.
        """
        pass


    @Name.setter
    @abc.abstractmethod
    def Name(self, value:str):
        """Sets the name of the worksheet.
        
        Args:
            value (str): The name to set for the worksheet.
        """
        pass


    @property

    @abc.abstractmethod
    def Visibility(self)->'WorksheetVisibility':
        """Gets the visibility state of the worksheet.
        
        Returns:
            WorksheetVisibility: An enumeration value representing the visibility state.
        """
        pass


    @Visibility.setter
    @abc.abstractmethod
    def Visibility(self, value:'WorksheetVisibility'):
        """Sets the visibility state of the worksheet.
        
        Args:
            value (WorksheetVisibility): An enumeration value representing the visibility state to set.
        """
        pass


    @property

    @abc.abstractmethod
    def TextBoxes(self)->'ITextBoxes':
        """Gets the collection of text boxes in the worksheet.
        
        Returns:
            ITextBoxes: A collection of text box objects in the worksheet.
        """
        pass


    @property

    @abc.abstractmethod
    def CheckBoxes(self)->'ICheckBoxes':
        """Gets the collection of check boxes in the worksheet.
        
        Returns:
            ICheckBoxes: A collection of check box objects in the worksheet.
        """
        pass


    @property

    @abc.abstractmethod
    def ComboBoxes(self)->'IComboBoxes':
        """Gets the collection of combo boxes in the worksheet.
        
        Returns:
            IComboBoxes: A collection of combo box objects in the worksheet.
        """
        pass


    @property

    @abc.abstractmethod
    def RadioButtons(self)->'IRadioButtons':
        """Gets the collection of radio buttons in the worksheet.
        
        Returns:
            IRadioButtons: A collection of radio button objects in the worksheet.
        """
        pass


    @property

    @abc.abstractmethod
    def CodeName(self)->str:
        """Gets the code name of the worksheet.
        
        Returns:
            str: The code name of the worksheet.
        """
        pass


    @CodeName.setter
    @abc.abstractmethod
    def CodeName(self, value:str):
        """Sets the code name of the worksheet.
        
        Args:
            value (str): The code name to set for the worksheet.
        """
        pass


    @property
    @abc.abstractmethod
    def ProtectContents(self)->bool:
        """Gets whether the contents of the worksheet are protected.
        
        Returns:
            bool: True if the contents are protected; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def ProtectDrawingObjects(self)->bool:
        """Gets whether the drawing objects in the worksheet are protected.
        
        Returns:
            bool: True if the drawing objects are protected; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def ProtectScenarios(self)->bool:
        """Gets whether the scenarios in the worksheet are protected.
        
        Returns:
            bool: True if the scenarios are protected; otherwise, False.
        """
        pass


    @property

    @abc.abstractmethod
    def Protection(self)->'SheetProtectionType':
        """Gets the protection type of the worksheet.
        
        Returns:
            SheetProtectionType: An enumeration value representing the protection type.
        """
        pass


    @property
    @abc.abstractmethod
    def IsPasswordProtected(self)->bool:
        """Gets whether the worksheet is protected with a password.
        
        Returns:
            bool: True if the worksheet is password protected; otherwise, False.
        """
        pass


    @abc.abstractmethod
    def Activate(self):
        """Activates the worksheet.
        
        Makes this worksheet the active sheet in the workbook.
        """
        pass


    @abc.abstractmethod
    def Select(self):
        """Selects the worksheet.
        
        Selects this worksheet in the workbook.
        """
        pass


    @abc.abstractmethod
    def Unselect(self):
        """Unselects the worksheet.
        
        Removes the selection from this worksheet in the workbook.
        """
        pass


    @dispatch

    @abc.abstractmethod
    def Protect(self ,password:str):
        """Protects the worksheet with a password.
        
        Args:
            password (str): The password to use for protection.
        """
        pass


    @dispatch

    @abc.abstractmethod
    def Protect(self ,password:str,options:SheetProtectionType):
        """Protects the worksheet with a password and specific protection options.
        
        Args:
            password (str): The password to use for protection.
            options (SheetProtectionType): The protection options to apply.
        """
        pass



    @abc.abstractmethod
    def Unprotect(self ,password:str):
        """Removes protection from the worksheet.
        
        Args:
            password (str): The password used to protect the worksheet.
        """
        pass


