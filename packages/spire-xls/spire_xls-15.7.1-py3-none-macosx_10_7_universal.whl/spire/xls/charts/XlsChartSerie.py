from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsChartSerie (  XlsObject, IChartSerie, INamedObject) :
    """
    Represents a chart series in an Excel chart, providing access to its data, formatting, and properties.
    """
    @property
    def ChartGroup(self)->int:
        """
        Gets the chart group number for this series.

        Returns:
            int: The chart group number.
        """
        GetDllLibXls().XlsChartSerie_get_ChartGroup.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_ChartGroup.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerie_get_ChartGroup, self.Ptr)
        return ret

    @property
    def Values(self)->'IXLSRange':
        """
        Gets or sets the range of values for this series.

        Returns:
            IXLSRange: The range containing the series values.
        """
        GetDllLibXls().XlsChartSerie_get_Values.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_Values.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_get_Values, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret

    @Values.setter
    def Values(self, value:'IXLSRange'):
        GetDllLibXls().XlsChartSerie_set_Values.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChartSerie_set_Values, self.Ptr, value.Ptr)

    @property
    def CategoryLabels(self)->'IXLSRange':
        """
        Gets or sets the range of category labels for this series.

        Returns:
            IXLSRange: The range containing the category labels.
        """
        GetDllLibXls().XlsChartSerie_get_CategoryLabels.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_CategoryLabels.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_get_CategoryLabels, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret

    @CategoryLabels.setter
    def CategoryLabels(self, value:'IXLSRange'):
        GetDllLibXls().XlsChartSerie_set_CategoryLabels.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChartSerie_set_CategoryLabels, self.Ptr, value.Ptr)

    @property
    def Bubbles(self)->'IXLSRange':
        """
        Gets or sets the range of bubble sizes for this series.

        Returns:
            IXLSRange: The range containing the bubble sizes.
        """
        GetDllLibXls().XlsChartSerie_get_Bubbles.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_Bubbles.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_get_Bubbles, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret

    @Bubbles.setter
    def Bubbles(self, value:'IXLSRange'):
        GetDllLibXls().XlsChartSerie_set_Bubbles.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChartSerie_set_Bubbles, self.Ptr, value.Ptr)

    @property
    def Name(self)->str:
        """
        Gets or sets the name of this series.

        Returns:
            str: The name of the series.
        """
        GetDllLibXls().XlsChartSerie_get_Name.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartSerie_get_Name, self.Ptr))
        return ret

    @Name.setter
    def Name(self, value:str):
        GetDllLibXls().XlsChartSerie_set_Name.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChartSerie_set_Name, self.Ptr, value)

    @property
    def NamedRange(self)->'CellRange':
        """
        Gets the named range associated with this series.

        Returns:
            CellRange: The named range for the series.
        """
        GetDllLibXls().XlsChartSerie_get_NamedRange.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_NamedRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_get_NamedRange, self.Ptr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret

    @property
    def NameOrFormula(self)->str:
        """
        Gets the name or formula of this series.

        Returns:
            str: The name or formula of the series.
        """
        GetDllLibXls().XlsChartSerie_get_NameOrFormula.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_NameOrFormula.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartSerie_get_NameOrFormula, self.Ptr))
        return ret

    @property
    def Number(self)->int:
        """
        Number of the series.

        """
        GetDllLibXls().XlsChartSerie_get_Number.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_Number.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerie_get_Number, self.Ptr)
        return ret

    @property
    def ParentSeries(self)->'XlsChartSeries':
        """
        Gets parent serie collection. Read - only.

        """
        GetDllLibXls().XlsChartSerie_get_ParentSeries.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_ParentSeries.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_get_ParentSeries, self.Ptr)
        ret = None if intPtr==None else XlsChartSeries(intPtr)
        return ret

    @property
    def UsePrimaryAxis(self)->bool:
        """
        Gets or sets whether this series uses the primary axis.

        Returns:
            bool: True if the series uses the primary axis; otherwise, False.
        """
        GetDllLibXls().XlsChartSerie_get_UsePrimaryAxis.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_UsePrimaryAxis.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerie_get_UsePrimaryAxis, self.Ptr)
        return ret

    @UsePrimaryAxis.setter
    def UsePrimaryAxis(self, value:bool):
        GetDllLibXls().XlsChartSerie_set_UsePrimaryAxis.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerie_set_UsePrimaryAxis, self.Ptr, value)

    @property
    def HasDroplines(self)->bool:
        """
        Gets or sets whether this series has droplines.

        Returns:
            bool: True if the series has droplines; otherwise, False.
        """
        GetDllLibXls().XlsChartSerie_get_HasDroplines.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_HasDroplines.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerie_get_HasDroplines, self.Ptr)
        return ret

    @HasDroplines.setter
    def HasDroplines(self, value:bool):
        GetDllLibXls().XlsChartSerie_set_HasDroplines.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerie_set_HasDroplines, self.Ptr, value)

    @property
    def DataPoints(self)->'IChartDataPoints':
        """
        Gets the collection of data points in this series.

        Returns:
            IChartDataPoints: The collection of data points.
        """
        GetDllLibXls().XlsChartSerie_get_DataPoints.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_DataPoints.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_get_DataPoints, self.Ptr)
        ret = None if intPtr==None else XlsChartDataPointsCollection(intPtr)
        return ret

    @property
    def PointNumber(self)->int:
        """
        Returns number of points in the series. Read-only.

        """
        GetDllLibXls().XlsChartSerie_get_PointNumber.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_PointNumber.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerie_get_PointNumber, self.Ptr)
        return ret

    @property
    def RealIndex(self)->int:
        """
        Gets or sets the real index of this series.

        Returns:
            int: The real index of the series.
        """
        GetDllLibXls().XlsChartSerie_get_RealIndex.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_RealIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerie_get_RealIndex, self.Ptr)
        return ret

    @RealIndex.setter
    def RealIndex(self, value:int):
        GetDllLibXls().XlsChartSerie_set_RealIndex.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerie_set_RealIndex, self.Ptr, value)

    @property
    def Format(self)->'IChartSerieDataFormat':
        """
        Gets the data format for this series.

        Returns:
            IChartSerieDataFormat: The data format of the series.
        """
        GetDllLibXls().XlsChartSerie_get_Format.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_Format.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_get_Format, self.Ptr)
        ret = None if intPtr==None else XlsChartSerieDataFormat(intPtr)
        return ret

    @property
    def SerieType(self)->'ExcelChartType':
        """
        Gets or sets the chart type for this series.

        Returns:
            ExcelChartType: The chart type of the series.
        """
        GetDllLibXls().XlsChartSerie_get_SerieType.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_SerieType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerie_get_SerieType, self.Ptr)
        objwraped = ExcelChartType(ret)
        return objwraped

    @SerieType.setter
    def SerieType(self, value:'ExcelChartType'):
        GetDllLibXls().XlsChartSerie_set_SerieType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerie_set_SerieType, self.Ptr, value.value)

    @property
    def StartType(self)->str:
        """
        Returns serie start type. Read-only.

        """
        GetDllLibXls().XlsChartSerie_get_StartType.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_StartType.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartSerie_get_StartType, self.Ptr))
        return ret

    @property
    def EnteredDirectlyValues(self)->List['SpireObject']:
        """
        Gets or sets the directly entered values for this series.

        Returns:
            List[SpireObject]: The list of directly entered values.
        """
        GetDllLibXls().XlsChartSerie_get_EnteredDirectlyValues.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_EnteredDirectlyValues.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().XlsChartSerie_get_EnteredDirectlyValues, self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, SpireObject)
        return ret

    @EnteredDirectlyValues.setter
    def EnteredDirectlyValues(self, value:List['SpireObject']):
        vCount = len(value)
        ArrayType = c_void_p * vCount
        vArray = ArrayType()
        for i in range(0, vCount):
            vArray[i] = value[i].Ptr
        GetDllLibXls().XlsChartSerie_set_EnteredDirectlyValues.argtypes=[c_void_p, ArrayType, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerie_set_EnteredDirectlyValues, self.Ptr, vArray, vCount)

    @property
    def EnteredDirectlyCategoryLabels(self)->List['SpireObject']:
        """
        Gets or sets the directly entered category labels for this series.

        Returns:
            List[SpireObject]: The list of directly entered category labels.
        """
        GetDllLibXls().XlsChartSerie_get_EnteredDirectlyCategoryLabels.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_EnteredDirectlyCategoryLabels.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().XlsChartSerie_get_EnteredDirectlyCategoryLabels, self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, SpireObject)
        return ret

    @EnteredDirectlyCategoryLabels.setter
    def EnteredDirectlyCategoryLabels(self, value:List['SpireObject']):
        vCount = len(value)
        ArrayType = c_void_p * vCount
        vArray = ArrayType()
        for i in range(0, vCount):
            vArray[i] = value[i].Ptr
        GetDllLibXls().XlsChartSerie_set_EnteredDirectlyCategoryLabels.argtypes=[c_void_p, ArrayType, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerie_set_EnteredDirectlyCategoryLabels, self.Ptr, vArray, vCount)

    @property
    def EnteredDirectlyBubbles(self)->List['SpireObject']:
        """
        Gets or sets the directly entered bubble sizes for this series.

        Returns:
            List[SpireObject]: The list of directly entered bubble sizes.
        """
        GetDllLibXls().XlsChartSerie_get_EnteredDirectlyBubbles.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_EnteredDirectlyBubbles.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().XlsChartSerie_get_EnteredDirectlyBubbles, self.Ptr)
        ret = GetVectorFromArray(intPtrArray, SpireObject)
        return ret

    @EnteredDirectlyBubbles.setter
    def EnteredDirectlyBubbles(self, value:List['SpireObject']):
        vCount = len(value)
        ArrayType = c_void_p * vCount
        vArray = ArrayType()
        for i in range(0, vCount):
            vArray[i] = value[i].Ptr
        GetDllLibXls().XlsChartSerie_set_EnteredDirectlyBubbles.argtypes=[c_void_p, ArrayType, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerie_set_EnteredDirectlyBubbles, self.Ptr, vArray, vCount)

    @property
    def ErrorBarsY(self)->'IChartErrorBars':
        """
        Represents Y error bars. Read only.

        """
        GetDllLibXls().XlsChartSerie_get_ErrorBarsY.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_ErrorBarsY.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_get_ErrorBarsY, self.Ptr)
        ret = None if intPtr==None else IChartErrorBars(intPtr)
        return ret

    @property
    def HasErrorBarsY(self)->bool:
        """
        Indicates if serie contains Y error bars.

        """
        GetDllLibXls().XlsChartSerie_get_HasErrorBarsY.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_HasErrorBarsY.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerie_get_HasErrorBarsY, self.Ptr)
        return ret

    @HasErrorBarsY.setter
    def HasErrorBarsY(self, value:bool):
        GetDllLibXls().XlsChartSerie_set_HasErrorBarsY.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerie_set_HasErrorBarsY, self.Ptr, value)

    @property
    def ErrorBarsX(self)->'IChartErrorBars':
        """
        Represents X error bars. Read only.

        """
        GetDllLibXls().XlsChartSerie_get_ErrorBarsX.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_ErrorBarsX.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_get_ErrorBarsX, self.Ptr)
        ret = None if intPtr==None else IChartErrorBars(intPtr)
        return ret

    @property
    def HasErrorBarsX(self)->bool:
        """
        Indicates if serie contains X error bars.

        """
        GetDllLibXls().XlsChartSerie_get_HasErrorBarsX.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_HasErrorBarsX.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerie_get_HasErrorBarsX, self.Ptr)
        return ret

    @HasErrorBarsX.setter
    def HasErrorBarsX(self, value:bool):
        GetDllLibXls().XlsChartSerie_set_HasErrorBarsX.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerie_set_HasErrorBarsX, self.Ptr, value)

    @property
    def TrendLines(self)->'IChartTrendLines':
        """
        Represents serie trend lines collection. Read only.

        """
        GetDllLibXls().XlsChartSerie_get_TrendLines.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_TrendLines.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_get_TrendLines, self.Ptr)
        ret = None if intPtr==None else IChartTrendLines(intPtr)
        return ret

    @property
    def InvertNegaColor(self)->bool:
        """
        Indicates wheter to invert its colors if the value is negative.

        """
        GetDllLibXls().XlsChartSerie_get_InvertNegaColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_InvertNegaColor.restype=c_bool
        return CallCFunction(GetDllLibXls().XlsChartSerie_get_InvertNegaColor, self.Ptr)

    @InvertNegaColor.setter
    def InvertNegaColor(self, value:bool):
        GetDllLibXls().XlsChartSerie_set_InvertNegaColor.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerie_set_InvertNegaColor, self.Ptr, value)

    @property
    def Index(self)->int:
        """
        Represents index of the series.

        """
        GetDllLibXls().XlsChartSerie_get_Index.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_Index.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerie_get_Index, self.Ptr)
        return ret

    @property
    def DataLabels(self)->'IChartDataLabels':
        """
        Gets the data labels for this series.

        Returns:
            IChartDataLabels: The data labels of the series.
        """
        GetDllLibXls().XlsChartSerie_get_DataLabels.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_DataLabels.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_get_DataLabels, self.Ptr)
        ret = None if intPtr==None else XlsChartDataLabels(intPtr)
        return ret

    @property
    def ParetoLineFormat(self)->'IChartFrameFormat':
        """
        Gets the Pareto line format for this series.

        Returns:
            IChartFrameFormat: The Pareto line format of the series.
        """
        GetDllLibXls().XlsChartSerie_get_ParetoLineFormat.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_get_ParetoLineFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_get_ParetoLineFormat, self.Ptr)
        ret = None if intPtr==None else XlsChartFrameFormat(intPtr)
        return ret

    @dispatch
    def ErrorBar(self ,bIsY:bool)->IChartErrorBars:
        """
        Gets the error bars for this series.

        Args:
            bIsY (bool): True for Y error bars, False for X error bars.

        Returns:
            IChartErrorBars: The error bars of the series.
        """
        GetDllLibXls().XlsChartSerie_ErrorBar.argtypes=[c_void_p ,c_bool]
        GetDllLibXls().XlsChartSerie_ErrorBar.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_ErrorBar, self.Ptr, bIsY)
        ret = None if intPtr==None else IChartErrorBars(intPtr)
        return ret

    @dispatch
    def ErrorBar(self ,bIsY:bool,include:ErrorBarIncludeType)->IChartErrorBars:
        """
        Gets the error bars for this series with specified include type.

        Args:
            bIsY (bool): True for Y error bars, False for X error bars.
            include (ErrorBarIncludeType): The include type for error bars.

        Returns:
            IChartErrorBars: The error bars of the series.
        """
        enuminclude:c_int = include.value

        GetDllLibXls().XlsChartSerie_ErrorBarBI.argtypes=[c_void_p ,c_bool,c_int]
        GetDllLibXls().XlsChartSerie_ErrorBarBI.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_ErrorBarBI, self.Ptr, bIsY,enuminclude)
        ret = None if intPtr==None else IChartErrorBars(intPtr)
        return ret

    @dispatch
    def ErrorBar(self ,bIsY:bool,include:ErrorBarIncludeType,type:ErrorBarType)->IChartErrorBars:
        """
        Gets the error bars for this series with specified include type and error bar type.

        Args:
            bIsY (bool): True for Y error bars, False for X error bars.
            include (ErrorBarIncludeType): The include type for error bars.
            type (ErrorBarType): The type of error bars.

        Returns:
            IChartErrorBars: The error bars of the series.
        """
        enuminclude:c_int = include.value
        enumtype:c_int = type.value

        GetDllLibXls().XlsChartSerie_ErrorBarBIT.argtypes=[c_void_p ,c_bool,c_int,c_int]
        GetDllLibXls().XlsChartSerie_ErrorBarBIT.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_ErrorBarBIT, self.Ptr, bIsY,enuminclude,enumtype)
        ret = None if intPtr==None else IChartErrorBars(intPtr)
        return ret

    @dispatch
    def ErrorBar(self ,bIsY:bool,include:ErrorBarIncludeType,type:ErrorBarType,numberValue:float)->IChartErrorBars:
        """
        Gets the error bars for this series with specified include type, error bar type, and number value.

        Args:
            bIsY (bool): True for Y error bars, False for X error bars.
            include (ErrorBarIncludeType): The include type for error bars.
            type (ErrorBarType): The type of error bars.
            numberValue (float): The number value for error bars.

        Returns:
            IChartErrorBars: The error bars of the series.
        """
        enuminclude:c_int = include.value
        enumtype:c_int = type.value

        GetDllLibXls().XlsChartSerie_ErrorBarBITN.argtypes=[c_void_p ,c_bool,c_int,c_int,c_double]
        GetDllLibXls().XlsChartSerie_ErrorBarBITN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_ErrorBarBITN, self.Ptr, bIsY,enuminclude,enumtype,numberValue)
        ret = None if intPtr==None else IChartErrorBars(intPtr)
        return ret

    @dispatch
    def ErrorBar(self ,bIsY:bool,plusRange:IXLSRange,minusRange:IXLSRange)->IChartErrorBars:
        """
        Gets the error bars for this series with specified plus and minus ranges.

        Args:
            bIsY (bool): True for Y error bars, False for X error bars.
            plusRange (IXLSRange): The range for plus error values.
            minusRange (IXLSRange): The range for minus error values.

        Returns:
            IChartErrorBars: The error bars of the series.
        """
        intPtrplusRange:c_void_p = plusRange.Ptr
        intPtrminusRange:c_void_p = minusRange.Ptr

        GetDllLibXls().XlsChartSerie_ErrorBarBPM.argtypes=[c_void_p ,c_bool,c_void_p,c_void_p]
        GetDllLibXls().XlsChartSerie_ErrorBarBPM.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_ErrorBarBPM, self.Ptr, bIsY,intPtrplusRange,intPtrminusRange)
        ret = None if intPtr==None else IChartErrorBars(intPtr)
        return ret

    def GetCommonSerieFormat(self)->'XlsChartFormat':
        """
        Gets the common format for this series.

        Returns:
            XlsChartFormat: The common format of the series.
        """
        GetDllLibXls().XlsChartSerie_GetCommonSerieFormat.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_GetCommonSerieFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_GetCommonSerieFormat, self.Ptr)
        ret = None if intPtr==None else XlsChartFormat(intPtr)
        return ret

    def GetSerieNameRange(self)->'IXLSRange':
        """
        Gets the range containing the series name.

        Returns:
            IXLSRange: The range containing the series name.
        """
        GetDllLibXls().XlsChartSerie_GetSerieNameRange.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerie_GetSerieNameRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerie_GetSerieNameRange, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret

    def SetDefaultName(self ,defaultName:str):
        """
        Sets the default name for this series.

        Args:
            defaultName (str): The default name to set.
        """
        GetDllLibXls().XlsChartSerie_SetDefaultName.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsChartSerie_SetDefaultName, self.Ptr, defaultName)

