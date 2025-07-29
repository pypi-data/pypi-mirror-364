from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IOleObjects (  CollectionBase[IOleObject]) :
    """Collection of OLE objects in an Excel worksheet.
    
    This interface represents a collection of OLE (Object Linking and Embedding) objects
    within an Excel worksheet. It provides methods to access existing OLE objects and
    add new ones to the worksheet.
    
    Inherits from:
        CollectionBase[IOleObject]: Base collection class for OLE objects
    """

    def Add(self ,fileName:str,stream:'Stream',linkType:'OleLinkType')->'IOleObject':
        """Adds a new OLE object to the collection.
        
        This method creates a new OLE object in the worksheet using the specified file
        and stream data, with the specified linking behavior.
        
        Args:
            fileName (str): The name of the file associated with the OLE object.
            stream (Stream): The stream containing the binary data of the OLE object.
            linkType (OleLinkType): The type of linking to use for the OLE object.
                This determines whether the object is embedded or linked.
        
        Returns:
            IOleObject: The newly created OLE object.
        """
        intPtrimage:c_void_p = stream.Ptr
        enumlinkType:c_int = linkType.value

        GetDllLibXls().IOleObjects_Add.argtypes=[c_void_p ,c_void_p,c_void_p,c_int]
        GetDllLibXls().IOleObjects_Add.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IOleObjects_Add, self.Ptr, fileName,intPtrimage,enumlinkType)
        ret = None if intPtr==None else IOleObject(intPtr)
        return ret


