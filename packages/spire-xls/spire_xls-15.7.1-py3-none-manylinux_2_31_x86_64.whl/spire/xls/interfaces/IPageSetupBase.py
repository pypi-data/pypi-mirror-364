from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IPageSetupBase (  IExcelApplication) :
    """
    Base interface for page setup options in Excel.
    
    This interface provides common properties for controlling how Excel documents
    are printed, including margins, headers, footers, and other print settings.
    """
    @property
    @abc.abstractmethod
    def AutoFirstPageNumber(self)->bool:
        """
        Gets whether the first page number is automatically set.
        
        Returns:
            bool: True if the first page number is automatically set, otherwise False.
        """
        pass


    @AutoFirstPageNumber.setter
    @abc.abstractmethod
    def AutoFirstPageNumber(self, value:bool):
        """
        Sets whether the first page number is automatically set.
        
        Args:
            value (bool): True to automatically set the first page number, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def BlackAndWhite(self)->bool:
        """
        Gets whether the document is printed in black and white.
        
        Returns:
            bool: True if the document is printed in black and white, otherwise False.
        """
        pass


    @BlackAndWhite.setter
    @abc.abstractmethod
    def BlackAndWhite(self, value:bool):
        """
        Sets whether the document is printed in black and white.
        
        Args:
            value (bool): True to print in black and white, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def BottomMargin(self)->float:
        """
        Gets the size of the bottom margin, in points.
        
        Returns:
            float: The bottom margin size in points.
        """
        pass


    @BottomMargin.setter
    @abc.abstractmethod
    def BottomMargin(self, value:float):
        """
        Sets the size of the bottom margin, in points.
        
        Args:
            value (float): The bottom margin size in points.
        """
        pass


    @property

    @abc.abstractmethod
    def CenterFooter(self)->str:
        """
        Gets the center section of the footer.
        
        Returns:
            str: The text for the center section of the footer.
        """
        pass


    @CenterFooter.setter
    @abc.abstractmethod
    def CenterFooter(self, value:str):
        """
        Sets the center section of the footer.
        
        Args:
            value (str): The text for the center section of the footer.
        """
        pass


    @property

    @abc.abstractmethod
    def CenterFooterImage(self)->'Stream':
        """
        Gets the image in the center section of the footer.
        
        Returns:
            Stream: The image stream for the center section of the footer.
        """
        pass


    @CenterFooterImage.setter
    @abc.abstractmethod
    def CenterFooterImage(self, value:'Stream'):
        """
        Sets the image in the center section of the footer.
        
        Args:
            value (Stream): The image stream for the center section of the footer.
        """
        pass


    @property

    @abc.abstractmethod
    def CenterHeader(self)->str:
        """
        Gets the center section of the header.
        
        Returns:
            str: The text for the center section of the header.
        """
        pass


    @CenterHeader.setter
    @abc.abstractmethod
    def CenterHeader(self, value:str):
        """
        Sets the center section of the header.
        
        Args:
            value (str): The text for the center section of the header.
        """
        pass


    @property

    @abc.abstractmethod
    def CenterHeaderImage(self)->'Stream':
        """
        Gets the image in the center section of the header.
        
        Returns:
            Stream: The image stream for the center section of the header.
        """
        pass


    @CenterHeaderImage.setter
    @abc.abstractmethod
    def CenterHeaderImage(self, value:'Stream'):
        """
        Sets the image in the center section of the header.
        
        Args:
            value (Stream): The image stream for the center section of the header.
        """
        pass


    @property
    @abc.abstractmethod
    def CenterHorizontally(self)->bool:
        """
        Gets whether the sheet is centered horizontally when printed.
        
        Returns:
            bool: True if the sheet is centered horizontally, otherwise False.
        """
        pass


    @CenterHorizontally.setter
    @abc.abstractmethod
    def CenterHorizontally(self, value:bool):
        """
        Sets whether the sheet is centered horizontally when printed.
        
        Args:
            value (bool): True to center the sheet horizontally, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def CenterVertically(self)->bool:
        """
        Gets whether the sheet is centered vertically when printed.
        
        Returns:
            bool: True if the sheet is centered vertically, otherwise False.
        """
        pass


    @CenterVertically.setter
    @abc.abstractmethod
    def CenterVertically(self, value:bool):
        """
        Sets whether the sheet is centered vertically when printed.
        
        Args:
            value (bool): True to center the sheet vertically, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def Copies(self)->int:
        """
        Gets the number of copies to print.
        
        Returns:
            int: The number of copies.
        """
        pass


    @Copies.setter
    @abc.abstractmethod
    def Copies(self, value:int):
        """
        Sets the number of copies to print.
        
        Args:
            value (int): The number of copies.
        """
        pass


    @property
    @abc.abstractmethod
    def Draft(self)->bool:
        """
        Gets whether the document is printed in draft quality.
        
        Returns:
            bool: True if the document is printed in draft quality, otherwise False.
        """
        pass


    @Draft.setter
    @abc.abstractmethod
    def Draft(self, value:bool):
        """
        Sets whether the document is printed in draft quality.
        
        Args:
            value (bool): True to print in draft quality, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def FirstPageNumber(self)->int:
        """
        Gets the first page number to be used when printing.
        
        Returns:
            int: The first page number.
        """
        pass


    @FirstPageNumber.setter
    @abc.abstractmethod
    def FirstPageNumber(self, value:int):
        """
        Sets the first page number to be used when printing.
        
        Args:
            value (int): The first page number.
        """
        pass


    @property
    @abc.abstractmethod
    def FooterMarginInch(self)->float:
        """
        Gets the distance from the bottom of the page to the footer, in inches.
        
        Returns:
            float: The footer margin in inches.
        """
        pass


    @FooterMarginInch.setter
    @abc.abstractmethod
    def FooterMarginInch(self, value:float):
        """
        Sets the distance from the bottom of the page to the footer, in inches.
        
        Args:
            value (float): The footer margin in inches.
        """
        pass


    @property
    @abc.abstractmethod
    def HeaderMarginInch(self)->float:
        """
        Gets the distance from the top of the page to the header, in inches.
        
        Returns:
            float: The header margin in inches.
        """
        pass


    @HeaderMarginInch.setter
    @abc.abstractmethod
    def HeaderMarginInch(self, value:float):
        """
        Sets the distance from the top of the page to the header, in inches.
        
        Args:
            value (float): The header margin in inches.
        """
        pass


    @property

    @abc.abstractmethod
    def LeftFooter(self)->str:
        """
        Gets the left section of the footer.
        
        Returns:
            str: The text for the left section of the footer.
        """
        pass


    @LeftFooter.setter
    @abc.abstractmethod
    def LeftFooter(self, value:str):
        """
        Sets the left section of the footer.
        
        Args:
            value (str): The text for the left section of the footer.
        """
        pass


    @property

    @abc.abstractmethod
    def LeftFooterImage(self)->'Stream':
        """
        Gets the image in the left section of the footer.
        
        Returns:
            Stream: The image stream for the left section of the footer.
        """
        pass


    @LeftFooterImage.setter
    @abc.abstractmethod
    def LeftFooterImage(self, value:'Stream'):
        """
        Sets the image in the left section of the footer.
        
        Args:
            value (Stream): The image stream for the left section of the footer.
        """
        pass


    @property

    @abc.abstractmethod
    def LeftHeader(self)->str:
        """
        Gets the left section of the header.
        
        Returns:
            str: The text for the left section of the header.
        """
        pass


    @LeftHeader.setter
    @abc.abstractmethod
    def LeftHeader(self, value:str):
        """
        Sets the left section of the header.
        
        Args:
            value (str): The text for the left section of the header.
        """
        pass


    @property

    @abc.abstractmethod
    def LeftHeaderImage(self)->'Stream':
        """
        Gets the image in the left section of the header.
        
        Returns:
            Stream: The image stream for the left section of the header.
        """
        pass


    @LeftHeaderImage.setter
    @abc.abstractmethod
    def LeftHeaderImage(self, value:'Stream'):
        """
        Sets the image in the left section of the header.
        
        Args:
            value (Stream): The image stream for the left section of the header.
        """
        pass


    @property
    @abc.abstractmethod
    def LeftMargin(self)->float:
        """
        Gets the size of the left margin, in points.
        
        Returns:
            float: The left margin size in points.
        """
        pass


    @LeftMargin.setter
    @abc.abstractmethod
    def LeftMargin(self, value:float):
        """
        Sets the size of the left margin, in points.
        
        Args:
            value (float): The left margin size in points.
        """
        pass


    @property

    @abc.abstractmethod
    def Order(self)->'OrderType':
        """
        Gets the page order for printing.
        
        Returns:
            OrderType: The page order type.
        """
        pass


    @Order.setter
    @abc.abstractmethod
    def Order(self, value:'OrderType'):
        """
        Sets the page order for printing.
        
        Args:
            value (OrderType): The page order type.
        """
        pass


    @property

    @abc.abstractmethod
    def Orientation(self)->'PageOrientationType':
        """
        Gets the orientation of the page.
        
        Returns:
            PageOrientationType: The page orientation type.
        """
        pass


    @Orientation.setter
    @abc.abstractmethod
    def Orientation(self, value:'PageOrientationType'):
        """
        Sets the orientation of the page.
        
        Args:
            value (PageOrientationType): The page orientation type.
        """
        pass


    @property

    @abc.abstractmethod
    def PaperSize(self)->'PaperSizeType':
        """
        Gets the size of the paper.
        
        Returns:
            PaperSizeType: The paper size type.
        """
        pass


    @PaperSize.setter
    @abc.abstractmethod
    def PaperSize(self, value:'PaperSizeType'):
        """
        Sets the size of the paper.
        
        Args:
            value (PaperSizeType): The paper size type.
        """
        pass


    @property

    @abc.abstractmethod
    def PrintComments(self)->'PrintCommentType':
        """
        Gets how comments are printed.
        
        Returns:
            PrintCommentType: The print comment type.
        """
        pass


    @PrintComments.setter
    @abc.abstractmethod
    def PrintComments(self, value:'PrintCommentType'):
        """
        Sets how comments are printed.
        
        Args:
            value (PrintCommentType): The print comment type.
        """
        pass


    @property

    @abc.abstractmethod
    def PrintErrors(self)->'PrintErrorsType':
        """
        Gets how errors are printed.
        
        Returns:
            PrintErrorsType: The print errors type.
        """
        pass


    @PrintErrors.setter
    @abc.abstractmethod
    def PrintErrors(self, value:'PrintErrorsType'):
        """
        Sets how errors are printed.
        
        Args:
            value (PrintErrorsType): The print errors type.
        """
        pass


    @property
    @abc.abstractmethod
    def PrintNotes(self)->bool:
        """
        Gets whether notes are printed.
        
        Returns:
            bool: True if notes are printed, otherwise False.
        """
        pass


    @PrintNotes.setter
    @abc.abstractmethod
    def PrintNotes(self, value:bool):
        """
        Sets whether notes are printed.
        
        Args:
            value (bool): True to print notes, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def PrintQuality(self)->int:
        """
        Gets the print quality in dots per inch.
        
        Returns:
            int: The print quality in DPI.
        """
        pass


    @PrintQuality.setter
    @abc.abstractmethod
    def PrintQuality(self, value:int):
        """
        Sets the print quality in dots per inch.
        
        Args:
            value (int): The print quality in DPI.
        """
        pass


    @property

    @abc.abstractmethod
    def RightFooter(self)->str:
        """
        Gets the right section of the footer.
        
        Returns:
            str: The text for the right section of the footer.
        """
        pass


    @RightFooter.setter
    @abc.abstractmethod
    def RightFooter(self, value:str):
        """
        Sets the right section of the footer.
        
        Args:
            value (str): The text for the right section of the footer.
        """
        pass


    @property

    @abc.abstractmethod
    def RightFooterImage(self)->'Stream':
        """
        Gets the image in the right section of the footer.
        
        Returns:
            Stream: The image stream for the right section of the footer.
        """
        pass


    @RightFooterImage.setter
    @abc.abstractmethod
    def RightFooterImage(self, value:'Stream'):
        """
        Sets the image in the right section of the footer.
        
        Args:
            value (Stream): The image stream for the right section of the footer.
        """
        pass


    @property

    @abc.abstractmethod
    def RightHeader(self)->str:
        """
        Gets the right section of the header.
        
        Returns:
            str: The text for the right section of the header.
        """
        pass


    @RightHeader.setter
    @abc.abstractmethod
    def RightHeader(self, value:str):
        """
        Sets the right section of the header.
        
        Args:
            value (str): The text for the right section of the header.
        """
        pass


    @property

    @abc.abstractmethod
    def RightHeaderImage(self)->'Stream':
        """
        Gets the image in the right section of the header.
        
        Returns:
            Stream: The image stream for the right section of the header.
        """
        pass


    @RightHeaderImage.setter
    @abc.abstractmethod
    def RightHeaderImage(self, value:'Stream'):
        """
        Sets the image in the right section of the header.
        
        Args:
            value (Stream): The image stream for the right section of the header.
        """
        pass


    @property
    @abc.abstractmethod
    def RightMargin(self)->float:
        """
        Gets the size of the right margin, in points.
        
        Returns:
            float: The right margin size in points.
        """
        pass


    @RightMargin.setter
    @abc.abstractmethod
    def RightMargin(self, value:float):
        """
        Sets the size of the right margin, in points.
        
        Args:
            value (float): The right margin size in points.
        """
        pass


    @property
    @abc.abstractmethod
    def TopMargin(self)->float:
        """
        Gets the size of the top margin, in points.
        
        Returns:
            float: The top margin size in points.
        """
        pass


    @TopMargin.setter
    @abc.abstractmethod
    def TopMargin(self, value:float):
        """
        Sets the size of the top margin, in points.
        
        Args:
            value (float): The top margin size in points.
        """
        pass


    @property
    @abc.abstractmethod
    def Zoom(self)->int:
        """
        Gets the zoom percentage for the worksheet.
        
        Returns:
            int: The zoom percentage.
        """
        pass


    @Zoom.setter
    @abc.abstractmethod
    def Zoom(self, value:int):
        """
        Sets the zoom percentage for the worksheet.
        
        Args:
            value (int): The zoom percentage.
        """
        pass


    @property

    @abc.abstractmethod
    def BackgoundImage(self)->'Stream':
        """
        Gets the background image of the page.
        
        Returns:
            Stream: The background image stream.
        """
        pass


    @BackgoundImage.setter
    @abc.abstractmethod
    def BackgoundImage(self, value:'Stream'):
        """
        Sets the background image of the page.
        
        Args:
            value (Stream): The background image stream.
        """
        pass


