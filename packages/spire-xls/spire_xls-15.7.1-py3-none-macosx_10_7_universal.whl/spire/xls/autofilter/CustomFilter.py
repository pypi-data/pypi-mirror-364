from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class CustomFilter (  IAutoFilterCondition) :
    """

    """
    @property

    def FilterOperatorType(self)->'FilterOperatorType':
        """
        Gets and sets the filter operator type.

        """
        GetDllLibXls().CustomFilter_get_FilterOperatorType.argtypes=[c_void_p]
        GetDllLibXls().CustomFilter_get_FilterOperatorType.restype=c_int
        ret = CallCFunction(GetDllLibXls().CustomFilter_get_FilterOperatorType, self.Ptr)
        objwraped = FilterOperatorType(ret)
        return objwraped

    @FilterOperatorType.setter
    def FilterOperatorType(self, value:'FilterOperatorType'):
        GetDllLibXls().CustomFilter_set_FilterOperatorType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().CustomFilter_set_FilterOperatorType, self.Ptr, value.value)

    @property

    def Criteria(self)->'SpireObject':
        """
        Gets and sets the criteria.

        """
        GetDllLibXls().CustomFilter_get_Criteria.argtypes=[c_void_p]
        GetDllLibXls().CustomFilter_get_Criteria.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CustomFilter_get_Criteria, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @Criteria.setter
    def Criteria(self, value:'SpireObject'):
        GetDllLibXls().CustomFilter_set_Criteria.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().CustomFilter_set_Criteria, self.Ptr, value.Ptr)

    @property

    def DataType(self)->'FilterDataType':
        """
        Gets or sets the data type for the custom filter.

        Returns:
            FilterDataType: The data type of the filter.
        """
        GetDllLibXls().CustomFilter_get_DataType.argtypes=[c_void_p]
        GetDllLibXls().CustomFilter_get_DataType.restype=c_int
        ret = CallCFunction(GetDllLibXls().CustomFilter_get_DataType, self.Ptr)
        objwraped = FilterDataType(ret)
        return objwraped

    @DataType.setter
    def DataType(self, value:'FilterDataType'):
        """
        Sets the data type for the custom filter.

        Args:
            value (FilterDataType): The data type to set.
        """
        GetDllLibXls().CustomFilter_set_DataType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().CustomFilter_set_DataType, self.Ptr, value.value)

    @property

    def ConditionOperator(self)->'FilterConditionType':
        """
        Gets or sets the condition operator for the custom filter.

        Returns:
            FilterConditionType: The condition operator.
        """
        GetDllLibXls().CustomFilter_get_ConditionOperator.argtypes=[c_void_p]
        GetDllLibXls().CustomFilter_get_ConditionOperator.restype=c_int
        ret = CallCFunction(GetDllLibXls().CustomFilter_get_ConditionOperator, self.Ptr)
        objwraped = FilterConditionType(ret)
        return objwraped

    @ConditionOperator.setter
    def ConditionOperator(self, value:'FilterConditionType'):
        """
        Sets the condition operator for the custom filter.

        Args:
            value (FilterConditionType): The condition operator to set.
        """
        GetDllLibXls().CustomFilter_set_ConditionOperator.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().CustomFilter_set_ConditionOperator, self.Ptr, value.value)

    @property

    def String(self)->str:
        """
        Gets or sets the string value for the custom filter.

        Returns:
            str: The string value.
        """
        GetDllLibXls().CustomFilter_get_String.argtypes=[c_void_p]
        GetDllLibXls().CustomFilter_get_String.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().CustomFilter_get_String, self.Ptr))
        return ret


    @String.setter
    def String(self, value:str):
        """
        Sets the string value for the custom filter.

        Args:
            value (str): The string value to set.
        """
        GetDllLibXls().CustomFilter_set_String.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().CustomFilter_set_String, self.Ptr, value)

    @property
    def Boolean(self)->bool:
        """
        Gets or sets the boolean value for the custom filter.

        Returns:
            bool: The boolean value.
        """
        GetDllLibXls().CustomFilter_get_Boolean.argtypes=[c_void_p]
        GetDllLibXls().CustomFilter_get_Boolean.restype=c_bool
        ret = CallCFunction(GetDllLibXls().CustomFilter_get_Boolean, self.Ptr)
        return ret

    @Boolean.setter
    def Boolean(self, value:bool):
        """
        Sets the boolean value for the custom filter.

        Args:
            value (bool): The boolean value to set.
        """
        GetDllLibXls().CustomFilter_set_Boolean.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().CustomFilter_set_Boolean, self.Ptr, value)

    @property
    def ErrorCode(self)->int:
        """
        Gets or sets the error code for the custom filter.

        Returns:
            int: The error code.
        """
        GetDllLibXls().CustomFilter_get_ErrorCode.argtypes=[c_void_p]
        GetDllLibXls().CustomFilter_get_ErrorCode.restype=c_int
        ret = CallCFunction(GetDllLibXls().CustomFilter_get_ErrorCode, self.Ptr)
        return ret

    @ErrorCode.setter
    def ErrorCode(self, value:int):
        """
        Sets the error code for the custom filter.

        Args:
            value (int): The error code to set.
        """
        GetDllLibXls().CustomFilter_set_ErrorCode.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().CustomFilter_set_ErrorCode, self.Ptr, value)

    @property
    def Double(self)->float:
        """
        Gets or sets the double value for the custom filter.

        Returns:
            float: The double value.
        """
        GetDllLibXls().CustomFilter_get_Double.argtypes=[c_void_p]
        GetDllLibXls().CustomFilter_get_Double.restype=c_double
        ret = CallCFunction(GetDllLibXls().CustomFilter_get_Double, self.Ptr)
        return ret

    @Double.setter
    def Double(self, value:float):
        """
        Sets the double value for the custom filter.

        Args:
            value (float): The double value to set.
        """
        GetDllLibXls().CustomFilter_set_Double.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().CustomFilter_set_Double, self.Ptr, value)

