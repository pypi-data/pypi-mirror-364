from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class SparklineGroupCollection (SpireObject) :
    """
    The SparklineGroupCollection represents the collection of SparklineGroup objects.

    """

    def get_Item(self ,index:int)->'SparklineGroup':
        """

        """
        
        GetDllLibXls().SparklineGroupCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().SparklineGroupCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().SparklineGroupCollection_get_Item, self.Ptr, index)
        ret = None if intPtr==None else SparklineGroup(intPtr)
        return ret



    def Clear(self ,sparklineGroup:'SparklineGroup'):
        """
        Clears the sparkline group.

        """
        intPtrsparklineGroup:c_void_p = sparklineGroup.Ptr

        GetDllLibXls().SparklineGroupCollection_Clear.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().SparklineGroupCollection_Clear, self.Ptr, intPtrsparklineGroup)

    @dispatch

    def AddGroup(self ,sparklineType:SparklineType)->SparklineGroup:
        """
        Adds the SparklineGroup instance.

        """
        enumsparklineType:c_int = sparklineType.value

        GetDllLibXls().SparklineGroupCollection_AddGroup.argtypes=[c_void_p ,c_int]
        GetDllLibXls().SparklineGroupCollection_AddGroup.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().SparklineGroupCollection_AddGroup, self.Ptr, enumsparklineType)
        ret = None if intPtr==None else SparklineGroup(intPtr)
        return ret


    @dispatch

    def AddGroup(self)->SparklineGroup:
        """
        Adds the SparklineGroup instance.

        """
        GetDllLibXls().SparklineGroupCollection_AddGroup1.argtypes=[c_void_p]
        GetDllLibXls().SparklineGroupCollection_AddGroup1.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().SparklineGroupCollection_AddGroup1, self.Ptr)
        ret = None if intPtr==None else SparklineGroup(intPtr)
        return ret


