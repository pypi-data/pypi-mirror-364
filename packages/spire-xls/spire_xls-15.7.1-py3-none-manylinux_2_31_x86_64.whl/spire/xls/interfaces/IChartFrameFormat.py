from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartFrameFormat (  IChartFillBorder) :
    """
    Represent the borders and layout options of the chart elements.

    """
    @property
    @abc.abstractmethod
    def IsBorderCornersRound(self)->bool:
        """
        Gets or sets flag if border corners is round.
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
            #True if the chart area has rounded corners
            chartArea = chart.ChartArea
            chartArea.IsBorderCornersRound = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @IsBorderCornersRound.setter
    @abc.abstractmethod
    def IsBorderCornersRound(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Border(self)->'IChartBorder':
        """
        Represents chart border. Read only.
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
            #border of the chart element
            chart.ChartTitleArea.Text = "Sample Chart"
            chart.ChartTitleArea.FrameFormat.Border.Color = Color.Red
            chart.ChartTitleArea.FrameFormat.Border.Pattern = ChartLinePatternType.DashDotDot
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @abc.abstractmethod
    def Clear(self):
        """
        Clear curent plot area.

        """
        pass


