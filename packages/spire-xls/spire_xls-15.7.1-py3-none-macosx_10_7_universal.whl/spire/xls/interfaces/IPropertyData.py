from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IPropertyData (abc.ABC) :
    """Property data interface for Excel document properties.
    
    This interface represents a single property in a document property collection,
    providing access to its value, name, and identifier. Property data can be
    used to store custom metadata about a document.
    """
    @property
    @abc.abstractmethod
    def Value(self)->'SpireObject':
        """Gets the value of the property.
        
        This property returns the current value stored in the property.
        The returned object can be of various types depending on the property.
        
        Returns:
            SpireObject: The value of the property.
        """
        pass


#    @property
#
#    @abc.abstractmethod
#    def Type(self)->'VarEnum':
#        """Gets the data type of the property value.
#        
#        This property returns an enumeration value indicating the data type
#        of the property value (such as string, integer, date, etc.).
#        
#        Returns:
#            VarEnum: The data type of the property value.
#        """
#        pass
#


    @property
    @abc.abstractmethod
    def Name(self)->str:
        """Gets the name of the property.
        
        This property returns the name that identifies the property in the collection.
        
        Returns:
            str: The name of the property.
        """
        pass


    @property
    @abc.abstractmethod
    def Id(self)->int:
        """Gets the identifier of the property.
        
        This property returns a numeric identifier for the property.
        
        Returns:
            int: The identifier of the property.
        """
        pass


    @Id.setter
    @abc.abstractmethod
    def Id(self, value:int):
        """Sets the identifier of the property.
        
        This property sets a numeric identifier for the property.
        
        Args:
            value (int): The new identifier for the property.
        """
        pass


    @abc.abstractmethod
    def SetValue(self, value:'SpireObject', type:'PropertyType')->bool:
        """Sets the value and type of the property.
        
        This method sets the value of the property with the specified type.
        
        Args:
            value (SpireObject): The new value to set for the property.
            type (PropertyType): The type of the property value.
            
        Returns:
            bool: True if the value was successfully set, otherwise False.
        """
        pass


