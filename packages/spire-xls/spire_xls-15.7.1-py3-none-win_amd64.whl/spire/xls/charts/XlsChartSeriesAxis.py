from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsChartSeriesAxis (  XlsChartAxis, IChartSeriesAxis) :
    """
    Represents the series axis of a chart.
    """
    @property
    def LabelsFrequency(self)->int:
        """
        Gets or sets the number of categories or series between tick-mark labels.

        Returns:
            int: The number of categories or series between tick-mark labels.
        """
        GetDllLibXls().XlsChartSeriesAxis_get_LabelsFrequency.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSeriesAxis_get_LabelsFrequency.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSeriesAxis_get_LabelsFrequency, self.Ptr)
        return ret

    @LabelsFrequency.setter
    def LabelsFrequency(self, value:int):
        """
        Sets the number of categories or series between tick-mark labels.

        Args:
            value (int): The number of categories or series between tick-mark labels.
        """
        GetDllLibXls().XlsChartSeriesAxis_set_LabelsFrequency.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSeriesAxis_set_LabelsFrequency, self.Ptr, value)

    @property
    def TickLabelSpacing(self)->int:
        """
        Gets or sets the number of categories or series between tick-mark labels.

        Returns:
            int: The number of categories or series between tick-mark labels.
        """
        GetDllLibXls().XlsChartSeriesAxis_get_TickLabelSpacing.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSeriesAxis_get_TickLabelSpacing.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSeriesAxis_get_TickLabelSpacing, self.Ptr)
        return ret

    @TickLabelSpacing.setter
    def TickLabelSpacing(self, value:int):
        """
        Sets the number of categories or series between tick-mark labels.

        Args:
            value (int): The number of categories or series between tick-mark labels.
        """
        GetDllLibXls().XlsChartSeriesAxis_set_TickLabelSpacing.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSeriesAxis_set_TickLabelSpacing, self.Ptr, value)

    @property
    def TickMarksFrequency(self)->int:
        """
        Gets the frequency of tick marks on the series axis.

        Returns:
            int: The frequency of tick marks on the series axis.
        """
        GetDllLibXls().XlsChartSeriesAxis_get_TickMarksFrequency.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSeriesAxis_get_TickMarksFrequency.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSeriesAxis_get_TickMarksFrequency, self.Ptr)
        return ret

    @TickMarksFrequency.setter
    def TickMarksFrequency(self, value:int):
        """
        Sets the frequency of tick marks on the series axis.

        Args:
            value (int): The frequency of tick marks on the series axis.
        """
        GetDllLibXls().XlsChartSeriesAxis_set_TickMarksFrequency.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSeriesAxis_set_TickMarksFrequency, self.Ptr, value)

    @property
    def TickMarkSpacing(self)->int:
        """
        Gets or sets the number of categories or series between tick marks.

        Returns:
            int: The number of categories or series between tick marks.
        """
        GetDllLibXls().XlsChartSeriesAxis_get_TickMarkSpacing.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSeriesAxis_get_TickMarkSpacing.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSeriesAxis_get_TickMarkSpacing, self.Ptr)
        return ret

    @TickMarkSpacing.setter
    def TickMarkSpacing(self, value:int):
        """
        Sets the number of categories or series between tick marks.

        Args:
            value (int): The number of categories or series between tick marks.
        """
        GetDllLibXls().XlsChartSeriesAxis_set_TickMarkSpacing.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSeriesAxis_set_TickMarkSpacing, self.Ptr, value)

    @property
    def IsReverseOrder(self)->bool:
        """
        Gets or sets whether to display categories in reverse order.

        Returns:
            bool: True if categories are displayed in reverse order; otherwise, False.
        """
        GetDllLibXls().XlsChartSeriesAxis_get_IsReverseOrder.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSeriesAxis_get_IsReverseOrder.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSeriesAxis_get_IsReverseOrder, self.Ptr)
        return ret

    @IsReverseOrder.setter
    def IsReverseOrder(self, value:bool):
        """
        Sets whether to display categories in reverse order.

        Args:
            value (bool): True to display categories in reverse order; otherwise, False.
        """
        GetDllLibXls().XlsChartSeriesAxis_set_IsReverseOrder.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSeriesAxis_set_IsReverseOrder, self.Ptr, value)

    @property
    def CrossesAt(self)->int:
        """
        Gets the point at which the series axis crosses.

        Returns:
            int: The point at which the series axis crosses.
        """
        GetDllLibXls().XlsChartSeriesAxis_get_CrossesAt.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSeriesAxis_get_CrossesAt.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSeriesAxis_get_CrossesAt, self.Ptr)
        return ret

    @CrossesAt.setter
    def CrossesAt(self, value:int):
        """
        Sets the point at which the series axis crosses.

        Args:
            value (int): The point at which the series axis crosses.
        """
        GetDllLibXls().XlsChartSeriesAxis_set_CrossesAt.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSeriesAxis_set_CrossesAt, self.Ptr, value)

    @property
    def IsBetween(self)->bool:
        """
        Gets whether the series axis is between categories.

        Returns:
            bool: True if the series axis is between categories; otherwise, False.
        """
        GetDllLibXls().XlsChartSeriesAxis_get_IsBetween.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSeriesAxis_get_IsBetween.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSeriesAxis_get_IsBetween, self.Ptr)
        return ret

    @IsBetween.setter
    def IsBetween(self, value:bool):
        """
        Sets whether the series axis is between categories.

        Args:
            value (bool): True if the series axis is between categories; otherwise, False.
        """
        GetDllLibXls().XlsChartSeriesAxis_set_IsBetween.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSeriesAxis_set_IsBetween, self.Ptr, value)

    @property
    def LogBase(self)->float:
        """
        Gets the logarithmic base for the series axis.

        Returns:
            float: The logarithmic base for the series axis.
        """
        GetDllLibXls().XlsChartSeriesAxis_get_LogBase.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSeriesAxis_get_LogBase.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartSeriesAxis_get_LogBase, self.Ptr)
        return ret

    @LogBase.setter
    def LogBase(self, value:float):
        """
        Sets the logarithmic base for the series axis.

        Args:
            value (float): The logarithmic base for the series axis.
        """
        GetDllLibXls().XlsChartSeriesAxis_set_LogBase.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartSeriesAxis_set_LogBase, self.Ptr, value)

    @property
    def IsLogScale(self)->bool:
        """
        Gets whether the series axis uses a logarithmic scale.

        Returns:
            bool: True if the series axis uses a logarithmic scale; otherwise, False.
        """
        GetDllLibXls().XlsChartSeriesAxis_get_IsLogScale.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSeriesAxis_get_IsLogScale.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSeriesAxis_get_IsLogScale, self.Ptr)
        return ret

    @IsLogScale.setter
    def IsLogScale(self, value:bool):
        """
        Sets whether the series axis uses a logarithmic scale.

        Args:
            value (bool): True if the series axis uses a logarithmic scale; otherwise, False.
        """
        GetDllLibXls().XlsChartSeriesAxis_set_IsLogScale.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSeriesAxis_set_IsLogScale, self.Ptr, value)

    @property
    def MaxValue(self)->float:
        """
        Gets the maximum value of the series axis.

        Returns:
            float: The maximum value of the series axis.
        """
        GetDllLibXls().XlsChartSeriesAxis_get_MaxValue.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSeriesAxis_get_MaxValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartSeriesAxis_get_MaxValue, self.Ptr)
        return ret

    @MaxValue.setter
    def MaxValue(self, value:float):
        """
        Sets the maximum value of the series axis.

        Args:
            value (float): The maximum value of the series axis.
        """
        GetDllLibXls().XlsChartSeriesAxis_set_MaxValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartSeriesAxis_set_MaxValue, self.Ptr, value)

    @property
    def MinValue(self)->float:
        """
        Gets the minimum value of the series axis.

        Returns:
            float: The minimum value of the series axis.
        """
        GetDllLibXls().XlsChartSeriesAxis_get_MinValue.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSeriesAxis_get_MinValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartSeriesAxis_get_MinValue, self.Ptr)
        return ret

    @MinValue.setter
    def MinValue(self, value:float):
        """
        Sets the minimum value of the series axis.

        Args:
            value (float): The minimum value of the series axis.
        """
        GetDllLibXls().XlsChartSeriesAxis_set_MinValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartSeriesAxis_set_MinValue, self.Ptr, value)

#
#    def Clone(self ,parent:'SpireObject',dicFontIndexes:'Dictionary2',dicNewSheetNames:'Dictionary2')->'XlsChartAxis':
#        """
#
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrdicFontIndexes:c_void_p = dicFontIndexes.Ptr
#        intPtrdicNewSheetNames:c_void_p = dicNewSheetNames.Ptr
#
#        GetDllLibXls().XlsChartSeriesAxis_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p]
#        GetDllLibXls().XlsChartSeriesAxis_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsChartSeriesAxis_Clone, self.Ptr, intPtrparent,intPtrdicFontIndexes,intPtrdicNewSheetNames)
#        ret = None if intPtr==None else XlsChartAxis(intPtr)
#        return ret
#


    @staticmethod
    def DefaultSeriesAxisId()->int:
        """
        Gets the default series axis ID.

        Returns:
            int: The default series axis ID.
        """
        #GetDllLibXls().XlsChartSeriesAxis_DefaultSeriesAxisId.argtypes=[]
        GetDllLibXls().XlsChartSeriesAxis_DefaultSeriesAxisId.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSeriesAxis_DefaultSeriesAxisId)
        return ret

