from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class Validation (  XlsValidationWrapper) :
    """Represents data validation settings for a cell or range in Excel.
    
    This class extends XlsValidationWrapper and provides functionality for
    defining and managing data validation rules that restrict the type of data
    or values that can be entered into cells in Excel worksheets.
    """
    @property

    def DataRange(self)->'CellRange':
        """Gets or sets the cell range to which the data validation applies.
        
        This property specifies the range of cells that will be validated according
        to the validation rules defined in this object.
        
        Returns:
            CellRange: The cell range object representing the data validation range.
        """
        GetDllLibXls().Validation_get_DataRange.argtypes=[c_void_p]
        GetDllLibXls().Validation_get_DataRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Validation_get_DataRange, self.Ptr)
        from spire.xls import CellRange
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @DataRange.setter
    def DataRange(self, value:'CellRange'):
        GetDllLibXls().Validation_set_DataRange.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().Validation_set_DataRange, self.Ptr, value.Ptr)

