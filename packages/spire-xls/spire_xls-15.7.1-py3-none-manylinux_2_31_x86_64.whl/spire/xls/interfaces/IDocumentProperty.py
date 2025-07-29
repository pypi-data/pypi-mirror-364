from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IDocumentProperty (abc.ABC) :
    """Document property interface.
    
    This interface provides functionality for accessing and managing document properties
    in Excel workbooks. Document properties include both built-in properties (such as title,
    author, subject) and custom properties. The interface allows reading and writing
    properties of various data types.
    """
    @property
    @abc.abstractmethod
    def IsBuiltIn(self)->bool:
        """Gets whether the property is a built-in document property.
        
        Returns:
            bool: True if the property is built-in, False if it is a custom property.
        """
        pass


    @property

    @abc.abstractmethod
    def PropertyId(self)->'BuiltInPropertyType':
        """Gets the ID of the built-in property.
        
        Returns:
            BuiltInPropertyType: The ID of the built-in property.
        """
        pass


    @property

    @abc.abstractmethod
    def Name(self)->str:
        """Gets the name of the document property.
        
        Returns:
            str: The name of the document property.
        """
        pass


    @property

    @abc.abstractmethod
    def Value(self)->'SpireObject':
        """Gets the value of the document property as a generic object.
        
        Returns:
            SpireObject: The value of the document property.
        """
        pass


    @Value.setter
    @abc.abstractmethod
    def Value(self, value:'SpireObject'):
        """Sets the value of the document property.
        
        Args:
            value (SpireObject): The value to set for the document property.
        """
        pass


    @property
    @abc.abstractmethod
    def Boolean(self)->bool:
        """Gets the value of the document property as a boolean.
        
        Returns:
            bool: The boolean value of the document property.
        """
        pass


    @Boolean.setter
    @abc.abstractmethod
    def Boolean(self, value:bool):
        """Sets the value of the document property as a boolean.
        
        Args:
            value (bool): The boolean value to set.
        """
        pass


    @property
    @abc.abstractmethod
    def Integer(self)->int:
        """Gets the value of the document property as an integer.
        
        Returns:
            int: The integer value of the document property.
        """
        pass


    @Integer.setter
    @abc.abstractmethod
    def Integer(self, value:int):
        """Sets the value of the document property as an integer.
        
        Args:
            value (int): The integer value to set.
        """
        pass


    @property
    @abc.abstractmethod
    def Int32(self)->int:
        """Gets the value of the document property as a 32-bit integer.
        
        Returns:
            int: The 32-bit integer value of the document property.
        """
        pass


    @Int32.setter
    @abc.abstractmethod
    def Int32(self, value:int):
        """Sets the value of the document property as a 32-bit integer.
        
        Args:
            value (int): The 32-bit integer value to set.
        """
        pass


    @property
    @abc.abstractmethod
    def Double(self)->float:
        """Gets the value of the document property as a double-precision floating-point number.
        
        Returns:
            float: The double-precision floating-point value of the document property.
        """
        pass


    @Double.setter
    @abc.abstractmethod
    def Double(self, value:float):
        """Sets the value of the document property as a double-precision floating-point number.
        
        Args:
            value (float): The double-precision floating-point value to set.
        """
        pass


    @property

    @abc.abstractmethod
    def Text(self)->str:
        """Gets the value of the document property as a text string.
        
        Returns:
            str: The text string value of the document property.
        """
        pass


    @Text.setter
    @abc.abstractmethod
    def Text(self, value:str):
        """Sets the value of the document property as a text string.
        
        Args:
            value (str): The text string value to set.
        """
        pass


    @property

    @abc.abstractmethod
    def DateTime(self)->'DateTime':
        """Gets the value of the document property as a date and time.
        
        Returns:
            DateTime: The date and time value of the document property.
        """
        pass


    @DateTime.setter
    @abc.abstractmethod
    def DateTime(self, value:'DateTime'):
        """Sets the value of the document property as a date and time.
        
        Args:
            value (DateTime): The date and time value to set.
        """
        pass


    @property

    @abc.abstractmethod
    def TimeSpan(self)->'TimeSpan':
        """Gets the value of the document property as a time span.
        
        Returns:
            TimeSpan: The time span value of the document property.
        """
        pass


    @TimeSpan.setter
    @abc.abstractmethod
    def TimeSpan(self, value:'TimeSpan'):
        """Sets the value of the document property as a time span.
        
        Args:
            value (TimeSpan): The time span value to set.
        """
        pass


    @property

    @abc.abstractmethod
    def LinkSource(self)->str:
        """Gets the source of the linked property.
        
        Returns:
            str: The source of the linked property.
        """
        pass


    @LinkSource.setter
    @abc.abstractmethod
    def LinkSource(self, value:str):
        """Sets the source of the linked property.
        
        Args:
            value (str): The source of the linked property.
        """
        pass


    @property
    @abc.abstractmethod
    def LinkToContent(self)->bool:
        """Gets whether the property is linked to content.
        
        Returns:
            bool: True if the property is linked to content, otherwise False.
        """
        pass


    @LinkToContent.setter
    @abc.abstractmethod
    def LinkToContent(self, value:bool):
        """Sets whether the property is linked to content.
        
        Args:
            value (bool): True to link the property to content, otherwise False.
        """
        pass


