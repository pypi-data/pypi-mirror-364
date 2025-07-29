from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsStylesCollection (  CollectionBase[CellStyleObject], IStyles) :
    """

    """

    def Contains(self ,name:str)->bool:
        """
        Check collection contains style with specified name.

        Args:
            name: Style name

        """
        
        GetDllLibXls().XlsStylesCollection_Contains.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsStylesCollection_Contains.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsStylesCollection_Contains, self.Ptr, name)
        return ret


    def Remove(self ,styleName:str):
        """
        Removes style from the colleciton.

        Args:
            styleName: Style to remove.

        """
        
        GetDllLibXls().XlsStylesCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsStylesCollection_Remove, self.Ptr, styleName)


    def get_Item(self ,name:str)->'IStyle':
        """

        """
        
        GetDllLibXls().XlsStylesCollection_get_Item.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsStylesCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsStylesCollection_get_Item, self.Ptr, name)
        ret = None if intPtr==None else CellStyle(intPtr)
        return ret



    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """

        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsStylesCollection_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsStylesCollection_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsStylesCollection_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    def UpdateStyleRecords(self):
        """

        """
        GetDllLibXls().XlsStylesCollection_UpdateStyleRecords.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsStylesCollection_UpdateStyleRecords, self.Ptr)

