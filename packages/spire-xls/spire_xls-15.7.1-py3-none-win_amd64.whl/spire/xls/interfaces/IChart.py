from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChart (abc.ABC) :
    """Chart interface for Excel workbooks.
    
    This interface represents a chart in an Excel workbook, either embedded in a worksheet
    or as a separate chart sheet. It provides properties and methods to customize the
    appearance and behavior of charts, including chart type, data range, axes, legend,
    and 3D formatting options.
    
    The IChart interface allows for complete control over all aspects of Excel charts,
    from basic formatting to advanced 3D visualization settings.
    """
    @property
    @abc.abstractmethod
    def ChartType(self)->'ExcelChartType':
        """Gets the type of the chart.
        
        This property returns the chart type, such as column, bar, line, pie, etc.
        The chart type determines how the data is visually represented in the chart.
        
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
            #Create chart and set chart type
            chart = workbook.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            chart.ChartType = ExcelChartType.PyramidBarStacked
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            ExcelChartType: The type of the chart.
        """
        pass


    @ChartType.setter
    @abc.abstractmethod
    def ChartType(self, value:'ExcelChartType'):
        """Sets the type of the chart.
        
        This property sets the chart type, such as column, bar, line, pie, etc.
        The chart type determines how the data is visually represented in the chart.
        
        Args:
            value (ExcelChartType): The chart type to set.
        """
        pass


    @property
    @abc.abstractmethod
    def DataRange(self)->'IXLSRange':
        """Gets the data range for the chart series.
        
        This property returns the worksheet range that contains the data used
        to create the chart. This includes both the data values and labels.
        
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
            #Create chart and set range
            chart = workbook.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            IXLSRange: The data range for the chart series.
        """
        pass


    @DataRange.setter
    @abc.abstractmethod
    def DataRange(self, value:'IXLSRange'):
        """Sets the data range for the chart series.
        
        This property sets the worksheet range that contains the data used
        to create the chart. This includes both the data values and labels.
        
        Args:
            value (IXLSRange): The data range to set for the chart series.
        """
        pass


    @property
    @abc.abstractmethod
    def SeriesDataFromRange(self)->bool:
        """Gets whether series data is organized by rows in the data range.
        
        When true, the series data is organized by rows in the data range,
        with each row representing a different series. When false, the series
        data is organized by columns, with each column representing a different series.
        
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
            #Create chart and set SeriesDataFromRange
            chart = workbook.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            chart.SeriesDataFromRange = false
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if series data is organized by rows, False if by columns.
        """
        pass


    @SeriesDataFromRange.setter
    @abc.abstractmethod
    def SeriesDataFromRange(self, value:bool):
        """Sets whether series data is organized by rows in the data range.
        
        When true, the series data is organized by rows in the data range,
        with each row representing a different series. When false, the series
        data is organized by columns, with each column representing a different series.
        
        Args:
            value (bool): True to organize series data by rows, False to organize by columns.
        """
        pass


    @property
    @abc.abstractmethod
    def PageSetup(self)->'IChartPageSetup':
        """Gets the page setup object for the chart.
        
        This property returns the page setup object that contains the page settings
        for the chart, such as paper size, orientation, margins, and print options.
        This is a read-only property.
        
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
            chart = workbook.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart page setup and paper size
            pageSetup = chart.PageSetup
            pageSetup.PaperSize = PaperSizeType.A3TransversePaper
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            IChartPageSetup: The page setup object for the chart.
        """
        pass


    @property
    @abc.abstractmethod
    def XPos(self)->float:
        """Gets the X-coordinate of the upper-left corner of the chart.
        
        This property returns the X-coordinate of the upper-left corner of the chart
        in points (1/72 inch). This is used to position the chart on a worksheet.
        
        Returns:
            float: The X-coordinate of the upper-left corner of the chart in points.
        """
        pass


    @XPos.setter
    @abc.abstractmethod
    def XPos(self, value:float):
        """Sets the X-coordinate of the upper-left corner of the chart.
        
        This property sets the X-coordinate of the upper-left corner of the chart
        in points (1/72 inch). This is used to position the chart on a worksheet.
        
        Args:
            value (float): The X-coordinate of the upper-left corner of the chart in points.
        """
        pass


    @property
    @abc.abstractmethod
    def YPos(self)->float:
        """Gets the Y-coordinate of the upper-left corner of the chart.
        
        This property returns the Y-coordinate of the upper-left corner of the chart
        in points (1/72 inch). This is used to position the chart on a worksheet.
        
        Returns:
            float: The Y-coordinate of the upper-left corner of the chart in points.
        """
        pass


    @YPos.setter
    @abc.abstractmethod
    def YPos(self, value:float):
        """Sets the Y-coordinate of the upper-left corner of the chart.
        
        This property sets the Y-coordinate of the upper-left corner of the chart
        in points (1/72 inch). This is used to position the chart on a worksheet.
        
        Args:
            value (float): The Y-coordinate of the upper-left corner of the chart in points.
        """
        pass


    @property
    @abc.abstractmethod
    def Width(self)->float:
        """Gets the width of the chart.
        
        This property returns the width of the chart in points (1/72 inch).
        
        Returns:
            float: The width of the chart in points.
        """
        pass


    @Width.setter
    @abc.abstractmethod
    def Width(self, value:float):
        """Sets the width of the chart.
        
        This property sets the width of the chart in points (1/72 inch).
        
        Args:
            value (float): The width of the chart in points.
        """
        pass


    @property
    @abc.abstractmethod
    def Height(self)->float:
        """Gets the height of the chart.
        
        This property returns the height of the chart in points (1/72 inch).
        
        Returns:
            float: The height of the chart in points.
        """
        pass


    @Height.setter
    @abc.abstractmethod
    def Height(self, value:float):
        """Sets the height of the chart.
        
        This property sets the height of the chart in points (1/72 inch).
        
        Args:
            value (float): The height of the chart in points.
        """
        pass


    @property
    @abc.abstractmethod
    def Name(self)->str:
        """Gets the name of the chart's worksheet.
        
        This property returns the name of the worksheet that contains the chart.
        For chart sheets, this is the name of the chart sheet.
        
        Returns:
            str: The name of the chart's worksheet.
        """
        pass


    @Name.setter
    @abc.abstractmethod
    def Name(self, value:str):
        """Sets the name of the chart's worksheet.
        
        This property sets the name of the worksheet that contains the chart.
        For chart sheets, this is the name of the chart sheet.
        
        Args:
            value (str): The new name for the chart's worksheet.
        """
        pass


    @property
    @abc.abstractmethod
    def PrimaryCategoryAxis(self)->'IChartCategoryAxis':
        """Gets the primary category axis of the chart.
        
        This property returns the primary category (X) axis object of the chart,
        allowing you to format and customize the axis appearance and behavior.
        This is a read-only property.
        
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
            chart = workbook.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Chart category axis
            categoryAxis = chart.PrimaryCategoryAxis
            #Set visibility
            categoryAxis.Visible = false
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            IChartCategoryAxis: The primary category axis object of the chart.
        """
        pass


    @property
    @abc.abstractmethod
    def PrimaryValueAxis(self)->'IChartValueAxis':
        """Gets the primary value axis of the chart.
        
        This property returns the primary value (Y) axis object of the chart,
        allowing you to format and customize the axis appearance and behavior.
        This is a read-only property.
        
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
            chart = workbook.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Chart value axis
            valueAxis = chart.PrimaryValueAxis
            #Set visibility
            valueAxis.Visible = false
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            IChartValueAxis: The primary value axis object of the chart.
        """
        pass


    @property
    @abc.abstractmethod
    def PrimarySerieAxis(self)->'IChartSeriesAxis':
        """
        Primary serie axis. Read-only.
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
            chart = workbook.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Surface3D
            #Chart series axis
            seriesAxis = chart.PrimarySerieAxis
            #Set visibility
            seriesAxis.Visible = false
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            IChartSeriesAxis: The primary series axis object of the chart.
        """
        pass


    @property
    @abc.abstractmethod
    def SecondaryCategoryAxis(self)->'IChartCategoryAxis':
        """Gets the secondary category axis of the chart.
        
        This property returns the secondary category (X) axis object of the chart,
        allowing you to format and customize the axis appearance and behavior.
        This is used for charts with two category axes. This is a read-only property.
        
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
            worksheet.Range["A3"].Value = "100"
            worksheet.Range["B3"].Value = "200"
            worksheet.Range["C3"].Value = "300"
            #Create chart and range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set secondary axis
            serie = chart.Series[1]
            serie.UsePrimaryAxis = false
            chart.SecondaryCategoryAxis.Visible = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            IChartCategoryAxis: The secondary category axis object of the chart.
        """
        pass


    @property
    @abc.abstractmethod
    def SecondaryValueAxis(self)->'IChartValueAxis':
        """Gets the secondary value axis of the chart.
        
        This property returns the secondary value (Y) axis object of the chart,
        allowing you to format and customize the axis appearance and behavior.
        This is used for charts with two value axes. This is a read-only property.
        
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
            worksheet.Range["A3"].Value = "100"
            worksheet.Range["B3"].Value = "200"
            worksheet.Range["C3"].Value = "300"
            #Create chart and range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set secondary axis
            serie = chart.Series[1]
            serie.UsePrimaryAxis = false
            chart.SecondaryValueAxis.Visible = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            IChartValueAxis: The secondary value axis object of the chart.
        """
        pass


    @property
    @abc.abstractmethod
    def ChartArea(self)->'IChartFrameFormat':
        """Gets the chart area format object of the chart.
        
        This property returns the chart area format object that represents the complete
        chart area, allowing you to format its appearance including borders, fill, and effects.
        The chart area is the entire area within the chart. This is a read-only property.
        
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

        Returns:
            IChartFrameFormat: The chart area format object of the chart.
        """
        pass


    @property
    @abc.abstractmethod
    def PlotArea(self)->'IChartFrameFormat':
        """Gets the plot area format object of the chart.
        
        This property returns the plot area format object that represents the plot area
        of the chart, allowing you to format its appearance including borders, fill, and effects.
        The plot area is the area where the data is plotted. This is a read-only property.
        
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

        Returns:
            IChartFrameFormat: The plot area format object of the chart.
        """
        pass


    @property
    @abc.abstractmethod
    def Walls(self)->'IChartWallOrFloor':
        """
        Represents chart walls. Read-only.
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

        Returns:
            IChartWallOrFloor: The walls object of the chart.
        """
        pass


    @property
    @abc.abstractmethod
    def Floor(self)->'IChartWallOrFloor':
        """Gets the floor object of the chart.
        
        This property returns the floor object that represents the floor of a 3D chart,
        allowing you to format its appearance including borders, fill, and effects.
        This is applicable only to 3D charts. This is a read-only property.
        
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

        Returns:
            IChartWallOrFloor: The floor object of the chart.
        """
        pass


    @property
    @abc.abstractmethod
    def DataTable(self)->'IChartDataTable':
        """Gets the data table object of the chart.
        
        This property returns the data table object that represents the data table
        displayed with the chart, allowing you to format its appearance and contents.
        A data table shows the chart data in a tabular format below the chart.
        
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

        Returns:
            IChartDataTable: The data table object of the chart.
        """
        pass


    @property
    @abc.abstractmethod
    def HasDataTable(self)->bool:
        """Gets whether the chart has a data table.
        
        This property indicates whether the chart displays a data table.
        A data table shows the chart data in a tabular format below the chart.
        
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
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if the chart has a data table, otherwise False.
        """
        pass


    @HasDataTable.setter
    @abc.abstractmethod
    def HasDataTable(self, value:bool):
        """Sets whether the chart has a data table.
        
        This property controls whether the chart displays a data table.
        A data table shows the chart data in a tabular format below the chart.
        
        Args:
            value (bool): True to display a data table, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def Legend(self)->'IChartLegend':
        """Gets the legend object of the chart.
        
        This property returns the legend object that represents the legend
        displayed with the chart, allowing you to format its appearance and position.
        A legend identifies the patterns or colors that are assigned to the
        categories in the chart.
        
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

        Returns:
            IChartLegend: The legend object of the chart.
        """
        pass


    @property
    @abc.abstractmethod
    def HasLegend(self)->bool:
        """Gets whether the chart has a legend.
        
        This property indicates whether the chart displays a legend.
        A legend identifies the patterns or colors that are assigned to the
        categories in the chart.
        
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
            #Set hasLegend
            chart.HasLegend = false
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if the chart has a legend, otherwise False.
        """
        pass


    @HasLegend.setter
    @abc.abstractmethod
    def HasLegend(self, value:bool):
        """Sets whether the chart has a legend.
        
        This property controls whether the chart displays a legend.
        A legend identifies the patterns or colors that are assigned to the
        categories in the chart.
        
        Args:
            value (bool): True to display a legend, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def Rotation(self)->int:
        """Gets the rotation angle of the 3-D chart view.
        
        This property returns the rotation angle of the 3-D chart view around the z-axis,
        in degrees. The value can range from 0 to 360 degrees. This property is applicable
        only to 3D charts.
        
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
            #Set Chart rotation
            chart.ChartType = ExcelChartType.Column3DClustered
            chart.Rotation = 50
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            int: The rotation angle of the 3-D chart view, from 0 to 360 degrees.
        """
        pass


    @Rotation.setter
    @abc.abstractmethod
    def Rotation(self, value:int):
        """Sets the rotation angle of the 3-D chart view.
        
        This property sets the rotation angle of the 3-D chart view around the z-axis,
        in degrees. The value can range from 0 to 360 degrees. This property is applicable
        only to 3D charts.
        
        Args:
            value (int): The rotation angle to set, from 0 to 360 degrees.
        """
        pass


    @property
    @abc.abstractmethod
    def Elevation(self)->int:
        """Gets the elevation angle of the 3-D chart view.
        
        This property returns the elevation angle of the 3-D chart view, in degrees.
        The value can range from -90 to 90 degrees, where 0 degrees represents a
        view level with the horizon. This property is applicable only to 3D charts.
        
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
            #Set Chart elevation
            chart.ChartType = ExcelChartType.Column3DClustered
            chart.Elevation = 50
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            int: The elevation angle of the 3-D chart view, from -90 to 90 degrees.
        """
        pass


    @Elevation.setter
    @abc.abstractmethod
    def Elevation(self, value:int):
        """Sets the elevation angle of the 3-D chart view.
        
        This property sets the elevation angle of the 3-D chart view, in degrees.
        The value can range from -90 to 90 degrees, where 0 degrees represents a
        view level with the horizon. This property is applicable only to 3D charts.
        
        Args:
            value (int): The elevation angle to set, from -90 to 90 degrees.
        """
        pass


    @property
    @abc.abstractmethod
    def Perspective(self)->int:
        """Gets the perspective of the 3-D chart view.
        
        This property returns the perspective for the 3-D chart view.
        The value can range from 0 to 100, where higher values indicate a
        more dramatic perspective effect. This property is applicable only
        to 3D charts.
        
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
            #Set Chart perspective
            chart.ChartType = ExcelChartType.Column3DClustered
            chart.Perspective = 70
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            int: The perspective of the 3-D chart view, from 0 to 100.
        """
        pass


    @Perspective.setter
    @abc.abstractmethod
    def Perspective(self, value:int):
        """Sets the perspective of the 3-D chart view.
        
        This property sets the perspective for the 3-D chart view.
        The value can range from 0 to 100, where higher values indicate a
        more dramatic perspective effect. This property is applicable only
        to 3D charts.
        
        Args:
            value (int): The perspective to set, from 0 to 100.
        """
        pass


    @property
    @abc.abstractmethod
    def HeightPercent(self)->int:
        """Gets the height of a 3-D chart as a percentage of the chart width.
        
        This property returns the height of a 3-D chart as a percentage of the chart width.
        The value can range from 5 to 500 percent. This property is applicable only to 3D charts.
        
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
            #Set Chart height percent
            chart.ChartType = ExcelChartType.Column3DClustered
            chart.AutoScaling = false
            chart.HeightPercent = 50
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            int: The height of the 3-D chart as a percentage of the chart width (5-500).
        """
        pass


    @HeightPercent.setter
    @abc.abstractmethod
    def HeightPercent(self, value:int):
        """Sets the height of a 3-D chart as a percentage of the chart width.
        
        This property sets the height of a 3-D chart as a percentage of the chart width.
        The value can range from 5 to 500 percent. This property is applicable only to 3D charts.
        
        Args:
            value (int): The height of the 3-D chart as a percentage of the chart width (5-500).
        """
        pass


    @property
    @abc.abstractmethod
    def DepthPercent(self)->int:
        """Gets the depth of a 3-D chart as a percentage of the chart width.
        
        This property returns the depth of a 3-D chart as a percentage of the chart width.
        The value can range from 20 to 2000 percent. This property is applicable only to 3D charts.
        
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
            #Set Chart depth percent
            chart.ChartType = ExcelChartType.Column3DClustered
            chart.DepthPercent = 500
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            int: The depth of the 3-D chart as a percentage of the chart width (20-2000).
        """
        pass


    @DepthPercent.setter
    @abc.abstractmethod
    def DepthPercent(self, value:int):
        """Sets the depth of a 3-D chart as a percentage of the chart width.
        
        This property sets the depth of a 3-D chart as a percentage of the chart width.
        The value can range from 20 to 2000 percent. This property is applicable only to 3D charts.
        
        Args:
            value (int): The depth of the 3-D chart as a percentage of the chart width (20-2000).
        """
        pass


    @property
    @abc.abstractmethod
    def GapDepth(self)->int:
        """Gets the distance between data series in a 3-D chart.
        
        This property returns the distance between data series in a 3-D chart,
        as a percentage of the marker width. The value can range from 0 to 500 percent.
        This property is applicable only to 3D charts.
        
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
            #Set gap depth
            chart.ChartType = ExcelChartType.Column3DClustered
            chart.GapDepth = 450
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            int: The distance between data series as a percentage of the marker width (0-500).
        """
        pass


    @GapDepth.setter
    @abc.abstractmethod
    def GapDepth(self, value:int):
        """Sets the distance between data series in a 3-D chart.
        
        This property sets the distance between data series in a 3-D chart,
        as a percentage of the marker width. The value can range from 0 to 500 percent.
        This property is applicable only to 3D charts.
        
        Args:
            value (int): The distance between data series as a percentage of the marker width (0-500).
        """
        pass


    @property
    @abc.abstractmethod
    def RightAngleAxes(self)->bool:
        """Gets whether the chart axes are at right angles.
        
        When true, the chart axes are at right angles, independent of chart rotation or elevation.
        This property is applicable only to 3D charts.
        
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
            #Set Chart rotation and RightAngleAxes
            chart.ChartType = ExcelChartType.Column3DClustered
            chart.Rotation = 50
            chart.RightAngleAxes = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if the chart axes are at right angles, otherwise False.
        """
        pass


    @RightAngleAxes.setter
    @abc.abstractmethod
    def RightAngleAxes(self, value:bool):
        """Sets whether the chart axes are at right angles.
        
        When true, the chart axes are at right angles, independent of chart rotation or elevation.
        This property is applicable only to 3D charts.
        
        Args:
            value (bool): True to set the chart axes at right angles, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def AutoScaling(self)->bool:
        """Gets whether Excel scales a 3-D chart for better viewing.
        
        When true, Excel scales a 3-D chart so that it's closer in size to the equivalent 2-D chart.
        This property is applicable only to 3D charts.
        
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
            #Set auto scaling
            chart.ChartType = ExcelChartType.Column3DClustered
            chart.HeightPercent = 50
            chart.AutoScaling = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if Excel automatically scales the 3-D chart, otherwise False.
        """
        pass


    @AutoScaling.setter
    @abc.abstractmethod
    def AutoScaling(self, value:bool):
        """Sets whether Excel scales a 3-D chart for better viewing.
        
        When true, Excel scales a 3-D chart so that it's closer in size to the equivalent 2-D chart.
        This property is applicable only to 3D charts.
        
        Args:
            value (bool): True to enable automatic scaling of the 3-D chart, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def WallsAndGridlines2D(self)->bool:
        """Gets whether gridlines are drawn two-dimensionally on a 3-D chart.
        
        When true, gridlines are drawn two-dimensionally on a 3-D chart,
        which can improve readability. This property is applicable only to 3D charts.
        
        Returns:
            bool: True if gridlines are drawn two-dimensionally, otherwise False.
        """
        pass


    @WallsAndGridlines2D.setter
    @abc.abstractmethod
    def WallsAndGridlines2D(self, value:bool):
        """Sets whether gridlines are drawn two-dimensionally on a 3-D chart.
        
        When true, gridlines are drawn two-dimensionally on a 3-D chart,
        which can improve readability. This property is applicable only to 3D charts.
        
        Args:
            value (bool): True to draw gridlines two-dimensionally, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def HasPlotArea(self)->bool:
        """Gets whether the chart has a plot area.
        
        This property indicates whether the chart displays a plot area.
        The plot area is the area where the data is plotted.
        
        Returns:
            bool: True if the chart has a plot area, otherwise False.
        """
        pass


    @HasPlotArea.setter
    @abc.abstractmethod
    def HasPlotArea(self, value:bool):
        """Sets whether the chart has a plot area.
        
        This property controls whether the chart displays a plot area.
        The plot area is the area where the data is plotted.
        
        Args:
            value (bool): True to display a plot area, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def DisplayBlanksAs(self)->'ChartPlotEmptyType':
        """Gets how blank cells are plotted on the chart.
        
        This property returns the way that blank cells are plotted on a chart,
        such as not plotted (gaps), plotted as zero, or plotted as interpolated values.
        
        Returns:
            ChartPlotEmptyType: The way blank cells are plotted on the chart.
        """
        pass


    @DisplayBlanksAs.setter
    @abc.abstractmethod
    def DisplayBlanksAs(self, value:'ChartPlotEmptyType'):
        """Sets how blank cells are plotted on the chart.
        
        This property sets the way that blank cells are plotted on a chart,
        such as not plotted (gaps), plotted as zero, or plotted as interpolated values.
        
        Args:
            value (ChartPlotEmptyType): The way to plot blank cells on the chart.
        """
        pass


    @property
    @abc.abstractmethod
    def PlotVisibleOnly(self)->bool:
        """Gets whether only visible cells are plotted in the chart.
        
        When true, only visible cells are plotted in the chart.
        When false, both visible and hidden cells are plotted.
        This is useful when working with filtered data or hidden rows/columns.
        
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
            #Hide column and create chart
            worksheet.Columns[2].ColumnWidth = 0
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set Plot visible only
            chart.PlotVisibleOnly = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if only visible cells are plotted, False if both visible and hidden cells are plotted.
        """
        pass


    @PlotVisibleOnly.setter
    @abc.abstractmethod
    def PlotVisibleOnly(self, value:bool):
        """Sets whether only visible cells are plotted in the chart.
        
        When true, only visible cells are plotted in the chart.
        When false, both visible and hidden cells are plotted.
        This is useful when working with filtered data or hidden rows/columns.
        
        Args:
            value (bool): True to plot only visible cells, False to plot both visible and hidden cells.
        """
        pass


    @property
    @abc.abstractmethod
    def SizeWithWindow(self)->bool:
        """Gets whether the chart resizes with the window.
        
        When true, Excel resizes the chart to match the size of the chart sheet window.
        When false, the chart size isn't attached to the window size.
        This property applies only to chart sheets, not embedded charts.
        
        Returns:
            bool: True if the chart resizes with the window, otherwise False.
        """
        pass


    @SizeWithWindow.setter
    @abc.abstractmethod
    def SizeWithWindow(self, value:bool):
        """Sets whether the chart resizes with the window.
        
        When true, Excel resizes the chart to match the size of the chart sheet window.
        When false, the chart size isn't attached to the window size.
        This property applies only to chart sheets, not embedded charts.
        
        Args:
            value (bool): True to resize the chart with the window, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def PivotTable(self)->'PivotTable':
        """Gets the pivot table source for the chart.
        
        This property returns the pivot table that provides the data for the chart.
        This is applicable only for pivot charts.
        
        Returns:
            PivotTable: The pivot table source for the chart.
        """
        pass


    @PivotTable.setter
    @abc.abstractmethod
    def PivotTable(self, value:'PivotTable'):
        """Sets the pivot table source for the chart.
        
        This property sets the pivot table that provides the data for the chart.
        This is applicable only for pivot charts.
        
        Args:
            value (PivotTable): The pivot table source to set for the chart.
        """
        pass


    @property
    @abc.abstractmethod
    def PivotChartType(self)->'ExcelChartType':
        """Gets the chart type for the pivot chart.
        
        This property returns the chart type used for the pivot chart,
        such as column, bar, line, pie, etc. This is applicable only for pivot charts.
        
        Returns:
            ExcelChartType: The chart type for the pivot chart.
        """
        pass


    @PivotChartType.setter
    @abc.abstractmethod
    def PivotChartType(self, value:'ExcelChartType'):
        """Sets the chart type for the pivot chart.
        
        This property sets the chart type used for the pivot chart,
        such as column, bar, line, pie, etc. This is applicable only for pivot charts.
        
        Args:
            value (ExcelChartType): The chart type to set for the pivot chart.
        """
        pass


    @property
    @abc.abstractmethod
    def DisplayEntireFieldButtons(self)->bool:
        """Gets whether all field buttons are displayed in the pivot chart.
        
        When true, all field buttons are displayed in the pivot chart.
        Field buttons allow users to interactively filter and manipulate the pivot chart.
        This is applicable only for pivot charts.
        
        Returns:
            bool: True if all field buttons are displayed, otherwise False.
        """
        pass


    @DisplayEntireFieldButtons.setter
    @abc.abstractmethod
    def DisplayEntireFieldButtons(self, value:bool):
        """Sets whether all field buttons are displayed in the pivot chart.
        
        When true, all field buttons are displayed in the pivot chart.
        Field buttons allow users to interactively filter and manipulate the pivot chart.
        This is applicable only for pivot charts.
        
        Args:
            value (bool): True to display all field buttons, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def DisplayValueFieldButtons(self)->bool:
        """Gets whether value field buttons are displayed in the pivot chart.
        
        When true, value field buttons are displayed in the pivot chart.
        Value field buttons allow users to interactively select which values to display in the pivot chart.
        This is applicable only for pivot charts.
        
        Returns:
            bool: True if value field buttons are displayed, otherwise False.
        """
        pass


    @DisplayValueFieldButtons.setter
    @abc.abstractmethod
    def DisplayValueFieldButtons(self, value:bool):
        """Sets whether value field buttons are displayed in the pivot chart.
        
        When true, value field buttons are displayed in the pivot chart.
        Value field buttons allow users to interactively select which values to display in the pivot chart.
        This is applicable only for pivot charts.
        
        Args:
            value (bool): True to display value field buttons, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def DisplayAxisFieldButtons(self)->bool:
        """Gets whether axis field buttons are displayed in the pivot chart.
        
        When true, axis field buttons are displayed in the pivot chart.
        Axis field buttons allow users to interactively select which fields to display on the axes.
        This is applicable only for pivot charts.
        
        Returns:
            bool: True if axis field buttons are displayed, otherwise False.
        """
        pass


    @DisplayAxisFieldButtons.setter
    @abc.abstractmethod
    def DisplayAxisFieldButtons(self, value:bool):
        """Sets whether axis field buttons are displayed in the pivot chart.
        
        When true, axis field buttons are displayed in the pivot chart.
        Axis field buttons allow users to interactively select which fields to display on the axes.
        This is applicable only for pivot charts.
        
        Args:
            value (bool): True to display axis field buttons, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def DisplayLegendFieldButtons(self)->bool:
        """Gets whether legend field buttons are displayed in the pivot chart.
        
        When true, legend field buttons are displayed in the pivot chart.
        Legend field buttons allow users to interactively select which fields to display in the legend.
        This is applicable only for pivot charts.
        
        Returns:
            bool: True if legend field buttons are displayed, otherwise False.
        """
        pass


    @DisplayLegendFieldButtons.setter
    @abc.abstractmethod
    def DisplayLegendFieldButtons(self, value:bool):
        """Sets whether legend field buttons are displayed in the pivot chart.
        
        When true, legend field buttons are displayed in the pivot chart.
        Legend field buttons allow users to interactively select which fields to display in the legend.
        This is applicable only for pivot charts.
        
        Args:
            value (bool): True to display legend field buttons, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def ShowReportFilterFieldButtons(self)->bool:
        """Gets whether report filter field buttons are displayed in the pivot chart.
        
        When true, report filter field buttons are displayed in the pivot chart.
        Report filter field buttons allow users to interactively filter the data displayed in the pivot chart.
        This is applicable only for pivot charts.
        
        Returns:
            bool: True if report filter field buttons are displayed, otherwise False.
        """
        pass


    @ShowReportFilterFieldButtons.setter
    @abc.abstractmethod
    def ShowReportFilterFieldButtons(self, value:bool):
        """

        """
        pass


