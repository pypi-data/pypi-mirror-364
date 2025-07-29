from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class DataBarBorder (SpireObject) :
    """
    Represents the border of a data bar in conditional formatting.
    """
    @property
    def Color(self)->'Color':
        """
        Gets or sets the color of the data bar border.

        Returns:
            Color: The color of the border.
        """
        GetDllLibXls().DataBarBorder_get_Color.argtypes=[c_void_p]
        GetDllLibXls().DataBarBorder_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().DataBarBorder_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        GetDllLibXls().DataBarBorder_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().DataBarBorder_set_Color, self.Ptr, value.Ptr)

    @property
    def Type(self)->'DataBarBorderType':
        """
        Gets or sets the type of the data bar border.

        Returns:
            DataBarBorderType: The type of the border.
        """
        GetDllLibXls().DataBarBorder_get_Type.argtypes=[c_void_p]
        GetDllLibXls().DataBarBorder_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibXls().DataBarBorder_get_Type, self.Ptr)
        objwraped = DataBarBorderType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'DataBarBorderType'):
        GetDllLibXls().DataBarBorder_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().DataBarBorder_set_Type, self.Ptr, value.value)

