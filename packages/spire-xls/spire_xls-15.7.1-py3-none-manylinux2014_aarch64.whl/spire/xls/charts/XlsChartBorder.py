from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsChartBorder (  XlsObject, IChartBorder, ICloneParent) :
    """
    Represents the border formatting for a chart element, providing properties to customize color, pattern, weight, and transparency.
    """
    @property
    def Color(self)->'Color':
        """
        Gets or sets the color of the border line.

        Returns:
            Color: The color of the border line.
        """
        GetDllLibXls().XlsChartBorder_get_Color.argtypes=[c_void_p]
        GetDllLibXls().XlsChartBorder_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartBorder_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        GetDllLibXls().XlsChartBorder_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChartBorder_set_Color, self.Ptr, value.Ptr)

    @property
    def Pattern(self)->'ChartLinePatternType':
        """
        Gets or sets the line pattern of the border.

        Returns:
            ChartLinePatternType: The line pattern type.
        """
        GetDllLibXls().XlsChartBorder_get_Pattern.argtypes=[c_void_p]
        GetDllLibXls().XlsChartBorder_get_Pattern.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartBorder_get_Pattern, self.Ptr)
        objwraped = ChartLinePatternType(ret)
        return objwraped

    @Pattern.setter
    def Pattern(self, value:'ChartLinePatternType'):
        GetDllLibXls().XlsChartBorder_set_Pattern.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartBorder_set_Pattern, self.Ptr, value.value)

    @property
    def Weight(self)->'ChartLineWeightType':
        """
        Gets or sets the weight (thickness) of the border line.

        Returns:
            ChartLineWeightType: The line weight type.
        """
        GetDllLibXls().XlsChartBorder_get_Weight.argtypes=[c_void_p]
        GetDllLibXls().XlsChartBorder_get_Weight.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartBorder_get_Weight, self.Ptr)
        objwraped = ChartLineWeightType(ret)
        return objwraped

    @Weight.setter
    def Weight(self, value:'ChartLineWeightType'):
        GetDllLibXls().XlsChartBorder_set_Weight.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartBorder_set_Weight, self.Ptr, value.value)

    @property
    def UseDefaultFormat(self)->bool:
        """
        Gets or sets a value indicating whether to use the default border format.

        Returns:
            bool: True to use default format; otherwise, False.
        """
        GetDllLibXls().XlsChartBorder_get_UseDefaultFormat.argtypes=[c_void_p]
        GetDllLibXls().XlsChartBorder_get_UseDefaultFormat.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartBorder_get_UseDefaultFormat, self.Ptr)
        return ret

    @UseDefaultFormat.setter
    def UseDefaultFormat(self, value:bool):
        GetDllLibXls().XlsChartBorder_set_UseDefaultFormat.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartBorder_set_UseDefaultFormat, self.Ptr, value)

    @property
    def UseDefaultLineColor(self)->bool:
        """
        Gets or sets a value indicating whether to use the default line color.

        Returns:
            bool: True to use default line color; otherwise, False.
        """
        GetDllLibXls().XlsChartBorder_get_UseDefaultLineColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartBorder_get_UseDefaultLineColor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartBorder_get_UseDefaultLineColor, self.Ptr)
        return ret

    @UseDefaultLineColor.setter
    def UseDefaultLineColor(self, value:bool):
        GetDllLibXls().XlsChartBorder_set_UseDefaultLineColor.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartBorder_set_UseDefaultLineColor, self.Ptr, value)

    @property
    def KnownColor(self)->'ExcelColors':
        """
        Gets or sets the known Excel color for the border line.

        Returns:
            ExcelColors: The known Excel color.
        """
        GetDllLibXls().XlsChartBorder_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartBorder_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartBorder_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsChartBorder_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartBorder_set_KnownColor, self.Ptr, value.value)

    @property
    def Transparency(self)->float:
        """
        Gets or sets the transparency of the border line.

        Returns:
            float: The transparency value (0.0-1.0).
        """
        GetDllLibXls().XlsChartBorder_get_Transparency.argtypes=[c_void_p]
        GetDllLibXls().XlsChartBorder_get_Transparency.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartBorder_get_Transparency, self.Ptr)
        return ret

    @Transparency.setter
    def Transparency(self, value:float):
        GetDllLibXls().XlsChartBorder_set_Transparency.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartBorder_set_Transparency, self.Ptr, value)

    @property
    def CustomLineWeight(self)->float:
        """
        Gets or sets the custom line weight (thickness) of the border.

        Returns:
            float: The custom line weight value.
        """
        GetDllLibXls().XlsChartBorder_get_CustomLineWeight.argtypes=[c_void_p]
        GetDllLibXls().XlsChartBorder_get_CustomLineWeight.restype=c_float
        ret = CallCFunction(GetDllLibXls().XlsChartBorder_get_CustomLineWeight, self.Ptr)
        return ret

    @CustomLineWeight.setter
    def CustomLineWeight(self, value:float):
        GetDllLibXls().XlsChartBorder_set_CustomLineWeight.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibXls().XlsChartBorder_set_CustomLineWeight, self.Ptr, value)


    def Clone(self ,parent:'SpireObject')->'XlsChartBorder':
        """
        Creates a copy of the current XlsChartBorder instance.

        Args:
            parent (SpireObject): The parent object for the cloned border.
        Returns:
            XlsChartBorder: The cloned XlsChartBorder object.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsChartBorder_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsChartBorder_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartBorder_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else XlsChartBorder(intPtr)
        return ret


