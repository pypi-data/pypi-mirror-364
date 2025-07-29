from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsChartCategoryAxis (  XlsChartAxis, IChartCategoryAxis, IChartValueAxis) :
    """
    Represents the category axis of a chart, providing access to its properties and formatting options.
    """
    @property
    def IsLogScale(self)->bool:
        """
        Gets or sets whether the category axis uses a logarithmic scale.

        Returns:
            bool: True if the category axis uses a logarithmic scale; otherwise, False.
        """
        GetDllLibXls().XlsChartCategoryAxis_get_IsLogScale.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_IsLogScale.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_IsLogScale, self.Ptr)
        return ret

    @IsLogScale.setter
    def IsLogScale(self, value:bool):
        GetDllLibXls().XlsChartCategoryAxis_set_IsLogScale.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_IsLogScale, self.Ptr, value)

    @property
    def MaxValue(self)->float:
        """
        Gets or sets the maximum value on the category axis.

        Returns:
            float: The maximum value on the category axis.
        """
        GetDllLibXls().XlsChartCategoryAxis_get_MaxValue.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_MaxValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_MaxValue, self.Ptr)
        return ret

    @MaxValue.setter
    def MaxValue(self, value:float):
        GetDllLibXls().XlsChartCategoryAxis_set_MaxValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_MaxValue, self.Ptr, value)

    @property
    def MinValue(self)->float:
        """
        Gets or sets the minimum value on the category axis.

        Returns:
            float: The minimum value on the category axis.
        """
        GetDllLibXls().XlsChartCategoryAxis_get_MinValue.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_MinValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_MinValue, self.Ptr)
        return ret

    @MinValue.setter
    def MinValue(self, value:float):
        GetDllLibXls().XlsChartCategoryAxis_set_MinValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_MinValue, self.Ptr, value)

    @property
    def LogBase(self)->float:
        """
        Gets or sets the logarithmic base for the category axis.

        Returns:
            float: The logarithmic base for the category axis.
        """
        GetDllLibXls().XlsChartCategoryAxis_get_LogBase.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_LogBase.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_LogBase, self.Ptr)
        return ret

    @LogBase.setter
    def LogBase(self, value:float):
        GetDllLibXls().XlsChartCategoryAxis_set_LogBase.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_LogBase, self.Ptr, value)

    @property
    def CrossValue(self)->float:
        """
        Value of category axis crosses.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_CrossValue.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_CrossValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_CrossValue, self.Ptr)
        return ret

    @CrossValue.setter
    def CrossValue(self, value:float):
        GetDllLibXls().XlsChartCategoryAxis_set_CrossValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_CrossValue, self.Ptr, value)

    @property
    def CrossesAt(self)->float:
        """
        Represents the point on the axis another axis crosses it.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_CrossesAt.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_CrossesAt.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_CrossesAt, self.Ptr)
        return ret

    @CrossesAt.setter
    def CrossesAt(self, value:float):
        GetDllLibXls().XlsChartCategoryAxis_set_CrossesAt.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_CrossesAt, self.Ptr, value)

    @property
    def IsMaxCross(self)->bool:
        """
        Value axis crosses at the far right category.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_IsMaxCross.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_IsMaxCross.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_IsMaxCross, self.Ptr)
        return ret

    @IsMaxCross.setter
    def IsMaxCross(self, value:bool):
        GetDllLibXls().XlsChartCategoryAxis_set_IsMaxCross.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_IsMaxCross, self.Ptr, value)

    @property
    def CrossingPoint(self)->float:
        """
        Represents the point on the axis another axis crosses it.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_CrossingPoint.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_CrossingPoint.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_CrossingPoint, self.Ptr)
        return ret

    @CrossingPoint.setter
    def CrossingPoint(self, value:float):
        GetDllLibXls().XlsChartCategoryAxis_set_CrossingPoint.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_CrossingPoint, self.Ptr, value)

    @property
    def LabelFrequency(self)->int:
        """
        Frequency of labels.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_LabelFrequency.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_LabelFrequency.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_LabelFrequency, self.Ptr)
        return ret

    @LabelFrequency.setter
    def LabelFrequency(self, value:int):
        GetDllLibXls().XlsChartCategoryAxis_set_LabelFrequency.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_LabelFrequency, self.Ptr, value)

    @property
    def TickLabelSpacing(self)->int:
        """
        Represents the number of categories or series between tick-mark labels.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_TickLabelSpacing.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_TickLabelSpacing.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_TickLabelSpacing, self.Ptr)
        return ret

    @TickLabelSpacing.setter
    def TickLabelSpacing(self, value:int):
        GetDllLibXls().XlsChartCategoryAxis_set_TickLabelSpacing.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_TickLabelSpacing, self.Ptr, value)

    @property
    def TickMarksFrequency(self)->int:
        """
        Frequency of tick marks.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_TickMarksFrequency.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_TickMarksFrequency.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_TickMarksFrequency, self.Ptr)
        return ret

    @TickMarksFrequency.setter
    def TickMarksFrequency(self, value:int):
        GetDllLibXls().XlsChartCategoryAxis_set_TickMarksFrequency.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_TickMarksFrequency, self.Ptr, value)

    @property
    def TickMarkSpacing(self)->int:
        """
        Represents the number of categories or series between tick marks.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_TickMarkSpacing.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_TickMarkSpacing.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_TickMarkSpacing, self.Ptr)
        return ret

    @TickMarkSpacing.setter
    def TickMarkSpacing(self, value:int):
        GetDllLibXls().XlsChartCategoryAxis_set_TickMarkSpacing.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_TickMarkSpacing, self.Ptr, value)

    @property
    def AxisBetweenCategories(self)->bool:
        """
        True if the value axis crosses the category axis between categories

        """
        GetDllLibXls().XlsChartCategoryAxis_get_AxisBetweenCategories.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_AxisBetweenCategories.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_AxisBetweenCategories, self.Ptr)
        return ret

    @AxisBetweenCategories.setter
    def AxisBetweenCategories(self, value:bool):
        GetDllLibXls().XlsChartCategoryAxis_set_AxisBetweenCategories.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_AxisBetweenCategories, self.Ptr, value)

    @property
    def IsReverseOrder(self)->bool:
        """
        Categories in reverse order.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_IsReverseOrder.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_IsReverseOrder.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_IsReverseOrder, self.Ptr)
        return ret

    @IsReverseOrder.setter
    def IsReverseOrder(self, value:bool):
        GetDllLibXls().XlsChartCategoryAxis_set_IsReverseOrder.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_IsReverseOrder, self.Ptr, value)

    @property
    def CategoryLabels(self)->'IXLSRange':
        """
        Gets or sets the range of cells containing the category labels.

        Returns:
            IXLSRange: The range of cells containing the category labels.
        """
        GetDllLibXls().XlsChartCategoryAxis_get_CategoryLabels.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_CategoryLabels.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_CategoryLabels, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret

    @CategoryLabels.setter
    def CategoryLabels(self, value:'IXLSRange'):
        GetDllLibXls().XlsChartCategoryAxis_set_CategoryLabels.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_CategoryLabels, self.Ptr, value.Ptr)

    @property
    def EnteredDirectlyCategoryLabels(self)->List['SpireObject']:
        """
        Entered directly category labels for the chart.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_EnteredDirectlyCategoryLabels.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_EnteredDirectlyCategoryLabels.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_EnteredDirectlyCategoryLabels, self.Ptr)
        ret = GetVectorFromArray(intPtrArray, SpireObject)
        return ret

    @EnteredDirectlyCategoryLabels.setter
    def EnteredDirectlyCategoryLabels(self, value:List['SpireObject']):
        vCount = len(value)
        ArrayType = c_void_p * vCount
        vArray = ArrayType()
        for i in range(0, vCount):
            vArray[i] = value[i].Ptr
        GetDllLibXls().XlsChartCategoryAxis_set_EnteredDirectlyCategoryLabels.argtypes=[c_void_p, ArrayType, c_int]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_EnteredDirectlyCategoryLabels, self.Ptr, vArray, vCount)

    @property
    def CategoryType(self)->'CategoryType':
        """
        Represents axis category type.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_CategoryType.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_CategoryType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_CategoryType, self.Ptr)
        objwraped = CategoryType(ret)
        return objwraped

    @CategoryType.setter
    def CategoryType(self, value:'CategoryType'):
        GetDllLibXls().XlsChartCategoryAxis_set_CategoryType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_CategoryType, self.Ptr, value.value)

    @property
    def Offset(self)->int:
        """
        Represents distance between the labels and axis line. The value can be from 0 through 1000.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_Offset.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_Offset.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_Offset, self.Ptr)
        return ret

    @Offset.setter
    def Offset(self, value:int):
        GetDllLibXls().XlsChartCategoryAxis_set_Offset.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_Offset, self.Ptr, value)

    @property
    def BaseUnit(self)->'ChartBaseUnitType':
        """
        Represents base unit for the specified category axis.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_BaseUnit.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_BaseUnit.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_BaseUnit, self.Ptr)
        objwraped = ChartBaseUnitType(ret)
        return objwraped

    @BaseUnit.setter
    def BaseUnit(self, value:'ChartBaseUnitType'):
        GetDllLibXls().XlsChartCategoryAxis_set_BaseUnit.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_BaseUnit, self.Ptr, value.value)

    @property
    def BaseUnitIsAuto(self)->bool:
        """
        True if use automatic base units for the specified category axis.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_BaseUnitIsAuto.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_BaseUnitIsAuto.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_BaseUnitIsAuto, self.Ptr)
        return ret

    @BaseUnitIsAuto.setter
    def BaseUnitIsAuto(self, value:bool):
        GetDllLibXls().XlsChartCategoryAxis_set_BaseUnitIsAuto.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_BaseUnitIsAuto, self.Ptr, value)

    @property
    def IsAutoMajor(self)->bool:
        """
        Automatic major selected.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_IsAutoMajor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_IsAutoMajor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_IsAutoMajor, self.Ptr)
        return ret

    @IsAutoMajor.setter
    def IsAutoMajor(self, value:bool):
        GetDllLibXls().XlsChartCategoryAxis_set_IsAutoMajor.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_IsAutoMajor, self.Ptr, value)

    @property
    def IsAutoMinor(self)->bool:
        """
        Automatic minor selected.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_IsAutoMinor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_IsAutoMinor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_IsAutoMinor, self.Ptr)
        return ret

    @IsAutoMinor.setter
    def IsAutoMinor(self, value:bool):
        GetDllLibXls().XlsChartCategoryAxis_set_IsAutoMinor.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_IsAutoMinor, self.Ptr, value)

    @property
    def IsAutoCross(self)->bool:
        """
        Automatic category crossing point selected.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_IsAutoCross.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_IsAutoCross.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_IsAutoCross, self.Ptr)
        return ret

    @property
    def IsAutoMax(self)->bool:
        """
        Automatic maximum selected.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_IsAutoMax.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_IsAutoMax.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_IsAutoMax, self.Ptr)
        return ret

    @IsAutoMax.setter
    def IsAutoMax(self, value:bool):
        GetDllLibXls().XlsChartCategoryAxis_set_IsAutoMax.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_IsAutoMax, self.Ptr, value)

    @property
    def IsAutoMin(self)->bool:
        """
        Automatic minimum selected.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_IsAutoMin.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_IsAutoMin.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_IsAutoMin, self.Ptr)
        return ret

    @IsAutoMin.setter
    def IsAutoMin(self, value:bool):
        GetDllLibXls().XlsChartCategoryAxis_set_IsAutoMin.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_IsAutoMin, self.Ptr, value)

    @property
    def MajorUnit(self)->float:
        """
        Value of major increment.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_MajorUnit.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_MajorUnit.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_MajorUnit, self.Ptr)
        return ret

    @MajorUnit.setter
    def MajorUnit(self, value:float):
        GetDllLibXls().XlsChartCategoryAxis_set_MajorUnit.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_MajorUnit, self.Ptr, value)

    @property
    def MinorUnit(self)->float:
        """
        Value of minor increment.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_MinorUnit.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_MinorUnit.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_MinorUnit, self.Ptr)
        return ret

    @MinorUnit.setter
    def MinorUnit(self, value:float):
        GetDllLibXls().XlsChartCategoryAxis_set_MinorUnit.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_MinorUnit, self.Ptr, value)

    @property
    def MajorUnitScale(self)->'ChartBaseUnitType':
        """
        Represens the major unit scale value for the category axis when the CategoryType property is set to TimeScale.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_MajorUnitScale.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_MajorUnitScale.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_MajorUnitScale, self.Ptr)
        objwraped = ChartBaseUnitType(ret)
        return objwraped

    @MajorUnitScale.setter
    def MajorUnitScale(self, value:'ChartBaseUnitType'):
        GetDllLibXls().XlsChartCategoryAxis_set_MajorUnitScale.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_MajorUnitScale, self.Ptr, value.value)

    @property
    def MinorUnitScale(self)->'ChartBaseUnitType':
        """
        Represens the minor unit scale value for the category axis when the CategoryType property is set to TimeScale.

        """
        GetDllLibXls().XlsChartCategoryAxis_get_MinorUnitScale.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_MinorUnitScale.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_MinorUnitScale, self.Ptr)
        objwraped = ChartBaseUnitType(ret)
        return objwraped

    @MinorUnitScale.setter
    def MinorUnitScale(self, value:'ChartBaseUnitType'):
        GetDllLibXls().XlsChartCategoryAxis_set_MinorUnitScale.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_MinorUnitScale, self.Ptr, value.value)

    @property
    def IsBinningByCategory(self)->bool:
        """
        True if bins generated by category values. otherwise False

        """
        GetDllLibXls().XlsChartCategoryAxis_get_IsBinningByCategory.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_IsBinningByCategory.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_IsBinningByCategory, self.Ptr)
        return ret

    @IsBinningByCategory.setter
    def IsBinningByCategory(self, value:bool):
        GetDllLibXls().XlsChartCategoryAxis_set_IsBinningByCategory.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_IsBinningByCategory, self.Ptr, value)

    @property
    def HasAutomaticBins(self)->bool:
        """
        Gets or sets whether the bins are automatically generated.

        Returns:
            bool: True if the bins are automatically generated; otherwise, False.
        """
        GetDllLibXls().XlsChartCategoryAxis_get_HasAutomaticBins.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_HasAutomaticBins.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_HasAutomaticBins, self.Ptr)
        return ret

    @HasAutomaticBins.setter
    def HasAutomaticBins(self, value:bool):
        GetDllLibXls().XlsChartCategoryAxis_set_HasAutomaticBins.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_HasAutomaticBins, self.Ptr, value)

    @property
    def NumberOfBins(self)->int:
        """
        Gets or sets the number of bins for the category axis.

        Returns:
            int: The number of bins for the category axis.
        """
        GetDllLibXls().XlsChartCategoryAxis_get_NumberOfBins.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_NumberOfBins.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_NumberOfBins, self.Ptr)
        return ret

    @NumberOfBins.setter
    def NumberOfBins(self, value:int):
        GetDllLibXls().XlsChartCategoryAxis_set_NumberOfBins.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_NumberOfBins, self.Ptr, value)

    @property
    def BinWidth(self)->float:
        """
        Gets or sets the width of each bin.

        Returns:
            float: The width of each bin.
        """
        GetDllLibXls().XlsChartCategoryAxis_get_BinWidth.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_BinWidth.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_BinWidth, self.Ptr)
        return ret

    @BinWidth.setter
    def BinWidth(self, value:float):
        GetDllLibXls().XlsChartCategoryAxis_set_BinWidth.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_BinWidth, self.Ptr, value)

    @property
    def UnderflowBinValue(self)->float:
        """
        Gets or sets the value below which data points are grouped into the underflow bin.

        Returns:
            float: The value below which data points are grouped into the underflow bin.
        """
        GetDllLibXls().XlsChartCategoryAxis_get_UnderflowBinValue.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_UnderflowBinValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_UnderflowBinValue, self.Ptr)
        return ret

    @UnderflowBinValue.setter
    def UnderflowBinValue(self, value:float):
        GetDllLibXls().XlsChartCategoryAxis_set_UnderflowBinValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_UnderflowBinValue, self.Ptr, value)

    @property
    def OverflowBinValue(self)->float:
        """
        Gets or sets the value above which data points are grouped into the overflow bin.

        Returns:
            float: The value above which data points are grouped into the overflow bin.
        """
        GetDllLibXls().XlsChartCategoryAxis_get_OverflowBinValue.argtypes=[c_void_p]
        GetDllLibXls().XlsChartCategoryAxis_get_OverflowBinValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_get_OverflowBinValue, self.Ptr)
        return ret

    @OverflowBinValue.setter
    def OverflowBinValue(self, value:float):
        GetDllLibXls().XlsChartCategoryAxis_set_OverflowBinValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartCategoryAxis_set_OverflowBinValue, self.Ptr, value)

