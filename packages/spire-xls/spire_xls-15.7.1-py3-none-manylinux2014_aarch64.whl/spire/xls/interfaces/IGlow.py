from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IGlow (abc.ABC) :
    """
    Interface for glow effect formatting in Excel.
    
    This interface provides properties and methods to manipulate glow effects
    for shapes and objects in Excel, including color, radius, and transparency.
    """
    @property
    @abc.abstractmethod
    def Color(self)->'Color':
        """
        Gets the color of the glow effect.

        Returns:
            Color: The color of the glow.
        """
        pass

    @Color.setter
    @abc.abstractmethod
    def Color(self, value:'Color'):
        """
        Sets the color of the glow effect.

        Args:
            value (Color): The color to set.
        """
        pass

    @property
    @abc.abstractmethod
    def SoftEdge(self)->int:
        """
        Gets the soft edge value of the glow effect.

        Returns:
            int: The soft edge value.
        """
        pass

    @SoftEdge.setter
    @abc.abstractmethod
    def SoftEdge(self, value:int):
        """
        Sets the soft edge value of the glow effect.

        Args:
            value (int): The soft edge value to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Transparency(self)->int:
        """
        Gets the transparency value of the glow effect.

        Returns:
            int: The transparency value.
        """
        pass

    @Transparency.setter
    @abc.abstractmethod
    def Transparency(self, value:int):
        """
        Sets the transparency value of the glow effect.

        Args:
            value (int): The transparency value to set.
        """
        pass

    @property
    @abc.abstractmethod
    def Radius(self)->int:
        """
        Gets the radius of the glow effect.

        Returns:
            int: The radius value.
        """
        pass

    @Radius.setter
    @abc.abstractmethod
    def Radius(self, value:int):
        """
        Sets the radius of the glow effect.

        Args:
            value (int): The radius value to set.
        """
        pass


