from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IGeomPathInfo (abc.ABC) :
    """
    Interface for geometric path information in Excel shapes.
    
    This interface provides properties and methods to manipulate geometric paths
    that define custom shapes, including their fill mode, dimensions, and path segments.
    """
    @property
    @abc.abstractmethod
    def ShowStroke(self)->bool:
        """
        Gets whether the stroke is shown for the path.

        Returns:
            bool: True if the stroke is shown, otherwise False.
        """
        pass

    @ShowStroke.setter
    @abc.abstractmethod
    def ShowStroke(self, value:bool):
        """
        Sets whether the stroke is shown for the path.

        Args:
            value (bool): True to show the stroke, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def ExtrusionOk(self)->bool:
        """
        Gets whether extrusion is allowed for the path.

        Returns:
            bool: True if extrusion is allowed, otherwise False.
        """
        pass

    @ExtrusionOk.setter
    @abc.abstractmethod
    def ExtrusionOk(self, value:bool):
        """
        Sets whether extrusion is allowed for the path.

        Args:
            value (bool): True to allow extrusion, otherwise False.
        """
        pass

    @property
    @abc.abstractmethod
    def Height(self)->int:
        """
        Gets the height of the path.

        Returns:
            int: The height value.
        """
        pass

    @property
    @abc.abstractmethod
    def Width(self)->int:
        """
        Gets the width of the path.

        Returns:
            int: The width value.
        """
        pass

    @property
    @abc.abstractmethod
    def FillMode(self)->'PathFillMode':
        """
        Gets the fill mode of the path.

        Returns:
            PathFillMode: The fill mode.
        """
        pass

    @FillMode.setter
    @abc.abstractmethod
    def FillMode(self, value:'PathFillMode'):
        """
        Sets the fill mode of the path.

        Args:
            value (PathFillMode): The fill mode to set.
        """
        pass

    @property
    @abc.abstractmethod
    def MsoLstCount(self)->int:
        """
        Gets the count of Mso list items in the path.

        Returns:
            int: The count of Mso list items.
        """
        pass

    @abc.abstractmethod
    def get_Item(self ,index:int)->'MsoPathInfo':
        """
        Gets the MsoPathInfo item by index.

        Args:
            index (int): The index of the item.

        Returns:
            MsoPathInfo: The MsoPathInfo item at the specified index.
        """
        pass

    @abc.abstractmethod
    def AddMso(self ,type:'MsoPathType')->'MsoPathInfo':
        """
        Adds a new MsoPathInfo item of the specified type.

        Args:
            type (MsoPathType): The type of Mso path to add.

        Returns:
            MsoPathInfo: The added MsoPathInfo item.
        """
        pass


