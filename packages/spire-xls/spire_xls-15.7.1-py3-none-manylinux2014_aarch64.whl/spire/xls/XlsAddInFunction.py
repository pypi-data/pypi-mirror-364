from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsAddInFunction (  XlsObject, IAddInFunction, ICloneParent) :
    """Represents an add-in function in Excel.
    
    This class provides properties and methods for manipulating add-in functions,
    including accessing and modifying function name and indexes. It extends XlsObject
    and implements the IAddInFunction and ICloneParent interfaces.
    """
    @property
    def BookIndex(self)->int:
        """Gets or sets the book index of the add-in function.
        
        Returns:
            int: The book index of the add-in function.
        """
        GetDllLibXls().XlsAddInFunction_get_BookIndex.argtypes=[c_void_p]
        GetDllLibXls().XlsAddInFunction_get_BookIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsAddInFunction_get_BookIndex, self.Ptr)
        return ret

    @BookIndex.setter
    def BookIndex(self, value:int):
        """Sets the book index of the add-in function.
        
        Args:
            value (int): The book index to set.
        """
        GetDllLibXls().XlsAddInFunction_set_BookIndex.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsAddInFunction_set_BookIndex, self.Ptr, value)

    @property
    def NameIndex(self)->int:
        """Gets or sets the name index of the add-in function.
        
        Returns:
            int: The name index of the add-in function.
        """
        GetDllLibXls().XlsAddInFunction_get_NameIndex.argtypes=[c_void_p]
        GetDllLibXls().XlsAddInFunction_get_NameIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsAddInFunction_get_NameIndex, self.Ptr)
        return ret

    @NameIndex.setter
    def NameIndex(self, value:int):
        """Sets the name index of the add-in function.
        
        Args:
            value (int): The name index to set.
        """
        GetDllLibXls().XlsAddInFunction_set_NameIndex.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsAddInFunction_set_NameIndex, self.Ptr, value)

    @property

    def Name(self)->str:
        """Gets the name of the add-in function.
        
        Returns:
            str: The name of the add-in function.
        """
        GetDllLibXls().XlsAddInFunction_get_Name.argtypes=[c_void_p]
        GetDllLibXls().XlsAddInFunction_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsAddInFunction_get_Name, self.Ptr))
        return ret



    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """Creates a new object that is a copy of the current instance.

        Args:
            parent (SpireObject): Parent object for a copy of this instance.

        Returns:
            SpireObject: A new object that is a copy of this instance.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsAddInFunction_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsAddInFunction_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsAddInFunction_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


