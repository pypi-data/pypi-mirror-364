from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartFormat (abc.ABC) :
    """
    Provides access to the formatting options for chart elements.

    """
    @property
    @abc.abstractmethod
    def IsVaryColor(self)->bool:
        """
        Vary color for each data point.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart format
            format = chart.Series[0].Format.Options
            #Set vary color
            format.IsVaryColor = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @IsVaryColor.setter
    @abc.abstractmethod
    def IsVaryColor(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def Overlap(self)->int:
        """
        Space between bars ( -100 : 100 ).
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnStacked
            #Set chart format
            format = chart.Series[0].Format.Options
            #Set overlap
            format.Overlap = 20
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @Overlap.setter
    @abc.abstractmethod
    def Overlap(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def GapWidth(self)->int:
        """
        Space between categories (percent of bar width), default = 50.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.Column3DStacked
            #Set chart format
            format = chart.Series[0].Format.Options
            #Set Gap width
            format.GapWidth = 400
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @GapWidth.setter
    @abc.abstractmethod
    def GapWidth(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def FirstSliceAngle(self)->int:
        """
        Angle of the first pie slice expressed in degrees. ( 0 - 360 ).
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
            #Set chart format
            format = chart.Series[0].Format.Options
            #Set Gap width
            format.FirstSliceAngle = 60
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @FirstSliceAngle.setter
    @abc.abstractmethod
    def FirstSliceAngle(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def DoughnutHoleSize(self)->int:
        """
        Size of center hole in a doughnut chart (as a percentage).( 10 - 90 ).
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Doughnut
            #Set chart format
            format = chart.Series[0].Format.Options
            #Set Doughnut hole size
            format.DoughnutHoleSize = 60
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @DoughnutHoleSize.setter
    @abc.abstractmethod
    def DoughnutHoleSize(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def BubbleScale(self)->int:
        """
        Percent of largest bubble compared to chart in general. ( 0 - 300 ).
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add(ExcelChartType.Bubble3D)
            chart.DataRange = worksheet.Range["A1:C2"]
            chart.Series[0].Bubbles = worksheet.Range["A2:C3"]
            #Set chart format
            format = chart.Series[0].Format.Options
            #Set bubble scale
            format.BubbleScale = 50
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @BubbleScale.setter
    @abc.abstractmethod
    def BubbleScale(self, value:int):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def SizeRepresents(self)->'BubbleSizeType':
        """
        Returns or sets what the bubble size represents on a bubble chart.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add(ExcelChartType.Bubble3D)
            chart.DataRange = worksheet.Range["A1:C2"]
            chart.Series[0].Bubbles = worksheet.Range["A2:C3"]
            #Set chart format
            format = chart.Series[0].Format.Options
            #Set bubble scale and size represents
            format.BubbleScale = 50
            format.SizeRepresents = BubbleSizeType.Width
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @SizeRepresents.setter
    @abc.abstractmethod
    def SizeRepresents(self, value:'BubbleSizeType'):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def ShowNegativeBubbles(self)->bool:
        """
        True to show negative bubbles.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add(ExcelChartType.Bubble3D)
            chart.DataRange = worksheet.Range["A1:D2"]
            chart.Series[0].Bubbles = worksheet.Range["A2:C3"]
            #Set chart format
            format = chart.Series[0].Format.Options
            #Set negative bubble visibility
            format.ShowNegativeBubbles = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @ShowNegativeBubbles.setter
    @abc.abstractmethod
    def ShowNegativeBubbles(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def HasRadarAxisLabels(self)->bool:
        """
        True if a radar chart has axis labels. Applies only to radar charts.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Radar
            #Set chart format
            format = chart.Series[0].Format.Options
            #Set radar label visibility
            format.HasRadarAxisLabels = false
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @HasRadarAxisLabels.setter
    @abc.abstractmethod
    def HasRadarAxisLabels(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def SplitType(self)->'SplitType':
        """
        Returns or sets the way the two sections of either a pie of pie chart or a bar of pie chart are split.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:F2"]
            #Set chart type
            chart.ChartType = ExcelChartType.PieOfPie
            #Set chart format
            format = chart.Series[0].Format.Options
            #Set split type
            format.SplitType = SplitType.Value
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @SplitType.setter
    @abc.abstractmethod
    def SplitType(self, value:'SplitType'):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def SplitValue(self)->int:
        """
        Returns or sets the threshold value separating the two sections of either a pie of pie chart or a bar of pie chart.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:F2"]
            #Set chart type
            chart.ChartType = ExcelChartType.PieOfPie
            #Set chart format
            format = chart.Series[0].Format.Options
            #Set split value
            format.SplitValue = 20
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @SplitValue.setter
    @abc.abstractmethod
    def SplitValue(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def PieSecondSize(self)->int:
        """
        Returns or sets the size of the secondary section of either a pie of pie chart or a bar of pie chart, as a percentage of the size of the primary pie. ( 5 - 200 ).
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:F2"]
            #Set chart type
            chart.ChartType = ExcelChartType.PieOfPie
            #Set chart format
            format = chart.Series[0].Format.Options
            #Set second pie size
            format.PieSecondSize = 40
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @PieSecondSize.setter
    @abc.abstractmethod
    def PieSecondSize(self, value:int):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def FirstDropBar(self)->'IChartDropBar':
        """
        Returns object that represents first drop bar.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.Line
            #Set chart drop bar
            dropBar = chart.Series[0].Format.Options.FirstDropBar

        """
        pass


    @property

    @abc.abstractmethod
    def SecondDropBar(self)->'IChartDropBar':
        """
        Returns object that represents second drop bar.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.Line
            #Set chart first drop bar
            dropBar = chart.Series[0].Format.Options.FirstDropBar
            #Set chart second drop bar
            dropBar = chart.Series[0].Format.Options.SecondDropBar

        """
        pass


    @property

    @abc.abstractmethod
    def PieSeriesLine(self)->'IChartBorder':
        """
        Represents series line properties. ( For pie of pie or pie of bar chart types only. ) Read only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:F2"]
            #Set chart type
            chart.ChartType = ExcelChartType.PieOfPie
            #Set pie series line border
            border =  chart.Series[0].Format.Options.PieSeriesLine
            #Set color
            border.Color = Color.Red
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


