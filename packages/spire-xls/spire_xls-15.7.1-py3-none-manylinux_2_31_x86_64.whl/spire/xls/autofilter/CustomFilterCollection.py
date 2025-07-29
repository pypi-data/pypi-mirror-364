from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class CustomFilterCollection (SpireObject) :
    """

    """

    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator for the collection.

        Returns:
            IEnumerator: The enumerator object.
        """
        GetDllLibXls().CustomFilterCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibXls().CustomFilterCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CustomFilterCollection_GetEnumerator, self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    def Clear(self):
        """
        Clears all filters from the collection.
        """
        GetDllLibXls().CustomFilterCollection_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().CustomFilterCollection_Clear, self.Ptr)

    @property
    def Capacity(self)->int:
        """
        Gets or sets the capacity of the collection.

        Returns:
            int: The capacity of the collection.
        """
        GetDllLibXls().CustomFilterCollection_get_Capacity.argtypes=[c_void_p]
        GetDllLibXls().CustomFilterCollection_get_Capacity.restype=c_int
        ret = CallCFunction(GetDllLibXls().CustomFilterCollection_get_Capacity, self.Ptr)
        return ret

    @Capacity.setter
    def Capacity(self, value:int):
        """
        Sets the capacity of the collection.

        Args:
            value (int): The new capacity value.
        """
        GetDllLibXls().CustomFilterCollection_set_Capacity.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().CustomFilterCollection_set_Capacity, self.Ptr, value)

    @property
    def Count(self)->int:
        """
        Gets the number of filters in the collection.

        Returns:
            int: The number of filters.
        """
        GetDllLibXls().CustomFilterCollection_get_Count.argtypes=[c_void_p]
        GetDllLibXls().CustomFilterCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibXls().CustomFilterCollection_get_Count, self.Ptr)
        return ret

    @property

    def RelationShip(self)->'RelationShip':
        """
        Gets or sets the relationship type for the custom filters.

        Returns:
            RelationShip: The relationship type.
        """
        GetDllLibXls().CustomFilterCollection_get_RelationShip.argtypes=[c_void_p]
        GetDllLibXls().CustomFilterCollection_get_RelationShip.restype=c_int
        ret = CallCFunction(GetDllLibXls().CustomFilterCollection_get_RelationShip, self.Ptr)
        objwraped = RelationShip(ret)
        return objwraped

    @RelationShip.setter
    def RelationShip(self, value:'RelationShip'):
        """
        Sets the relationship type for the custom filters.

        Args:
            value (RelationShip): The relationship type to set.
        """
        GetDllLibXls().CustomFilterCollection_set_RelationShip.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().CustomFilterCollection_set_RelationShip, self.Ptr, value.value)


    def Add(self ,customFilter:'CustomFilter'):
        """
        Adds a custom filter to the collection.

        Args:
            customFilter (CustomFilter): The custom filter to add.
        """
        intPtrcustomFilter:c_void_p = customFilter.Ptr

        GetDllLibXls().CustomFilterCollection_Add.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().CustomFilterCollection_Add, self.Ptr, intPtrcustomFilter)


    def get_Item(self ,index:int)->'CustomFilter':
        """
        Gets the custom filter at the specified index.

        Args:
            index (int): The index of the custom filter.
        Returns:
            CustomFilter: The custom filter at the specified index.
        """
        
        GetDllLibXls().CustomFilterCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().CustomFilterCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CustomFilterCollection_get_Item, self.Ptr, index)
        ret = None if intPtr==None else CustomFilter(intPtr)
        return ret



    def GetByIndex(self ,index:int)->'CustomFilter':
        """
        Gets the custom filter by index.

        Args:
            index (int): The index of the custom filter.
        Returns:
            CustomFilter: The custom filter at the specified index.
        """
        
        GetDllLibXls().CustomFilterCollection_GetByIndex.argtypes=[c_void_p ,c_int]
        GetDllLibXls().CustomFilterCollection_GetByIndex.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CustomFilterCollection_GetByIndex, self.Ptr, index)
        ret = None if intPtr==None else CustomFilter(intPtr)
        return ret


