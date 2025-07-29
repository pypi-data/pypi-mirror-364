from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartSeriesAxis (  IChartAxis) :
    """
    Represents the chart series Axis.

    """
    @property
    @abc.abstractmethod
    def LabelsFrequency(self)->int:
        """
        Frequency of labels.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.Column3D
            #Set LabelsFrequency
            chart.PrimarySerieAxis.LabelsFrequency = 2
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @LabelsFrequency.setter
    @abc.abstractmethod
    def LabelsFrequency(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def TickLabelSpacing(self)->int:
        """
        Represents the number of categories or series between tick-mark labels.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.Column3D
            #Set tick label spacing
            chart.PrimarySerieAxis.TickLabelSpacing = 2
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @TickLabelSpacing.setter
    @abc.abstractmethod
    def TickLabelSpacing(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def TickMarksFrequency(self)->int:
        """
        Frequency of tick marks.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.Column3D
            #Set tick mark frequency
            chart.PrimarySerieAxis.TickMarksFrequency = 2
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @TickMarksFrequency.setter
    @abc.abstractmethod
    def TickMarksFrequency(self, value:int):
        """

        """
        pass


