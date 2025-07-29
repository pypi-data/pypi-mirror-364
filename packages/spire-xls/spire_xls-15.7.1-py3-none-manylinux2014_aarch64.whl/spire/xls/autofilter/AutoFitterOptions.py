from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class AutoFitterOptions (SpireObject) :
    """
    Configuration options for automatic column/row sizing operations.
    """
    @property
    def AutoFitMergedCells(self)->bool:
        """
        Indicates whether auto fit row height when the cells is merged in a row. The default value is false.

        Returns:
            bool: True if auto fit is enabled for merged cells, otherwise False.
        """
        GetDllLibXls().AutoFitterOptions_get_AutoFitMergedCells.argtypes=[c_void_p]
        GetDllLibXls().AutoFitterOptions_get_AutoFitMergedCells.restype=c_bool
        ret = CallCFunction(GetDllLibXls().AutoFitterOptions_get_AutoFitMergedCells, self.Ptr)
        return ret

    @AutoFitMergedCells.setter
    def AutoFitMergedCells(self, value:bool):
        """
        Sets whether to auto fit row height when the cells are merged in a row.

        Args:
            value (bool): True to enable auto fit for merged cells, otherwise False.
        """
        GetDllLibXls().AutoFitterOptions_set_AutoFitMergedCells.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().AutoFitterOptions_set_AutoFitMergedCells, self.Ptr, value)

    @property
    def OnlyAuto(self)->bool:
        """
        Indicates whether only fit the rows which height are not customed. The default value is false.

        Returns:
            bool: True if only auto rows are fitted, otherwise False.
        """
        GetDllLibXls().AutoFitterOptions_get_OnlyAuto.argtypes=[c_void_p]
        GetDllLibXls().AutoFitterOptions_get_OnlyAuto.restype=c_bool
        ret = CallCFunction(GetDllLibXls().AutoFitterOptions_get_OnlyAuto, self.Ptr)
        return ret

    @OnlyAuto.setter
    def OnlyAuto(self, value:bool):
        """
        Sets whether only fit the rows which height are not customed.

        Args:
            value (bool): True to fit only auto rows, otherwise False.
        """
        GetDllLibXls().AutoFitterOptions_set_OnlyAuto.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().AutoFitterOptions_set_OnlyAuto, self.Ptr, value)

    @property
    def IgnoreHidden(self)->bool:
        """
        Indicates whether to ignore hidden rows/columns when autofitting. Default is False.

        Returns:
            bool: True if hidden rows/columns are ignored, otherwise False.
        """
        GetDllLibXls().AutoFitterOptions_get_IgnoreHidden.argtypes=[c_void_p]
        GetDllLibXls().AutoFitterOptions_get_IgnoreHidden.restype=c_bool
        ret = CallCFunction(GetDllLibXls().AutoFitterOptions_get_IgnoreHidden, self.Ptr)
        return ret

    @IgnoreHidden.setter
    def IgnoreHidden(self, value:bool):
        """
        Sets whether to ignore hidden rows/columns when autofitting.

        Args:
            value (bool): True to ignore hidden rows/columns, otherwise False.
        """
        GetDllLibXls().AutoFitterOptions_set_IgnoreHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().AutoFitterOptions_set_IgnoreHidden, self.Ptr, value)

