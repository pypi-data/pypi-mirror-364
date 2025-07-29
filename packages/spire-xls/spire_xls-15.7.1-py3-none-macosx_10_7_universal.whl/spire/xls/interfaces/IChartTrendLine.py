from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from spire.xls.charts.ChartBorder import *
from ctypes import *
import abc

class IChartTrendLine (SpireObject) :
    """
    Represents ChartTrendLine interface.

    """
    @property

    def Chart3DOptions(self)->'IFormat3D':
        """
        Gets the IThreeDFormat object. Read-only.[Deprecated]

        """
        GetDllLibXls().IChartTrendLine_get_Chart3DOptions.argtypes=[c_void_p]
        GetDllLibXls().IChartTrendLine_get_Chart3DOptions.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IChartTrendLine_get_Chart3DOptions, self.Ptr)
        ret = None if intPtr==None else Format3D(intPtr)
        return ret


    @property

    def Shadow(self)->'IShadow':
        """
        Gets the shadow.Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add(ExcelChartType.ScatterMarkers)
            #Add serie and set serie Y and X Values
            serie = chart.Series.Add()
            serie.Values = worksheet.Range["A2:C2"]
            serie.CategoryLabels = worksheet.Range["A1:C1"]
            #Get chart trendlines collection and Add trendline
            trendLines = serie.TrendLines
            trendline = trendLines.Add()
            #Set trendline shadow color
            trendline.Shadow.Color = Color.Red
            #Set trendline shadow outer presets
            trendline.Shadow.ShadowOuterType = XLSXChartShadowOuterType.OffsetDiagonalTopRight
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartTrendLine_get_Shadow.argtypes=[c_void_p]
        GetDllLibXls().IChartTrendLine_get_Shadow.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IChartTrendLine_get_Shadow, self.Ptr)
        ret = None if intPtr==None else ChartShadow(intPtr)
        return ret


    @property

    def Border(self)->'IChartBorder':
        """
        Represents border object. Read only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Add serie and set serie Y and X Values
            serie = chart.Series.Add()
            serie.Values = worksheet.Range["A2:C2"]
            serie.CategoryLabels = worksheet.Range["A1:C1"]
            #Get chart trendlines collection
            trendLines = serie.TrendLines
            #Add trendline
            trendline = trendLines.Add()
            #Set trendline broder properties
            trendline.Border.Color = Color.Red
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartTrendLine_get_Border.argtypes=[c_void_p]
        GetDllLibXls().IChartTrendLine_get_Border.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IChartTrendLine_get_Border, self.Ptr)
        ret = None if intPtr==None else ChartBorder(intPtr)
        return ret


    @property
    def Backward(self)->float:
        """
        Represents number of periods that the trendline extends backward.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add(ExcelChartType.ScatterMarkers)
            #Add serie and set serie Y and X Values
            serie = chart.Series.Add()
            serie.Values = worksheet.Range["A2:C2"]
            serie.CategoryLabels = worksheet.Range["A1:C1"]
            #Set X axis minimum and maximum values
            chart.PrimaryCategoryAxis.MinValue = -2
            chart.PrimaryCategoryAxis.MaxValue = 2
            #Get chart trendlines collection and Add trendline
            trendLines = serie.TrendLines
            trendline = trendLines.Add()
            #Set backward forecast value
            trendline.Backward = 3
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartTrendLine_get_Backward.argtypes=[c_void_p]
        GetDllLibXls().IChartTrendLine_get_Backward.restype=c_double
        ret = CallCFunction(GetDllLibXls().IChartTrendLine_get_Backward, self.Ptr)
        return ret

    @Backward.setter
    def Backward(self, value:float):
        GetDllLibXls().IChartTrendLine_set_Backward.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().IChartTrendLine_set_Backward, self.Ptr, value)

    @property
    def Forward(self)->float:
        """
        Represents number of periods that the trendline extends forward.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add(ExcelChartType.ScatterMarkers)
            #Add serie and set serie Y and X Values
            serie = chart.Series.Add()
            serie.Values = worksheet.Range["A2:C2"]
            serie.CategoryLabels = worksheet.Range["A1:C1"]
            #Set X axis minimum and maximum values
            chart.PrimaryCategoryAxis.MinValue = -2
            chart.PrimaryCategoryAxis.MaxValue = 2
            #Get chart trendlines collection and Add trendline
            trendLines = serie.TrendLines
            trendline = trendLines.Add()
            #Set backward forecast value
            trendline.Forward = 3
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartTrendLine_get_Forward.argtypes=[c_void_p]
        GetDllLibXls().IChartTrendLine_get_Forward.restype=c_double
        ret = CallCFunction(GetDllLibXls().IChartTrendLine_get_Forward, self.Ptr)
        return ret

    @Forward.setter
    def Forward(self, value:float):
        GetDllLibXls().IChartTrendLine_set_Forward.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().IChartTrendLine_set_Forward, self.Ptr, value)

    @property
    def DisplayEquation(self)->bool:
        """
        True if the equation for the trendline is displayed on the chart.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and Get chart serie
            chart = worksheet.Charts.Add(ExcelChartType.ColumnClustered)
            chart.DataRange = worksheet.Range["A1:C3"]
            serie = chart.Series[0]
            #Get chart trendlines collection and Add trendline
            trendLines = serie.TrendLines
            trendline = trendLines.Add()
            #Set equation in trendline
            trendline.DisplayEquation = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartTrendLine_get_DisplayEquation.argtypes=[c_void_p]
        GetDllLibXls().IChartTrendLine_get_DisplayEquation.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IChartTrendLine_get_DisplayEquation, self.Ptr)
        return ret

    @DisplayEquation.setter
    def DisplayEquation(self, value:bool):
        GetDllLibXls().IChartTrendLine_set_DisplayEquation.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IChartTrendLine_set_DisplayEquation, self.Ptr, value)

    @property
    def DisplayRSquared(self)->bool:
        """
        True if the R-squared value of the trendline is displayed on the chart.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and Get chart serie
            chart = worksheet.Charts.Add(ExcelChartType.ColumnClustered)
            chart.DataRange = worksheet.Range["A1:C3"]
            serie = chart.Series[0]
            #Get chart trendlines collection and Add trendline
            trendLines = serie.TrendLines
            trendline = trendLines.Add()
            #Set RSquared value for trendline
            trendline.DisplayRSquared = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartTrendLine_get_DisplayRSquared.argtypes=[c_void_p]
        GetDllLibXls().IChartTrendLine_get_DisplayRSquared.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IChartTrendLine_get_DisplayRSquared, self.Ptr)
        return ret

    @DisplayRSquared.setter
    def DisplayRSquared(self, value:bool):
        GetDllLibXls().IChartTrendLine_set_DisplayRSquared.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IChartTrendLine_set_DisplayRSquared, self.Ptr, value)

    @property
    def Intercept(self)->float:
        """
        Represents point where the trendline crosses the value axis.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add(ExcelChartType.ScatterMarkers)
            #Add serie and set serie Y and X Values
            serie = chart.Series.Add()
            serie.Values = worksheet.Range["A2:C2"]
            serie.CategoryLabels = worksheet.Range["A1:C1"]
            #Get chart trendlines collection and Add trendline
            trendLines = serie.TrendLines
            trendline = trendLines.Add()
            #Set intercept value
            trendline.Intercept = 10
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartTrendLine_get_Intercept.argtypes=[c_void_p]
        GetDllLibXls().IChartTrendLine_get_Intercept.restype=c_double
        ret = CallCFunction(GetDllLibXls().IChartTrendLine_get_Intercept, self.Ptr)
        return ret

    @Intercept.setter
    def Intercept(self, value:float):
        GetDllLibXls().IChartTrendLine_set_Intercept.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().IChartTrendLine_set_Intercept, self.Ptr, value)

    @property
    def InterceptIsAuto(self)->bool:
        """
        True if the point where the trendline crosses the value axis is automatically determined by the regression.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add(ExcelChartType.ScatterMarkers)
            #Add serie and set serie Y and X Values
            serie = chart.Series.Add()
            serie.Values = worksheet.Range["A2:C2"]
            serie.CategoryLabels = worksheet.Range["A1:C1"]
            #Get chart trendlines collection and Add trendline
            trendLines = serie.TrendLines
            trendline = trendLines.Add()
            #Set intercept value
            trendline.Intercept = 10
            #Check trendline intercept is automatic
            print("Is Trendline Intercept value is automatic:" + trendline.InterceptIsAuto.ToString())
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartTrendLine_get_InterceptIsAuto.argtypes=[c_void_p]
        GetDllLibXls().IChartTrendLine_get_InterceptIsAuto.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IChartTrendLine_get_InterceptIsAuto, self.Ptr)
        return ret

    @property

    def Type(self)->'TrendLineType':
        """
        Represents trend line type.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and Get chart serie
            chart = worksheet.Charts.Add(ExcelChartType.ColumnClustered)
            chart.DataRange = worksheet.Range["A1:C3"]
            serie = chart.Series[0]
            #Get chart trendlines collection and Add trendline
            trendLines = serie.TrendLines
            trendline = trendLines.Add()
            #Set trendline type
            trendline.Type = TrendLineType.Polynomial
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartTrendLine_get_Type.argtypes=[c_void_p]
        GetDllLibXls().IChartTrendLine_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibXls().IChartTrendLine_get_Type, self.Ptr)
        objwraped = TrendLineType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'TrendLineType'):
        GetDllLibXls().IChartTrendLine_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().IChartTrendLine_set_Type, self.Ptr, value.value)

    @property
    def Order(self)->int:
        """
        Represents for Moving Averange and Polynomial trend line type order value.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add(ExcelChartType.ColumnClustered)
            #Add serie and set serie Y and X Values
            serie = chart.Series.Add()
            serie.Values = worksheet.Range["A2:C2"]
            serie.CategoryLabels = worksheet.Range["A1:C1"]
            #Get chart trendlines collection and Add trendline
            trendLines = serie.TrendLines
            trendline = trendLines.Add()
            #Set trendline type
            trendline.Type = TrendLineType.Polynomial
            #Set trendline order
            trendline.Order = 6
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartTrendLine_get_Order.argtypes=[c_void_p]
        GetDllLibXls().IChartTrendLine_get_Order.restype=c_int
        ret = CallCFunction(GetDllLibXls().IChartTrendLine_get_Order, self.Ptr)
        return ret

    @Order.setter
    def Order(self, value:int):
        GetDllLibXls().IChartTrendLine_set_Order.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().IChartTrendLine_set_Order, self.Ptr, value)

    @property
    def NameIsAuto(self)->bool:
        """
        Indicates if name is default.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and Get chart serie
            chart = worksheet.Charts.Add(ExcelChartType.ColumnClustered)
            chart.DataRange = worksheet.Range["A1:C3"]
            serie = chart.Series[0]
            #Get chart trendlines collection and Add trendline
            trendLines = serie.TrendLines
            trendline = trendLines.Add(TrendLineType.Logarithmic)
            #Set trendline name
            trendline.Name = "Trendline 1"
            #Check trendline name is automatic
            print(trendline.NameIsAuto)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartTrendLine_get_NameIsAuto.argtypes=[c_void_p]
        GetDllLibXls().IChartTrendLine_get_NameIsAuto.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IChartTrendLine_get_NameIsAuto, self.Ptr)
        return ret

    @NameIsAuto.setter
    def NameIsAuto(self, value:bool):
        GetDllLibXls().IChartTrendLine_set_NameIsAuto.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IChartTrendLine_set_NameIsAuto, self.Ptr, value)

    @property

    def Name(self)->str:
        """
        Represents trendline name.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and Get chart serie
            chart = worksheet.Charts.Add(ExcelChartType.ColumnClustered)
            chart.DataRange = worksheet.Range["A1:C3"]
            serie = chart.Series[0]
            #Get chart trendlines collection and Add trendline
            trendLines = serie.TrendLines
            trendline = trendLines.Add(TrendLineType.Logarithmic)
            #Get trendline Name
            print(trendline.Name)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartTrendLine_get_Name.argtypes=[c_void_p]
        GetDllLibXls().IChartTrendLine_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().IChartTrendLine_get_Name, self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        GetDllLibXls().IChartTrendLine_set_Name.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().IChartTrendLine_set_Name, self.Ptr, value)

    @property

    def DataLabel(self)->'IChartDataLabels':
        """
        Returns data label. Read only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and Get chart serie
            chart = worksheet.Charts.Add(ExcelChartType.ColumnClustered)
            chart.DataRange = worksheet.Range["A1:C3"]
            serie = chart.Series[0]
            #Get chart trendlines collection and Add trendline
            trendLines = serie.TrendLines
            trendline = trendLines.Add()
            #Enable trendline data label by DisplayRSquared
            trendline.DisplayRSquared = true
            #Set data label text
            trendline.DataLabel.Text = "y=10*x"
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartTrendLine_get_DataLabel.argtypes=[c_void_p]
        GetDllLibXls().IChartTrendLine_get_DataLabel.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IChartTrendLine_get_DataLabel, self.Ptr)
        ret = None if intPtr==None else XlsChartDataLabels(intPtr)
        return ret


    @property

    def Formula(self)->str:
        """
        Return trendline formula. Read only.

        """
        GetDllLibXls().IChartTrendLine_get_Formula.argtypes=[c_void_p]
        GetDllLibXls().IChartTrendLine_get_Formula.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().IChartTrendLine_get_Formula, self.Ptr))
        return ret


    def ClearFormats(self):
        """
        Clears current trend line.

        """
        GetDllLibXls().IChartTrendLine_ClearFormats.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().IChartTrendLine_ClearFormats, self.Ptr)

