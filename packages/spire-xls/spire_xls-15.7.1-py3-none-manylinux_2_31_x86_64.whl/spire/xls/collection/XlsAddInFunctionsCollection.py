from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsAddInFunctionsCollection (  CollectionBase[XlsAddInFunction],IAddInFunctions) :
    """

    """

    def get_Item(self ,index:int)->'IAddInFunction':
        """

        """
        
        GetDllLibXls().XlsAddInFunctionsCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsAddInFunctionsCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsAddInFunctionsCollection_get_Item, self.Ptr, index)
        ret = None if intPtr==None else XlsAddInFunction(intPtr)
        return ret


    @dispatch

    def Add(self ,fileName:str,functionName:str)->int:
        """
        Adds new add-in function.

        Args:
            fileName: File name.
            functionName: Function name.

        Returns:
            Index of the new function.

        """
        
        GetDllLibXls().XlsAddInFunctionsCollection_Add.argtypes=[c_void_p ,c_void_p,c_void_p]
        GetDllLibXls().XlsAddInFunctionsCollection_Add.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsAddInFunctionsCollection_Add, self.Ptr, fileName,functionName)
        return ret

    @dispatch

    def Add(self ,functionName:str)->int:
        """
        Adds new add-in function.

        Args:
            functionName: Function to add.

        Returns:
            Index of the added function.

        """
        
        GetDllLibXls().XlsAddInFunctionsCollection_AddF.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsAddInFunctionsCollection_AddF.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsAddInFunctionsCollection_AddF, self.Ptr, functionName)
        return ret

    @dispatch

    def Add(self ,bookIndex:int,nameIndex:int):
        """

        """
        
        GetDllLibXls().XlsAddInFunctionsCollection_AddBN.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsAddInFunctionsCollection_AddBN, self.Ptr, bookIndex,nameIndex)


    def RemoveAt(self ,index:int):
        """
        Removes add-in function with specified index.

        Args:
            index: Item index to remove.

        """
        
        GetDllLibXls().XlsAddInFunctionsCollection_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsAddInFunctionsCollection_RemoveAt, self.Ptr, index)


    def Contains(self ,workbookName:str)->bool:
        """

        """
        
        GetDllLibXls().XlsAddInFunctionsCollection_Contains.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsAddInFunctionsCollection_Contains.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsAddInFunctionsCollection_Contains, self.Ptr, workbookName)
        return ret


    def CopyFrom(self ,addinFunctions:'XlsAddInFunctionsCollection'):
        """

        """
        intPtraddinFunctions:c_void_p = addinFunctions.Ptr

        GetDllLibXls().XlsAddInFunctionsCollection_CopyFrom.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsAddInFunctionsCollection_CopyFrom, self.Ptr, intPtraddinFunctions)

