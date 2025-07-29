from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class HPageBreaksCollection (  XlsHPageBreaksCollection) :
    """

    """
    @dispatch

    def get_Item(self ,index:int)->HPageBreak:
        """

        """
        
        GetDllLibXls().HPageBreaksCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().HPageBreaksCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().HPageBreaksCollection_get_Item, self.Ptr, index)
        ret = None if intPtr==None else HPageBreak(intPtr)
        return ret


    @dispatch

    def get_Item(self ,location:CellRange)->HPageBreak:
        """
        Gets page break object item.

        """
        intPtrlocation:c_void_p = location.Ptr

        GetDllLibXls().HPageBreaksCollection_get_ItemL.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().HPageBreaksCollection_get_ItemL.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().HPageBreaksCollection_get_ItemL, self.Ptr, intPtrlocation)
        ret = None if intPtr==None else HPageBreak(intPtr)
        return ret



    def Add(self ,range:'CellRange')->'HPageBreak':
        """
        Adds a horizontal page break.

        Args:
            location: range which new page break inserted.

        Returns:
            HPageBreak added.

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().HPageBreaksCollection_Add.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().HPageBreaksCollection_Add.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().HPageBreaksCollection_Add, self.Ptr, intPtrrange)
        ret = None if intPtr==None else HPageBreak(intPtr)
        return ret



    def Remove(self ,range:'CellRange'):
        """

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().HPageBreaksCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().HPageBreaksCollection_Remove, self.Ptr, intPtrrange)

    @dispatch

    def GetPageBreak(self ,rowIndex:int)->HPageBreak:
        """
        Returns page break at the specified row.

        Args:
            rowIndex: Row index.

        Returns:
            Page break object.

        """
        
        GetDllLibXls().HPageBreaksCollection_GetPageBreak.argtypes=[c_void_p ,c_int]
        GetDllLibXls().HPageBreaksCollection_GetPageBreak.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().HPageBreaksCollection_GetPageBreak, self.Ptr, rowIndex)
        ret = None if intPtr==None else HPageBreak(intPtr)
        return ret


    @dispatch

    def GetPageBreak(self ,range:CellRange)->HPageBreak:
        """
        Returns page break at the specified range.

        Args:
            range: Range object.

        Returns:
            Page break object.

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().HPageBreaksCollection_GetPageBreakR.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().HPageBreaksCollection_GetPageBreakR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().HPageBreaksCollection_GetPageBreakR, self.Ptr, intPtrrange)
        ret = None if intPtr==None else HPageBreak(intPtr)
        return ret


