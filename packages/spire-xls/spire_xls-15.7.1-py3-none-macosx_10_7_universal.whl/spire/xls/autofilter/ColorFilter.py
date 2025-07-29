from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ColorFilter (SpireObject) :
    """

    """
    @property
    def FilterByFillColor(self)->bool:
        """
        Gets or sets whether to filter by fill color.

        Returns:
            bool: True if filtering by fill color is enabled, otherwise False.
        """
        GetDllLibXls().ColorFilter_get_FilterByFillColor.argtypes=[c_void_p]
        GetDllLibXls().ColorFilter_get_FilterByFillColor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ColorFilter_get_FilterByFillColor, self.Ptr)
        return ret

    @FilterByFillColor.setter
    def FilterByFillColor(self, value:bool):
        """
        Sets whether to filter by fill color.

        Args:
            value (bool): True to enable filtering by fill color, otherwise False.
        """
        GetDllLibXls().ColorFilter_set_FilterByFillColor.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ColorFilter_set_FilterByFillColor, self.Ptr, value)

    @property
    def Value(self)->'Color':
        """
        Gets or sets the color value used for filtering.

        Returns:
            Color: The color used for filtering.
        """
        GetDllLibXls().ColorFilter_get_Value.argtypes=[c_void_p]
        GetDllLibXls().ColorFilter_get_Value.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ColorFilter_get_Value, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    @Value.setter
    def Value(self, value:'Color'):
        """
        Sets the color value used for filtering.

        Args:
            value (Color): The color to use for filtering.
        """
        GetDllLibXls().ColorFilter_set_Value.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ColorFilter_set_Value, self.Ptr, value.Ptr)

