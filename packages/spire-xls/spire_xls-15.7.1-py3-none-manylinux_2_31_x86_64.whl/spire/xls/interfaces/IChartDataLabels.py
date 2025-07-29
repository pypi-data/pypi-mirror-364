from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartDataLabels (  IChartTextArea) :
    """
    Represents a collection of chart data labels.

    """
    @property
    @abc.abstractmethod
    def HasSeriesName(self)->bool:
        """
        Indicates whether series name is in data labels.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnClustered
            #Get the chart serie
            serie = chart.Series[0]
            #Get serie data labels
            dataLabels = serie.DataPoints.DefaultDataPoint.DataLabels
            #Set the data label to show the serie name
            dataLabels.HasSeriesName = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @HasSeriesName.setter
    @abc.abstractmethod
    def HasSeriesName(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def HasCategoryName(self)->bool:
        """
        Indicates whether category name is in data labels.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnClustered
            #Get the chart serie
            serie = chart.Series[0]
            #Get serie data labels
            dataLabels = serie.DataPoints.DefaultDataPoint.DataLabels
            #Set the data label to show the category names
            dataLabels.HasCategoryName = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @HasCategoryName.setter
    @abc.abstractmethod
    def HasCategoryName(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def HasValue(self)->bool:
        """
        Indicates whether value is in data labels.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnClustered
            #Get the chart serie
            serie = chart.Series[0]
            #Get serie data labels
            dataLabels = serie.DataPoints.DefaultDataPoint.DataLabels
            #Set the data label to show the values
            dataLabels.HasValue = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @HasValue.setter
    @abc.abstractmethod
    def HasValue(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def HasPercentage(self)->bool:
        """
        Indicates whether percentage is in data labels.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Pie
            #Get the chart serie
            serie = chart.Series[0]
            #Get serie data labels
            dataLabels = serie.DataPoints.DefaultDataPoint.DataLabels
            #Set the data label to show the percentage values
            dataLabels.HasPercentage = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @HasPercentage.setter
    @abc.abstractmethod
    def HasPercentage(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def HasBubbleSize(self)->bool:
        """
        Indicates whether bubble size is in data labels.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.Bubble
            #Get the chart serie
            serie = chart.Series[0]
            #Get serie data labels
            dataLabels = serie.DataPoints.DefaultDataPoint.DataLabels
            #Set the data label to show the bubble sizes
            dataLabels.HasBubbleSize = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @HasBubbleSize.setter
    @abc.abstractmethod
    def HasBubbleSize(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Delimiter(self)->str:
        """
        Delimeter.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnClustered
            #Get the chart serie
            serie = chart.Series[0]
            #Get serie data labels
            dataLabels = serie.DataPoints.DefaultDataPoint.DataLabels
            #Set ' ' symbol as separator for data labels
            dataLabels.HasValue = true
            dataLabels.HasSeriesName = true
            dataLabels.Delimiter =" "
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @Delimiter.setter
    @abc.abstractmethod
    def Delimiter(self, value:str):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def HasLegendKey(self)->bool:
        """
        Indicates whether legend key is in data labels.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnClustered
            #Get the chart serie
            serie = chart.Series[0]
            #Get serie data labels
            dataLabels = serie.DataPoints.DefaultDataPoint.DataLabels
            #Set the data label to show the legend key
            dataLabels.HasValue = true
            dataLabels.HasLegendKey = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @HasLegendKey.setter
    @abc.abstractmethod
    def HasLegendKey(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Position(self)->'DataLabelPositionType':
        """
        Represents data labels position.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Pie
            #Get the chart serie
            serie = chart.Series[0]
            #Get serie data labels
            dataLabels = serie.DataPoints.DefaultDataPoint.DataLabels
            #Set the data label to show the leader lines
            dataLabels.HasValue = true
            dataLabels.Position = DataLabelPositionType.Outside
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @Position.setter
    @abc.abstractmethod
    def Position(self, value:'DataLabelPositionType'):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def ShowLeaderLines(self)->bool:
        """
        Indicates whether Leader Lines is in data labels.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Pie
            #Get the chart serie
            serie = chart.Series[0]
            #Get serie data labels
            dataLabels = serie.DataPoints.DefaultDataPoint.DataLabels
            #Set the data label to show the leader lines
            dataLabels.HasValue = true
            dataLabels.Position = DataLabelPositionType.Outside
            dataLabels.ShowLeaderLines = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @ShowLeaderLines.setter
    @abc.abstractmethod
    def ShowLeaderLines(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def NumberFormat(self)->str:
        """
        Represents trend line label number format.

        """
        pass


    @NumberFormat.setter
    @abc.abstractmethod
    def NumberFormat(self, value:str):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def IsTextWrapped(self)->bool:
        """

        """
        pass


    @IsTextWrapped.setter
    @abc.abstractmethod
    def IsTextWrapped(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def IsResizeShapeToFitText(self)->bool:
        """

        """
        pass


    @IsResizeShapeToFitText.setter
    @abc.abstractmethod
    def IsResizeShapeToFitText(self, value:bool):
        """

        """
        pass


