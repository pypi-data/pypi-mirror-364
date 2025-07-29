from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc
from spire.xls.pivot_tables.PivotField import PivotField

class PivotReportFilter (SpireObject) :

    """Represents a report filter in a PivotTable.
    
    This class provides functionality for managing report filters (page filters)
    in a PivotTable, allowing for filtering of data displayed in the PivotTable.
    """
    @dispatch
    def __init__(self,field_name:str,is_new:bool):
        """Initializes a new instance of the PivotReportFilter class with a field name and creation flag.
        
        Args:
            field_name (str): The name of the field to use as a report filter.
            is_new (bool): True to create a new filter; otherwise, False.
        """
        GetDllLibXls().PivotReportFilter_CreateFI.argtypes=[c_wchar_p, c_bool]
        GetDllLibXls().PivotReportFilter_CreateFI.restype = c_void_p
        intPtr = CallCFunction(GetDllLibXls().PivotReportFilter_CreateFI,field_name,is_new)
        
        super(PivotReportFilter, self).__init__(intPtr)


    @dispatch
    def __init__(self,field_name:str,pivotTable:'XlsPivotTable'):
        """Initializes a new instance of the PivotReportFilter class with a field name and pivot table.
        
        Args:
            field_name (str): The name of the field to use as a report filter.
            pivotTable (XlsPivotTable): The pivot table to apply the filter to.
        """
        GetDllLibXls().PivotReportFilter_CreateFP.argtypes=[c_wchar_p, c_void_p]
        GetDllLibXls().PivotReportFilter_CreateFP.restype = c_void_p
        intPtr = CallCFunction(GetDllLibXls().PivotReportFilter_CreateFP,field_name,pivotTable.Ptr)
        
        super(PivotReportFilter, self).__init__(intPtr)
    
    
    @dispatch
    def __init__(self,field:PivotField,pivotTable:'XlsPivotTable'):
        """Initializes a new instance of the PivotReportFilter class with a pivot field and pivot table.
        
        Args:
            field (PivotField): The pivot field to use as a report filter.
            pivotTable (XlsPivotTable): The pivot table to apply the filter to.
        """
        GetDllLibXls().PivotReportFilter_CreateFP2.argtypes=[c_void_p, c_void_p]
        GetDllLibXls().PivotReportFilter_CreateFP2.restype = c_void_p
        intPtr = CallCFunction(GetDllLibXls().PivotReportFilter_CreateFP2,field.Ptr,pivotTable.Ptr)
        
        super(PivotReportFilter, self).__init__(intPtr)

    @dispatch
    def __init__(self,index:int,pivotTable:'XlsPivotTable'):
        """Initializes a new instance of the PivotReportFilter class with a field index and pivot table.
        
        Args:
            index (int): The index of the field to use as a report filter.
            pivotTable (XlsPivotTable): The pivot table to apply the filter to.
        """
        GetDllLibXls().PivotReportFilter_CreateIP.argtypes=[c_int, c_void_p]
        GetDllLibXls().PivotReportFilter_CreateIP.restype = c_void_p
        intPtr = CallCFunction(GetDllLibXls().PivotReportFilter_CreateIP,index,pivotTable.Ptr)
        
        super(PivotReportFilter, self).__init__(intPtr)

    @dispatch
    def __init__(self,fieldName:str):
        """Initializes a new instance of the PivotReportFilter class with a field name.
        
        Args:
            fieldName (str): The name of the field to use as a report filter.
        """
        GetDllLibXls().PivotReportFilter_Create.argtypes=[ c_void_p]
        GetDllLibXls().PivotReportFilter_Create.restype = c_void_p
        intPtr = CallCFunction(GetDllLibXls().PivotReportFilter_Create,fieldName)
        
        super(PivotReportFilter, self).__init__(intPtr)
    """
    Represent the report filter of PivotTable

    """
    @property
    def IsMultipleSelect(self)->bool:
        """Gets whether multiple selection is enabled for the filter field.
        
        Returns:
            bool: True if multiple selection is enabled; otherwise, False.
        """
        GetDllLibXls().PivotReportFilter_get_IsMultipleSelect.argtypes=[c_void_p]
        GetDllLibXls().PivotReportFilter_get_IsMultipleSelect.restype=c_bool
        ret = CallCFunction(GetDllLibXls().PivotReportFilter_get_IsMultipleSelect, self.Ptr)
        return ret

    @IsMultipleSelect.setter
    def IsMultipleSelect(self, value:bool):
        """Sets whether multiple selection is enabled for the filter field.
        
        Args:
            value (bool): True to enable multiple selection; otherwise, False.
        """
        GetDllLibXls().PivotReportFilter_set_IsMultipleSelect.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().PivotReportFilter_set_IsMultipleSelect, self.Ptr, value)

    @property

    def FilterItemStrings(self)->List[str]:
        """Gets the collection of filter item strings.
        
        When IsMultipleSelect is false, only the first value of the string array will be used.
        The possible values must be from field values.
        
        Returns:
            List[str]: A list of filter item strings.
        """
        GetDllLibXls().PivotReportFilter_get_FilterItemStrings.argtypes=[c_void_p]
        GetDllLibXls().PivotReportFilter_get_FilterItemStrings.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().PivotReportFilter_get_FilterItemStrings, self.Ptr)
        ret = GetStrVectorFromArray(intPtrArray, str)
        return ret



    @FilterItemStrings.setter
    def FilterItemStrings(self, value:List[str]):
        """Sets the collection of filter item strings.
        
        When IsMultipleSelect is false, only the first value of the string array will be used.
        The possible values must be from field values.
        
        Args:
            value (List[str]): A list of filter item strings to set.
        """
        countValue = len(value)
        ArrayTypeValue = c_wchar_p * countValue
        ArrayTypeValues = ArrayTypeValue()
        for i in range(0, countValue):
            ArrayTypeValues[i] = value[i]

        GetDllLibXls().PivotReportFilter_set_FilterItemStrings.argtypes=[c_void_p, ArrayTypeValue]
        CallCFunction(GetDllLibXls().PivotReportFilter_set_FilterItemStrings, self.Ptr, ArrayTypeValues,countValue)


    @property

    def FieldString(self)->str:
        """Gets the field string of the report filter.
        
        Returns:
            str: The field string of the report filter.
        """
        GetDllLibXls().PivotReportFilter_get_FieldString.argtypes=[c_void_p]
        GetDllLibXls().PivotReportFilter_get_FieldString.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().PivotReportFilter_get_FieldString, self.Ptr))
        return ret


    @FieldString.setter
    def FieldString(self, value:str):
        """Sets the field string of the report filter.
        
        Args:
            value (str): The field string to set for the report filter.
        """
        GetDllLibXls().PivotReportFilter_set_FieldString.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().PivotReportFilter_set_FieldString, self.Ptr, value)

    @property

    def FieldName(self)->str:
        """Gets the name of the filter field.
        
        Returns:
            str: The name of the filter field.
        """
        GetDllLibXls().PivotReportFilter_get_FieldName.argtypes=[c_void_p]
        GetDllLibXls().PivotReportFilter_get_FieldName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().PivotReportFilter_get_FieldName, self.Ptr))
        return ret


    @FieldName.setter
    def FieldName(self, value:str):
        """Sets the name of the filter field.
        
        Args:
            value (str): The name to set for the filter field.
        """
        GetDllLibXls().PivotReportFilter_set_FieldName.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().PivotReportFilter_set_FieldName, self.Ptr, value)

