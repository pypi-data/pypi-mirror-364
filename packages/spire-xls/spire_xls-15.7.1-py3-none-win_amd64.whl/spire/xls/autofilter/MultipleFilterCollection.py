from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class MultipleFilterCollection (SpireObject) :
    """

    """

    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator for the collection.

        Returns:
            IEnumerator: The enumerator object.
        """
        GetDllLibXls().MultipleFilterCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibXls().MultipleFilterCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().MultipleFilterCollection_GetEnumerator, self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    def Clear(self):
        """
        Clears all filters from the collection.
        """
        GetDllLibXls().MultipleFilterCollection_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().MultipleFilterCollection_Clear, self.Ptr)

    @property
    def Capacity(self)->int:
        """
        Gets or sets the capacity of the collection.

        Returns:
            int: The capacity of the collection.
        """
        GetDllLibXls().MultipleFilterCollection_get_Capacity.argtypes=[c_void_p]
        GetDllLibXls().MultipleFilterCollection_get_Capacity.restype=c_int
        ret = CallCFunction(GetDllLibXls().MultipleFilterCollection_get_Capacity, self.Ptr)
        return ret

    @Capacity.setter
    def Capacity(self, value:int):
        """
        Sets the capacity of the collection.

        Args:
            value (int): The new capacity value.
        """
        GetDllLibXls().MultipleFilterCollection_set_Capacity.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().MultipleFilterCollection_set_Capacity, self.Ptr, value)

    @property
    def Count(self)->int:
        """
        Gets the number of filters in the collection.

        Returns:
            int: The number of filters.
        """
        GetDllLibXls().MultipleFilterCollection_get_Count.argtypes=[c_void_p]
        GetDllLibXls().MultipleFilterCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibXls().MultipleFilterCollection_get_Count, self.Ptr)
        return ret


    def RemoveDateFilter(self ,type:'DateTimeGroupingType',year:int,month:int,day:int,hour:int,minute:int,second:int):
        """
        Removes a date filter from the collection.

        Args:
            type (DateTimeGroupingType): The grouping type.
            year (int): The year value.
            month (int): The month value.
            day (int): The day value.
            hour (int): The hour value.
            minute (int): The minute value.
            second (int): The second value.
        """
        enumtype:c_int = type.value

        GetDllLibXls().MultipleFilterCollection_RemoveDateFilter.argtypes=[c_void_p ,c_int,c_int,c_int,c_int,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().MultipleFilterCollection_RemoveDateFilter, self.Ptr, enumtype,year,month,day,hour,minute,second)


    def RemoveAt(self ,index:int):
        """
        Removes a filter at the specified index.

        Args:
            index (int): The index of the filter to remove.
        """
        
        GetDllLibXls().MultipleFilterCollection_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().MultipleFilterCollection_RemoveAt, self.Ptr, index)


    def RemoveFilter(self ,filter:str):
        """
        Removes a filter by its string value.

        Args:
            filter (str): The filter value to remove.
        """
        
        GetDllLibXls().MultipleFilterCollection_RemoveFilter.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().MultipleFilterCollection_RemoveFilter, self.Ptr, filter)

    @property
    def MatchBlank(self)->bool:
        """
        Gets or sets whether to match blank values in the filter.

        Returns:
            bool: True if matching blank values, otherwise False.
        """
        GetDllLibXls().MultipleFilterCollection_get_MatchBlank.argtypes=[c_void_p]
        GetDllLibXls().MultipleFilterCollection_get_MatchBlank.restype=c_bool
        ret = CallCFunction(GetDllLibXls().MultipleFilterCollection_get_MatchBlank, self.Ptr)
        return ret

    @MatchBlank.setter
    def MatchBlank(self, value:bool):
        """
        Sets whether to match blank values in the filter.

        Args:
            value (bool): True to match blank values, otherwise False.
        """
        GetDllLibXls().MultipleFilterCollection_set_MatchBlank.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().MultipleFilterCollection_set_MatchBlank, self.Ptr, value)


    def get_Item(self ,index:int)->'SpireObject':
        """
        Gets the filter at the specified index.

        Args:
            index (int): The index of the filter.
        Returns:
            SpireObject: The filter object at the specified index.
        """
        
        GetDllLibXls().MultipleFilterCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().MultipleFilterCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().MultipleFilterCollection_get_Item, self.Ptr, index)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def GetByIndex(self ,index:int)->'SpireObject':
        """
        Gets the filter by index.

        Args:
            index (int): The index of the filter.
        Returns:
            SpireObject: The filter object at the specified index.
        """
        
        GetDllLibXls().MultipleFilterCollection_GetByIndex.argtypes=[c_void_p ,c_int]
        GetDllLibXls().MultipleFilterCollection_GetByIndex.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().MultipleFilterCollection_GetByIndex, self.Ptr, index)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @dispatch

    def Add(self ,filter:str):
        """
        Adds a filter to the collection by string value.

        Args:
            filter (str): The filter value to add.
        """
        
        GetDllLibXls().MultipleFilterCollection_Add.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().MultipleFilterCollection_Add, self.Ptr, filter)

    @dispatch

    def Add(self ,filter:DateTimeGroupItem):
        """
        Adds a filter to the collection by DateTimeGroupItem.

        Args:
            filter (DateTimeGroupItem): The filter item to add.
        """
        intPtrfilter:c_void_p = filter.Ptr

        GetDllLibXls().MultipleFilterCollection_AddF.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().MultipleFilterCollection_AddF, self.Ptr, intPtrfilter)

    @dispatch

    def Add(self ,type:DateTimeGroupingType,year:int,month:int,day:int):
        """
        Adds a filter to the collection by date components.

        Args:
            type (DateTimeGroupingType): The grouping type.
            year (int): The year value.
            month (int): The month value.
            day (int): The day value.
        """
        enumtype:c_int = type.value

        GetDllLibXls().MultipleFilterCollection_AddTYMD.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().MultipleFilterCollection_AddTYMD, self.Ptr, enumtype,year,month,day)

