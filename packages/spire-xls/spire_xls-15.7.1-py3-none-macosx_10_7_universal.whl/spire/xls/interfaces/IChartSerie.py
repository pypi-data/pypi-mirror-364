from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartSerie (  IExcelApplication) :
    """
    Represents a series in the chart.

    """
    @property

    @abc.abstractmethod
    def Values(self)->'IXLSRange':
        """
        Values range for the series.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set serie
            serie = chart.Series.Add()
            #Set category labels and values
            serie.CategoryLabels = worksheet.Range["A1:C1"]
            serie.Values = worksheet.Range["A2:C2"]
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @Values.setter
    @abc.abstractmethod
    def Values(self, value:'IXLSRange'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def CategoryLabels(self)->'IXLSRange':
        """
        Category labels for the series.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set serie
            serie = chart.Series.Add()
            #Set category labels and values
            serie.CategoryLabels = worksheet.Range["A1:C1"]
            serie.Values = worksheet.Range["A2:C2"]
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @CategoryLabels.setter
    @abc.abstractmethod
    def CategoryLabels(self, value:'IXLSRange'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Bubbles(self)->'IXLSRange':
        """
        Bubble sizes for the series.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set serie
            serie = chart.Series.Add(ExcelChartType.Bubble)
            #Set values and bubble chart range
            serie.Values = worksheet.Range["A1:C1"];
            serie.Bubbles = worksheet.Range["A2:C2"]
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @Bubbles.setter
    @abc.abstractmethod
    def Bubbles(self, value:'IXLSRange'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Name(self)->str:
        """
        Name of the series.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set serie
            serie = chart.Series.Add("BarSerie")
            #Set category labels and values
            serie.CategoryLabels = worksheet.Range["A1:C1"]
            serie.Values = worksheet.Range["A2:C2"]
            #Get Serie name
            Console.Write(serie.Name)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @Name.setter
    @abc.abstractmethod
    def Name(self, value:str):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def NamedRange(self)->'CellRange':
        """
        Series Name range for the series.

        """
        pass


    @property
    @abc.abstractmethod
    def UsePrimaryAxis(self)->bool:
        """
        Indicates whether to use primary axis for series drawing.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet["A1:C3"]
            #Set secondary axis
            serie = chart.Series[1]
            serie.UsePrimaryAxis = false
            chart.SecondaryCategoryAxis.Visible = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @UsePrimaryAxis.setter
    @abc.abstractmethod
    def UsePrimaryAxis(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def DataPoints(self)->'IChartDataPoints':
        """
        Returns collection of data points. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet["A1:C3"]
            #Set data points
            dataPoints = chart.Series[0].DataPoints
            #Set data labels value visibility
            dataPoints.DefaultDataPoint.DataLabels.HasValue = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property

    @abc.abstractmethod
    def Format(self)->'IChartSerieDataFormat':
        """
        Returns format of current serie.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Line
            #Set serie format
            format = chart.Series[0].Format
            #Set marker style
            format.MarkerStyle = ChartMarkerType.Star
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property

    @abc.abstractmethod
    def SerieType(self)->'ExcelChartType':
        """
        Represents serie type.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet["A1:C2"]
            #Set chart type
            chart.Series[0].SerieType = ExcelChartType.Line
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @SerieType.setter
    @abc.abstractmethod
    def SerieType(self, value:'ExcelChartType'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def EnteredDirectlyValues(self)->List['SpireObject']:
        """
        Represents value as entered directly.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set serie
            serie = chart.Series.Add(ExcelChartType.Pie)
            #Set direct values
            serie.EnteredDirectlyValues = new object[] { 2000, 1000, 1000 }
            #Set direct category label
            serie.EnteredDirectlyCategoryLabels = new object[] { "Total Income", "Expenses", "Profit" }
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @EnteredDirectlyValues.setter
    @abc.abstractmethod
    def EnteredDirectlyValues(self, value:List['SpireObject']):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def EnteredDirectlyCategoryLabels(self)->List['SpireObject']:
        """
        Represents category values as entered directly.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set serie
            serie = chart.Series.Add(ExcelChartType.Pie)
            #Set direct values
            serie.EnteredDirectlyValues = new object[] { 2000, 1000, 1000 }
            #Set direct category label
            serie.EnteredDirectlyCategoryLabels = new object[] { "Total Income", "Expenses", "Profit" }
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @EnteredDirectlyCategoryLabels.setter
    @abc.abstractmethod
    def EnteredDirectlyCategoryLabels(self, value:List['SpireObject']):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def EnteredDirectlyBubbles(self)->List['SpireObject']:
        """
        Represents bubble values as entered directly.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set serie
            serie = chart.Series.Add(ExcelChartType.Bubble)
            #Set direct values
            serie.EnteredDirectlyValues = new object[] { 10, 20, 30 }
            #Set bubble chart direct values
            serie.EnteredDirectlyBubbles = new object[] { 1, 4, 2 }
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @EnteredDirectlyBubbles.setter
    @abc.abstractmethod
    def EnteredDirectlyBubbles(self, value:List['SpireObject']):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def ErrorBarsY(self)->'IChartErrorBars':
        """
        Represents Y error bars. Read only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set chart type
            chart.ChartType = ExcelChartType.ScatterLine
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set error bar
            chart.Series[0].HasErrorBarsY = true
            errorBar = chart.Series[0].ErrorBarsY
            #Set error bar type
            errorBar.Type = ErrorBarType.Percentage
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property
    @abc.abstractmethod
    def HasErrorBarsY(self)->bool:
        """
        Indicates if serie contains Y error bars.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set chart type
            chart.ChartType = ExcelChartType.ScatterLine
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set error bar
            chart.Series[0].HasErrorBarsY = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @HasErrorBarsY.setter
    @abc.abstractmethod
    def HasErrorBarsY(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def ErrorBarsX(self)->'IChartErrorBars':
        """
        Represents X error bars. Read only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set chart type
            chart.ChartType = ExcelChartType.ScatterLine
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set error bar
            chart.Series[0].HasErrorBarsX = true
            errorBar = chart.Series[0].ErrorBarsX
            #Set error bar type
            errorBar.Type = ErrorBarType.Percentage
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property
    @abc.abstractmethod
    def HasErrorBarsX(self)->bool:
        """
        Indicates if serie contains X error bars.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set chart type
            chart.ChartType = ExcelChartType.ScatterLine
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set error bar
            chart.Series[0].HasErrorBarsX = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @HasErrorBarsX.setter
    @abc.abstractmethod
    def HasErrorBarsX(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def TrendLines(self)->'IChartTrendLines':
        """
        Represents serie trend lines collection. Read only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set trend line
            trendLines = chart.Series[0].TrendLines
            trendLine = trendLines.Add(TrendLineType.Linear)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property

    @abc.abstractmethod
    def DataLabels(self)->'IChartDataLabels':
        """

        """
        pass


    @dispatch

    @abc.abstractmethod
    def ErrorBar(self ,bIsY:bool)->IChartErrorBars:
        """
        Creates error bar object.

        Args:
            bIsY: If true - on Y axis; otherwise on X axis.

        Returns:
            Return error bar objcet.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set error bar
            chart.Series[0].ErrorBar(true)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def ErrorBar(self ,bIsY:bool,include:ErrorBarIncludeType)->IChartErrorBars:
        """
        Creates error bar object.

        Args:
            bIsY: If true - on Y axis; otherwise on X axis.
            include: Represents include type.

        Returns:
            Return error bar objcet.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set error bar
            chart.Series[0].ErrorBar(true, ErrorBarIncludeType.Plus)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def ErrorBar(self ,bIsY:bool,include:ErrorBarIncludeType,type:ErrorBarType)->IChartErrorBars:
        """
        Creates error bar object.

        Args:
            bIsY: If true - on Y axis; otherwise on X axis.
            include: Represents include type.
            type: Represents error bar type.

        Returns:
            Return error bar objcet.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set error bar
            chart.Series[0].ErrorBar(true, ErrorBarIncludeType.Plus, ErrorBarType.Percentage)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def ErrorBar(self ,bIsY:bool,include:ErrorBarIncludeType,type:ErrorBarType,numberValue:float)->IChartErrorBars:
        """
        Creates error bar object.

        Args:
            bIsY: If true - on Y axis; otherwise on X axis.
            include: Represents include type.
            type: Represents error bar type.
            numberValue: Represents number value.

        Returns:
            Return error bar objcet.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set error bar
            chart.Series[0].ErrorBar(true, ErrorBarIncludeType.Plus, ErrorBarType.Percentage, 50)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def ErrorBar(self ,bIsY:bool,plusRange:IXLSRange,minusRange:IXLSRange)->IChartErrorBars:
        """
        Sets custom error bar type.

        Args:
            bIsY: If true - on Y axis; otherwise on X axis.
            plusRange: Represents plus range.
            minusRange: Represents minus range.

        Returns:
            Returns error bar object.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set chart type
            chart.ChartType = ExcelChartType.ScatterLine
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set error bar
            chart.Series[0].ErrorBar(false, worksheet.Range["A3"], worksheet.Range["B3"])
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


