from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class DateTimeGroupItem (SpireObject) :
    """

    """
    @property
    def MinValue(self)->'DateTime':
        """
        Gets the minimum value for the date-time group item.

        Returns:
            DateTime: The minimum value.
        """
        GetDllLibXls().DateTimeGroupItem_get_MinValue.argtypes=[c_void_p]
        GetDllLibXls().DateTimeGroupItem_get_MinValue.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().DateTimeGroupItem_get_MinValue, self.Ptr)
        ret = None if intPtr==None else DateTime(intPtr)
        return ret


    @property
    def DateTimeGroupingType(self)->'DateTimeGroupingType':
        """
        Gets or sets the date-time grouping type.

        Returns:
            DateTimeGroupingType: The grouping type.
        """
        GetDllLibXls().DateTimeGroupItem_get_DateTimeGroupingType.argtypes=[c_void_p]
        GetDllLibXls().DateTimeGroupItem_get_DateTimeGroupingType.restype=c_int
        ret = CallCFunction(GetDllLibXls().DateTimeGroupItem_get_DateTimeGroupingType, self.Ptr)
        objwraped = DateTimeGroupingType(ret)
        return objwraped

    @DateTimeGroupingType.setter
    def DateTimeGroupingType(self, value:'DateTimeGroupingType'):
        """
        Sets the date-time grouping type.

        Args:
            value (DateTimeGroupingType): The grouping type to set.
        """
        GetDllLibXls().DateTimeGroupItem_set_DateTimeGroupingType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().DateTimeGroupItem_set_DateTimeGroupingType, self.Ptr, value.value)

    @property
    def Year(self)->int:
        """
        Gets or sets the year value.

        Returns:
            int: The year value.
        """
        GetDllLibXls().DateTimeGroupItem_get_Year.argtypes=[c_void_p]
        GetDllLibXls().DateTimeGroupItem_get_Year.restype=c_int
        ret = CallCFunction(GetDllLibXls().DateTimeGroupItem_get_Year, self.Ptr)
        return ret

    @Year.setter
    def Year(self, value:int):
        """
        Sets the year value.

        Args:
            value (int): The year value to set.
        """
        GetDllLibXls().DateTimeGroupItem_set_Year.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().DateTimeGroupItem_set_Year, self.Ptr, value)

    @property
    def Month(self)->int:
        """
        Gets or sets the month value.

        Returns:
            int: The month value.
        """
        GetDllLibXls().DateTimeGroupItem_get_Month.argtypes=[c_void_p]
        GetDllLibXls().DateTimeGroupItem_get_Month.restype=c_int
        ret = CallCFunction(GetDllLibXls().DateTimeGroupItem_get_Month, self.Ptr)
        return ret

    @Month.setter
    def Month(self, value:int):
        """
        Sets the month value.

        Args:
            value (int): The month value to set.
        """
        GetDllLibXls().DateTimeGroupItem_set_Month.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().DateTimeGroupItem_set_Month, self.Ptr, value)

    @property
    def Day(self)->int:
        """
        Gets or sets the day value.

        Returns:
            int: The day value.
        """
        GetDllLibXls().DateTimeGroupItem_get_Day.argtypes=[c_void_p]
        GetDllLibXls().DateTimeGroupItem_get_Day.restype=c_int
        ret = CallCFunction(GetDllLibXls().DateTimeGroupItem_get_Day, self.Ptr)
        return ret

    @Day.setter
    def Day(self, value:int):
        """
        Sets the day value.

        Args:
            value (int): The day value to set.
        """
        GetDllLibXls().DateTimeGroupItem_set_Day.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().DateTimeGroupItem_set_Day, self.Ptr, value)

    @property
    def Hour(self)->int:
        """
        Gets or sets the hour value.

        Returns:
            int: The hour value.
        """
        GetDllLibXls().DateTimeGroupItem_get_Hour.argtypes=[c_void_p]
        GetDllLibXls().DateTimeGroupItem_get_Hour.restype=c_int
        ret = CallCFunction(GetDllLibXls().DateTimeGroupItem_get_Hour, self.Ptr)
        return ret

    @Hour.setter
    def Hour(self, value:int):
        """
        Sets the hour value.

        Args:
            value (int): The hour value to set.
        """
        GetDllLibXls().DateTimeGroupItem_set_Hour.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().DateTimeGroupItem_set_Hour, self.Ptr, value)

    @property
    def Minute(self)->int:
        """
        Gets or sets the minute value.

        Returns:
            int: The minute value.
        """
        GetDllLibXls().DateTimeGroupItem_get_Minute.argtypes=[c_void_p]
        GetDllLibXls().DateTimeGroupItem_get_Minute.restype=c_int
        ret = CallCFunction(GetDllLibXls().DateTimeGroupItem_get_Minute, self.Ptr)
        return ret

    @Minute.setter
    def Minute(self, value:int):
        """
        Sets the minute value.

        Args:
            value (int): The minute value to set.
        """
        GetDllLibXls().DateTimeGroupItem_set_Minute.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().DateTimeGroupItem_set_Minute, self.Ptr, value)

    @property
    def Second(self)->int:
        """
        Gets or sets the second value.

        Returns:
            int: The second value.
        """
        GetDllLibXls().DateTimeGroupItem_get_Second.argtypes=[c_void_p]
        GetDllLibXls().DateTimeGroupItem_get_Second.restype=c_int
        ret = CallCFunction(GetDllLibXls().DateTimeGroupItem_get_Second, self.Ptr)
        return ret

    @Second.setter
    def Second(self, value:int):
        """
        Sets the second value.

        Args:
            value (int): The second value to set.
        """
        GetDllLibXls().DateTimeGroupItem_set_Second.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().DateTimeGroupItem_set_Second, self.Ptr, value)

