from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IDigitalSignature (abc.ABC) :
    """Digital signature interface.
    
    This interface represents a digital signature in an Excel workbook.
    Digital signatures are used to authenticate the identity of the document creator
    and ensure that the document has not been altered since it was signed.
    The interface provides access to signature properties such as comments, sign time,
    and validity status.
    
    Note: The Certificate property is currently commented out, which may indicate that
    functionality is not yet implemented or is in development.
    """
#    @property
#
#    @abc.abstractmethod
#    def Certificate(self)->'X509Certificate2':
#        """
#    <summary>
#        Certificate object that was used to sign.
#    </summary>
#        """
#        pass
#


#    @Certificate.setter
#    @abc.abstractmethod
#    def Certificate(self, value:'X509Certificate2'):
#        """
#
#        """
#        pass
#


    @property

    @abc.abstractmethod
    def Comments(self)->str:
        """Gets the comments associated with the digital signature.
        
        Returns:
            str: The comments associated with the signature.
        """
        pass


    @Comments.setter
    @abc.abstractmethod
    def Comments(self, value:str):
        """Sets the comments associated with the digital signature.
        
        Args:
            value (str): The comments to associate with the signature.
        """
        pass


    @property

    @abc.abstractmethod
    def SignTime(self)->'DateTime':
        """Gets the time when the document was signed.
        
        Returns:
            DateTime: The time when the document was signed.
        """
        pass


    @SignTime.setter
    @abc.abstractmethod
    def SignTime(self, value:'DateTime'):
        """Sets the time when the document was signed.
        
        Args:
            value (DateTime): The time when the document was signed.
        """
        pass


    @property
    @abc.abstractmethod
    def IsValid(self)->bool:
        """Gets whether this digital signature is valid.
        
        Returns:
            bool: True if the digital signature is valid, otherwise False.
        """
        pass


    @IsValid.setter
    @abc.abstractmethod
    def IsValid(self, value:bool):
        """Sets whether this digital signature is valid.
        
        Args:
            value (bool): True to mark the signature as valid, otherwise False.
        """
        pass


