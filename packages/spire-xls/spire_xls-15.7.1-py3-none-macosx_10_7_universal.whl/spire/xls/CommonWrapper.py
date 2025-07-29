from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class CommonWrapper (  SpireObject, IOptimizedUpdate, ICloneParent) :
    """Represents a common wrapper for Excel objects.
    
    This class extends SpireObject and implements IOptimizedUpdate and ICloneParent interfaces,
    providing basic functionality for Excel objects, including batch update operations and
    cloning capabilities. It serves as a base class for more specialized wrapper classes.
    """
    def BeginUpdate(self):
        """Begins a batch update operation.
        
        This method marks the beginning of a series of changes to the object properties.
        Changes made between BeginUpdate and EndUpdate are applied together for better performance.
        """
        GetDllLibXls().CommonWrapper_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().CommonWrapper_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """Ends a batch update operation.
        
        This method completes the batch update started with BeginUpdate and
        applies all pending changes to the object properties.
        """
        GetDllLibXls().CommonWrapper_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().CommonWrapper_EndUpdate, self.Ptr)


    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """Creates a copy of the current object with the specified parent.
        
        This method creates a new object with the same properties as the current object,
        but with a different parent object.
        
        Args:
            parent (SpireObject): The parent object for the cloned object.
            
        Returns:
            SpireObject: A new object that is a copy of the current object.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().CommonWrapper_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().CommonWrapper_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CommonWrapper_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


