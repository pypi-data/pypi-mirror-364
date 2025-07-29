from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsPivotCacheField (SpireObject) :
    """Represents a field in a PivotCache.
    
    This class provides functionality for managing fields in a PivotCache,
    including field properties such as name, data type, and formula.
    """
    @property

    def Formula(self)->str:
        """Gets the formula for the field.
        
        Returns:
            str: The formula for the field.
        """
        GetDllLibXls().XlsPivotCacheField_get_Formula.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCacheField_get_Formula.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPivotCacheField_get_Formula, self.Ptr))
        return ret


    @Formula.setter
    def Formula(self, value:str):
        """Sets the formula for the field.
        
        Args:
            value (str): The formula to set for the field.
        """
        GetDllLibXls().XlsPivotCacheField_set_Formula.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPivotCacheField_set_Formula, self.Ptr, value)

    @property
    def IsDataBaseField(self)->bool:
        """Gets whether the field is a database field.
        
        Returns:
            bool: True if the field is a database field; otherwise, False.
        """
        GetDllLibXls().XlsPivotCacheField_get_IsDataBaseField.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCacheField_get_IsDataBaseField.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCacheField_get_IsDataBaseField, self.Ptr)
        return ret

    @IsDataBaseField.setter
    def IsDataBaseField(self, value:bool):
        """Sets whether the field is a database field.
        
        Args:
            value (bool): True to set as a database field; otherwise, False.
        """
        GetDllLibXls().XlsPivotCacheField_set_IsDataBaseField.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotCacheField_set_IsDataBaseField, self.Ptr, value)

    @property
    def IsDouble(self)->bool:
        """Gets whether the field contains double-precision floating-point values.
        
        Returns:
            bool: True if the field contains double values; otherwise, False.
        """
        GetDllLibXls().XlsPivotCacheField_get_IsDouble.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCacheField_get_IsDouble.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCacheField_get_IsDouble, self.Ptr)
        return ret

    @IsDouble.setter
    def IsDouble(self, value:bool):
        """Sets whether the field contains double-precision floating-point values.
        
        Args:
            value (bool): True to set as containing double values; otherwise, False.
        """
        GetDllLibXls().XlsPivotCacheField_set_IsDouble.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotCacheField_set_IsDouble, self.Ptr, value)

    @property
    def IsDoubleInt(self)->bool:
        """Gets whether the field contains double integer values.
        
        Returns:
            bool: True if the field contains double integer values; otherwise, False.
        """
        GetDllLibXls().XlsPivotCacheField_get_IsDoubleInt.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCacheField_get_IsDoubleInt.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCacheField_get_IsDoubleInt, self.Ptr)
        return ret

    @IsDoubleInt.setter
    def IsDoubleInt(self, value:bool):
        """Sets whether the field contains double integer values.
        
        Args:
            value (bool): True to set as containing double integer values; otherwise, False.
        """
        GetDllLibXls().XlsPivotCacheField_set_IsDoubleInt.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotCacheField_set_IsDoubleInt, self.Ptr, value)

    @property
    def IsString(self)->bool:
        """Gets whether the field contains string values.
        
        Returns:
            bool: True if the field contains string values; otherwise, False.
        """
        GetDllLibXls().XlsPivotCacheField_get_IsString.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCacheField_get_IsString.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCacheField_get_IsString, self.Ptr)
        return ret

    @IsString.setter
    def IsString(self, value:bool):
        """Sets whether the field contains string values.
        
        Args:
            value (bool): True to set as containing string values; otherwise, False.
        """
        GetDllLibXls().XlsPivotCacheField_set_IsString.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotCacheField_set_IsString, self.Ptr, value)

    @property
    def IsDate(self)->bool:
        """Gets whether the field contains date values.
        
        Returns:
            bool: True if the field contains date values; otherwise, False.
        """
        GetDllLibXls().XlsPivotCacheField_get_IsDate.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCacheField_get_IsDate.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCacheField_get_IsDate, self.Ptr)
        return ret

    @property
    def ItemCount(self)->int:
        """Gets the number of items in the field.
        
        Returns:
            int: The number of items in the field.
        """
        GetDllLibXls().XlsPivotCacheField_get_ItemCount.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCacheField_get_ItemCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotCacheField_get_ItemCount, self.Ptr)
        return ret

    @property

    def Name(self)->str:
        """Gets the name of the field.
        
        Returns:
            str: The name of the field.
        """
        GetDllLibXls().XlsPivotCacheField_get_Name.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCacheField_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPivotCacheField_get_Name, self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        """Sets the name of the field.
        
        Args:
            value (str): The name to set for the field.
        """
        GetDllLibXls().XlsPivotCacheField_set_Name.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPivotCacheField_set_Name, self.Ptr, value)

    @property
    def Index(self)->int:
        """Gets the index of the field in the collection.
        
        Returns:
            int: The zero-based index of the field.
        """
        GetDllLibXls().XlsPivotCacheField_get_Index.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCacheField_get_Index.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotCacheField_get_Index, self.Ptr)
        return ret

    @Index.setter
    def Index(self, value:int):
        """Sets the index of the field in the collection.
        
        Args:
            value (int): The zero-based index to set for the field.
        """
        GetDllLibXls().XlsPivotCacheField_set_Index.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotCacheField_set_Index, self.Ptr, value)

    @property

    def DataType(self)->'PivotDataType':
        """Gets the data type of the field.
        
        Returns:
            PivotDataType: An enumeration value representing the data type.
        """
        GetDllLibXls().XlsPivotCacheField_get_DataType.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCacheField_get_DataType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotCacheField_get_DataType, self.Ptr)
        objwraped = PivotDataType(ret)
        return objwraped

    @property
    def IsFormulaField(self)->bool:
        """Gets whether the field is a formula field.
        
        Returns:
            bool: True if the field is a formula field; otherwise, False.
        """
        GetDllLibXls().XlsPivotCacheField_get_IsFormulaField.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCacheField_get_IsFormulaField.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCacheField_get_IsFormulaField, self.Ptr)
        return ret

    @property

    def Caption(self)->str:
        """Gets the caption of the field.
        
        Returns:
            str: The caption of the field.
        """
        GetDllLibXls().XlsPivotCacheField_get_Caption.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCacheField_get_Caption.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPivotCacheField_get_Caption, self.Ptr))
        return ret


    @Caption.setter
    def Caption(self, value:str):
        """Sets the caption of the field.
        
        Args:
            value (str): The caption to set for the field.
        """
        GetDllLibXls().XlsPivotCacheField_set_Caption.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPivotCacheField_set_Caption, self.Ptr, value)

    @property
    def isfieldgroup(self)->bool:
        """Gets whether the field is a field group.
        
        Returns:
            bool: True if the field is a field group; otherwise, False.
        """
        GetDllLibXls().XlsPivotCacheField_get_isfieldgroup.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCacheField_get_isfieldgroup.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCacheField_get_isfieldgroup, self.Ptr)
        return ret


    def GetValue(self ,index:int)->'SpireObject':
        """Gets the value at the specified index in the field.
        
        Args:
            index (int): The zero-based index of the value to retrieve.
            
        Returns:
            SpireObject: The value at the specified index.
        """
        
        GetDllLibXls().XlsPivotCacheField_GetValue.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsPivotCacheField_GetValue.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotCacheField_GetValue, self.Ptr, index)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


