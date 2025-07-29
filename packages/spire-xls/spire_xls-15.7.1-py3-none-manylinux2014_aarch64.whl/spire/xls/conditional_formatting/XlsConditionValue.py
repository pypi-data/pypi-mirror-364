from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsConditionValue (  SpireObject, IConditionValue) :
    """
    Represents a condition value for conditional formatting in Excel.
    """
    @property
    def IsGTE(self)->bool:
        """
        Gets or sets whether the comparison is greater than or equal to the threshold.

        Returns:
            bool: True if greater than or equal; otherwise, False.
        """
        GetDllLibXls().XlsConditionValue_get_IsGTE.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionValue_get_IsGTE.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionValue_get_IsGTE, self.Ptr)
        return ret

    @IsGTE.setter
    def IsGTE(self, value:bool):
        GetDllLibXls().XlsConditionValue_set_IsGTE.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionValue_set_IsGTE, self.Ptr, value)

    @property
    def Type(self)->'ConditionValueType':
        """
        Gets or sets the type of the condition value.

        Returns:
            ConditionValueType: The type of the condition value.
        """
        GetDllLibXls().XlsConditionValue_get_Type.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionValue_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionValue_get_Type, self.Ptr)
        objwraped = ConditionValueType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'ConditionValueType'):
        GetDllLibXls().XlsConditionValue_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionValue_set_Type, self.Ptr, value.value)

    @property
    def Value(self)->'SpireObject':
        """
        Gets or sets the value for the condition.

        Returns:
            SpireObject: The value for the condition.
        """
        GetDllLibXls().XlsConditionValue_get_Value.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionValue_get_Value.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionValue_get_Value, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret

    @Value.setter
    def Value(self, value:'SpireObject'):
        GetDllLibXls().XlsConditionValue_set_Value.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsConditionValue_set_Value, self.Ptr, value.Ptr)

    @staticmethod
    def op_Equality(first:'XlsConditionValue',second:'XlsConditionValue')->bool:
        """
        Determines whether two XlsConditionValue instances are equal.

        Args:
            first (XlsConditionValue): The first instance to compare.
            second (XlsConditionValue): The second instance to compare.
        Returns:
            bool: True if equal; otherwise, False.
        """
        intPtrfirst:c_void_p = first.Ptr
        intPtrsecond:c_void_p = second.Ptr

        GetDllLibXls().XlsConditionValue_op_Equality.argtypes=[ c_void_p,c_void_p]
        GetDllLibXls().XlsConditionValue_op_Equality.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionValue_op_Equality,  intPtrfirst,intPtrsecond)
        return ret

    @staticmethod
    def op_Inequality(first:'XlsConditionValue',second:'XlsConditionValue')->bool:
        """
        Determines whether two XlsConditionValue instances are not equal.

        Args:
            first (XlsConditionValue): The first instance to compare.
            second (XlsConditionValue): The second instance to compare.
        Returns:
            bool: True if not equal; otherwise, False.
        """
        intPtrfirst:c_void_p = first.Ptr
        intPtrsecond:c_void_p = second.Ptr

        GetDllLibXls().XlsConditionValue_op_Inequality.argtypes=[ c_void_p,c_void_p]
        GetDllLibXls().XlsConditionValue_op_Inequality.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionValue_op_Inequality,  intPtrfirst,intPtrsecond)
        return ret

    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified object is equal to the current object.

        Args:
            obj (SpireObject): The object to compare with the current object.
        Returns:
            bool: True if equal; otherwise, False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibXls().XlsConditionValue_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsConditionValue_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionValue_Equals, self.Ptr, intPtrobj)
        return ret

    def GetHashCode(self)->int:
        """
        Returns the hash code for this instance.

        Returns:
            int: The hash code for this instance.
        """
        GetDllLibXls().XlsConditionValue_GetHashCode.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionValue_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionValue_GetHashCode, self.Ptr)
        return ret

