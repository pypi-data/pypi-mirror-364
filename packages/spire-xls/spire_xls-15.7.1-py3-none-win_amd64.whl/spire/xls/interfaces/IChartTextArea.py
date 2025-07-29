from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartTextArea (  IFont) :
    """
    Represents the Text Area in a chart.

    """
    @property

    @abc.abstractmethod
    def Text(self)->str:
        """
        Area's text.Some items(such as legend,axis...) maybe invalid.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Cone3DClustered
            #Set the Area's text in the chart
            chart.ChartTitleArea.Text = "Student Chart"
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @Text.setter
    @abc.abstractmethod
    def Text(self, value:str):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def TextRotationAngle(self)->int:
        """
        Text rotation angle.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Cone3DClustered
            #Set the Area's text in the chart
            chart.ChartTitleArea.Text = "Student Chart"
            #Set the Text rotation angle
            chart.ChartTitleArea.TextRotationAngle = 30
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @TextRotationAngle.setter
    @abc.abstractmethod
    def TextRotationAngle(self, value:int):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def FrameFormat(self)->'IChartFrameFormat':
        """
        Return format of the text area.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Cone3DClustered
            #Get the formatting options of the chart for text area
            chart.ChartTitleArea.Text = "Student Chart"
            chart.ChartTitleArea.FrameFormat.Border.Color = Color.Brown
            chart.ChartTitleArea.FrameFormat.Interior.Pattern = ExcelPatternType.Percent25
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property

    @abc.abstractmethod
    def BackgroundMode(self)->'ChartBackgroundMode':
        """
        Display mode of the background.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Cone3DClustered
            #Set the Area's text in the chart
            chart.ChartTitleArea.Text = "Student Chart"
            #Set the Display mode of the background
            chart.ChartTitleArea.BackgroundMode = ChartBackgroundMode.Opaque
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @BackgroundMode.setter
    @abc.abstractmethod
    def BackgroundMode(self, value:'ChartBackgroundMode'):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def IsAutoMode(self)->bool:
        """
        True if background is set to automatic.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            #Set range
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Cone3DClustered
            #Set the Area's text in the chart
            chart.ChartTitleArea.Text = "Student Chart"
            #True if background is set to automatic
            print(chart.ChartTitleArea.IsAutoMode)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


