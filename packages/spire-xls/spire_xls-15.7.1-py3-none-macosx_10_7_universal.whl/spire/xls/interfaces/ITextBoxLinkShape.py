from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ITextBoxLinkShape (  ITextBoxShape) :
    """Interface for linked text box shapes in Excel worksheets.
    
    This interface represents a text box shape that is linked to another object
    and provides properties to access and modify its rotation and hyperlink attributes.
    """
    @property
    @abc.abstractmethod
    def Rotation(self)->int:
        """Gets the rotation angle of the linked text box shape in degrees.
        
        Returns:
            int: The rotation angle in degrees.
        """
        pass


    @Rotation.setter
    @abc.abstractmethod
    def Rotation(self, value:int):
        """Sets the rotation angle of the linked text box shape in degrees.
        
        Args:
            value (int): The rotation angle in degrees to set.
        """
        pass


    @property

    @abc.abstractmethod
    def HyLink(self)->'IHyperLink':
        """Gets the hyperlink associated with the linked text box shape.
        
        Returns:
            IHyperLink: An object that represents the hyperlink associated with the text box.
        """
        pass


