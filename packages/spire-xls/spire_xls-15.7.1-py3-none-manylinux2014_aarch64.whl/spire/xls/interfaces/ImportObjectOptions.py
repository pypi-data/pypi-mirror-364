from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ImportObjectOptions (SpireObject) :
    """
    Represents options for importing objects into Excel.
    
    This class provides various settings to control how data is imported into Excel worksheets.
    """
    @property
    def ConvertNumericData(self)->bool:
        """
        Gets whether to convert text data to numeric data during import.
        
        Returns:
            bool: True if numeric data conversion is enabled, False otherwise.
        """
        GetDllLibXls().ImportObjectOptions_get_ConvertNumericData.argtypes=[c_void_p]
        GetDllLibXls().ImportObjectOptions_get_ConvertNumericData.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ImportObjectOptions_get_ConvertNumericData, self.Ptr)
        return ret

    @ConvertNumericData.setter
    def ConvertNumericData(self, value:bool):
        """
        Sets whether to convert text data to numeric data during import.
        
        Args:
            value (bool): True to enable numeric data conversion, False otherwise.
        """
        GetDllLibXls().ImportObjectOptions_set_ConvertNumericData.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ImportObjectOptions_set_ConvertNumericData, self.Ptr, value)

    @property
    def InsertRows(self)->bool:
        """
        Gets whether to insert rows when importing data.
        
        Returns:
            bool: True if rows should be inserted, False otherwise.
        """
        GetDllLibXls().ImportObjectOptions_get_InsertRows.argtypes=[c_void_p]
        GetDllLibXls().ImportObjectOptions_get_InsertRows.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ImportObjectOptions_get_InsertRows, self.Ptr)
        return ret

    @InsertRows.setter
    def InsertRows(self, value:bool):
        """
        Sets whether to insert rows when importing data.
        
        Args:
            value (bool): True to insert rows, False otherwise.
        """
        GetDllLibXls().ImportObjectOptions_set_InsertRows.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ImportObjectOptions_set_InsertRows, self.Ptr, value)

    @property
    def CheckMergedCells(self)->bool:
        """
        Gets whether to check for merged cells during import.
        
        Returns:
            bool: True if merged cells should be checked, False otherwise.
        """
        GetDllLibXls().ImportObjectOptions_get_CheckMergedCells.argtypes=[c_void_p]
        GetDllLibXls().ImportObjectOptions_get_CheckMergedCells.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ImportObjectOptions_get_CheckMergedCells, self.Ptr)
        return ret

    @CheckMergedCells.setter
    def CheckMergedCells(self, value:bool):
        """
        Sets whether to check for merged cells during import.
        
        Args:
            value (bool): True to check merged cells, False otherwise.
        """
        GetDllLibXls().ImportObjectOptions_set_CheckMergedCells.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ImportObjectOptions_set_CheckMergedCells, self.Ptr, value)

    @property
    def IsFieldNameShown(self)->bool:
        """
        Gets whether field names should be shown in the imported data.
        
        Returns:
            bool: True if field names should be shown, False otherwise.
        """
        GetDllLibXls().ImportObjectOptions_get_IsFieldNameShown.argtypes=[c_void_p]
        GetDllLibXls().ImportObjectOptions_get_IsFieldNameShown.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ImportObjectOptions_get_IsFieldNameShown, self.Ptr)
        return ret

    @IsFieldNameShown.setter
    def IsFieldNameShown(self, value:bool):
        """
        Sets whether field names should be shown in the imported data.
        
        Args:
            value (bool): True to show field names, False otherwise.
        """
        GetDllLibXls().ImportObjectOptions_set_IsFieldNameShown.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ImportObjectOptions_set_IsFieldNameShown, self.Ptr, value)

    @property

    def DateFormat(self)->str:
        """
        Gets the date format to use when importing date values.
        
        Returns:
            str: The date format string.
        """
        GetDllLibXls().ImportObjectOptions_get_DateFormat.argtypes=[c_void_p]
        GetDllLibXls().ImportObjectOptions_get_DateFormat.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ImportObjectOptions_get_DateFormat, self.Ptr))
        return ret


    @DateFormat.setter
    def DateFormat(self, value:str):
        """
        Sets the date format to use when importing date values.
        
        Args:
            value (str): The date format string.
        """
        GetDllLibXls().ImportObjectOptions_set_DateFormat.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ImportObjectOptions_set_DateFormat, self.Ptr, value)

