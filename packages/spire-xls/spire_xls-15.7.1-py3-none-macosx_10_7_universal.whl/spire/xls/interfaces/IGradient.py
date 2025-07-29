from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IGradient (abc.ABC) :
    """
    Interface for gradient fill formatting in Excel.
    
    This interface provides properties and methods to manipulate gradient fills
    in Excel objects, including colors, styles, and variants.
    """
    @property
    @abc.abstractmethod
    def BackColorObject(self)->'OColor':
        """
        Gets the background color object of the gradient.

        Returns:
            OColor: The background color object.
        """
        pass

    @property
    @abc.abstractmethod
    def ForeColorObject(self)->'OColor':
        """
        Gets the foreground color object of the gradient.

        Returns:
            OColor: The foreground color object.
        """
        pass

    @property
    @abc.abstractmethod
    def BackColor(self)->'Color':
        """
        Gets the background color of the gradient.

        Returns:
            Color: The background color.
        """
        pass

    @BackColor.setter
    @abc.abstractmethod
    def BackColor(self, value:'Color'):
        """
        Sets the background color of the gradient.

        Args:
            value (Color): The background color to set.
        """
        pass

    @property
    @abc.abstractmethod
    def BackKnownColor(self)->'ExcelColors':
        """
        Gets the known background color of the gradient.

        Returns:
            ExcelColors: The known background color.
        """
        pass

    @BackKnownColor.setter
    @abc.abstractmethod
    def BackKnownColor(self, value:'ExcelColors'):
        """
        Sets the known background color of the gradient.

        Args:
            value (ExcelColors): The known background color to set.
        """
        pass

    @property
    @abc.abstractmethod
    def ForeColor(self)->'Color':
        """
        Gets the foreground color of the gradient.

        Returns:
            Color: The foreground color.
        """
        pass

    @ForeColor.setter
    @abc.abstractmethod
    def ForeColor(self, value:'Color'):
        """
        Sets the foreground color of the gradient.

        Args:
            value (Color): The foreground color to set.
        """
        pass

    @property
    @abc.abstractmethod
    def ForeKnownColor(self)->'ExcelColors':
        """
        Gets the known foreground color of the gradient.

        Returns:
            ExcelColors: The known foreground color.
        """
        pass

    @ForeKnownColor.setter
    @abc.abstractmethod
    def ForeKnownColor(self, value:'ExcelColors'):
        """
        Sets the known foreground color of the gradient.

        Args:
            value (ExcelColors): The known foreground color to set.
        """
        pass

    @property
    @abc.abstractmethod
    def GradientStyle(self)->'GradientStyleType':
        """
        Gets the gradient style type.

        Returns:
            GradientStyleType: The gradient style type.
        """
        pass

    @GradientStyle.setter
    @abc.abstractmethod
    def GradientStyle(self, value:'GradientStyleType'):
        """
        Sets the gradient style type.

        Args:
            value (GradientStyleType): The gradient style type to set.
        """
        pass

    @property
    @abc.abstractmethod
    def GradientVariant(self)->'GradientVariantsType':
        """
        Gets the gradient variant type.

        Returns:
            GradientVariantsType: The gradient variant type.
        """
        pass

    @GradientVariant.setter
    @abc.abstractmethod
    def GradientVariant(self, value:'GradientVariantsType'):
        """
        Sets the gradient variant type.

        Args:
            value (GradientVariantsType): The gradient variant type to set.
        """
        pass

    @abc.abstractmethod
    def CompareTo(self ,gradient:'IGradient')->int:
        """
        Compares this gradient with another gradient.

        Args:
            gradient (IGradient): The gradient to compare with.

        Returns:
            int: The comparison result.
        """
        pass

    @dispatch
    @abc.abstractmethod
    def TwoColorGradient(self):
        """
        Applies a two-color gradient.
        """
        pass

    @dispatch
    @abc.abstractmethod
    def TwoColorGradient(self ,style:GradientStyleType,variant:GradientVariantsType):
        """
        Applies a two-color gradient with the specified style and variant.

        Args:
            style (GradientStyleType): The gradient style type.
            variant (GradientVariantsType): The gradient variant type.
        """
        pass


