from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsChartValueAxis (  XlsChartAxis, IChartValueAxis) :
    """
    Represents the value axis of a chart, providing access to its properties and formatting options.
    """
    @property
    def LogBase(self)->float:
        """
        Gets or sets the logarithmic base for the value axis.

        Returns:
            float: The logarithmic base for the value axis.
        """
        GetDllLibXls().XlsChartValueAxis_get_LogBase.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_LogBase.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_LogBase, self.Ptr)
        return ret

    @LogBase.setter
    def LogBase(self, value:float):
        GetDllLibXls().XlsChartValueAxis_set_LogBase.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartValueAxis_set_LogBase, self.Ptr, value)

    @property
    def MinValue(self)->float:
        """
        Gets or sets the minimum value on the value axis.

        Returns:
            float: The minimum value on the value axis.
        """
        GetDllLibXls().XlsChartValueAxis_get_MinValue.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_MinValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_MinValue, self.Ptr)
        return ret

    @MinValue.setter
    def MinValue(self, value:float):
        GetDllLibXls().XlsChartValueAxis_set_MinValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartValueAxis_set_MinValue, self.Ptr, value)

    @property
    def MaxValue(self)->float:
        """
        Gets the maximum value on the axis.

        Returns:
            float: The maximum value on the axis.
        """
        GetDllLibXls().XlsChartValueAxis_get_MaxValue.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_MaxValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_MaxValue, self.Ptr)
        return ret

    @MaxValue.setter
    def MaxValue(self, value:float):
        GetDllLibXls().XlsChartValueAxis_set_MaxValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartValueAxis_set_MaxValue, self.Ptr, value)

    @property
    def MajorUnit(self)->float:
        """
        Gets the major unit of the axis.

        Returns:
            float: The major unit of the axis.
        """
        GetDllLibXls().XlsChartValueAxis_get_MajorUnit.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_MajorUnit.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_MajorUnit, self.Ptr)
        return ret

    @MajorUnit.setter
    def MajorUnit(self, value:float):
        GetDllLibXls().XlsChartValueAxis_set_MajorUnit.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartValueAxis_set_MajorUnit, self.Ptr, value)

    @property
    def MinorUnit(self)->float:
        """
        Gets or sets the minor unit value for the value axis.

        Returns:
            float: The minor unit value for the value axis.
        """
        GetDllLibXls().XlsChartValueAxis_get_MinorUnit.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_MinorUnit.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_MinorUnit, self.Ptr)
        return ret

    @MinorUnit.setter
    def MinorUnit(self, value:float):
        GetDllLibXls().XlsChartValueAxis_set_MinorUnit.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartValueAxis_set_MinorUnit, self.Ptr, value)

    @property
    def CrossValue(self)->float:
        """
        Gets or sets the value at which the value axis crosses.

        Returns:
            float: The value at which the value axis crosses.
        """
        GetDllLibXls().XlsChartValueAxis_get_CrossValue.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_CrossValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_CrossValue, self.Ptr)
        return ret

    @CrossValue.setter
    def CrossValue(self, value:float):
        GetDllLibXls().XlsChartValueAxis_set_CrossValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartValueAxis_set_CrossValue, self.Ptr, value)

    @property
    def CrossesAt(self)->float:
        """
        Gets or sets the point at which another axis crosses this value axis.

        Returns:
            float: The point at which another axis crosses this value axis.
        """
        GetDllLibXls().XlsChartValueAxis_get_CrossesAt.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_CrossesAt.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_CrossesAt, self.Ptr)
        return ret

    @CrossesAt.setter
    def CrossesAt(self, value:float):
        GetDllLibXls().XlsChartValueAxis_set_CrossesAt.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartValueAxis_set_CrossesAt, self.Ptr, value)

    @property
    def IsAutoMin(self)->bool:
        """
        Gets whether the minimum value is automatically set.

        Returns:
            bool: True if the minimum value is automatically set; otherwise, False.
        """
        GetDllLibXls().XlsChartValueAxis_get_IsAutoMin.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_IsAutoMin.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_IsAutoMin, self.Ptr)
        return ret

    @IsAutoMin.setter
    def IsAutoMin(self, value:bool):
        GetDllLibXls().XlsChartValueAxis_set_IsAutoMin.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartValueAxis_set_IsAutoMin, self.Ptr, value)

    @property
    def IsAutoMax(self)->bool:
        """
        Gets whether the maximum value is automatically set.

        Returns:
            bool: True if the maximum value is automatically set; otherwise, False.
        """
        GetDllLibXls().XlsChartValueAxis_get_IsAutoMax.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_IsAutoMax.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_IsAutoMax, self.Ptr)
        return ret

    @IsAutoMax.setter
    def IsAutoMax(self, value:bool):
        GetDllLibXls().XlsChartValueAxis_set_IsAutoMax.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartValueAxis_set_IsAutoMax, self.Ptr, value)

    @property
    def IsAutoMajor(self)->bool:
        """
        Gets or sets whether the major unit is automatically set.

        Returns:
            bool: True if the major unit is automatically set; otherwise, False.
        """
        GetDllLibXls().XlsChartValueAxis_get_IsAutoMajor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_IsAutoMajor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_IsAutoMajor, self.Ptr)
        return ret

    @IsAutoMajor.setter
    def IsAutoMajor(self, value:bool):
        GetDllLibXls().XlsChartValueAxis_set_IsAutoMajor.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartValueAxis_set_IsAutoMajor, self.Ptr, value)

    @property
    def IsAutoMinor(self)->bool:
        """
        Gets or sets whether the minor unit is automatically set.

        Returns:
            bool: True if the minor unit is automatically set; otherwise, False.
        """
        GetDllLibXls().XlsChartValueAxis_get_IsAutoMinor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_IsAutoMinor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_IsAutoMinor, self.Ptr)
        return ret

    @IsAutoMinor.setter
    def IsAutoMinor(self, value:bool):
        GetDllLibXls().XlsChartValueAxis_set_IsAutoMinor.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartValueAxis_set_IsAutoMinor, self.Ptr, value)

    @property
    def IsAutoCross(self)->bool:
        """
        Gets whether the crossing point is automatically set.

        Returns:
            bool: True if the crossing point is automatically set; otherwise, False.
        """
        GetDllLibXls().XlsChartValueAxis_get_IsAutoCross.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_IsAutoCross.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_IsAutoCross, self.Ptr)
        return ret

    @property
    def IsLogScale(self)->bool:
        """
        Gets or sets whether the value axis uses a logarithmic scale.

        Returns:
            bool: True if the value axis uses a logarithmic scale; otherwise, False.
        """
        GetDllLibXls().XlsChartValueAxis_get_IsLogScale.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_IsLogScale.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_IsLogScale, self.Ptr)
        return ret

    @IsLogScale.setter
    def IsLogScale(self, value:bool):
        GetDllLibXls().XlsChartValueAxis_set_IsLogScale.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartValueAxis_set_IsLogScale, self.Ptr, value)

    @property
    def IsReverseOrder(self)->bool:
        """
        Gets whether the axis is in reverse order.

        Returns:
            bool: True if the axis is in reverse order; otherwise, False.
        """
        GetDllLibXls().XlsChartValueAxis_get_IsReverseOrder.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_IsReverseOrder.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_IsReverseOrder, self.Ptr)
        return ret

    @IsReverseOrder.setter
    def IsReverseOrder(self, value:bool):
        GetDllLibXls().XlsChartValueAxis_set_IsReverseOrder.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartValueAxis_set_IsReverseOrder, self.Ptr, value)

    @property
    def IsMaxCross(self)->bool:
        """
        Gets whether the axis crosses at the maximum value.

        Returns:
            bool: True if the axis crosses at the maximum value; otherwise, False.
        """
        GetDllLibXls().XlsChartValueAxis_get_IsMaxCross.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_IsMaxCross.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_IsMaxCross, self.Ptr)
        return ret

    @property
    def DisplayUnitCustom(self)->float:
        """
        Gets the custom display unit of the axis.

        Returns:
            float: The custom display unit of the axis.
        """
        GetDllLibXls().XlsChartValueAxis_get_DisplayUnitCustom.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_DisplayUnitCustom.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_DisplayUnitCustom, self.Ptr)
        return ret

    @DisplayUnitCustom.setter
    def DisplayUnitCustom(self, value:float):
        GetDllLibXls().XlsChartValueAxis_set_DisplayUnitCustom.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartValueAxis_set_DisplayUnitCustom, self.Ptr, value)

    @property
    def DisplayUnit(self)->'ChartDisplayUnitType':
        """
        Gets the display unit of the axis.

        Returns:
            ChartDisplayUnitType: The display unit of the axis.
        """
        GetDllLibXls().XlsChartValueAxis_get_DisplayUnit.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_DisplayUnit.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_DisplayUnit, self.Ptr)
        objwraped = ChartDisplayUnitType(ret)
        return objwraped

    @DisplayUnit.setter
    def DisplayUnit(self, value:'ChartDisplayUnitType'):
        GetDllLibXls().XlsChartValueAxis_set_DisplayUnit.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartValueAxis_set_DisplayUnit, self.Ptr, value.value)

    @property
    def HasDisplayUnitLabel(self)->bool:
        """
        Gets whether the axis has a display unit label.

        Returns:
            bool: True if the axis has a display unit label; otherwise, False.
        """
        GetDllLibXls().XlsChartValueAxis_get_HasDisplayUnitLabel.argtypes=[c_void_p]
        GetDllLibXls().XlsChartValueAxis_get_HasDisplayUnitLabel.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartValueAxis_get_HasDisplayUnitLabel, self.Ptr)
        return ret

    @HasDisplayUnitLabel.setter
    def HasDisplayUnitLabel(self, value:bool):
        GetDllLibXls().XlsChartValueAxis_set_HasDisplayUnitLabel.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartValueAxis_set_HasDisplayUnitLabel, self.Ptr, value)

#
#    def Clone(self ,parent:'SpireObject',dicFontIndexes:'Dictionary2',dicNewSheetNames:'Dictionary2')->'XlsChartAxis':
#        """
#
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrdicFontIndexes:c_void_p = dicFontIndexes.Ptr
#        intPtrdicNewSheetNames:c_void_p = dicNewSheetNames.Ptr
#
#        GetDllLibXls().XlsChartValueAxis_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p]
#        GetDllLibXls().XlsChartValueAxis_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsChartValueAxis_Clone, self.Ptr, intPtrparent,intPtrdicFontIndexes,intPtrdicNewSheetNames)
#        ret = None if intPtr==None else XlsChartAxis(intPtr)
#        return ret
#


