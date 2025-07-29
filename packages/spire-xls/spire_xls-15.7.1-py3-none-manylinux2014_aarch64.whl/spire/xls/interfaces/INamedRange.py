from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class INamedRange (  IExcelApplication) :
    """Named range interface for Excel.
    
    This interface represents a named range in an Excel workbook. Named ranges provide
    a way to refer to a cell or range of cells by a name instead of a cell reference.
    This allows for easier formula creation and maintenance in Excel.
    
    Named ranges can have local scope (specific to a worksheet) or workbook scope (available throughout
    the entire workbook). This interface provides properties and methods to manage and manipulate
    named ranges.
    
    Inherits from:
        IExcelApplication: Excel application interface
    """
    @property
    @abc.abstractmethod
    def Index(self)->int:
        """Gets the index of the named range in the collection.
        
        This property returns the one-based position of the named range within
        the collection of named ranges.
        
        Returns:
            int: The index of the named range.
        """
        pass


    @property
    @abc.abstractmethod
    def Name(self)->str:
        """Gets the name of the named range.
        
        This property returns the name used to identify the range in the workbook.
        The name can be used in formulas to refer to the range.
        
        Returns:
            str: The name of the named range.
        """
        pass


    @Name.setter
    @abc.abstractmethod
    def Name(self, value:str):
        """Sets the name of the named range.
        
        This property sets the name used to identify the range in the workbook.
        The name must follow Excel's naming rules (start with a letter or underscore,
        contain only letters, numbers, periods, and underscores, and not match a cell reference).
        
        Args:
            value (str): The new name for the named range.
        """
        pass


    @property
    @abc.abstractmethod
    def NameLocal(self)->str:
        """Gets the localized name of the named range.
        
        This property returns the name of the range in the user interface language
        of the Excel version that created the named range. This can be different
        from the Name property in localized versions of Excel.
        
        Returns:
            str: The localized name of the named range.
        """
        pass


    @NameLocal.setter
    @abc.abstractmethod
    def NameLocal(self, value:str):
        """Sets the localized name of the named range.
        
        This property sets the name of the range in the user interface language
        of the Excel version that created the named range.
        
        Args:
            value (str): The new localized name for the named range.
        """
        pass


    @property
    @abc.abstractmethod
    def RefersToRange(self)->'IXLSRange':
        """Gets the range object that the named range refers to.
        
        This property returns the actual cell range that is associated with the named range.
        This allows direct access to the cells within the named range.
        
        Returns:
            IXLSRange: The range object that the named range refers to.
        """
        pass


    @RefersToRange.setter
    @abc.abstractmethod
    def RefersToRange(self, value:'IXLSRange'):
        """Sets the range object that the named range refers to.
        
        This property allows changing which cells the named range refers to.
        
        Args:
            value (IXLSRange): The new range object that the named range should refer to.
        """
        pass


    @property
    @abc.abstractmethod
    def Value(self)->str:
        """Gets the reference formula of the named range.
        
        This property returns the formula text that defines the named range,
        such as "=Sheet1!$A$1:$B$10" in the A1-style reference format.
        
        Returns:
            str: The formula text that defines the named range.
        """
        pass


    @Value.setter
    @abc.abstractmethod
    def Value(self, value:str):
        """Sets the reference formula of the named range.
        
        This property sets the formula text that defines the named range,
        such as "=Sheet1!$A$1:$B$10" in the A1-style reference format.
        
        Args:
            value (str): The new formula text that defines the named range.
        """
        pass


    @property
    @abc.abstractmethod
    def Visible(self)->bool:
        """Gets whether the named range is visible in the Name Manager.
        
        When true, the named range appears in Excel's Name Manager and name lists.
        When false, the named range is hidden from these interfaces but still can be used in formulas.
        
        Returns:
            bool: True if the named range is visible, otherwise False.
        """
        pass


    @Visible.setter
    @abc.abstractmethod
    def Visible(self, value:bool):
        """Sets whether the named range is visible in the Name Manager.
        
        When set to true, the named range will appear in Excel's Name Manager and name lists.
        When set to false, the named range will be hidden from these interfaces but still can be used in formulas.
        
        Args:
            value (bool): True to make the named range visible, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsLocal(self)->bool:
        """Gets whether the named range is local to a specific worksheet.
        
        When true, the named range is only available in the worksheet where it is defined.
        When false, the named range has workbook scope and is available throughout the entire workbook.
        
        Returns:
            bool: True if the named range is local to a worksheet, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def ValueR1C1(self)->str:
        """Gets the reference formula of the named range in R1C1 notation.
        
        This property returns the formula text that defines the named range in R1C1-style 
        reference format (e.g., "=Sheet1!R1C1:R10C2") instead of the A1-style format.
        R1C1 notation is an alternative reference style where both rows and columns are numbered.
        
        Returns:
            str: The formula text that defines the named range in R1C1 notation.
        """
        pass


    @property
    @abc.abstractmethod
    def Worksheet(self)->'IWorksheet':
        """Gets the worksheet that contains the named range.
        
        This property returns the worksheet where the named range is defined.
        For a workbook-scoped named range, this property may return the worksheet
        containing the range it refers to.
        
        Returns:
            IWorksheet: The worksheet that contains the named range.
        """
        pass


    @property
    @abc.abstractmethod
    def Scope(self)->str:
        """Gets the scope of the named range.
        
        This property returns a string that identifies the scope of the named range,
        which can be either a specific worksheet name or the name of the workbook.
        
        Returns:
            str: The scope of the named range.
        """
        pass


    @abc.abstractmethod
    def Delete(self):
        """Deletes the named range.
        
        This method removes the named range from the workbook or worksheet.
        Note that this does not delete the cells that the named range refers to,
        only the name definition.
        """
        pass