#
#    def Clone(self ,parent:'SpireObject',dicFontIndexes:'Dictionary2',dicNewSheetNames:'Dictionary2')->'XlsChartAxis':
#        """
#
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrdicFontIndexes:c_void_p = dicFontIndexes.Ptr
#        intPtrdicNewSheetNames:c_void_p = dicNewSheetNames.Ptr
#
#        GetDllLibXls().XlsChartCategoryAxis_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p]
#        GetDllLibXls().XlsChartCategoryAxis_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_Clone, self.Ptr, intPtrparent,intPtrdicFontIndexes,intPtrdicNewSheetNames)
#        ret = None if intPtr==None else XlsChartAxis(intPtr)
#        return ret
#

    @staticmethod
    def DefaultCategoryAxisId()->int:
        """
        Gets the default category axis ID.

        Returns:
            int: The default category axis ID.
        """
        #GetDllLibXls().XlsChartCategoryAxis_DefaultCategoryAxisId.argtypes=[]
        GetDllLibXls().XlsChartCategoryAxis_DefaultCategoryAxisId.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_DefaultCategoryAxisId)
        return ret

    @staticmethod
    def DefaultSecondaryCategoryAxisId()->int:
        """
        Gets the default secondary category axis ID.

        Returns:
            int: The default secondary category axis ID.
        """
        #GetDllLibXls().XlsChartCategoryAxis_DefaultSecondaryCategoryAxisId.argtypes=[]
        GetDllLibXls().XlsChartCategoryAxis_DefaultSecondaryCategoryAxisId.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartCategoryAxis_DefaultSecondaryCategoryAxisId)
        return ret

