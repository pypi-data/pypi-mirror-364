from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class Chart (  XlsChartShape) :
    """

    """
    @property

    def Series(self)->'ChartSeries':
        """
        Returns an object that represents either a single series (a Series object) or a collection of all the series (a SeriesCollection collection) in the chart or chart group.

        """
        GetDllLibXls().Chart_get_Series.argtypes=[c_void_p]
        GetDllLibXls().Chart_get_Series.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Chart_get_Series, self.Ptr)
        ret = None if intPtr==None else ChartSeries(intPtr)
        return ret


    @property

    def ChartTitleArea(self)->'ChartTextArea':
        """
        Gets title text area. Read-only.

        """
        GetDllLibXls().Chart_get_ChartTitleArea.argtypes=[c_void_p]
        GetDllLibXls().Chart_get_ChartTitleArea.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Chart_get_ChartTitleArea, self.Ptr)
        ret = None if intPtr==None else ChartTextArea(intPtr)
        return ret


    @property

    def ChartArea(self)->'ChartArea':
        """
        Returns a ChartArea object that represents the complete chart area for the chart.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Add data
            worksheet.Range["A1"].Text = "Jan"
            worksheet.Range["B1"].Text = "Feb"
            worksheet.Range["C1"].Text = "Mar"
            worksheet.Range["A2"].Text = "10"
            worksheet.Range["B2"].Text = "20"
            worksheet.Range["C2"].Text = "30"
            #Create chart and range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart frame format
            frameFormat = chart.ChartArea
            #Set color
            frameFormat.Fill.ForeColor = System.Drawing.Color.Red
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().Chart_get_ChartArea.argtypes=[c_void_p]
        GetDllLibXls().Chart_get_ChartArea.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Chart_get_ChartArea, self.Ptr)
        ret = None if intPtr==None else ChartArea(intPtr)
        return ret


    @property

    def DataRange(self)->'CellRange':
        """
        DataRange for the chart series.

        """
        GetDllLibXls().Chart_get_DataRange.argtypes=[c_void_p]
        GetDllLibXls().Chart_get_DataRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Chart_get_DataRange, self.Ptr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @DataRange.setter
    def DataRange(self, value:'CellRange'):
        GetDllLibXls().Chart_set_DataRange.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().Chart_set_DataRange, self.Ptr, value.Ptr)

    @property

    def DataTable(self)->'ChartDataTable':
        """
        Returns a DataTable object that represents the chart data table.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Add data
            worksheet.Range["A1"].Text = "Jan"
            worksheet.Range["B1"].Text = "Feb"
            worksheet.Range["C1"].Text = "Mar"
            worksheet.Range["A2"].Text = "10"
            worksheet.Range["B2"].Text = "20"
            worksheet.Range["C2"].Text = "30"
            #Create chart and range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set Chart data table
            chart.HasDataTable = true
            dataTable = chart.DataTable
            #Set border
            dataTable.HasBorders = false
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().Chart_get_DataTable.argtypes=[c_void_p]
        GetDllLibXls().Chart_get_DataTable.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Chart_get_DataTable, self.Ptr)
        ret = None if intPtr==None else ChartDataTable(intPtr)
        return ret


    @property

    def Floor(self)->'ChartWallOrFloor':
        """
        Returns a Floor object that represents the floor of the 3-D chart.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Get chart
            chart = worksheet.Charts[0]
            #Set chart wall
            floor = chart.Floor
            #Set color
            floor.Fill.FillType = ShapeFillType.SolidColor
            floor.Fill.ForeColor = System.Drawing.Color.Red
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().Chart_get_Floor.argtypes=[c_void_p]
        GetDllLibXls().Chart_get_Floor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Chart_get_Floor, self.Ptr)
        ret = None if intPtr==None else ChartWallOrFloor(intPtr)
        return ret


    @property

    def Legend(self)->'ChartLegend':
        """
        Represents chart legend.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Add data
            worksheet.Range["A1"].Text = "Jan"
            worksheet.Range["B1"].Text = "Feb"
            worksheet.Range["C1"].Text = "Mar"
            worksheet.Range["A2"].Text = "10"
            worksheet.Range["B2"].Text = "20"
            worksheet.Range["C2"].Text = "30"
            #Create chart and range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart legend and legend position
            legend = chart.Legend
            legend.Position = LegendPositionType.Left
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().Chart_get_Legend.argtypes=[c_void_p]
        GetDllLibXls().Chart_get_Legend.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Chart_get_Legend, self.Ptr)
        ret = None if intPtr==None else ChartLegend(intPtr)
        return ret


    @property

    def PageSetup(self)->'ChartPageSetup':
        """
        Page setup for the chart.

        """
        GetDllLibXls().Chart_get_PageSetup.argtypes=[c_void_p]
        GetDllLibXls().Chart_get_PageSetup.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Chart_get_PageSetup, self.Ptr)
        ret = None if intPtr==None else ChartPageSetup(intPtr)
        return ret


    @property

    def PlotArea(self)->'ChartPlotArea':
        """
        Returns a PlotArea object that represents the plot area of a chart.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Add data
            worksheet.Range["A1"].Text = "Jan"
            worksheet.Range["B1"].Text = "Feb"
            worksheet.Range["C1"].Text = "Mar"
            worksheet.Range["A2"].Text = "10"
            worksheet.Range["B2"].Text = "20"
            worksheet.Range["C2"].Text = "30"
            #Create chart and range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart frame format
            frameFormat = chart.PlotArea
            #Set color
            frameFormat.Fill.ForeColor = System.Drawing.Color.Red
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().Chart_get_PlotArea.argtypes=[c_void_p]
        GetDllLibXls().Chart_get_PlotArea.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Chart_get_PlotArea, self.Ptr)
        ret = None if intPtr==None else ChartPlotArea(intPtr)
        return ret


    @property

    def PrimaryCategoryAxis(self)->'ChartCategoryAxis':
        """
        Returns primary category axis.

        """
        GetDllLibXls().Chart_get_PrimaryCategoryAxis.argtypes=[c_void_p]
        GetDllLibXls().Chart_get_PrimaryCategoryAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Chart_get_PrimaryCategoryAxis, self.Ptr)
        ret = None if intPtr==None else ChartCategoryAxis(intPtr)
        return ret


    @property

    def PrimaryValueAxis(self)->'ChartValueAxis':
        """
        Returns primary value axis.

        """
        GetDllLibXls().Chart_get_PrimaryValueAxis.argtypes=[c_void_p]
        GetDllLibXls().Chart_get_PrimaryValueAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Chart_get_PrimaryValueAxis, self.Ptr)
        ret = None if intPtr==None else ChartValueAxis(intPtr)
        return ret


    @property

    def PrimarySerieAxis(self)->'ChartSeriesAxis':
        """
        Returns primary series axis. Read-only.

        """
        GetDllLibXls().Chart_get_PrimarySerieAxis.argtypes=[c_void_p]
        GetDllLibXls().Chart_get_PrimarySerieAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Chart_get_PrimarySerieAxis, self.Ptr)
        ret = None if intPtr==None else ChartSeriesAxis(intPtr)
        return ret


    @property

    def SecondaryCategoryAxis(self)->'ChartCategoryAxis':
        """
        Returns secondary category axis.

        """
        GetDllLibXls().Chart_get_SecondaryCategoryAxis.argtypes=[c_void_p]
        GetDllLibXls().Chart_get_SecondaryCategoryAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Chart_get_SecondaryCategoryAxis, self.Ptr)
        ret = None if intPtr==None else ChartCategoryAxis(intPtr)
        return ret


    @property

    def SecondaryValueAxis(self)->'ChartValueAxis':
        """
        Returns secondary value axis. Read-only.

        """
        GetDllLibXls().Chart_get_SecondaryValueAxis.argtypes=[c_void_p]
        GetDllLibXls().Chart_get_SecondaryValueAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Chart_get_SecondaryValueAxis, self.Ptr)
        ret = None if intPtr==None else ChartValueAxis(intPtr)
        return ret


    @property

    def Workbook(self)->'Workbook':
        """
        Workbook contains the chart.

        """
        GetDllLibXls().Chart_get_Workbook.argtypes=[c_void_p]
        GetDllLibXls().Chart_get_Workbook.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Chart_get_Workbook, self.Ptr)
        ret = None if intPtr==None else Workbook(intPtr)
        return ret


    @property

    def Walls(self)->'ChartWallOrFloor':
        """
        Represents chart walls.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Get chart
            chart = worksheet.Charts[0]
            #Set chart wall
            wall = chart.Walls
            #Set color
            wall.Fill.FillType = ShapeFillType.SolidColor
            wall.Fill.ForeColor = System.Drawing.Color.Red
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().Chart_get_Walls.argtypes=[c_void_p]
        GetDllLibXls().Chart_get_Walls.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Chart_get_Walls, self.Ptr)
        ret = None if intPtr==None else ChartWallOrFloor(intPtr)
        return ret


    @property

    def Worksheet(self)->'SpireObject':
        """
        Worksheet which contains the chart.

        """
        GetDllLibXls().Chart_get_Worksheet.argtypes=[c_void_p]
        GetDllLibXls().Chart_get_Worksheet.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Chart_get_Worksheet, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


