from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartFillBorder (abc.ABC) :
    """
    Provides formatting options for area elements in the chart.

    """
    @property
    @abc.abstractmethod
    def HasInterior(self)->bool:
        """
        This property indicates whether interior object was created. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Column3DClustered
            #Create a fill border and set interior value
            fillBorder = chart.ChartArea
            chart.ChartArea.Interior.ForegroundColor = Color.Yellow
            #True if the chart element has interior formatting
            if (fillBorder.HasInterior){#Your Code Here}
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property
    @abc.abstractmethod
    def HasLineProperties(self)->bool:
        """
        This property indicates whether line formatting object was created. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Column3DClustered
            #Create a fill border and set line border value
            fillBorder = chart.ChartArea
            chart.ChartArea.Border.Color = Color.Yellow
            #True if the chart element has line formatting
            if (fillBorder.HasLineProperties){#Your Code Here}
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property
    @abc.abstractmethod
    def HasFormat3D(self)->bool:
        """
        Gets a value indicating whether [has3d properties].
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Column3DClustered
            #Create a fill border and set 3D formatting value
            fillBorder = chart.ChartArea
            chart.ChartArea.Format3D.BevelTopType = XLSXChartBevelType.Slope
            #True if the chart element has 3D formatting
            if (fillBorder.HasFormat3D){#Your Code Here}
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property
    @abc.abstractmethod
    def HasShadow(self)->bool:
        """
        Gets a value indicating whether this instance has shadow properties.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Column3DClustered
            #Create a fill border and set line border value
            fillBorder = chart.ChartArea
            chart.ChartArea.Shadow.ShadowOuterType = XLSXChartShadowOuterType.OffsetBottom
            #True if the chart element has 3D formatting
            if (fillBorder.HasShadow){#Your Code Here}
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property

    @abc.abstractmethod
    def LineProperties(self)->'ChartBorder':
        """
        Returns object, that represents line properties. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Column3DClustered
            #Gets line formatting properties for the chart element
            border = chart.PlotArea.Border
            border.Pattern = ChartLinePatternType.DashDotDot
            border.Color = Color.Orange
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property

    @abc.abstractmethod
    def Interior(self)->'IChartInterior':
        """
        Returns object, that represents area properties. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Column3DClustered
            #Gets interior formatting properties for the chart element
            chartInterior = chart.ChartArea.Interior
            chartInterior.BackgroundColor = Color.Beige
            chartInterior.Pattern = ExcelPatternType.DarkDownwardDiagonal
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property

    @abc.abstractmethod
    def Fill(self)->'IShapeFill':
        """
        Represents XlsFill options. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Column3DClustered
            #Gets fill options for the chart element
            fillChart = chart.ChartArea.Fill
            fillChart.FillType = ShapeFillType.Gradient
            fillChart.BackColor = Color.FromArgb(205, 217, 234)
            fillChart.ForeColor = Color.White
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property

    @abc.abstractmethod
    def Format3D(self)->'Format3D':
        """
        Gets the chart3 D properties.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Column3DClustered
            #Gets 3D-effect properties for the chart element
            threeDFromat = chart.ChartArea.Format3D
            threeDFromat.BevelTopType = XLSXChartBevelType.Slope
            threeDFromat.BevelTopHeight = 16
            threeDFromat.BevelTopWidth = 7
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property

    @abc.abstractmethod
    def Shadow(self)->'ChartShadow':
        """
        Gets the shadow properties.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set chart type
            chart.ChartType = ExcelChartType.Column3DClustered
            #Gets shadow formatting properties for the chart element
            shadowChart = chart.ChartArea.Shadow
            shadowChart.ShadowPrespectiveType = XLSXChartPrespectiveType.Below
            shadowChart.Color = Color.Aqua
            shadowChart.Blur = 22
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


