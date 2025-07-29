from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IPageSetup (  IPageSetupBase, IExcelApplication) :
    """
    Interface for page setup options in Excel worksheets.
    
    This interface inherits from IPageSetupBase and IExcelApplication and provides
    properties to control how worksheets are printed.
    """
    @property
    @abc.abstractmethod
    def FitToPagesTall(self)->int:
        """
        Gets the number of pages tall the worksheet will be scaled to when printed.
        
        Returns:
            int: The number of pages tall.
        """
        pass


    @FitToPagesTall.setter
    @abc.abstractmethod
    def FitToPagesTall(self, value:int):
        """
        Sets the number of pages tall the worksheet will be scaled to when printed.
        
        Args:
            value (int): The number of pages tall.
        """
        pass


    @property
    @abc.abstractmethod
    def FitToPagesWide(self)->int:
        """
        Gets the number of pages wide the worksheet will be scaled to when printed.
        
        Returns:
            int: The number of pages wide.
        """
        pass


    @FitToPagesWide.setter
    @abc.abstractmethod
    def FitToPagesWide(self, value:int):
        """
        Sets the number of pages wide the worksheet will be scaled to when printed.
        
        Args:
            value (int): The number of pages wide.
        """
        pass


    @property
    @abc.abstractmethod
    def IsPrintGridlines(self)->bool:
        """
        Gets whether gridlines are printed.
        
        Returns:
            bool: True if gridlines are printed, otherwise False.
        """
        pass


    @IsPrintGridlines.setter
    @abc.abstractmethod
    def IsPrintGridlines(self, value:bool):
        """
        Sets whether gridlines are printed.
        
        Args:
            value (bool): True to print gridlines, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsPrintHeadings(self)->bool:
        """
        Gets whether row and column headings are printed.
        
        Returns:
            bool: True if headings are printed, otherwise False.
        """
        pass


    @IsPrintHeadings.setter
    @abc.abstractmethod
    def IsPrintHeadings(self, value:bool):
        """
        Sets whether row and column headings are printed.
        
        Args:
            value (bool): True to print headings, otherwise False.
        """
        pass


    @property

    @abc.abstractmethod
    def PrintArea(self)->str:
        """
        Gets the print area as a string in the format of "A1:D10".
        
        Returns:
            str: The print area range string.
        """
        pass


    @PrintArea.setter
    @abc.abstractmethod
    def PrintArea(self, value:str):
        """
        Sets the print area as a string in the format of "A1:D10".
        
        Args:
            value (str): The print area range string.
        """
        pass


    @property

    @abc.abstractmethod
    def PrintTitleColumns(self)->str:
        """
        Gets the columns that contain the cells to be repeated on the left of each printed page.
        
        Returns:
            str: The title columns range string.
        """
        pass


    @PrintTitleColumns.setter
    @abc.abstractmethod
    def PrintTitleColumns(self, value:str):
        """
        Sets the columns that contain the cells to be repeated on the left of each printed page.
        
        Args:
            value (str): The title columns range string.
        """
        pass


    @property

    @abc.abstractmethod
    def PrintTitleRows(self)->str:
        """
        Gets the rows that contain the cells to be repeated at the top of each printed page.
        
        Returns:
            str: The title rows range string.
        """
        pass


    @PrintTitleRows.setter
    @abc.abstractmethod
    def PrintTitleRows(self, value:str):
        """
        Sets the rows that contain the cells to be repeated at the top of each printed page.
        
        Args:
            value (str): The title rows range string.
        """
        pass


    @property
    @abc.abstractmethod
    def IsSummaryRowBelow(self)->bool:
        """
        Gets whether summary rows appear below detail rows.
        
        Returns:
            bool: True if summary rows appear below detail rows, otherwise False.
        """
        pass


    @IsSummaryRowBelow.setter
    @abc.abstractmethod
    def IsSummaryRowBelow(self, value:bool):
        """
        Sets whether summary rows appear below detail rows.
        
        Args:
            value (bool): True to place summary rows below detail rows, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsSummaryColumnRight(self)->bool:
        """
        Gets whether summary columns appear to the right of detail columns.
        
        Returns:
            bool: True if summary columns appear to the right of detail columns, otherwise False.
        """
        pass


    @IsSummaryColumnRight.setter
    @abc.abstractmethod
    def IsSummaryColumnRight(self, value:bool):
        """
        Sets whether summary columns appear to the right of detail columns.
        
        Args:
            value (bool): True to place summary columns to the right of detail columns, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsFitToPage(self)->bool:
        """
        Gets whether the worksheet is scaled to fit on one page when printed.
        
        Returns:
            bool: True if the worksheet is scaled to fit on one page, otherwise False.
        """
        pass


    @IsFitToPage.setter
    @abc.abstractmethod
    def IsFitToPage(self, value:bool):
        """Sets whether the worksheet is scaled to fit on one page when printed.
        
        When set to True, the worksheet will be automatically scaled to fit on one page
        when printed. This setting affects both the width and height of the printed output.
        
        Args:
            value (bool): True to scale the worksheet to fit on one page, otherwise False.
        """
        pass


