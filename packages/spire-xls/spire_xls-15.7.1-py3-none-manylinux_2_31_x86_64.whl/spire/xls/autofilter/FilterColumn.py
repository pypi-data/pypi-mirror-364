from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class FilterColumn (  SpireObject,IAutoFilter) :
    """

    """
    @property
    def Visibledropdown(self)->bool:
        """
        Indicates whether the AutoFilter button for this column is visible.

        """
        GetDllLibXls().FilterColumn_get_Visibledropdown.argtypes=[c_void_p]
        GetDllLibXls().FilterColumn_get_Visibledropdown.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FilterColumn_get_Visibledropdown, self.Ptr)
        return ret

    @Visibledropdown.setter
    def Visibledropdown(self, value:bool):
        GetDllLibXls().FilterColumn_set_Visibledropdown.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FilterColumn_set_Visibledropdown, self.Ptr, value)

    @property
    def Filter(self)->'SpireObject':
        """
        Gets or sets the filter object for this column.

        Returns:
            SpireObject: The filter object.
        """
        GetDllLibXls().FilterColumn_get_Filter.argtypes=[c_void_p]
        GetDllLibXls().FilterColumn_get_Filter.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().FilterColumn_get_Filter, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret

    @Filter.setter
    def Filter(self, value:'SpireObject'):
        """
        Sets the filter object for this column.

        Args:
            value (SpireObject): The filter object to set.
        """
        GetDllLibXls().FilterColumn_set_Filter.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().FilterColumn_set_Filter, self.Ptr, value.Ptr)

    @property
    def FilterType(self)->'FilterType':
        """
        Gets or sets the filter type for this column.

        Returns:
            FilterType: The filter type.
        """
        GetDllLibXls().FilterColumn_get_FilterType.argtypes=[c_void_p]
        GetDllLibXls().FilterColumn_get_FilterType.restype=c_int
        ret = CallCFunction(GetDllLibXls().FilterColumn_get_FilterType, self.Ptr)
        objwraped = FilterType(ret)
        return objwraped

    @FilterType.setter
    def FilterType(self, value:'FilterType'):
        """
        Sets the filter type for this column.

        Args:
            value (FilterType): The filter type to set.
        """
        GetDllLibXls().FilterColumn_set_FilterType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().FilterColumn_set_FilterType, self.Ptr, value.value)

    @property
    def FieldIndex(self)->int:
        """
        Gets or sets the field index for this filter column.

        Returns:
            int: The field index.
        """
        GetDllLibXls().FilterColumn_get_FieldIndex.argtypes=[c_void_p]
        GetDllLibXls().FilterColumn_get_FieldIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().FilterColumn_get_FieldIndex, self.Ptr)
        return ret

    @FieldIndex.setter
    def FieldIndex(self, value:int):
        """
        Sets the field index for this filter column.

        Args:
            value (int): The field index to set.
        """
        GetDllLibXls().FilterColumn_set_FieldIndex.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().FilterColumn_set_FieldIndex, self.Ptr, value)

    @property
    def Top10Items(self)->int:
        """
        number of items display in Top10Items mode.

        """
        GetDllLibXls().FilterColumn_get_Top10Items.argtypes=[c_void_p]
        GetDllLibXls().FilterColumn_get_Top10Items.restype=c_int
        ret = CallCFunction(GetDllLibXls().FilterColumn_get_Top10Items, self.Ptr)
        return ret

    @Top10Items.setter
    def Top10Items(self, value:int):
        GetDllLibXls().FilterColumn_set_Top10Items.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().FilterColumn_set_Top10Items, self.Ptr, value)

    @property
    def IsTop10Items(self)->bool:
        """
        Highest-valued 10 items displayed

        """
        GetDllLibXls().FilterColumn_get_IsTop10Items.argtypes=[c_void_p]
        GetDllLibXls().FilterColumn_get_IsTop10Items.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FilterColumn_get_IsTop10Items, self.Ptr)
        return ret

    @IsTop10Items.setter
    def IsTop10Items(self, value:bool):
        GetDllLibXls().FilterColumn_set_IsTop10Items.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FilterColumn_set_IsTop10Items, self.Ptr, value)

    @property
    def ShowTopItem(self)->bool:
        """
        Gets or sets whether to show the top item in the filter.

        Returns:
            bool: True if showing the top item, otherwise False.
        """
        GetDllLibXls().FilterColumn_get_ShowTopItem.argtypes=[c_void_p]
        GetDllLibXls().FilterColumn_get_ShowTopItem.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FilterColumn_get_ShowTopItem, self.Ptr)
        return ret

    @ShowTopItem.setter
    def ShowTopItem(self, value:bool):
        """
        Sets whether to show the top item in the filter.

        Args:
            value (bool): True to show the top item, otherwise False.
        """
        GetDllLibXls().FilterColumn_set_ShowTopItem.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FilterColumn_set_ShowTopItem, self.Ptr, value)

    @property
    def IsSimple2(self)->bool:
        """
        True if the second condition is a simple equality.

        """
        GetDllLibXls().FilterColumn_get_IsSimple2.argtypes=[c_void_p]
        GetDllLibXls().FilterColumn_get_IsSimple2.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FilterColumn_get_IsSimple2, self.Ptr)
        return ret

    @IsSimple2.setter
    def IsSimple2(self, value:bool):
        GetDllLibXls().FilterColumn_set_IsSimple2.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FilterColumn_set_IsSimple2, self.Ptr, value)

    @property
    def IsSimple1(self)->bool:
        """
        True if the first condition is a simple equality.

        """
        GetDllLibXls().FilterColumn_get_IsSimple1.argtypes=[c_void_p]
        GetDllLibXls().FilterColumn_get_IsSimple1.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FilterColumn_get_IsSimple1, self.Ptr)
        return ret

    @IsSimple1.setter
    def IsSimple1(self, value:bool):
        GetDllLibXls().FilterColumn_set_IsSimple1.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FilterColumn_set_IsSimple1, self.Ptr, value)

    @property
    def IsTop10Percent(self)->bool:
        """
        Highest-valued 10 items displayed (percentage specified in condition)

        """
        GetDllLibXls().FilterColumn_get_IsTop10Percent.argtypes=[c_void_p]
        GetDllLibXls().FilterColumn_get_IsTop10Percent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FilterColumn_get_IsTop10Percent, self.Ptr)
        return ret

    @IsTop10Percent.setter
    def IsTop10Percent(self, value:bool):
        GetDllLibXls().FilterColumn_set_IsTop10Percent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FilterColumn_set_IsTop10Percent, self.Ptr, value)

    @property
    def IsAnd(self)->bool:
        """
        Logical AND of FirstCondtion and SecondCondition.

        """
        GetDllLibXls().FilterColumn_get_IsAnd.argtypes=[c_void_p]
        GetDllLibXls().FilterColumn_get_IsAnd.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FilterColumn_get_IsAnd, self.Ptr)
        return ret

    @IsAnd.setter
    def IsAnd(self, value:bool):
        GetDllLibXls().FilterColumn_set_IsAnd.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().FilterColumn_set_IsAnd, self.Ptr, value)

    @property
    def IsFiltered(self)->bool:
        """
        Gets whether the column is currently filtered.

        Returns:
            bool: True if filtered, otherwise False.
        """
        GetDllLibXls().FilterColumn_get_IsFiltered.argtypes=[c_void_p]
        GetDllLibXls().FilterColumn_get_IsFiltered.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FilterColumn_get_IsFiltered, self.Ptr)
        return ret

    @property
    def SecondCondition(self)->'IAutoFilterCondition':
        """
        Gets the second condition of the autofilter.

        Returns:
            IAutoFilterCondition: The second condition object.
        """
        GetDllLibXls().FilterColumn_get_SecondCondition.argtypes=[c_void_p]
        GetDllLibXls().FilterColumn_get_SecondCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().FilterColumn_get_SecondCondition, self.Ptr)
        ret = None if intPtr==None else IAutoFilterCondition(intPtr)
        return ret

    @property
    def FirstCondition(self)->'IAutoFilterCondition':
        """
        Gets the first condition of the autofilter.

        Returns:
            IAutoFilterCondition: The first condition object.
        """
        GetDllLibXls().FilterColumn_get_FirstCondition.argtypes=[c_void_p]
        GetDllLibXls().FilterColumn_get_FirstCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().FilterColumn_get_FirstCondition, self.Ptr)
        ret = None if intPtr==None else IAutoFilterCondition(intPtr)
        return ret

    @property
    def HasFirstCondition(self)->bool:
        """
        Gets whether the first condition is used.

        Returns:
            bool: True if the first condition is used, otherwise False.
        """
        GetDllLibXls().FilterColumn_get_HasFirstCondition.argtypes=[c_void_p]
        GetDllLibXls().FilterColumn_get_HasFirstCondition.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FilterColumn_get_HasFirstCondition, self.Ptr)
        return ret

    @property
    def HasSecondCondition(self)->bool:
        """
        Gets whether the second condition is used.

        Returns:
            bool: True if the second condition is used, otherwise False.
        """
        GetDllLibXls().FilterColumn_get_HasSecondCondition.argtypes=[c_void_p]
        GetDllLibXls().FilterColumn_get_HasSecondCondition.restype=c_bool
        ret = CallCFunction(GetDllLibXls().FilterColumn_get_HasSecondCondition, self.Ptr)
        return ret

