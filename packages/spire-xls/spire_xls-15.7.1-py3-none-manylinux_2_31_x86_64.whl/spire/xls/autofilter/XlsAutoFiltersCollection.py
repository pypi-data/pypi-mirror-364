from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsAutoFiltersCollection (  SpireObject, IAutoFilters) :
    """

    """
    @property
    def Sorter(self)->'DataSorter':
        """
        Gets the DataSorter object for the auto filters collection.

        Returns:
            DataSorter: The DataSorter object.
        """
        GetDllLibXls().XlsAutoFiltersCollection_get_Sorter.argtypes=[c_void_p]
        GetDllLibXls().XlsAutoFiltersCollection_get_Sorter.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsAutoFiltersCollection_get_Sorter, self.Ptr)
        ret = None if intPtr==None else DataSorter(intPtr)
        return ret


    @property
    def Range(self)->'IXLSRange':
        """
        Gets or sets the filtered range.

        Returns:
            IXLSRange: The filtered range.
        """
        GetDllLibXls().XlsAutoFiltersCollection_get_Range.argtypes=[c_void_p]
        GetDllLibXls().XlsAutoFiltersCollection_get_Range.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsAutoFiltersCollection_get_Range, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @Range.setter
    def Range(self, value:'IXLSRange'):
        """
        Sets the filtered range.

        Args:
            value (IXLSRange): The range to set as filtered.
        """
        GetDllLibXls().XlsAutoFiltersCollection_set_Range.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsAutoFiltersCollection_set_Range, self.Ptr, value.Ptr)

    @property
    def AddressR1C1(self)->str:
        """
        Gets address of filtered range in R1C1 style. Read only.

        Returns:
            str: The address in R1C1 style.
        """
        GetDllLibXls().XlsAutoFiltersCollection_get_AddressR1C1.argtypes=[c_void_p]
        GetDllLibXls().XlsAutoFiltersCollection_get_AddressR1C1.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsAutoFiltersCollection_get_AddressR1C1, self.Ptr))
        return ret


    @property
    def Worksheet(self)->'Worksheet':
        """
        Gets the worksheet associated with the auto filters collection.

        Returns:
            Worksheet: The worksheet object.
        """
        GetDllLibXls().XlsAutoFiltersCollection_get_Worksheet.argtypes=[c_void_p]
        GetDllLibXls().XlsAutoFiltersCollection_get_Worksheet.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsAutoFiltersCollection_get_Worksheet, self.Ptr)
        ret = None if intPtr==None else Worksheet(intPtr)
        return ret


    @property
    def HasFiltered(self)->bool:
        """
        Gets whether the collection has filtered data.

        Returns:
            bool: True if filtered, otherwise False.
        """
        GetDllLibXls().XlsAutoFiltersCollection_get_HasFiltered.argtypes=[c_void_p]
        GetDllLibXls().XlsAutoFiltersCollection_get_HasFiltered.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsAutoFiltersCollection_get_HasFiltered, self.Ptr)
        return ret


    def get_Item(self ,columnIndex:int)->'FilterColumn':
        """
        Gets the auto filter item by column index.

        Args:
            columnIndex (int): The column index.
        Returns:
            FilterColumn: The filter column object.
        """
        
        GetDllLibXls().XlsAutoFiltersCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsAutoFiltersCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsAutoFiltersCollection_get_Item, self.Ptr, columnIndex)
        ret = None if intPtr==None else FilterColumn(intPtr)
        return ret


    @property
    def Count(self)->int:
        """
        Gets the number of filter columns in the collection.

        Returns:
            int: The count of filter columns.
        """
        GetDllLibXls().XlsAutoFiltersCollection_get_Count.argtypes=[c_void_p]
        GetDllLibXls().XlsAutoFiltersCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsAutoFiltersCollection_get_Count, self.Ptr)
        return ret


    def Clone(self ,parent:'XlsWorksheet')->'XlsAutoFiltersCollection':
        """
        Clones the auto filters collection for the specified worksheet.

        Args:
            parent (XlsWorksheet): The worksheet to clone to.
        Returns:
            XlsAutoFiltersCollection: The cloned collection.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsAutoFiltersCollection_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsAutoFiltersCollection_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsAutoFiltersCollection_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else XlsAutoFiltersCollection(intPtr)
        return ret


