from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ExportTableOptions (SpireObject) :
    """Represents options for exporting Excel tables to other formats.
    
    This class provides properties to control the behavior when exporting Excel tables
    to other formats such as DataTable, CSV, etc. It allows customization of data formatting,
    column names handling, and formula calculation during the export process.
    """
    @property
    def KeepDataFormat(self)->bool:
        """Gets or sets whether to keep the original data format when exporting.
        
        When set to True, the exported data will maintain the same formatting as in Excel.
        When set to False, the data may be converted to native types in the target format.
        
        Returns:
            bool: True if the original data format should be kept; otherwise, False.
        """
        GetDllLibXls().ExportTableOptions_get_KeepDataFormat.argtypes=[c_void_p]
        GetDllLibXls().ExportTableOptions_get_KeepDataFormat.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExportTableOptions_get_KeepDataFormat, self.Ptr)
        return ret

    @KeepDataFormat.setter
    def KeepDataFormat(self, value:bool):
        GetDllLibXls().ExportTableOptions_set_KeepDataFormat.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExportTableOptions_set_KeepDataFormat, self.Ptr, value)

    @property
    def ExportColumnNames(self)->bool:
        """Gets or sets whether to export column names when exporting.
        
        When set to True, the first row of the exported data will contain column names.
        When set to False, only the data will be exported without column names.
        
        Returns:
            bool: True if column names should be exported; otherwise, False.
        """
        GetDllLibXls().ExportTableOptions_get_ExportColumnNames.argtypes=[c_void_p]
        GetDllLibXls().ExportTableOptions_get_ExportColumnNames.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExportTableOptions_get_ExportColumnNames, self.Ptr)
        return ret

    @ExportColumnNames.setter
    def ExportColumnNames(self, value:bool):
        GetDllLibXls().ExportTableOptions_set_ExportColumnNames.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExportTableOptions_set_ExportColumnNames, self.Ptr, value)

    @property

    def RenameStrategy(self)->'RenameStrategy':
        """Gets or sets the strategy for renaming columns when exporting.
        
        This property determines how column names are handled when there are duplicates or invalid names
        in the target format.
        
        Returns:
            RenameStrategy: An enumeration value representing the strategy for renaming columns.
        """
        GetDllLibXls().ExportTableOptions_get_RenameStrategy.argtypes=[c_void_p]
        GetDllLibXls().ExportTableOptions_get_RenameStrategy.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExportTableOptions_get_RenameStrategy, self.Ptr)
        objwraped = RenameStrategy(ret)
        return objwraped

    @RenameStrategy.setter
    def RenameStrategy(self, value:'RenameStrategy'):
        GetDllLibXls().ExportTableOptions_set_RenameStrategy.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExportTableOptions_set_RenameStrategy, self.Ptr, value.value)

    @property
    def ComputedFormulaValue(self)->bool:
        """Gets or sets whether to export the computed values of formulas.
        
        When set to True, the result of formula calculations will be exported.
        When set to False, the formulas themselves may be exported depending on the target format.
        
        Returns:
            bool: True if computed formula values should be exported; otherwise, False.
        """
        GetDllLibXls().ExportTableOptions_get_ComputedFormulaValue.argtypes=[c_void_p]
        GetDllLibXls().ExportTableOptions_get_ComputedFormulaValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExportTableOptions_get_ComputedFormulaValue, self.Ptr)
        return ret

    @ComputedFormulaValue.setter
    def ComputedFormulaValue(self, value:bool):
        GetDllLibXls().ExportTableOptions_set_ComputedFormulaValue.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExportTableOptions_set_ComputedFormulaValue, self.Ptr, value)

