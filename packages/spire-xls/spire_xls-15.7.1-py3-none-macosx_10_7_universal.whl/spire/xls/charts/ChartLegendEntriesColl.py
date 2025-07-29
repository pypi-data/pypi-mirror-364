from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ChartLegendEntriesColl (  XlsObject, IChartLegendEntries) :
    """
    Represents a collection of legend entries in a chart legend.
    Provides methods to add, remove, and manage legend entries.
    """
    @property
    def Count(self)->int:
        """
        Gets the number of legend entries in the collection.

        Returns:
            int: The number of legend entries.
        """
        GetDllLibXls().ChartLegendEntriesColl_get_Count.argtypes=[c_void_p]
        GetDllLibXls().ChartLegendEntriesColl_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartLegendEntriesColl_get_Count, self.Ptr)
        return ret


    def get_Item(self ,iIndex:int)->'IChartLegendEntry':
        """
        Gets the legend entry at the specified index.

        Args:
            iIndex (int): The zero-based index of the legend entry to get.
        Returns:
            IChartLegendEntry: The legend entry at the specified index.
        """
        
        GetDllLibXls().ChartLegendEntriesColl_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().ChartLegendEntriesColl_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartLegendEntriesColl_get_Item, self.Ptr, iIndex)
        ret = None if intPtr==None else XlsChartLegendEntry(intPtr)
        return ret


    @dispatch

    def Add(self ,iIndex:int)->XlsChartLegendEntry:
        """
        Adds a new legend entry at the specified index.

        Args:
            iIndex (int): The index at which to add the new legend entry.
        Returns:
            XlsChartLegendEntry: The newly added legend entry.
        """
        
        GetDllLibXls().ChartLegendEntriesColl_Add.argtypes=[c_void_p ,c_int]
        GetDllLibXls().ChartLegendEntriesColl_Add.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartLegendEntriesColl_Add, self.Ptr, iIndex)
        ret = None if intPtr==None else XlsChartLegendEntry(intPtr)
        return ret


    @dispatch

    def Add(self ,iIndex:int,entry:XlsChartLegendEntry)->XlsChartLegendEntry:
        """
        Adds an existing legend entry to the collection at the specified index.

        Args:
            iIndex (int): The index at which to add the legend entry.
            entry (XlsChartLegendEntry): The legend entry to add.
        Returns:
            XlsChartLegendEntry: The added legend entry.
        """
        intPtrentry:c_void_p = entry.Ptr

        GetDllLibXls().ChartLegendEntriesColl_AddIE.argtypes=[c_void_p ,c_int,c_void_p]
        GetDllLibXls().ChartLegendEntriesColl_AddIE.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartLegendEntriesColl_AddIE, self.Ptr, iIndex,intPtrentry)
        ret = None if intPtr==None else XlsChartLegendEntry(intPtr)
        return ret



    def Contains(self ,iIndex:int)->bool:
        """
        Determines whether the collection contains a legend entry at the specified index.

        Args:
            iIndex (int): The index to check for a legend entry.
        Returns:
            bool: True if the collection contains a legend entry at the specified index; otherwise, False.
        """
        
        GetDllLibXls().ChartLegendEntriesColl_Contains.argtypes=[c_void_p ,c_int]
        GetDllLibXls().ChartLegendEntriesColl_Contains.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartLegendEntriesColl_Contains, self.Ptr, iIndex)
        return ret


    def CanDelete(self ,iIndex:int)->bool:
        """
        Determines whether the legend entry at the specified index can be deleted.

        Args:
            iIndex (int): The index of the legend entry to check.
        Returns:
            bool: True if the legend entry can be deleted; otherwise, False.
        """
        
        GetDllLibXls().ChartLegendEntriesColl_CanDelete.argtypes=[c_void_p ,c_int]
        GetDllLibXls().ChartLegendEntriesColl_CanDelete.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartLegendEntriesColl_CanDelete, self.Ptr, iIndex)
        return ret


    def Remove(self ,iIndex:int):
        """
        Removes the legend entry at the specified index from the collection.

        Args:
            iIndex (int): The index of the legend entry to remove.
        """
        
        GetDllLibXls().ChartLegendEntriesColl_Remove.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().ChartLegendEntriesColl_Remove, self.Ptr, iIndex)

    def Clear(self):
        """
        Removes all legend entries from the collection.
        """
        GetDllLibXls().ChartLegendEntriesColl_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().ChartLegendEntriesColl_Clear, self.Ptr)

#
#    def Clone(self ,parent:'SpireObject',dicIndexes:'Dictionary2',dicNewSheetNames:'Dictionary2')->'ChartLegendEntriesColl':
#        """
#
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrdicIndexes:c_void_p = dicIndexes.Ptr
#        intPtrdicNewSheetNames:c_void_p = dicNewSheetNames.Ptr
#
#        GetDllLibXls().ChartLegendEntriesColl_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p]
#        GetDllLibXls().ChartLegendEntriesColl_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().ChartLegendEntriesColl_Clone, self.Ptr, intPtrparent,intPtrdicIndexes,intPtrdicNewSheetNames)
#        ret = None if intPtr==None else ChartLegendEntriesColl(intPtr)
#        return ret
#



    def UpdateEntries(self ,entryIndex:int,value:int):
        """
        Updates the value of the legend entry at the specified index.

        Args:
            entryIndex (int): The index of the legend entry to update.
            value (int): The new value to set for the legend entry.
        """
        
        GetDllLibXls().ChartLegendEntriesColl_UpdateEntries.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().ChartLegendEntriesColl_UpdateEntries, self.Ptr, entryIndex,value)

