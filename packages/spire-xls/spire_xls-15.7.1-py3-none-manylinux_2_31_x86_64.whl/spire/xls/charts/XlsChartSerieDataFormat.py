from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from spire.xls.charts.ChartBorder import *
from ctypes import *
import abc

class XlsChartSerieDataFormat (  XlsObject, IChartSerieDataFormat, IChartFillBorder) :
    """
    Represents the data format of a chart series, including properties for formatting, markers, and visual effects.
    """
    @property
    def ShowMeanMarkers(self)->bool:
        """
        Gets or sets whether to display mean markers in a Box and Whisker chart.

        Returns:
            bool: True if mean markers should be displayed; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowMeanMarkers.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowMeanMarkers.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_ShowMeanMarkers, self.Ptr)
        return ret

    @ShowMeanMarkers.setter
    def ShowMeanMarkers(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_ShowMeanMarkers.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_ShowMeanMarkers, self.Ptr, value)

    @property
    def ShowInnerPoints(self)->bool:
        """
        Gets or sets whether to display inner points in a Box and Whisker chart.

        Returns:
            bool: True if inner points should be displayed; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowInnerPoints.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowInnerPoints.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_ShowInnerPoints, self.Ptr)
        return ret

    @ShowInnerPoints.setter
    def ShowInnerPoints(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_ShowInnerPoints.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_ShowInnerPoints, self.Ptr, value)

    @property
    def ShowOutlierPoints(self)->bool:
        """
        Gets or sets whether to display outlier points in a Box and Whisker chart.

        Returns:
            bool: True if outlier points should be displayed; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowOutlierPoints.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowOutlierPoints.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_ShowOutlierPoints, self.Ptr)
        return ret

    @ShowOutlierPoints.setter
    def ShowOutlierPoints(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_ShowOutlierPoints.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_ShowOutlierPoints, self.Ptr, value)

    @property
    def QuartileCalculationType(self)->'ExcelQuartileCalculation':
        """
        Gets or sets whether the quartile calculation is exclusive or inclusive.

        Returns:
            ExcelQuartileCalculation: The quartile calculation type.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_QuartileCalculationType.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_QuartileCalculationType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_QuartileCalculationType, self.Ptr)
        objwraped = ExcelQuartileCalculation(ret)
        return objwraped

    @QuartileCalculationType.setter
    def QuartileCalculationType(self, value:'ExcelQuartileCalculation'):
        GetDllLibXls().XlsChartSerieDataFormat_set_QuartileCalculationType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_QuartileCalculationType, self.Ptr, value.value)

    @property
    def MarkerBackColorObject(self)->'OColor':
        """
        Gets the object that holds the marker background color.

        Returns:
            OColor: The marker background color object.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerBackColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerBackColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_MarkerBackColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret

    @property
    def MarkerForeColorObject(self)->'OColor':
        """
        Gets the object that holds the marker foreground color.

        Returns:
            OColor: The marker foreground color object.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerForeColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerForeColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_MarkerForeColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret

    @property
    def AreaProperties(self)->'IChartInterior':
        """
        Gets the area properties of the chart series data format.

        Returns:
            IChartInterior: The area properties of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_AreaProperties.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_AreaProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_AreaProperties, self.Ptr)
        ret = None if intPtr==None else IChartInterior(intPtr)
        return ret

    @property
    def BarType(self)->'BaseFormatType':
        """
        Gets the bar type of the chart series data format.

        Returns:
            BaseFormatType: The bar type of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_BarType.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_BarType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_BarType, self.Ptr)
        objwraped = BaseFormatType(ret)
        return objwraped

    @BarType.setter
    def BarType(self, value:'BaseFormatType'):
        GetDllLibXls().XlsChartSerieDataFormat_set_BarType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_BarType, self.Ptr, value.value)

    @property
    def BarTopType(self)->'TopFormatType':
        """
        Gets the bar top type of the chart series data format.

        Returns:
            TopFormatType: The bar top type of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_BarTopType.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_BarTopType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_BarTopType, self.Ptr)
        objwraped = TopFormatType(ret)
        return objwraped

    @BarTopType.setter
    def BarTopType(self, value:'TopFormatType'):
        GetDllLibXls().XlsChartSerieDataFormat_set_BarTopType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_BarTopType, self.Ptr, value.value)

    @property
    def MarkerBackgroundColor(self)->'Color':
        """
        Gets the marker background color of the chart series data format.

        Returns:
            Color: The marker background color of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerBackgroundColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerBackgroundColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_MarkerBackgroundColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    @MarkerBackgroundColor.setter
    def MarkerBackgroundColor(self, value:'Color'):
        GetDllLibXls().XlsChartSerieDataFormat_set_MarkerBackgroundColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_MarkerBackgroundColor, self.Ptr, value.Ptr)

    @property
    def MarkerForegroundColor(self)->'Color':
        """
        Gets the marker foreground color of the chart series data format.

        Returns:
            Color: The marker foreground color of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerForegroundColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerForegroundColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_MarkerForegroundColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    @MarkerForegroundColor.setter
    def MarkerForegroundColor(self, value:'Color'):
        GetDllLibXls().XlsChartSerieDataFormat_set_MarkerForegroundColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_MarkerForegroundColor, self.Ptr, value.Ptr)

    @property
    def MarkerStyle(self)->'ChartMarkerType':
        """
        Gets the marker style of the chart series data format.

        Returns:
            ChartMarkerType: The marker style of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_MarkerStyle, self.Ptr)
        objwraped = ChartMarkerType(ret)
        return objwraped

    @MarkerStyle.setter
    def MarkerStyle(self, value:'ChartMarkerType'):
        GetDllLibXls().XlsChartSerieDataFormat_set_MarkerStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_MarkerStyle, self.Ptr, value.value)

    @property
    def MarkerForegroundKnownColor(self)->'ExcelColors':
        """
        Gets the marker foreground known color of the chart series data format.

        Returns:
            ExcelColors: The marker foreground known color of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerForegroundKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerForegroundKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_MarkerForegroundKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @MarkerForegroundKnownColor.setter
    def MarkerForegroundKnownColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsChartSerieDataFormat_set_MarkerForegroundKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_MarkerForegroundKnownColor, self.Ptr, value.value)

    @property
    def MarkerBackgroundKnownColor(self)->'ExcelColors':
        """
        Gets the marker background known color of the chart series data format.

        Returns:
            ExcelColors: The marker background known color of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerBackgroundKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerBackgroundKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_MarkerBackgroundKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @MarkerBackgroundKnownColor.setter
    def MarkerBackgroundKnownColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsChartSerieDataFormat_set_MarkerBackgroundKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_MarkerBackgroundKnownColor, self.Ptr, value.value)

    @property
    def MarkerSize(self)->int:
        """
        Gets the marker size of the chart series data format.

        Returns:
            int: The marker size of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerSize.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerSize.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_MarkerSize, self.Ptr)
        return ret

    @MarkerSize.setter
    def MarkerSize(self, value:int):
        GetDllLibXls().XlsChartSerieDataFormat_set_MarkerSize.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_MarkerSize, self.Ptr, value)

    @property
    def IsAutoMarker(self)->bool:
        """
        Gets whether the marker is automatically set.

        Returns:
            bool: True if the marker is automatically set; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_IsAutoMarker.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_IsAutoMarker.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_IsAutoMarker, self.Ptr)
        return ret

    @IsAutoMarker.setter
    def IsAutoMarker(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_IsAutoMarker.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_IsAutoMarker, self.Ptr, value)

    @property
    def Percent(self)->int:
        """
        Gets the percent of the chart series data format.

        Returns:
            int: The percent of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_Percent.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_Percent.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_Percent, self.Ptr)
        return ret

    @Percent.setter
    def Percent(self, value:int):
        GetDllLibXls().XlsChartSerieDataFormat_set_Percent.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_Percent, self.Ptr, value)

    @property
    def Is3DBubbles(self)->bool:
        """
        Gets whether the chart series data format uses 3D bubbles.

        Returns:
            bool: True if the chart series data format uses 3D bubbles; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_Is3DBubbles.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_Is3DBubbles.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_Is3DBubbles, self.Ptr)
        return ret

    @Is3DBubbles.setter
    def Is3DBubbles(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_Is3DBubbles.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_Is3DBubbles, self.Ptr, value)

    @property
    def Options(self)->'IChartFormat':
        """
        Gets the options of the chart series data format.

        Returns:
            IChartFormat: The options of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_Options.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_Options.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_Options, self.Ptr)
        ret = None if intPtr==None else XlsChartFormat(intPtr)
        return ret

    @property
    def IsMarkerSupported(self)->bool:
        """
        Gets whether the marker is supported.

        Returns:
            bool: True if the marker is supported; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_IsMarkerSupported.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_IsMarkerSupported.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_IsMarkerSupported, self.Ptr)
        return ret

    @property
    def IsShadow(self)->bool:
        """
        Gets whether the chart series data format has a shadow.

        Returns:
            bool: True if the chart series data format has a shadow; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_IsShadow.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_IsShadow.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_IsShadow, self.Ptr)
        return ret

    @IsShadow.setter
    def IsShadow(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_IsShadow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_IsShadow, self.Ptr, value)

    @property
    def IsShowBackground(self)->bool:
        """
        Gets whether the background is shown.

        Returns:
            bool: True if the background is shown; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_IsShowBackground.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_IsShowBackground.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_IsShowBackground, self.Ptr)
        return ret

    @property
    def IsShowForeground(self)->bool:
        """
        Gets whether the foreground is shown.

        Returns:
            bool: True if the foreground is shown; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_IsShowForeground.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_IsShowForeground.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_IsShowForeground, self.Ptr)
        return ret

    @property
    def IsSmoothed(self)->bool:
        """
        Gets whether the chart series data format is smoothed.

        Returns:
            bool: True if the chart series data format is smoothed; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_IsSmoothed.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_IsSmoothed.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_IsSmoothed, self.Ptr)
        return ret

    @property
    def IsSmoothedLine(self)->bool:
        """
        Gets whether the chart series data format has a smoothed line.

        Returns:
            bool: True if the chart series data format has a smoothed line; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_IsSmoothedLine.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_IsSmoothedLine.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_IsSmoothedLine, self.Ptr)
        return ret

    @IsSmoothedLine.setter
    def IsSmoothedLine(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_IsSmoothedLine.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_IsSmoothedLine, self.Ptr, value)

    @property
    def IsSupportFill(self)->bool:
        """
        Gets whether the chart series data format supports fill.

        Returns:
            bool: True if the chart series data format supports fill; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_IsSupportFill.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_IsSupportFill.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_IsSupportFill, self.Ptr)
        return ret

    @property
    def HasInterior(self)->bool:
        """
        Gets whether the chart series data format has an interior.

        Returns:
            bool: True if the chart series data format has an interior; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_HasInterior.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_HasInterior.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_HasInterior, self.Ptr)
        return ret

    @property
    def HasLineProperties(self)->bool:
        """
        Gets whether the chart series data format has line properties.

        Returns:
            bool: True if the chart series data format has line properties; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_HasLineProperties.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_HasLineProperties.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_HasLineProperties, self.Ptr)
        return ret

    @property
    def HasFormat3D(self)->bool:
        """
        Gets whether the chart series data format has 3D format.

        Returns:
            bool: True if the chart series data format has 3D format; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_HasFormat3D.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_HasFormat3D.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_HasFormat3D, self.Ptr)
        return ret

    @property
    def HasShadow(self)->bool:
        """
        Gets whether the chart series data format has a shadow.

        Returns:
            bool: True if the chart series data format has a shadow; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_HasShadow.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_HasShadow.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_HasShadow, self.Ptr)
        return ret

    @property
    def LineProperties(self)->'ChartBorder':
        """
        Gets the line properties of the chart series data format.

        Returns:
            ChartBorder: The line properties of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_LineProperties.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_LineProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_LineProperties, self.Ptr)
        ret = None if intPtr==None else ChartBorder(intPtr)
        return ret

    @property
    def Interior(self)->'IChartInterior':
        """
        Gets the interior of the chart series data format.

        Returns:
            IChartInterior: The interior of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_Interior.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_Interior.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_Interior, self.Ptr)
        ret = None if intPtr==None else IChartInterior(intPtr)
        return ret

    @property
    def Fill(self)->'IShapeFill':
        """
        Gets the fill of the chart series data format.

        Returns:
            IShapeFill: The fill of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_Fill.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_Fill, self.Ptr)
        ret = None if intPtr==None else XlsShapeFill(intPtr)
        return ret

    @property
    def MarkerFill(self)->'IShapeFill':
        """
        Gets the marker fill of the chart series data format.

        Returns:
            IShapeFill: The marker fill of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerFill.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_MarkerFill, self.Ptr)
        ret = None if intPtr==None else XlsShapeFill(intPtr)
        return ret

    @property
    def Format3D(self)->'Format3D':
        """
        Gets the 3D format of the chart series data format.

        Returns:
            Format3D: The 3D format of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_Format3D.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_Format3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_Format3D, self.Ptr)
        ret = None if intPtr==None else Format3D(intPtr)
        return ret

    @property
    def Shadow(self)->'ChartShadow':
        """
        Gets the shadow of the chart series data format.

        Returns:
            ChartShadow: The shadow of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_Shadow.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_Shadow.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_Shadow, self.Ptr)
        ret = None if intPtr==None else ChartShadow(intPtr)
        return ret

    @property
    def ForeGroundColor(self)->'Color':
        """
        Gets the foreground color of the chart series data format.

        Returns:
            Color: The foreground color of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_ForeGroundColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_ForeGroundColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_ForeGroundColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    @ForeGroundColor.setter
    def ForeGroundColor(self, value:'Color'):
        GetDllLibXls().XlsChartSerieDataFormat_set_ForeGroundColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_ForeGroundColor, self.Ptr, value.Ptr)

    @property
    def ForeGroundKnownColor(self)->'ExcelColors':
        """
        Gets the foreground known color of the chart series data format.

        Returns:
            ExcelColors: The foreground known color of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_ForeGroundKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_ForeGroundKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_ForeGroundKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @ForeGroundKnownColor.setter
    def ForeGroundKnownColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsChartSerieDataFormat_set_ForeGroundKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_ForeGroundKnownColor, self.Ptr, value.value)

    @property
    def MarkerTransparencyValue(self)->float:
        """
        Gets the marker transparency value of the chart series data format.

        Returns:
            float: The marker transparency value of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerTransparencyValue.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerTransparencyValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_MarkerTransparencyValue, self.Ptr)
        return ret

    @MarkerTransparencyValue.setter
    def MarkerTransparencyValue(self, value:float):
        GetDllLibXls().XlsChartSerieDataFormat_set_MarkerTransparencyValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_MarkerTransparencyValue, self.Ptr, value)

    @property
    def ForeGroundColorObject(self)->'OColor':
        """
        Gets the foreground color object of the chart series data format.

        Returns:
            OColor: The foreground color object of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_ForeGroundColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_ForeGroundColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_ForeGroundColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret

    @property
    def BackGroundKnownColor(self)->'ExcelColors':
        """
        Gets the background known color of the chart series data format.

        Returns:
            ExcelColors: The background known color of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_BackGroundKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_BackGroundKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_BackGroundKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @BackGroundKnownColor.setter
    def BackGroundKnownColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsChartSerieDataFormat_set_BackGroundKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_BackGroundKnownColor, self.Ptr, value.value)

    @property
    def BackGroundColor(self)->'Color':
        """
        Gets the background color of the chart series data format.

        Returns:
            Color: The background color of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_BackGroundColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_BackGroundColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_BackGroundColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    @BackGroundColor.setter
    def BackGroundColor(self, value:'Color'):
        GetDllLibXls().XlsChartSerieDataFormat_set_BackGroundColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_BackGroundColor, self.Ptr, value.Ptr)

    @property
    def BackGroundColorObject(self)->'OColor':
        """
        Gets the background color object of the chart series data format.

        Returns:
            OColor: The background color object of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_BackGroundColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_BackGroundColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_BackGroundColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret

    @property
    def Pattern(self)->'ExcelPatternType':
        """
        Gets the pattern of the chart series data format.

        Returns:
            ExcelPatternType: The pattern of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_Pattern.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_Pattern.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_Pattern, self.Ptr)
        objwraped = ExcelPatternType(ret)
        return objwraped

    @Pattern.setter
    def Pattern(self, value:'ExcelPatternType'):
        GetDllLibXls().XlsChartSerieDataFormat_set_Pattern.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_Pattern, self.Ptr, value.value)

    @property
    def IsAutomaticFormat(self)->bool:
        """
        Gets or sets whether the format is automatic.

        Returns:
            bool: True if the format is automatic; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_IsAutomaticFormat.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_IsAutomaticFormat.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_IsAutomaticFormat, self.Ptr)
        return ret

    @IsAutomaticFormat.setter
    def IsAutomaticFormat(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_IsAutomaticFormat.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_IsAutomaticFormat, self.Ptr, value)

    @property
    def Visible(self)->bool:
        """
        Gets or sets whether the chart series data format is visible.

        Returns:
            bool: True if the chart series data format is visible; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_Visible.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_Visible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_Visible, self.Ptr)
        return ret

    @Visible.setter
    def Visible(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_Visible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_Visible, self.Ptr, value)

    @property
    def ShowActiveValue(self)->bool:
        """
        Gets or sets whether to show the active value.

        Returns:
            bool: True if the active value should be shown; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowActiveValue.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowActiveValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_ShowActiveValue, self.Ptr)
        return ret

    @ShowActiveValue.setter
    def ShowActiveValue(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_ShowActiveValue.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_ShowActiveValue, self.Ptr, value)

    @property
    def Has_dPtPieExplosion(self)->bool:
        """
        Gets or sets whether the chart series data format has pie explosion.

        Returns:
            bool: True if the chart series data format has pie explosion; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_Has_dPtPieExplosion.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_Has_dPtPieExplosion.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_Has_dPtPieExplosion, self.Ptr)
        return ret

    @Has_dPtPieExplosion.setter
    def Has_dPtPieExplosion(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_Has_dPtPieExplosion.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_Has_dPtPieExplosion, self.Ptr, value)

    @property
    def HasBorder(self)->bool:
        """
        Gets whether the chart series data format has a border.

        Returns:
            bool: True if the chart series data format has a border; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_HasBorder.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_HasBorder.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_HasBorder, self.Ptr)
        return ret

    @property
    def HasBorderLine(self)->bool:
        """
        Gets whether the chart series data format has a border line.

        Returns:
            bool: True if the chart series data format has a border line; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_HasBorderLine.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_HasBorderLine.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_HasBorderLine, self.Ptr)
        return ret

    @property
    def IsBorderSupported(self)->bool:
        """
        Gets whether the chart series data format supports borders.

        Returns:
            bool: True if the chart series data format supports borders; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_IsBorderSupported.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_IsBorderSupported.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_IsBorderSupported, self.Ptr)
        return ret

    @property
    def IsFormatted(self)->bool:
        """
        Gets whether the chart series data format is formatted.

        Returns:
            bool: True if the chart series data format is formatted; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_IsFormatted.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_IsFormatted.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_IsFormatted, self.Ptr)
        return ret

    @property
    def IsInteriorSupported(self)->bool:
        """
        Gets whether the chart series data format supports interior formatting.

        Returns:
            bool: True if the chart series data format supports interior formatting; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_IsInteriorSupported.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_IsInteriorSupported.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_IsInteriorSupported, self.Ptr)
        return ret

    @property
    def IsMarker(self)->bool:
        """
        Gets whether the chart series data format has markers.

        Returns:
            bool: True if the chart series data format has markers; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_IsMarker.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_IsMarker.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_IsMarker, self.Ptr)
        return ret

    @property
    def ParentSerie(self)->'XlsChartSerie':
        """
        Gets the parent series of the chart series data format.

        Returns:
            XlsChartSerie: The parent series of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_ParentSerie.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_ParentSerie.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_ParentSerie, self.Ptr)
        ret = None if intPtr==None else XlsChartSerie(intPtr)
        return ret

    @property
    def SeriesNumber(self)->int:
        """
        Gets or sets the series number of the chart series data format.

        Returns:
            int: The series number of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_SeriesNumber.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_SeriesNumber.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_SeriesNumber, self.Ptr)
        return ret

    @SeriesNumber.setter
    def SeriesNumber(self, value:int):
        GetDllLibXls().XlsChartSerieDataFormat_set_SeriesNumber.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_SeriesNumber, self.Ptr, value)

    @property
    def ShowBubble(self)->bool:
        """
        Gets or sets whether to show bubbles in the chart series data format.

        Returns:
            bool: True if bubbles should be shown; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowBubble.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowBubble.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_ShowBubble, self.Ptr)
        return ret

    @ShowBubble.setter
    def ShowBubble(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_ShowBubble.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_ShowBubble, self.Ptr, value)

    @property
    def ShowCategoryLabel(self)->bool:
        """
        Gets or sets whether to show category labels in the chart series data format.

        Returns:
            bool: True if category labels should be shown; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowCategoryLabel.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowCategoryLabel.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_ShowCategoryLabel, self.Ptr)
        return ret

    @ShowCategoryLabel.setter
    def ShowCategoryLabel(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_ShowCategoryLabel.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_ShowCategoryLabel, self.Ptr, value)

    @property
    def ShowPieInPercents(self)->bool:
        """
        Gets or sets whether to show pie values as percentages.

        Returns:
            bool: True if pie values should be shown as percentages; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowPieInPercents.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowPieInPercents.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_ShowPieInPercents, self.Ptr)
        return ret

    @ShowPieInPercents.setter
    def ShowPieInPercents(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_ShowPieInPercents.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_ShowPieInPercents, self.Ptr, value)

    @property
    def ShowPieCategoryLabel(self)->bool:
        """
        Gets or sets whether to show pie category labels.

        Returns:
            bool: True if pie category labels should be shown; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowPieCategoryLabel.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowPieCategoryLabel.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_ShowPieCategoryLabel, self.Ptr)
        return ret

    @ShowPieCategoryLabel.setter
    def ShowPieCategoryLabel(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_ShowPieCategoryLabel.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_ShowPieCategoryLabel, self.Ptr, value)

    @property
    def SmoothLine(self)->bool:
        """
        Gets or sets whether to use smooth lines in the chart series data format.

        Returns:
            bool: True if smooth lines should be used; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_SmoothLine.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_SmoothLine.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_SmoothLine, self.Ptr)
        return ret

    @SmoothLine.setter
    def SmoothLine(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_SmoothLine.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_SmoothLine, self.Ptr, value)

    @property
    def MarkerBorderWidth(self)->float:
        """
        Gets or sets the marker border width of the chart series data format.

        Returns:
            float: The marker border width of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerBorderWidth.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_MarkerBorderWidth.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_MarkerBorderWidth, self.Ptr)
        return ret

    @MarkerBorderWidth.setter
    def MarkerBorderWidth(self, value:float):
        GetDllLibXls().XlsChartSerieDataFormat_set_MarkerBorderWidth.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_MarkerBorderWidth, self.Ptr, value)

    @property
    def ShowConnectorLines(self)->bool:
        """
        Gets or sets whether to show connector lines in the chart series data format.

        Returns:
            bool: True if connector lines should be shown; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowConnectorLines.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowConnectorLines.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_ShowConnectorLines, self.Ptr)
        return ret

    @ShowConnectorLines.setter
    def ShowConnectorLines(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_ShowConnectorLines.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_ShowConnectorLines, self.Ptr, value)

    @property
    def TreeMapLabelOption(self)->'ExcelTreeMapLabelOption':
        """
        Gets or sets the tree map label option of the chart series data format.

        Returns:
            ExcelTreeMapLabelOption: The tree map label option of the chart series data format.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_TreeMapLabelOption.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_TreeMapLabelOption.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_TreeMapLabelOption, self.Ptr)
        objwraped = ExcelTreeMapLabelOption(ret)
        return objwraped

    @TreeMapLabelOption.setter
    def TreeMapLabelOption(self, value:'ExcelTreeMapLabelOption'):
        GetDllLibXls().XlsChartSerieDataFormat_set_TreeMapLabelOption.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_TreeMapLabelOption, self.Ptr, value.value)

    @property
    def ShowMeanLine(self)->bool:
        """
        Gets or sets whether to show the mean line in the chart series data format.

        Returns:
            bool: True if the mean line should be shown; otherwise, False.
        """
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowMeanLine.argtypes=[c_void_p]
        GetDllLibXls().XlsChartSerieDataFormat_get_ShowMeanLine.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_get_ShowMeanLine, self.Ptr)
        return ret

    @ShowMeanLine.setter
    def ShowMeanLine(self, value:bool):
        GetDllLibXls().XlsChartSerieDataFormat_set_ShowMeanLine.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartSerieDataFormat_set_ShowMeanLine, self.Ptr, value)

