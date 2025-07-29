from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IInterior (abc.ABC) :
    """
    Interface for interior formatting in Excel.
    
    This interface provides properties and methods to manipulate the interior
    formatting of Excel objects, including colors, patterns, and gradients.
    """
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
            value (ExcelColors): The known color to set.
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
            value (Color): The color to set.
        """
        pass

    @property
    @abc.abstractmethod
    def KnownColor(self)->'ExcelColors':
        """
        Gets the known color of the interior.

        Returns:
            ExcelColors: The known color of the interior.
        """
        pass

    @KnownColor.setter
    @abc.abstractmethod
    def KnownColor(self, value:'ExcelColors'):
        """
        Sets the known color of the interior.

        Args:
            value (ExcelColors): The known color to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Color(self)->'Color':
        """
        Gets the color of the interior.

        Returns:
            Color: The color of the interior.
        """
        pass

    @Color.setter
    @abc.abstractmethod
    def Color(self, value:'Color'):
        """
        Sets the color of the interior.

        Args:
            value (Color): The color to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Gradient(self)->'ExcelGradient':
        """
        Gets the gradient of the interior.

        Returns:
            ExcelGradient: The gradient object.
        """
        pass

    @property
    @abc.abstractmethod
    def FillPattern(self)->'ExcelPatternType':
        """
        Gets the fill pattern type of the interior.

        Returns:
            ExcelPatternType: The fill pattern type.
        """
        pass

    @FillPattern.setter
    @abc.abstractmethod
    def FillPattern(self, value:'ExcelPatternType'):
        """
        Sets the fill pattern type of the interior.

        Args:
            value (ExcelPatternType): The fill pattern type to set.
        """
        pass


