from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartInterior (abc.ABC) :
    """Chart interior interface.
    
    This interface represents the interior formatting of chart elements in Excel.
    It provides functionality for customizing the appearance of chart areas and plot areas,
    including setting foreground and background colors, patterns, and format options.
    The interior formatting controls the fill characteristics of chart elements.
    """
    @property

    @abc.abstractmethod
    def ForegroundColor(self)->'Color':
        """
        Foreground color (RGB).
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Cone3DClustered
            #Set the foreground color of the chart
            chart.ChartArea.Interior.ForegroundColor = Color.Blue
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @ForegroundColor.setter
    @abc.abstractmethod
    def ForegroundColor(self, value:'Color'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def BackgroundColor(self)->'Color':
        """
        Background color (RGB).
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Cone3DClustered
            #Set the backgroundColor color of the chart
            chart.ChartArea.Interior.BackgroundColor = Color.Pink
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @BackgroundColor.setter
    @abc.abstractmethod
    def BackgroundColor(self, value:'Color'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Pattern(self)->'ExcelPatternType':
        """
        Area pattern.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Cone3DClustered
            #Set the pattern of the chart
            chart.ChartArea.Interior.Pattern = ExcelPatternType.Angle
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @Pattern.setter
    @abc.abstractmethod
    def Pattern(self, value:'ExcelPatternType'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def ForegroundKnownColor(self)->'ExcelColors':
        """
        Index of foreground color.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Cone3DClustered
            #Set the index of foreground color
            chart.ChartArea.Interior.ForegroundKnownColor = ExcelColors.Red
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @ForegroundKnownColor.setter
    @abc.abstractmethod
    def ForegroundKnownColor(self, value:'ExcelColors'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def BackgroundKnownColor(self)->'ExcelColors':
        """
        Background color index.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Cone3DClustered
            #Set the index of background color
            chart.ChartArea.Interior.BackgroundKnownColor = ExcelColors.Red
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @BackgroundKnownColor.setter
    @abc.abstractmethod
    def BackgroundKnownColor(self, value:'ExcelColors'):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def UseDefaultFormat(self)->bool:
        """
        If true - use automatic format; otherwise custom.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Cone3DClustered
            #True to use default format for interior
            chart.ChartArea.Interior.UseDefaultFormat = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @UseDefaultFormat.setter
    @abc.abstractmethod
    def UseDefaultFormat(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def SwapColorsOnNegative(self)->bool:
        """
        Foreground and background are swapped when the data value is negative.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Cone3DClustered
            #True if foreground and background colors are swapped when the data value is negative
            chart.Series[0].Format.Interior.SwapColorsOnNegative = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @SwapColorsOnNegative.setter
    @abc.abstractmethod
    def SwapColorsOnNegative(self, value:bool):
        """

        """
        pass


