from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartSerieDataFormat (  IChartFillBorder) :
    """
    Represents formatting options for the series data.

    """
    @property

    @abc.abstractmethod
    def AreaProperties(self)->'IChartInterior':
        """
        Returns object, that represents aera properties. Read only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set interior
            interior = chart.Series[0].Format.AreaProperties
            #Set color
            interior.ForegroundColor = Color.Red
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property

    @abc.abstractmethod
    def BarType(self)->'BaseFormatType':
        """
        Represents the base data format.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Bar3DStacked
            #Set Bar shape base
            chart.Series[0].Format.BarType = BaseFormatType.Circle
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @BarType.setter
    @abc.abstractmethod
    def BarType(self, value:'BaseFormatType'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def BarTopType(self)->'TopFormatType':
        """
        Represents the top data format.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Bar3DStacked
            #Set Bar shape base
            chart.Series[0].Format.BarTopType = TopFormatType.Sharp
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @BarTopType.setter
    @abc.abstractmethod
    def BarTopType(self, value:'TopFormatType'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def MarkerBackgroundColor(self)->'Color':
        """
        Foreground color: RGB value (high byte = 0).
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Line
            #Set serie format
            format = chart.Series[0].Format
            #Set marker style
            format.MarkerStyle = ChartMarkerType.Circle
            #Set color
            format.MarkerBackgroundColor = Color.Red
            format.MarkerForegroundColor = Color.Black
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @MarkerBackgroundColor.setter
    @abc.abstractmethod
    def MarkerBackgroundColor(self, value:'Color'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def MarkerForegroundColor(self)->'Color':
        """
        Background color: RGB value (high byte = 0).
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Line
            #Set serie format
            format = chart.Series[0].Format
            #Set marker style
            format.MarkerStyle = ChartMarkerType.Circle
            #Set color
            format.MarkerBackgroundColor = Color.Red
            format.MarkerForegroundColor = Color.Black
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @MarkerForegroundColor.setter
    @abc.abstractmethod
    def MarkerForegroundColor(self, value:'Color'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def MarkerStyle(self)->'ChartMarkerType':
        """
        Type of marker.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
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


    @MarkerStyle.setter
    @abc.abstractmethod
    def MarkerStyle(self, value:'ChartMarkerType'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def MarkerForegroundKnownColor(self)->'ExcelColors':
        """
        Index to color of marker border.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Line
            #Set serie format
            format = chart.Series[0].Format
            #Set marker style
            format.MarkerStyle = ChartMarkerType.Circle
            #Set color
            format.MarkerBackgroundKnownColor = ExcelColors.Red
            format.MarkerForegroundKnownColor = ExcelColors.Black
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @MarkerForegroundKnownColor.setter
    @abc.abstractmethod
    def MarkerForegroundKnownColor(self, value:'ExcelColors'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def MarkerBackgroundKnownColor(self)->'ExcelColors':
        """
        Index to color of marker XlsFill.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Line
            #Set serie format
            format = chart.Series[0].Format
            #Set marker style
            format.MarkerStyle = ChartMarkerType.Circle
            #Set color
            format.MarkerBackgroundKnownColor = ExcelColors.Red
            format.MarkerForegroundKnownColor = ExcelColors.Black
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @MarkerBackgroundKnownColor.setter
    @abc.abstractmethod
    def MarkerBackgroundKnownColor(self, value:'ExcelColors'):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def MarkerSize(self)->int:
        """
        Size of line markers.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Line
            #Set serie format
            format = chart.Series[0].Format
            #Set marker style
            format.MarkerStyle = ChartMarkerType.Circle
            #Set marker size
            format.MarkerSize = 10
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @MarkerSize.setter
    @abc.abstractmethod
    def MarkerSize(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def IsAutoMarker(self)->bool:
        """
        Automatic color.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:F2"]
            #Set chart type
            chart.ChartType = ExcelChartType.LineMarkers
            #Set serie data format
            format = chart.Series[0].DataPoints.DefaultDataPoint.DataFormat
            #Check auto marker
            Console.Write(format.IsAutoMarker)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @IsAutoMarker.setter
    @abc.abstractmethod
    def IsAutoMarker(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def Percent(self)->int:
        """
        Distance of pie slice from center of pie.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Pie
            #Set percent
            chart.Series[0].Format.Percent = 30
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @Percent.setter
    @abc.abstractmethod
    def Percent(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def Is3DBubbles(self)->bool:
        """
        True to draw bubbles with 3D effects.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Bubble3D
            #Set serie format
            format = chart.Series[0].Format
            #Check type
            print(format.Is3DBubbles)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @Is3DBubbles.setter
    @abc.abstractmethod
    def Is3DBubbles(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Options(self)->'IChartFormat':
        """
        Gets common serie options. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Column3DStacked
            #Set options
            options = chart.Series[0].Format.Options
            #Set Gap width
            options.GapWidth = 400
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property
    @abc.abstractmethod
    def IsMarkerSupported(self)->bool:
        """
        Indicates whether marker is supported by this chart/series.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Pie
            #Set serie format
            format = chart.Series[0].Format
            #Check marker support
            print(format.IsMarkerSupported)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


