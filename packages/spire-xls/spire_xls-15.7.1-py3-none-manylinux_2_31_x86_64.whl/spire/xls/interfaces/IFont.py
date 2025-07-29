from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IFont (  IExcelApplication, IOptimizedUpdate) :
    """
    Interface for font objects in Excel.
    
    This interface extends IExcelApplication and IOptimizedUpdate to provide
    properties and methods for manipulating font attributes in Excel, including
    style, size, color, and text effects.
    """
    @property
    @abc.abstractmethod
    def IsBold(self)->bool:
        """
        Gets whether the font is bold.

        Returns:
            bool: True if the font is bold, otherwise False.
        """
        pass

    @IsBold.setter
    @abc.abstractmethod
    def IsBold(self, value:bool):
        """
        Sets whether the font is bold.

        Args:
            value (bool): True to set bold, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def KnownColor(self)->'ExcelColors':
        """
        Gets the known color of the font.

        Returns:
            ExcelColors: The known color.
        """
        pass

    @KnownColor.setter
    @abc.abstractmethod
    def KnownColor(self, value:'ExcelColors'):
        """
        Sets the known color of the font.

        Args:
            value (ExcelColors): The known color to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Color(self)->'Color':
        """
        Gets the color of the font.

        Returns:
            Color: The color of the font.
        """
        pass

    @Color.setter
    @abc.abstractmethod
    def Color(self, value:'Color'):
        """
        Sets the color of the font.

        Args:
            value (Color): The color to set.
        """
        pass

    @abc.abstractmethod
    def SetThemeColor(self ,type:'ThemeColorType',tint:float):
        """
        Sets the theme color for the font.

        Args:
            type (ThemeColorType): The theme color type.
            tint (float): The tint value.
        """
        pass

    @property
    @abc.abstractmethod
    def IsItalic(self)->bool:
        """
        Gets whether the font is italic.

        Returns:
            bool: True if the font is italic, otherwise False.
        """
        pass

    @IsItalic.setter
    @abc.abstractmethod
    def IsItalic(self, value:bool):
        """
        Sets whether the font is italic.

        Args:
            value (bool): True to set italic, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def Size(self)->float:
        """
        Gets the size of the font.

        Returns:
            float: The font size.
        """
        pass

    @Size.setter
    @abc.abstractmethod
    def Size(self, value:float):
        """
        Sets the size of the font.

        Args:
            value (float): The font size to set.
        """
        pass

    @property
    @abc.abstractmethod
    def IsStrikethrough(self)->bool:
        """
        Gets whether the font is strikethrough.

        Returns:
            bool: True if strikethrough, otherwise False.
        """
        pass

    @IsStrikethrough.setter
    @abc.abstractmethod
    def IsStrikethrough(self, value:bool):
        """
        Sets whether the font is strikethrough.

        Args:
            value (bool): True to set strikethrough, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def IsSubscript(self)->bool:
        """
        Gets whether the font is subscript.

        Returns:
            bool: True if subscript, otherwise False.
        """
        pass

    @IsSubscript.setter
    @abc.abstractmethod
    def IsSubscript(self, value:bool):
        """
        Sets whether the font is subscript.

        Args:
            value (bool): True to set subscript, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def StrikethroughType(self)->str:
        """
        Gets the strikethrough type of the font.

        Returns:
            str: The strikethrough type.
        """
        pass

    @StrikethroughType.setter
    @abc.abstractmethod
    def StrikethroughType(self, value:str):
        """
        Sets the strikethrough type of the font.

        Args:
            value (str): The strikethrough type to set.
        """
        pass

    @property
    @abc.abstractmethod
    def IsSuperscript(self)->bool:
        """
        Gets whether the font is superscript.

        Returns:
            bool: True if superscript, otherwise False.
        """
        pass

    @IsSuperscript.setter
    @abc.abstractmethod
    def IsSuperscript(self, value:bool):
        """
        Sets whether the font is superscript.

        Args:
            value (bool): True to set superscript, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def Underline(self)->'FontUnderlineType':
        """
        Gets the underline type of the font.

        Returns:
            FontUnderlineType: The underline type.
        """
        pass

    @Underline.setter
    @abc.abstractmethod
    def Underline(self, value:'FontUnderlineType'):
        """
        Sets the underline type of the font.

        Args:
            value (FontUnderlineType): The underline type to set.
        """
        pass

    @property
    @abc.abstractmethod
    def FontName(self)->str:
        """
        Gets the font name.

        Returns:
            str: The font name.
        """
        pass

    @FontName.setter
    @abc.abstractmethod
    def FontName(self, value:str):
        """
        Sets the font name.

        Args:
            value (str): The font name to set.
        """
        pass

    @property
    @abc.abstractmethod
    def VerticalAlignment(self)->'FontVertialAlignmentType':
        """
        Gets the vertical alignment of the font.

        Returns:
            FontVertialAlignmentType: The vertical alignment.
        """
        pass

    @VerticalAlignment.setter
    @abc.abstractmethod
    def VerticalAlignment(self, value:'FontVertialAlignmentType'):
        """
        Sets the vertical alignment of the font.

        Args:
            value (FontVertialAlignmentType): The vertical alignment to set.
        """
        pass

    @property
    @abc.abstractmethod
    def IsAutoColor(self)->bool:
        """
        Gets whether the font is auto color.

        Returns:
            bool: True if auto color, otherwise False.
        """
        pass

    @abc.abstractmethod
    def GenerateNativeFont(self)->'Font':
        """
        Generates a native font.

        Returns:
            Font: The generated native font.
        """
        pass


