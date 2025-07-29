from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class VPageBreaksCollection (  XlsVPageBreaksCollection) :
    """

    """

    def get_Item(self ,index:int)->'VPageBreak':
        """
        Gets a object from collection

        """
        
        GetDllLibXls().VPageBreaksCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().VPageBreaksCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().VPageBreaksCollection_get_Item, self.Ptr, index)
        ret = None if intPtr==None else VPageBreak(intPtr)
        return ret



    def Add(self ,range:'CellRange')->'VPageBreak':
        """
        Adds a horizontal page break.

        Args:
            range: Range which a page break need inserted.

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().VPageBreaksCollection_Add.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().VPageBreaksCollection_Add.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().VPageBreaksCollection_Add, self.Ptr, intPtrrange)
        ret = None if intPtr==None else VPageBreak(intPtr)
        return ret



    def Remove(self ,range:'CellRange'):
        """
        Remove page break with specified range.

        Args:
            range: range object.

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().VPageBreaksCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().VPageBreaksCollection_Remove, self.Ptr, intPtrrange)

    @dispatch

    def GetPageBreak(self ,columnIndex:int)->VPageBreak:
        """
        Returns page break at the specified Column index.

        Args:
            rowIndex: Column index.

        """
        
        GetDllLibXls().VPageBreaksCollection_GetPageBreak.argtypes=[c_void_p ,c_int]
        GetDllLibXls().VPageBreaksCollection_GetPageBreak.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().VPageBreaksCollection_GetPageBreak, self.Ptr, columnIndex)
        ret = None if intPtr==None else VPageBreak(intPtr)
        return ret


    @dispatch

    def GetPageBreak(self ,range:CellRange)->VPageBreak:
        """
        Returns page break at the specified range.

        Args:
            range: range object.

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().VPageBreaksCollection_GetPageBreakR.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().VPageBreaksCollection_GetPageBreakR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().VPageBreaksCollection_GetPageBreakR, self.Ptr, intPtrrange)
        ret = None if intPtr==None else VPageBreak(intPtr)
        return ret


