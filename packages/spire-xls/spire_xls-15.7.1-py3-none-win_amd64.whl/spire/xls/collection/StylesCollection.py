from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class StylesCollection (  XlsStylesCollection) :
    """

    """
    @dispatch

    def get_Item(self ,Index:int)->CellStyle:
        """
        gets a object from a collection.

        """
        
        GetDllLibXls().StylesCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().StylesCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().StylesCollection_get_Item, self.Ptr, Index)
        ret = None if intPtr==None else CellStyle(intPtr)
        return ret


    @dispatch

    def get_Item(self ,name:str)->CellStyle:
        """
        gets a object from a collection.

        """
        
        GetDllLibXls().StylesCollection_get_ItemN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().StylesCollection_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().StylesCollection_get_ItemN, self.Ptr, name)
        ret = None if intPtr==None else CellStyle(intPtr)
        return ret


    @dispatch

    def Add(self ,name:str)->CellStyle:
        """
        Adds a new style.

        Args:
            name: Style name

        """
        
        GetDllLibXls().StylesCollection_Add.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().StylesCollection_Add.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().StylesCollection_Add, self.Ptr, name)
        ret = None if intPtr==None else CellStyle(intPtr)
        return ret


    @dispatch

    def Add(self ,style:CellStyle):
        """
        Adds a style.

        Args:
            style: Style to added.

        """
        intPtrstyle:c_void_p = style.Ptr

        GetDllLibXls().StylesCollection_AddS.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().StylesCollection_AddS, self.Ptr, intPtrstyle)


    def Remove(self ,style:'CellStyle'):
        """

        """
        intPtrstyle:c_void_p = style.Ptr

        GetDllLibXls().StylesCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().StylesCollection_Remove, self.Ptr, intPtrstyle)


    def Contains(self ,style:'CellStyle')->'CellStyle':
        """
        Style which is in collection.

        Args:
            style: Style object.

        """
        intPtrstyle:c_void_p = style.Ptr

        GetDllLibXls().StylesCollection_Contains.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().StylesCollection_Contains.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().StylesCollection_Contains, self.Ptr, intPtrstyle)
        ret = None if intPtr==None else CellStyle(intPtr)
        return ret


    @staticmethod

    def Compare(source:'CellStyle',destination:'CellStyle')->bool:
        """

        """
        intPtrsource:c_void_p = source.Ptr
        intPtrdestination:c_void_p = destination.Ptr

        GetDllLibXls().StylesCollection_Compare.argtypes=[ c_void_p,c_void_p]
        GetDllLibXls().StylesCollection_Compare.restype=c_bool
        ret = CallCFunction(GetDllLibXls().StylesCollection_Compare,  intPtrsource,intPtrdestination)
        return ret


    def Replace(self ,style:'CellStyle'):
        """

        """
        intPtrstyle:c_void_p = style.Ptr

        GetDllLibXls().StylesCollection_Replace.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().StylesCollection_Replace, self.Ptr, intPtrstyle)


    def GetDefaultStyle(self ,styleName:str)->'CellStyle':
        """

        """
        
        GetDllLibXls().StylesCollection_GetDefaultStyle.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().StylesCollection_GetDefaultStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().StylesCollection_GetDefaultStyle, self.Ptr, styleName)
        ret = None if intPtr==None else CellStyle(intPtr)
        return ret


