from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class Top10Filter (SpireObject) :
    """

    """
    @property
    def IsTop(self)->bool:
        """
        Gets or sets whether the filter is for top values.

        Returns:
            bool: True if filtering for top values, otherwise False.
        """
        GetDllLibXls().Top10Filter_get_IsTop.argtypes=[c_void_p]
        GetDllLibXls().Top10Filter_get_IsTop.restype=c_bool
        ret = CallCFunction(GetDllLibXls().Top10Filter_get_IsTop, self.Ptr)
        return ret

    @IsTop.setter
    def IsTop(self, value:bool):
        """
        Sets whether the filter is for top values.

        Args:
            value (bool): True to filter for top values, otherwise False.
        """
        GetDllLibXls().Top10Filter_set_IsTop.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().Top10Filter_set_IsTop, self.Ptr, value)

    @property
    def IsPercent(self)->bool:
        """
        Gets or sets whether the filter is based on percentage.

        Returns:
            bool: True if filtering by percentage, otherwise False.
        """
        GetDllLibXls().Top10Filter_get_IsPercent.argtypes=[c_void_p]
        GetDllLibXls().Top10Filter_get_IsPercent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().Top10Filter_get_IsPercent, self.Ptr)
        return ret

    @IsPercent.setter
    def IsPercent(self, value:bool):
        """
        Sets whether the filter is based on percentage.

        Args:
            value (bool): True to filter by percentage, otherwise False.
        """
        GetDllLibXls().Top10Filter_set_IsPercent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().Top10Filter_set_IsPercent, self.Ptr, value)

    @property
    def Items(self)->int:
        """
        Gets or sets the number of items to filter.

        Returns:
            int: The number of items to filter.
        """
        GetDllLibXls().Top10Filter_get_Items.argtypes=[c_void_p]
        GetDllLibXls().Top10Filter_get_Items.restype=c_int
        ret = CallCFunction(GetDllLibXls().Top10Filter_get_Items, self.Ptr)
        return ret

    @Items.setter
    def Items(self, value:int):
        """
        Sets the number of items to filter.

        Args:
            value (int): The number of items to filter.
        """
        GetDllLibXls().Top10Filter_set_Items.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().Top10Filter_set_Items, self.Ptr, value)

    @property
    def Criteria(self)->'SpireObject':
        """
        Gets or sets the criteria for the filter.

        Returns:
            SpireObject: The criteria object.
        """
        GetDllLibXls().Top10Filter_get_Criteria.argtypes=[c_void_p]
        GetDllLibXls().Top10Filter_get_Criteria.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Top10Filter_get_Criteria, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret

    @Criteria.setter
    def Criteria(self, value:'SpireObject'):
        """
        Sets the criteria for the filter.

        Args:
            value (SpireObject): The criteria object.
        """
        GetDllLibXls().Top10Filter_set_Criteria.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().Top10Filter_set_Criteria, self.Ptr, value.Ptr)

