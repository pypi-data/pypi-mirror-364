from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartAxis (abc.ABC) :
    """Chart axis interface for Excel charts.
    
    This interface represents a chart axis in Excel. It provides properties and methods
    to customize the appearance and behavior of chart axes, including formatting options,
    gridlines, tick marks, and text display settings.
    
    The IChartAxis serves as the base interface for more specific axis types like
    IChartValueAxis and IChartCategoryAxis.
    """
    @property
    @abc.abstractmethod
    def NumberFormat(self)->str:
        """Gets the number format string for the axis labels.
        
        This property returns the format code that Excel uses to format numbers on the axis.
        Format codes are the same as those used in the Format Cells dialog box in Excel.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Add data
            worksheet.Range["A1"].Text = "Jan"
            worksheet.Range["B1"].Text = "Feb"
            worksheet.Range["C1"].Text = "Mar"
            worksheet.Range["A2"].Text = "10000"
            worksheet.Range["B2"].Text = "20000"
            worksheet.Range["C2"].Text = "30000"
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart value axis
            chartAxis = chart.PrimaryValueAxis
            #Set number format
            chartAxis.NumberFormat = @"$#,#0_);($#,#0)"
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            str: The number format string for the axis labels.
        """
        pass


    @NumberFormat.setter
    @abc.abstractmethod
    def NumberFormat(self, value:str):
        """Sets the number format string for the axis labels.
        
        This property sets the format code that Excel uses to format numbers on the axis.
        Format codes are the same as those used in the Format Cells dialog box in Excel.
        
        Args:
            value (str): The number format string to apply to the axis labels.
        """
        pass


    @property
    @abc.abstractmethod
    def AxisType(self)->'AxisType':
        """Gets the type of the axis.
        
        This property returns the type of the axis, which can be a category axis,
        value axis, or series axis. This is a read-only property.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Add data
            worksheet.Range["A1"].Text = "Jan"
            worksheet.Range["B1"].Text = "Feb"
            worksheet.Range["C1"].Text = "Mar"
            worksheet.Range["A2"].Text = "10000"
            worksheet.Range["B2"].Text = "20000"
            worksheet.Range["C2"].Text = "30000"
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart value axis
            chartAxis = chart.PrimaryValueAxis
            #Get axis type
            print(chartAxis.AxisType)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            AxisType: The type of the axis.
        """
        pass


    @property
    @abc.abstractmethod
    def Title(self)->str:
        """Gets the title text of the axis.
        
        This property returns the text displayed as the title for the axis.
        
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
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart category axis
            categoryAxis = chart.PrimaryCategoryAxis
            #Set category title
            categoryAxis.Title = "Categories"
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            str: The title text of the axis.
        """
        pass


    @Title.setter
    @abc.abstractmethod
    def Title(self, value:str):
        """Sets the title text of the axis.
        
        This property sets the text displayed as the title for the axis.
        
        Args:
            value (str): The title text to set for the axis.
        """
        pass


    @property
    @abc.abstractmethod
    def TextRotationAngle(self)->int:
        """Gets the rotation angle of the axis text labels.
        
        This property specifies the angle of rotation for the text in the axis labels.
        The value should be an integer between -90 and 90 degrees, where positive values
        rotate the text upward and negative values rotate the text downward.
        
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
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart category axis
            chartAxis =  chart.PrimaryCategoryAxis
            #Set text rotation angle
            chartAxis.TextRotationAngle = 90
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            int: The rotation angle of the axis text labels, between -90 and 90 degrees.
        """
        pass


    @TextRotationAngle.setter
    @abc.abstractmethod
    def TextRotationAngle(self, value:int):
        """Sets the rotation angle of the axis text labels.
        
        This property specifies the angle of rotation for the text in the axis labels.
        The value should be an integer between -90 and 90 degrees, where positive values
        rotate the text upward and negative values rotate the text downward.
        
        Args:
            value (int): The rotation angle to set, between -90 and 90 degrees.
        """
        pass


    @property
    @abc.abstractmethod
    def TitleArea(self)->'IChartTextArea':
        """Gets the text area object for the axis title.
        
        This property returns the text area object that represents the axis title,
        allowing you to format the title's appearance including font, color, and borders.
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
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart category axis
            categoryAxis = chart.PrimaryCategoryAxis
            #Set category title
            categoryAxis.Title = "Categories"
            #Set title area
            titleArea = categoryAxis.TitleArea
            #Set color
            titleArea.FrameFormat.Fill.ForeKnownColor = ExcelColors.Red
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            IChartTextArea: The text area object for the axis title.
        """
        pass


    @property
    @abc.abstractmethod
    def Font(self)->'IFont':
        """Gets the font object for the axis labels.
        
        This property returns the font object that represents the font used for the axis labels,
        allowing you to format the font properties such as name, size, color, and style.
        
        Returns:
            IFont: The font object for the axis labels.
        """
        pass


    @property
    @abc.abstractmethod
    def MajorGridLines(self)->'IChartGridLine':
        """Gets the major gridlines object for the axis.
        
        This property returns the gridlines object that represents the major gridlines for the axis,
        allowing you to format their appearance or hide them.
        
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
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart axis
            chartAxis =  chart.PrimaryCategoryAxis
            #Set visibility
            chartAxis.HasMajorGridLines = true
            #Set grid lines
            gridLine = chartAxis.MajorGridLines
            gridLine.LineProperties.Color = Color.Red
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            IChartGridLine: The major gridlines object for the axis.
        """
        pass


    @property
    @abc.abstractmethod
    def MinorGridLines(self)->'IChartGridLine':
        """Gets the minor gridlines object for the axis.
        
        This property returns the gridlines object that represents the minor gridlines for the axis,
        allowing you to format their appearance or hide them.
        
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
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart axis
            chartAxis =  chart.PrimaryCategoryAxis
            #Set visibility
            chartAxis.HasMinorGridLines = true
            #Set grid lines
            gridLine = chartAxis.MinorGridLines
            gridLine.LineProperties.Color = Color.Red
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            IChartGridLine: The minor gridlines object for the axis.
        """
        pass


    @property
    @abc.abstractmethod
    def HasMinorGridLines(self)->bool:
        """Gets whether the axis displays minor gridlines.
        
        This property indicates whether minor gridlines are displayed for the axis.
        Minor gridlines are the lighter lines that appear between the major gridlines.
        
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
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart axis
            chartAxis =  chart.PrimaryCategoryAxis
            #Set visibility
            chartAxis.HasMinorGridLines = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if the axis displays minor gridlines, otherwise False.
        """
        pass


    @HasMinorGridLines.setter
    @abc.abstractmethod
    def HasMinorGridLines(self, value:bool):
        """Sets whether the axis displays minor gridlines.
        
        This property controls whether minor gridlines are displayed for the axis.
        Minor gridlines are the lighter lines that appear between the major gridlines.
        
        Args:
            value (bool): True to display minor gridlines, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def HasMajorGridLines(self)->bool:
        """Gets whether the axis displays major gridlines.
        
        This property indicates whether major gridlines are displayed for the axis.
        Major gridlines are the primary lines that correspond to the major tick marks on the axis.
        
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
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart axis
            chartAxis =  chart.PrimaryCategoryAxis
            #Set visibility
            chartAxis.HasMajorGridLines = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if the axis displays major gridlines, otherwise False.
        """
        pass


    @HasMajorGridLines.setter
    @abc.abstractmethod
    def HasMajorGridLines(self, value:bool):
        """Sets whether the axis displays major gridlines.
        
        This property controls whether major gridlines are displayed for the axis.
        Major gridlines are the primary lines that correspond to the major tick marks on the axis.
        
        Args:
            value (bool): True to display major gridlines, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def MinorTickMark(self)->'TickMarkType':
        """Gets the type of minor tick marks for the axis.
        
        This property returns the type of minor tick marks displayed on the axis,
        such as inside, outside, cross, or none.
        
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
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart category axis
            categoryAxis = chart.PrimaryCategoryAxis
            #Set category minor tick type
            categoryAxis.MinorTickMark = TickMarkType.TickMarkCross
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            TickMarkType: The type of minor tick marks for the axis.
        """
        pass


    @MinorTickMark.setter
    @abc.abstractmethod
    def MinorTickMark(self, value:'TickMarkType'):
        """Sets the type of minor tick marks for the axis.
        
        This property sets the type of minor tick marks displayed on the axis,
        such as inside, outside, cross, or none.
        
        Args:
            value (TickMarkType): The type of minor tick marks to display.
        """
        pass


    @property
    @abc.abstractmethod
    def MajorTickMark(self)->'TickMarkType':
        """Gets the type of major tick marks for the axis.
        
        This property returns the type of major tick marks displayed on the axis,
        such as inside, outside, cross, or none.
        
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
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart category axis
            categoryAxis = chart.PrimaryCategoryAxis
            #Set category minor tick type
            categoryAxis.MajorTickMark = TickMarkType.TickMarkCross
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            TickMarkType: The type of major tick marks for the axis.
        """
        pass


    @MajorTickMark.setter
    @abc.abstractmethod
    def MajorTickMark(self, value:'TickMarkType'):
        """Sets the type of major tick marks for the axis.
        
        This property sets the type of major tick marks displayed on the axis,
        such as inside, outside, cross, or none.
        
        Args:
            value (TickMarkType): The type of major tick marks to display.
        """
        pass


    @property
    @abc.abstractmethod
    def Border(self)->'ChartBorder':
        """Gets the border object for the axis.
        
        This property returns the border object that represents the line of the axis itself,
        allowing you to format its appearance including color, style, and weight.
        
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
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart value axis
            valueAxis = chart.PrimaryValueAxis
            #Set axis border
            valueAxis.Border.Color = Color.Red
            valueAxis.Border.Weight = BorderWeight.Medium
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            ChartBorder: The border object for the axis.
        """
        pass


    @property
    @abc.abstractmethod
    def TickLabelPosition(self)->'TickLabelPositionType':
        """Gets the position of the tick labels on the axis.
        
        This property returns the position of the tick labels relative to the axis,
        such as high, low, next to the axis, or none.
        
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
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart category axis
            categoryAxis = chart.PrimaryCategoryAxis
            #Set category tick labels position
            categoryAxis.TickLabelPosition = TickLabelPositionType.TickLabelPositionHigh
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            TickLabelPositionType: The position of the tick labels on the axis.
        """
        pass


    @TickLabelPosition.setter
    @abc.abstractmethod
    def TickLabelPosition(self, value:'TickLabelPositionType'):
        """Sets the position of the tick labels on the axis.
        
        This property sets the position of the tick labels relative to the axis,
        such as high, low, next to the axis, or none.
        
        Args:
            value (TickLabelPositionType): The position to place the tick labels.
        """
        pass


    @property
    @abc.abstractmethod
    def Visible(self)->bool:
        """Gets whether the axis is visible.
        
        This property indicates whether the axis is displayed in the chart.
        When set to False, the axis and its labels are hidden.
        
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
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart axis
            chartAxis =  chart.PrimaryCategoryAxis
            #Set visibility
            chartAxis.Visible = false
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if the axis is visible, otherwise False.
        """
        pass


    @Visible.setter
    @abc.abstractmethod
    def Visible(self, value:bool):
        """Sets whether the axis is visible.
        
        This property controls whether the axis is displayed in the chart.
        When set to False, the axis and its labels are hidden.
        
        Args:
            value (bool): True to make the axis visible, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def Alignment(self)->'AxisTextDirectionType':
        """Gets the text alignment for the axis labels.
        
        This property returns the text direction and alignment for the axis labels,
        such as horizontal, vertical, or rotated.
        
        Returns:
            AxisTextDirectionType: The text alignment for the axis labels.
        """
        pass


    @Alignment.setter
    @abc.abstractmethod
    def Alignment(self, value:'AxisTextDirectionType'):
        """Sets the text alignment for the axis labels.
        
        This property sets the text direction and alignment for the axis labels,
        such as horizontal, vertical, or rotated.
        
        Args:
            value (AxisTextDirectionType): The text alignment to set for the axis labels.
        """
        pass


    @property
    @abc.abstractmethod
    def Shadow(self)->'ChartShadow':
        """Gets the shadow object for the axis.
        
        This property returns the shadow object that represents the shadow effect applied to the axis,
        allowing you to format the shadow's appearance.
        
        Returns:
            ChartShadow: The shadow object for the axis.
        """
        pass


    @property
    @abc.abstractmethod
    def Chart3DOptions(self)->'IFormat3D':
        """Gets the 3D format properties for the axis.
        
        This property returns the 3D format object that represents the three-dimensional
        formatting properties for the axis in a 3D chart.
        
        Returns:
            IFormat3D: The 3D format properties object for the axis.
        """
        pass


    @property
    @abc.abstractmethod
    def IsSourceLinked(self)->bool:
        """Gets whether the axis title text is linked to the source data.
        
        This property indicates whether the axis title text is automatically generated
        from the source data or manually specified.
        
        Returns:
            bool: True if the axis title is linked to the source data, otherwise False.
        """
        pass


    @IsSourceLinked.setter
    @abc.abstractmethod
    def IsSourceLinked(self, value:bool):
        """Sets whether the axis title text is linked to the source data.
        
        This property controls whether the axis title text is automatically generated
        from the source data or manually specified.
        
        Args:
            value (bool): True to link the axis title to the source data, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def TextDirection(self)->'TextVerticalValue':
        """Gets the text direction for the axis labels.
        
        This property returns the vertical text direction for the axis labels,
        such as horizontal, vertical, or rotated text.
        
        Returns:
            TextVerticalValue: The text direction for the axis labels.
        """
        pass


    @TextDirection.setter
    @abc.abstractmethod
    def TextDirection(self, value:'TextVerticalValue'):
        """Sets the text direction for the axis labels.
        
        This property sets the vertical text direction for the axis labels,
        such as horizontal, vertical, or rotated text.
        
        Args:
            value (TextVerticalValue): The text direction to set for the axis labels.
        """
        pass


