from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ConditionalFormats (  CondFormatCollectionWrapper) :
    """
    Contains a collection of conditional formats for a worksheet or range.
    """

    def get_Item(self ,index:int)->'ConditionalFormatWrapper':
        """
        Gets the conditional format at the specified index.

        Args:
            index (int): The index of the conditional format.
        Returns:
            ConditionalFormatWrapper: The conditional format at the specified index.
        """
        
        GetDllLibXls().ConditionalFormats_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().ConditionalFormats_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormats_get_Item, self.Ptr, index)
        ret = None if intPtr==None else ConditionalFormatWrapper(intPtr)
        return ret


    @dispatch
    def AddCondition(self)->ConditionalFormatWrapper:
        """
        Adds a new conditional format to the collection.

        Returns:
            ConditionalFormatWrapper: The newly added conditional format.
        """
        GetDllLibXls().ConditionalFormats_AddCondition.argtypes=[c_void_p]
        GetDllLibXls().ConditionalFormats_AddCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormats_AddCondition, self.Ptr)
        ret = None if intPtr==None else ConditionalFormatWrapper(intPtr)
        return ret


    @dispatch
    def AddCondition(self ,type:ConditionalFormatType,stopIsTrue:bool)->ConditionalFormatWrapper:
        """
        Adds a new conditional format to the collection with the specified type and stopIfTrue flag.

        Args:
            type (ConditionalFormatType): The type of the conditional format.
            stopIsTrue (bool): Whether to stop if the condition is true.
        Returns:
            ConditionalFormatWrapper: The newly added conditional format.
        """
        enumtype:c_int = type.value

        GetDllLibXls().ConditionalFormats_AddConditionTS.argtypes=[c_void_p ,c_int,c_bool]
        GetDllLibXls().ConditionalFormats_AddConditionTS.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ConditionalFormats_AddConditionTS, self.Ptr, enumtype,stopIsTrue)
        ret = None if intPtr==None else ConditionalFormatWrapper(intPtr)
        return ret


