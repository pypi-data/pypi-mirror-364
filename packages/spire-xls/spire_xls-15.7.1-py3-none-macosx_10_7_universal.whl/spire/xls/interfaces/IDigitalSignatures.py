from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IDigitalSignatures (  abc.ABC) :
    """Digital signatures collection interface.
    
    This interface represents a collection of digital signatures in an Excel workbook.
    Digital signatures are used to authenticate the identity of the document creator
    and ensure that the document has not been altered since it was signed.
    
    Note: The Add method is currently commented out, which may indicate that
    functionality is not yet implemented or is in development.
    """
#
#    @abc.abstractmethod
#    def Add(self ,certificate:'X509Certificate2',comments:str,signTime:'DateTime')->'IDigitalSignature':
#        """
#    <summary>
#        create a signature and add to DigitalSignatureCollection.
#    </summary>
#    <param name="certificate">Certificate object that was used to sign</param>
#    <param name="comments">Signature Comments</param>
#    <param name="signTime">Sign Time</param>
#        """
#        pass
#


