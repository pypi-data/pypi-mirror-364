from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsEventArgs (SpireObject) :
    """Class used as message sender on Property value change.
    
    This class provides old and new values which allow user to create advanced logic.
    It can be used to track changes in property values and implement custom behaviors
    based on these changes.
    """
    @property

    def newValue(self)->'SpireObject':
        """Gets the new property value.
        
        Returns:
            SpireObject: The new value of the property after the change.
        """
        GetDllLibXls().XlsEventArgs_get_newValue.argtypes=[c_void_p]
        GetDllLibXls().XlsEventArgs_get_newValue.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsEventArgs_get_newValue, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @property

    def oldValue(self)->'SpireObject':
        """Gets the old property value.
        
        Returns:
            SpireObject: The original value of the property before the change.
        """
        GetDllLibXls().XlsEventArgs_get_oldValue.argtypes=[c_void_p]
        GetDllLibXls().XlsEventArgs_get_oldValue.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsEventArgs_get_oldValue, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @property

    def Name(self)->str:
        """Gets the name of the property.
        
        Returns:
            str: The name of the property that was changed.
        """
        GetDllLibXls().XlsEventArgs_get_Name.argtypes=[c_void_p]
        GetDllLibXls().XlsEventArgs_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsEventArgs_get_Name, self.Ptr))
        return ret


    @property

    def Next(self)->'XlsEventArgs':
        """Gets or sets the next event args in the chain.
        
        If more than one property must be changed on one send message, this property
        allows creating a one-way directed list of property changes.
        
        Returns:
            XlsEventArgs: The next event args in the chain.
        """
        GetDllLibXls().XlsEventArgs_get_Next.argtypes=[c_void_p]
        GetDllLibXls().XlsEventArgs_get_Next.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsEventArgs_get_Next, self.Ptr)
        ret = None if intPtr==None else XlsEventArgs(intPtr)
        return ret


    @Next.setter
    def Next(self, value:'XlsEventArgs'):
        """Sets the next event args in the chain.
        
        Args:
            value (XlsEventArgs): The next event args to add to the chain.
        """
        GetDllLibXls().XlsEventArgs_set_Next.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsEventArgs_set_Next, self.Ptr, value.Ptr)

    @staticmethod

    def get_Empty()->'XlsEventArgs':
        """Gets an empty XlsEventArgs instance.
        
        Returns:
            XlsEventArgs: An empty instance of XlsEventArgs.
        """
        #GetDllLibXls().XlsEventArgs_get_Empty.argtypes=[]
        GetDllLibXls().XlsEventArgs_get_Empty.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsEventArgs_get_Empty)
        ret = None if intPtr==None else XlsEventArgs(intPtr)
        return ret


