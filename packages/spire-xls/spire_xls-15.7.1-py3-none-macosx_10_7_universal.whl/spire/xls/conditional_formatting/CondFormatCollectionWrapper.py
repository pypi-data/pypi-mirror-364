from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class CondFormatCollectionWrapper (  CommonWrapper, IConditionalFormats) :
    """
    Represents a collection of conditional formats in a worksheet or range.
    """

    def GetEnumerator(self)->'IEnumerator':
        """
        Returns an enumerator that iterates through the collection.

        Returns:
            IEnumerator: An enumerator for the collection.
        """
        GetDllLibXls().CondFormatCollectionWrapper_GetEnumerator.argtypes=[c_void_p]
        GetDllLibXls().CondFormatCollectionWrapper_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CondFormatCollectionWrapper_GetEnumerator, self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    def BeginUpdate(self):
        """
        Begins batch update of the collection.
        """
        GetDllLibXls().CondFormatCollectionWrapper_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().CondFormatCollectionWrapper_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """
        Ends batch update of the collection.
        """
        GetDllLibXls().CondFormatCollectionWrapper_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().CondFormatCollectionWrapper_EndUpdate, self.Ptr)

    @property
    def Count(self)->int:
        """
        Gets the number of conditional formats in the collection.

        Returns:
            int: The number of conditional formats.
        """
        GetDllLibXls().CondFormatCollectionWrapper_get_Count.argtypes=[c_void_p]
        GetDllLibXls().CondFormatCollectionWrapper_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibXls().CondFormatCollectionWrapper_get_Count, self.Ptr)
        return ret


    def get_Item(self ,index:int)->'IConditionalFormat':
        """
        Gets the conditional format at the specified index.

        Args:
            index (int): The index of the conditional format.
        Returns:
            IConditionalFormat: The conditional format at the specified index.
        """
        
        GetDllLibXls().CondFormatCollectionWrapper_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().CondFormatCollectionWrapper_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CondFormatCollectionWrapper_get_Item, self.Ptr, index)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def AddCondition(self)->'IConditionalFormat':
        """
        Adds a new conditional format to the collection.

        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        GetDllLibXls().CondFormatCollectionWrapper_AddCondition.argtypes=[c_void_p]
        GetDllLibXls().CondFormatCollectionWrapper_AddCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CondFormatCollectionWrapper_AddCondition, self.Ptr)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret


    def Remove(self):
        """
        Removes all conditional formats from the collection.
        """
        GetDllLibXls().CondFormatCollectionWrapper_Remove.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().CondFormatCollectionWrapper_Remove, self.Ptr)


    def RemoveAt(self ,index:int):
        """
        Removes the conditional format at the specified index.

        Args:
            index (int): The index of the conditional format to remove.
        """
        
        GetDllLibXls().CondFormatCollectionWrapper_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().CondFormatCollectionWrapper_RemoveAt, self.Ptr, index)

    @property

    def Parent(self)->'SpireObject':
        """
        Gets the parent object of the collection.

        Returns:
            SpireObject: The parent object.
        """
        GetDllLibXls().CondFormatCollectionWrapper_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().CondFormatCollectionWrapper_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CondFormatCollectionWrapper_get_Parent, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def GetCondition(self ,iCondition:int)->'XlsConditionalFormat':
        """
        Gets the conditional format at the specified condition index.

        Args:
            iCondition (int): The condition index.
        Returns:
            XlsConditionalFormat: The conditional format at the specified index.
        """
        
        GetDllLibXls().CondFormatCollectionWrapper_GetCondition.argtypes=[c_void_p ,c_int]
        GetDllLibXls().CondFormatCollectionWrapper_GetCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CondFormatCollectionWrapper_GetCondition, self.Ptr, iCondition)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def AddRange(self ,range:'IXLSRange'):
        """
        Adds a range to the collection for conditional formatting.

        Args:
            range (IXLSRange): The range to add.
        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().CondFormatCollectionWrapper_AddRange.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().CondFormatCollectionWrapper_AddRange, self.Ptr, intPtrrange)

