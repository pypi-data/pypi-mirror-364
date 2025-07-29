from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ColorConditionValue (  XlsConditionValue) :
    """
    Represents a condition value with an associated color for conditional formatting.
    """
    @property
    def FormatColor(self)->'Color':
        """
        Gets or sets the format color for the condition value.

        Returns:
            Color: The format color.
        """
        GetDllLibXls().ColorConditionValue_get_FormatColor.argtypes=[c_void_p]
        GetDllLibXls().ColorConditionValue_get_FormatColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ColorConditionValue_get_FormatColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @FormatColor.setter
    def FormatColor(self, value:'Color'):
        GetDllLibXls().ColorConditionValue_set_FormatColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ColorConditionValue_set_FormatColor, self.Ptr, value.Ptr)

    @property
    def IsGTE(self)->bool:
        """
        Gets or sets whether the comparison is greater than or equal to the threshold.

        Returns:
            bool: True if greater than or equal; otherwise, False.
        """
        GetDllLibXls().ColorConditionValue_get_IsGTE.argtypes=[c_void_p]
        GetDllLibXls().ColorConditionValue_get_IsGTE.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ColorConditionValue_get_IsGTE, self.Ptr)
        return ret

    @IsGTE.setter
    def IsGTE(self, value:bool):
        GetDllLibXls().ColorConditionValue_set_IsGTE.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ColorConditionValue_set_IsGTE, self.Ptr, value)

    @property
    def Position(self)->'ConditionValuePosition':
        """
        Gets the position of the condition value in the scale.

        Returns:
            ConditionValuePosition: The position in the scale.
        """
        GetDllLibXls().ColorConditionValue_get_Position.argtypes=[c_void_p]
        GetDllLibXls().ColorConditionValue_get_Position.restype=c_int
        ret = CallCFunction(GetDllLibXls().ColorConditionValue_get_Position, self.Ptr)
        objwraped = ConditionValuePosition(ret)
        return objwraped

    @property
    def Type(self)->'ConditionValueType':
        """
        Gets or sets the type of the condition value.

        Returns:
            ConditionValueType: The type of the condition value.
        """
        GetDllLibXls().ColorConditionValue_get_Type.argtypes=[c_void_p]
        GetDllLibXls().ColorConditionValue_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibXls().ColorConditionValue_get_Type, self.Ptr)
        objwraped = ConditionValueType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'ConditionValueType'):
        GetDllLibXls().ColorConditionValue_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ColorConditionValue_set_Type, self.Ptr, value.value)

    @property
    def Value(self)->str:
        """
        Gets or sets the value for the condition.

        Returns:
            str: The value for the condition.
        """
        GetDllLibXls().ColorConditionValue_get_Value.argtypes=[c_void_p]
        GetDllLibXls().ColorConditionValue_get_Value.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ColorConditionValue_get_Value, self.Ptr))
        return ret


    @Value.setter
    def Value(self, value:str):
        GetDllLibXls().ColorConditionValue_set_Value.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ColorConditionValue_set_Value, self.Ptr, value)

