from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class CellValueChangedEventArgs (SpireObject) :
    """

    """
    @property

    def OldValue(self)->'SpireObject':
        """
        Gets or sets the old value.

        """
        GetDllLibXls().CellValueChangedEventArgs_get_OldValue.argtypes=[c_void_p]
        GetDllLibXls().CellValueChangedEventArgs_get_OldValue.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CellValueChangedEventArgs_get_OldValue, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @OldValue.setter
    def OldValue(self, value:'SpireObject'):
        GetDllLibXls().CellValueChangedEventArgs_set_OldValue.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().CellValueChangedEventArgs_set_OldValue, self.Ptr, value.Ptr)

    @property

    def NewValue(self)->'SpireObject':
        """
        Gets or sets the new value.

        """
        GetDllLibXls().CellValueChangedEventArgs_get_NewValue.argtypes=[c_void_p]
        GetDllLibXls().CellValueChangedEventArgs_get_NewValue.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CellValueChangedEventArgs_get_NewValue, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @NewValue.setter
    def NewValue(self, value:'SpireObject'):
        GetDllLibXls().CellValueChangedEventArgs_set_NewValue.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().CellValueChangedEventArgs_set_NewValue, self.Ptr, value.Ptr)

    @property

    def Range(self)->'IXLSRange':
        """
        Gets or sets the range.

        """
        GetDllLibXls().CellValueChangedEventArgs_get_Range.argtypes=[c_void_p]
        GetDllLibXls().CellValueChangedEventArgs_get_Range.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CellValueChangedEventArgs_get_Range, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @Range.setter
    def Range(self, value:'IXLSRange'):
        GetDllLibXls().CellValueChangedEventArgs_set_Range.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().CellValueChangedEventArgs_set_Range, self.Ptr, value.Ptr)

