from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class TextBoxShapeBase (  ITextBoxShape) :
    """Base abstract class for text box shapes in Excel.
    
    This class implements the ITextBoxShape interface and provides the foundation for
    text box shapes in Excel worksheets. It defines abstract properties for text wrapping,
    margins, inset mode, and fill color that derived classes must implement.
    """
    @property
    @abc.abstractmethod
    def IsWrapText(self)->bool:
        """Gets or sets whether text is wrapped within the text box.
        
        Returns:
            bool: True if text wrapping is enabled; otherwise, False.
        """
        pass


    @IsWrapText.setter
    @abc.abstractmethod
    def IsWrapText(self, value:bool):
        """Sets whether text is wrapped within the text box.
        
        Args:
            value (bool): True to enable text wrapping; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def InnerLeftMargin(self)->float:
        """Gets or sets the left margin within the text box in points.
        
        Returns:
            float: The left margin value in points.
        """
        pass


    @InnerLeftMargin.setter
    @abc.abstractmethod
    def InnerLeftMargin(self, value:float):
        """Sets the left margin within the text box in points.
        
        Args:
            value (float): The left margin value in points.
        """
        pass


    @property
    @abc.abstractmethod
    def InnerRightMargin(self)->float:
        """Gets or sets the right margin within the text box in points.
        
        Returns:
            float: The right margin value in points.
        """
        pass


    @InnerRightMargin.setter
    @abc.abstractmethod
    def InnerRightMargin(self, value:float):
        """Sets the right margin within the text box in points.
        
        Args:
            value (float): The right margin value in points.
        """
        pass


    @property
    @abc.abstractmethod
    def InnerTopMargin(self)->float:
        """Gets or sets the top margin within the text box in points.
        
        Returns:
            float: The top margin value in points.
        """
        pass


    @InnerTopMargin.setter
    @abc.abstractmethod
    def InnerTopMargin(self, value:float):
        """Sets the top margin within the text box in points.
        
        Args:
            value (float): The top margin value in points.
        """
        pass


    @property
    @abc.abstractmethod
    def InnerBottomMargin(self)->float:
        """Gets or sets the bottom margin within the text box in points.
        
        Returns:
            float: The bottom margin value in points.
        """
        pass


    @InnerBottomMargin.setter
    @abc.abstractmethod
    def InnerBottomMargin(self, value:float):
        """Sets the bottom margin within the text box in points.
        
        Args:
            value (float): The bottom margin value in points.
        """
        pass


    @property

    @abc.abstractmethod
    def InsetMode(self)->str:
        """Gets or sets the inset mode for the text box.
        
        The inset mode determines how text is positioned within the text box.
        
        Returns:
            str: The inset mode string.
        """
        pass


    @InsetMode.setter
    @abc.abstractmethod
    def InsetMode(self, value:str):
        """Sets the inset mode for the text box.
        
        Args:
            value (str): The inset mode string.
        """
        pass


    @property

    @abc.abstractmethod
    def FillColor(self)->'Color':
        """Gets or sets the fill color of the text box.
        
        Returns:
            Color: The fill color object.
        """
        pass


    @FillColor.setter
    @abc.abstractmethod
    def FillColor(self, value:'Color'):
        """Sets the fill color of the text box.
        
        Args:
            value (Color): The fill color object.
        """
        pass


