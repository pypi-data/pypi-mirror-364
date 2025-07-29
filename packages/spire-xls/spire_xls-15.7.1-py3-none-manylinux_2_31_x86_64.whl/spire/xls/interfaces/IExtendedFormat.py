from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IExtendedFormat (  IExcelApplication) :
    """
    Interface for extended formatting in Excel.
    
    This interface extends IExcelApplication to provide properties and methods
    for manipulating cell formatting, including borders, patterns, alignment,
    fonts, and number formats.
    """
    @property
    @abc.abstractmethod
    def Borders(self)->'IBorders':
        """
        Gets the borders of the extended format.

        Returns:
            IBorders: The borders object.
        """
        pass

    @property
    @abc.abstractmethod
    def FillPattern(self)->'ExcelPatternType':
        """
        Gets the fill pattern type.

        Returns:
            ExcelPatternType: The fill pattern type.
        """
        pass

    @FillPattern.setter
    @abc.abstractmethod
    def FillPattern(self, value:'ExcelPatternType'):
        """
        Sets the fill pattern type.

        Args:
            value (ExcelPatternType): The fill pattern type to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Font(self)->'IFont':
        """
        Gets the font of the extended format.

        Returns:
            IFont: The font object.
        """
        pass

    @property
    @abc.abstractmethod
    def FormulaHidden(self)->bool:
        """
        Gets whether the formula is hidden.

        Returns:
            bool: True if the formula is hidden, otherwise False.
        """
        pass

    @FormulaHidden.setter
    @abc.abstractmethod
    def FormulaHidden(self, value:bool):
        """
        Sets whether the formula is hidden.

        Args:
            value (bool): True to hide the formula, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def HorizontalAlignment(self)->'HorizontalAlignType':
        """
        Gets the horizontal alignment type.

        Returns:
            HorizontalAlignType: The horizontal alignment type.
        """
        pass

    @HorizontalAlignment.setter
    @abc.abstractmethod
    def HorizontalAlignment(self, value:'HorizontalAlignType'):
        """
        Sets the horizontal alignment type.

        Args:
            value (HorizontalAlignType): The horizontal alignment type to set.
        """
        pass

    @property
    @abc.abstractmethod
    def IncludeAlignment(self)->bool:
        """
        Gets whether alignment is included.

        Returns:
            bool: True if alignment is included, otherwise False.
        """
        pass

    @IncludeAlignment.setter
    @abc.abstractmethod
    def IncludeAlignment(self, value:bool):
        """
        Sets whether alignment is included.

        Args:
            value (bool): True to include alignment, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def IncludeBorder(self)->bool:
        """
        Gets whether border is included.

        Returns:
            bool: True if border is included, otherwise False.
        """
        pass

    @IncludeBorder.setter
    @abc.abstractmethod
    def IncludeBorder(self, value:bool):
        """
        Sets whether border is included.

        Args:
            value (bool): True to include border, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def IncludeFont(self)->bool:
        """
        Gets whether font is included.

        Returns:
            bool: True if font is included, otherwise False.
        """
        pass

    @IncludeFont.setter
    @abc.abstractmethod
    def IncludeFont(self, value:bool):
        """
        Sets whether font is included.

        Args:
            value (bool): True to include font, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def IncludeNumberFormat(self)->bool:
        """
        Gets whether number format is included.

        Returns:
            bool: True if number format is included, otherwise False.
        """
        pass

    @IncludeNumberFormat.setter
    @abc.abstractmethod
    def IncludeNumberFormat(self, value:bool):
        """
        Sets whether number format is included.

        Args:
            value (bool): True to include number format, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def IncludePatterns(self)->bool:
        """
        Gets whether patterns are included.

        Returns:
            bool: True if patterns are included, otherwise False.
        """
        pass

    @IncludePatterns.setter
    @abc.abstractmethod
    def IncludePatterns(self, value:bool):
        """
        Sets whether patterns are included.

        Args:
            value (bool): True to include patterns, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def IncludeProtection(self)->bool:
        """
        Gets whether protection is included.

        Returns:
            bool: True if protection is included, otherwise False.
        """
        pass

    @IncludeProtection.setter
    @abc.abstractmethod
    def IncludeProtection(self, value:bool):
        """
        Sets whether protection is included.

        Args:
            value (bool): True to include protection, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def IndentLevel(self)->int:
        """
        Gets the indent level.

        Returns:
            int: The indent level.
        """
        pass

    @IndentLevel.setter
    @abc.abstractmethod
    def IndentLevel(self, value:int):
        """
        Sets the indent level.
        
        Args:
            value (int): The indent level to set.
        """
        pass

    @property
    @abc.abstractmethod
    def IsFirstSymbolApostrophe(self)->bool:
        """
        Gets whether the first symbol is an apostrophe.
        
        Returns:
            bool: True if the first symbol is an apostrophe, otherwise False.
        """
        pass

    @IsFirstSymbolApostrophe.setter
    @abc.abstractmethod
    def IsFirstSymbolApostrophe(self, value:bool):
        """
        Sets whether the first symbol is an apostrophe.
        
        Args:
            value (bool): True to set the first symbol as an apostrophe, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def Locked(self)->bool:
        """
        Gets whether the cell is locked.
        
        Returns:
            bool: True if the cell is locked, otherwise False.
        """
        pass

    @Locked.setter
    @abc.abstractmethod
    def Locked(self, value:bool):
        """
        Sets whether the cell is locked.
        
        Args:
            value (bool): True to lock the cell, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def JustifyLast(self)->bool:
        """
        Gets whether the last line is justified.
        
        Returns:
            bool: True if the last line is justified, otherwise False.
        """
        pass

    @JustifyLast.setter
    @abc.abstractmethod
    def JustifyLast(self, value:bool):
        """
        Sets whether the last line is justified.
        
        Args:
            value (bool): True to justify the last line, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def NumberFormat(self)->str:
        """
        Gets the number format string.
        
        Returns:
            str: The number format string.
        """
        pass

    @NumberFormat.setter
    @abc.abstractmethod
    def NumberFormat(self, value:str):
        """
        Sets the number format string.
        
        Args:
            value (str): The number format string to set.
        """
        pass

    @property
    @abc.abstractmethod
    def NumberFormatIndex(self)->int:
        """
        Gets the number format index.
        
        Returns:
            int: The number format index.
        """
        pass

    @NumberFormatIndex.setter
    @abc.abstractmethod
    def NumberFormatIndex(self, value:int):
        """
        Sets the number format index.
        
        Args:
            value (int): The number format index to set.
        """
        pass

    @property
    @abc.abstractmethod
    def NumberFormatLocal(self)->str:
        """
        Gets the localized number format string.
        
        Returns:
            str: The localized number format string.
        """
        pass

    @NumberFormatLocal.setter
    @abc.abstractmethod
    def NumberFormatLocal(self, value:str):
        """
        Sets the localized number format string.
        
        Args:
            value (str): The localized number format string to set.
        """
        pass

    @property
    @abc.abstractmethod
    def NumberFormatSettings(self)->'INumberFormat':
        """
        Gets the number format settings.
        
        Returns:
            INumberFormat: The number format settings object.
        """
        pass

    @property
    @abc.abstractmethod
    def ReadingOrder(self)->'ReadingOrderType':
        """
        Gets the reading order type.
        
        Returns:
            ReadingOrderType: The reading order type.
        """
        pass

    @ReadingOrder.setter
    @abc.abstractmethod
    def ReadingOrder(self, value:'ReadingOrderType'):
        """
        Sets the reading order type.
        
        Args:
            value (ReadingOrderType): The reading order type to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Rotation(self)->int:
        """
        Gets the text rotation angle in degrees.
        
        Returns:
            int: The rotation angle in degrees.
        """
        pass

    @Rotation.setter
    @abc.abstractmethod
    def Rotation(self, value:int):
        """
        Sets the text rotation angle in degrees.
        
        Args:
            value (int): The rotation angle in degrees to set.
        """
        pass

    @property
    @abc.abstractmethod
    def ShrinkToFit(self)->bool:
        """
        Gets whether text shrinks to fit in the cell.
        
        Returns:
            bool: True if text shrinks to fit, otherwise False.
        """
        pass

    @ShrinkToFit.setter
    @abc.abstractmethod
    def ShrinkToFit(self, value:bool):
        """
        Sets whether text shrinks to fit in the cell.
        
        Args:
            value (bool): True to shrink text to fit, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def VerticalAlignment(self)->'VerticalAlignType':
        """
        Gets the vertical alignment type.
        
        Returns:
            VerticalAlignType: The vertical alignment type.
        """
        pass

    @VerticalAlignment.setter
    @abc.abstractmethod
    def VerticalAlignment(self, value:'VerticalAlignType'):
        """
        Sets the vertical alignment type.
        
        Args:
            value (VerticalAlignType): The vertical alignment type to set.
        """
        pass

    @property
    @abc.abstractmethod
    def WrapText(self)->bool:
        """
        Gets whether text wraps in the cell.
        
        Returns:
            bool: True if text wraps, otherwise False.
        """
        pass

    @WrapText.setter
    @abc.abstractmethod
    def WrapText(self, value:bool):
        """
        Sets whether text wraps in the cell.
        
        Args:
            value (bool): True to wrap text, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def PatternKnownColor(self)->'ExcelColors':
        """
        Gets the known color of the pattern.
        
        Returns:
            ExcelColors: The known color of the pattern.
        """
        pass

    @PatternKnownColor.setter
    @abc.abstractmethod
    def PatternKnownColor(self, value:'ExcelColors'):
        """
        Sets the known color of the pattern.
        
        Args:
            value (ExcelColors): The known color of the pattern to set.
        """
        pass

    @property
    @abc.abstractmethod
    def PatternColor(self)->'Color':
        """
        Gets the color of the pattern.
        
        Returns:
            Color: The color of the pattern.
        """
        pass

    @PatternColor.setter
    @abc.abstractmethod
    def PatternColor(self, value:'Color'):
        """
        Sets the color of the pattern.
        
        Args:
            value (Color): The color of the pattern to set.
        """
        pass

    @property
    @abc.abstractmethod
    def KnownColor(self)->'ExcelColors':
        """
        Gets the known color of the cell.
        
        Returns:
            ExcelColors: The known color of the cell.
        """
        pass

    @KnownColor.setter
    @abc.abstractmethod
    def KnownColor(self, value:'ExcelColors'):
        """
        Sets the known color of the cell.
        
        Args:
            value (ExcelColors): The known color of the cell to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Color(self)->'Color':
        """
        Gets the color of the cell.
        
        Returns:
            Color: The color of the cell.
        """
        pass

    @Color.setter
    @abc.abstractmethod
    def Color(self, value:'Color'):
        """
        Sets the color of the cell.
        
        Args:
            value (Color): The color of the cell to set.
        """
        pass

    @property
    @abc.abstractmethod
    def IsModified(self)->bool:
        """
        Gets whether the format has been modified.
        
        Returns:
            bool: True if the format has been modified, otherwise False.
        """
        pass

    @abc.abstractmethod
    def SetThemeColor(self ,type:'ThemeColorType',tint:float):
        """
        Sets the theme color with a specified tint.
        
        Args:
            type (ThemeColorType): The theme color type.
            tint (float): The tint value to apply to the theme color.
        """
        pass

#
#    @abc.abstractmethod
#    def GetThemeColor(self ,type:'ThemeColorType&',tint:'Double&')->bool:
#        """
#
#        """
#        pass
#


