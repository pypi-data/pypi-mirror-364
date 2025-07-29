from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IConditionalFormat (  IExcelApplication) :
    """Conditional format interface.
    
    This interface represents a conditional formatting rule in Excel. Conditional formatting
    allows cells to be formatted based on their values or other conditions. The interface
    provides methods for setting various formatting options like font styles, colors, borders,
    and specialized conditional formats like data bars, icon sets, and color scales.
    
    Inherits from:
        IExcelApplication: Excel application interface
    """
    @property

    @abc.abstractmethod
    def FormatType(self)->'ConditionalFormatType':
        """Gets the type of conditional format.
        
        Returns:
            ConditionalFormatType: The type of conditional format.
        """
        pass


    @FormatType.setter
    @abc.abstractmethod
    def FormatType(self, value:'ConditionalFormatType'):
        """Sets the type of conditional format.
        
        Args:
            value (ConditionalFormatType): The type of conditional format to set.
        """
        pass


    @property

    @abc.abstractmethod
    def Operator(self)->'ComparisonOperatorType':
        """Gets the comparison operator used in the conditional format.
        
        Returns:
            ComparisonOperatorType: The comparison operator.
        """
        pass


    @Operator.setter
    @abc.abstractmethod
    def Operator(self, value:'ComparisonOperatorType'):
        """Sets the comparison operator used in the conditional format.
        
        Args:
            value (ComparisonOperatorType): The comparison operator to set.
        """
        pass


    @property
    @abc.abstractmethod
    def IsBold(self)->bool:
        """Gets whether the font is bold when the condition is met.
        
        Returns:
            bool: True if the font is bold when the condition is met, otherwise False.
        """
        pass


    @IsBold.setter
    @abc.abstractmethod
    def IsBold(self, value:bool):
        """Sets whether the font is bold when the condition is met.
        
        Args:
            value (bool): True to make the font bold when the condition is met, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsItalic(self)->bool:
        """Gets whether the font is italic when the condition is met.
        
        Returns:
            bool: True if the font is italic when the condition is met, otherwise False.
        """
        pass


    @IsItalic.setter
    @abc.abstractmethod
    def IsItalic(self, value:bool):
        """Sets whether the font is italic when the condition is met.
        
        Args:
            value (bool): True to make the font italic when the condition is met, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def Priority(self)->int:
        """Gets the priority of the conditional format.
        
        The priority determines the order in which multiple conditional formats are evaluated.
        Lower numbers indicate higher priority.
        
        Returns:
            int: The priority value.
        """
        pass


    @Priority.setter
    @abc.abstractmethod
    def Priority(self, value:int):
        """Sets the priority of the conditional format.
        
        The priority determines the order in which multiple conditional formats are evaluated.
        Lower numbers indicate higher priority.
        
        Args:
            value (int): The priority value to set.
        """
        pass


    @property

    @abc.abstractmethod
    def FontKnownColor(self)->'ExcelColors':
        """Gets the predefined color of the font when the condition is met.
        
        Returns:
            ExcelColors: The predefined color of the font.
        """
        pass


    @FontKnownColor.setter
    @abc.abstractmethod
    def FontKnownColor(self, value:'ExcelColors'):
        """Sets the predefined color of the font when the condition is met.
        
        Args:
            value (ExcelColors): The predefined color to set for the font.
        """
        pass


    @property

    @abc.abstractmethod
    def FontColor(self)->'Color':
        """Gets the custom color of the font when the condition is met.
        
        Returns:
            Color: The custom color of the font.
        """
        pass


    @FontColor.setter
    @abc.abstractmethod
    def FontColor(self, value:'Color'):
        """Sets the custom color of the font when the condition is met.
        
        Args:
            value (Color): The custom color to set for the font.
        """
        pass


    @property

    @abc.abstractmethod
    def Underline(self)->'FontUnderlineType':
        """Gets the underline style of the font when the condition is met.
        
        Returns:
            FontUnderlineType: The underline style of the font.
        """
        pass


    @Underline.setter
    @abc.abstractmethod
    def Underline(self, value:'FontUnderlineType'):
        """Sets the underline style of the font when the condition is met.
        
        Args:
            value (FontUnderlineType): The underline style to set for the font.
        """
        pass


    @property
    @abc.abstractmethod
    def IsStrikeThrough(self)->bool:
        """Gets whether the font has strikethrough formatting when the condition is met.
        
        Returns:
            bool: True if the font has strikethrough formatting when the condition is met, otherwise False.
        """
        pass


    @IsStrikeThrough.setter
    @abc.abstractmethod
    def IsStrikeThrough(self, value:bool):
        """Sets whether the font has strikethrough formatting when the condition is met.
        
        Args:
            value (bool): True to apply strikethrough formatting when the condition is met, otherwise False.
        """
        pass


    @property

    @abc.abstractmethod
    def LeftBorderKnownColor(self)->'ExcelColors':
        """Gets the predefined color of the left border when the condition is met.
        
        Returns:
            ExcelColors: The predefined color of the left border.
        """
        pass


    @LeftBorderKnownColor.setter
    @abc.abstractmethod
    def LeftBorderKnownColor(self, value:'ExcelColors'):
        """Sets the predefined color of the left border when the condition is met.
        
        Args:
            value (ExcelColors): The predefined color to set for the left border.
        """
        pass


    @property

    @abc.abstractmethod
    def LeftBorderColor(self)->'Color':
        """Gets the custom color of the left border when the condition is met.
        
        Returns:
            Color: The custom color of the left border.
        """
        pass


    @LeftBorderColor.setter
    @abc.abstractmethod
    def LeftBorderColor(self, value:'Color'):
        """Sets the custom color of the left border when the condition is met.
        
        Args:
            value (Color): The custom color to set for the left border.
        """
        pass


    @property

    @abc.abstractmethod
    def LeftBorderStyle(self)->'LineStyleType':
        """Gets the style of the left border when the condition is met.
        
        Returns:
            LineStyleType: The style of the left border.
        """
        pass


    @LeftBorderStyle.setter
    @abc.abstractmethod
    def LeftBorderStyle(self, value:'LineStyleType'):
        """Sets the style of the left border when the condition is met.
        
        Args:
            value (LineStyleType): The style to set for the left border.
        """
        pass


    @property

    @abc.abstractmethod
    def RightBorderKnownColor(self)->'ExcelColors':
        """Gets the predefined color of the right border when the condition is met.
        
        Returns:
            ExcelColors: The predefined color of the right border.
        """
        pass


    @RightBorderKnownColor.setter
    @abc.abstractmethod
    def RightBorderKnownColor(self, value:'ExcelColors'):
        """Sets the predefined color of the right border when the condition is met.
        
        Args:
            value (ExcelColors): The predefined color to set for the right border.
        """
        pass


    @property

    @abc.abstractmethod
    def RightBorderColor(self)->'Color':
        """Gets the custom color of the right border when the condition is met.
        
        Returns:
            Color: The custom color of the right border.
        """
        pass


    @RightBorderColor.setter
    @abc.abstractmethod
    def RightBorderColor(self, value:'Color'):
        """Sets the custom color of the right border when the condition is met.
        
        Args:
            value (Color): The custom color to set for the right border.
        """
        pass


    @property

    @abc.abstractmethod
    def RightBorderStyle(self)->'LineStyleType':
        """Gets the style of the right border when the condition is met.
        
        Returns:
            LineStyleType: The style of the right border.
        """
        pass


    @RightBorderStyle.setter
    @abc.abstractmethod
    def RightBorderStyle(self, value:'LineStyleType'):
        """Sets the style of the right border when the condition is met.
        
        Args:
            value (LineStyleType): The style to set for the right border.
        """
        pass


    @property

    @abc.abstractmethod
    def TopBorderKnownColor(self)->'ExcelColors':
        """Gets the predefined color of the top border when the condition is met.
        
        Returns:
            ExcelColors: The predefined color of the top border.
        """
        pass


    @TopBorderKnownColor.setter
    @abc.abstractmethod
    def TopBorderKnownColor(self, value:'ExcelColors'):
        """Sets the predefined color of the top border when the condition is met.
        
        Args:
            value (ExcelColors): The predefined color to set for the top border.
        """
        pass


    @property

    @abc.abstractmethod
    def TopBorderColor(self)->'Color':
        """Gets the custom color of the top border when the condition is met.
        
        Returns:
            Color: The custom color of the top border.
        """
        pass


    @TopBorderColor.setter
    @abc.abstractmethod
    def TopBorderColor(self, value:'Color'):
        """Sets the custom color of the top border when the condition is met.
        
        Args:
            value (Color): The custom color to set for the top border.
        """
        pass


    @property

    @abc.abstractmethod
    def TopBorderStyle(self)->'LineStyleType':
        """Gets the style of the top border when the condition is met.
        
        Returns:
            LineStyleType: The style of the top border.
        """
        pass


    @TopBorderStyle.setter
    @abc.abstractmethod
    def TopBorderStyle(self, value:'LineStyleType'):
        """Sets the style of the top border when the condition is met.
        
        Args:
            value (LineStyleType): The style to set for the top border.
        """
        pass


    @property

    @abc.abstractmethod
    def BottomBorderKnownColor(self)->'ExcelColors':
        """Gets the predefined color of the bottom border when the condition is met.
        
        Returns:
            ExcelColors: The predefined color of the bottom border.
        """
        pass


    @BottomBorderKnownColor.setter
    @abc.abstractmethod
    def BottomBorderKnownColor(self, value:'ExcelColors'):
        """Sets the predefined color of the bottom border when the condition is met.
        
        Args:
            value (ExcelColors): The predefined color to set for the bottom border.
        """
        pass


    @property

    @abc.abstractmethod
    def BottomBorderColor(self)->'Color':
        """Gets the custom color of the bottom border when the condition is met.
        
        Returns:
            Color: The custom color of the bottom border.
        """
        pass


    @BottomBorderColor.setter
    @abc.abstractmethod
    def BottomBorderColor(self, value:'Color'):
        """Sets the custom color of the bottom border when the condition is met.
        
        Args:
            value (Color): The custom color to set for the bottom border.
        """
        pass


    @property

    @abc.abstractmethod
    def BottomBorderStyle(self)->'LineStyleType':
        """Gets the style of the bottom border when the condition is met.
        
        Returns:
            LineStyleType: The style of the bottom border.
        """
        pass


    @BottomBorderStyle.setter
    @abc.abstractmethod
    def BottomBorderStyle(self, value:'LineStyleType'):
        """Sets the style of the bottom border when the condition is met.
        
        Args:
            value (LineStyleType): The style to set for the bottom border.
        """
        pass


    @property

    @abc.abstractmethod
    def FirstFormula(self)->str:
        """Gets the first formula used in the conditional format.
        
        For conditional formats that use formulas (like formula-based conditions),
        this property contains the first formula expression.
        
        Returns:
            str: The first formula expression.
        """
        pass


    @FirstFormula.setter
    @abc.abstractmethod
    def FirstFormula(self, value:str):
        """Sets the first formula used in the conditional format.
        
        For conditional formats that use formulas (like formula-based conditions),
        this property sets the first formula expression.
        
        Args:
            value (str): The first formula expression to set.
        """
        pass


    @property

    @abc.abstractmethod
    def SecondFormula(self)->str:
        """Gets the second formula used in the conditional format.
        
        For conditional formats that use two formulas (like between conditions),
        this property contains the second formula expression.
        
        Returns:
            str: The second formula expression.
        """
        pass


    @SecondFormula.setter
    @abc.abstractmethod
    def SecondFormula(self, value:str):
        """Sets the second formula used in the conditional format.
        
        For conditional formats that use two formulas (like between conditions),
        this property sets the second formula expression.
        
        Args:
            value (str): The second formula expression to set.
        """
        pass


    @property

    @abc.abstractmethod
    def KnownColor(self)->'ExcelColors':
        """Gets the predefined color for general formatting when the condition is met.
        
        Returns:
            ExcelColors: The predefined color.
        """
        pass


    @KnownColor.setter
    @abc.abstractmethod
    def KnownColor(self, value:'ExcelColors'):
        """Sets the predefined color for general formatting when the condition is met.
        
        Args:
            value (ExcelColors): The predefined color to set.
        """
        pass


    @property

    @abc.abstractmethod
    def Color(self)->'Color':
        """Gets the custom color for general formatting when the condition is met.
        
        Returns:
            Color: The custom color.
        """
        pass


    @Color.setter
    @abc.abstractmethod
    def Color(self, value:'Color'):
        """Sets the custom color for general formatting when the condition is met.
        
        Args:
            value (Color): The custom color to set.
        """
        pass


    @property

    @abc.abstractmethod
    def BackKnownColor(self)->'ExcelColors':
        """Gets the predefined background color when the condition is met.
        
        Returns:
            ExcelColors: The predefined background color.
        """
        pass


    @BackKnownColor.setter
    @abc.abstractmethod
    def BackKnownColor(self, value:'ExcelColors'):
        """Sets the predefined background color when the condition is met.
        
        Args:
            value (ExcelColors): The predefined background color to set.
        """
        pass


    @property

    @abc.abstractmethod
    def BackColor(self)->'Color':
        """Gets the custom background color when the condition is met.
        
        Returns:
            Color: The custom background color.
        """
        pass


    @BackColor.setter
    @abc.abstractmethod
    def BackColor(self, value:'Color'):
        """Sets the custom background color when the condition is met.
        
        Args:
            value (Color): The custom background color to set.
        """
        pass


    @property

    @abc.abstractmethod
    def FillPattern(self)->'ExcelPatternType':
        """Gets the fill pattern type when the condition is met.
        
        Returns:
            ExcelPatternType: The fill pattern type.
        """
        pass


    @FillPattern.setter
    @abc.abstractmethod
    def FillPattern(self, value:'ExcelPatternType'):
        """Sets the fill pattern type when the condition is met.
        
        Args:
            value (ExcelPatternType): The fill pattern type to set.
        """
        pass


    @property
    @abc.abstractmethod
    def IsSuperScript(self)->bool:
        """Gets whether the font is superscript when the condition is met.
        
        Returns:
            bool: True if the font is superscript when the condition is met, otherwise False.
        """
        pass


    @IsSuperScript.setter
    @abc.abstractmethod
    def IsSuperScript(self, value:bool):
        """Sets whether the font is superscript when the condition is met.
        
        Args:
            value (bool): True to make the font superscript when the condition is met, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsSubScript(self)->bool:
        """Gets whether the font is subscript when the condition is met.
        
        Returns:
            bool: True if the font is subscript when the condition is met, otherwise False.
        """
        pass


    @IsSubScript.setter
    @abc.abstractmethod
    def IsSubScript(self, value:bool):
        """Sets whether the font is subscript when the condition is met.
        
        Args:
            value (bool): True to make the font subscript when the condition is met, otherwise False.
        """
        pass


    @property

    @abc.abstractmethod
    def DataBar(self)->'DataBar':
        """Gets the data bar conditional format settings.
        
        Returns:
            DataBar: The data bar conditional format settings.
        """
        pass


    @property

    @abc.abstractmethod
    def IconSet(self)->'IconSet':
        """Gets the icon set conditional format settings.
        
        Returns:
            IconSet: The icon set conditional format settings.
        """
        pass


    @property

    @abc.abstractmethod
    def ColorScale(self)->'ColorScale':
        """Gets the color scale conditional format settings.
        
        Returns:
            ColorScale: The color scale conditional format settings.
        """
        pass


