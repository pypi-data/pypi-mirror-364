from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartDataTable (  IFont, IExcelApplication, IOptimizedUpdate) :
    """
    Represents the chart data table.

    """
    @property
    @abc.abstractmethod
    def HasHorzBorder(self)->bool:
        """
        True if data table has horizontal border.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:F2"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnClustered
            #Enabling the data table
            chart.HasDataTable = true
            #Get data table of the chart
            dataTable = chart.DataTable
            #Set false to remove the horizontal border in data table
            dataTable.HasHorzBorder = false
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @HasHorzBorder.setter
    @abc.abstractmethod
    def HasHorzBorder(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def HasVertBorder(self)->bool:
        """
        True if data table has vertical border.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:F2"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnClustered
            #Enabling the data table
            chart.HasDataTable = true
            #Get data table of the chart
            dataTable = chart.DataTable
            #Set false to remove the vertical border in data table
            dataTable.HasVertBorder = false
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @HasVertBorder.setter
    @abc.abstractmethod
    def HasVertBorder(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def HasBorders(self)->bool:
        """
        True if data table has borders.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:F2"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnClustered
            #Enabling the data table
            chart.HasDataTable = true
            #Get data table of the chart
            dataTable = chart.DataTable
            #Set false to remove the borders in data table
            dataTable.HasBorders = false
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @HasBorders.setter
    @abc.abstractmethod
    def HasBorders(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def ShowSeriesKeys(self)->bool:
        """
        True if there is series keys in the data table.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:F2"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnClustered
            #Enabling the data table
            chart.HasDataTable = true
            #Get data table of the chart
            dataTable = chart.DataTable
            #Set true to show series keys in the data table
            dataTable.ShowSeriesKeys = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @ShowSeriesKeys.setter
    @abc.abstractmethod
    def ShowSeriesKeys(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def BackgroundMode(self)->'ChartBackgroundMode':
        """

        """
        pass


    @BackgroundMode.setter
    @abc.abstractmethod
    def BackgroundMode(self, value:'ChartBackgroundMode'):
        """

        """
        pass


