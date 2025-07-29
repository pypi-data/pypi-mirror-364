from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartLegendEntry (abc.ABC) :
    """Chart legend entry interface.
    
    This interface represents an individual entry in a chart legend. Each legend entry corresponds
    to a data series in the chart and displays the name and visual representation (color/pattern)
    of that series. The interface provides functionality for formatting legend entries, including
    text formatting, deletion, and background mode settings.
    """
    @property
    @abc.abstractmethod
    def IsDeleted(self)->bool:
        """
        If true then this entry deleted. otherwise false.
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
            #Create a chartLegend
            chartLegend = chart.Legend
            chartLegend.LegendEntries[0].Delete()
            #True if the entry is deleted
            isDeletedEntry = chartLegend.LegendEntries[0].IsDeleted
            if(isDeletedEntry){ #Your code here }
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @IsDeleted.setter
    @abc.abstractmethod
    def IsDeleted(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def IsFormatted(self)->bool:
        """
        True if the legend entry has been formatted.
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
            #Create a chartLegend
            chartLegend = chart.Legend
            chartLegend.LegendEntries[1].TextArea.Color = Color.Blue
            #True if the legend entry is formatted
            isEntryFromatted = chartLegend.LegendEntries[1].IsFormatted
            if(isEntryFromatted){ #Your code here }
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @IsFormatted.setter
    @abc.abstractmethod
    def IsFormatted(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def TextArea(self)->'IChartTextArea':
        """
        Represents text area.
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
            #Create a chartLegend
            chartLegend = chart.Legend
            chartLegend.LegendEntries[1].TextArea.Color = Color.Blue
            chartLegend.LegendEntries[1].TextArea.Size = 10
            chartLegend.LegendEntries[1].TextArea.FontName = "Bernard MT Condensed"
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property

    @abc.abstractmethod
    def BackgroundMode(self)->'ChartBackgroundMode':
        """
        Display mode of the background.

        """
        pass


    @BackgroundMode.setter
    @abc.abstractmethod
    def BackgroundMode(self, value:'ChartBackgroundMode'):
        """

        """
        pass


    @abc.abstractmethod
    def Delete(self):
        """
        Deletes current legend entry.
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
            #Create a chartLegend
            chartLegend = chart.Legend
            #Delete the first legend entry out of five entires
            chartLegend.LegendEntries[0].Delete()
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


