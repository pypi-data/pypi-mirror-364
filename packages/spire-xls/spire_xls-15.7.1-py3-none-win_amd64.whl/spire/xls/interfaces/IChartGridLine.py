from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartGridLine (abc.ABC) :
    """Chart grid line interface.
    
    This interface represents the grid lines in an Excel chart. Grid lines are horizontal or
    vertical lines that extend from the tick marks on an axis across the plot area, making it
    easier to view and evaluate data points. The interface provides functionality for formatting
    grid lines, including border properties, 3D effects, shadows, line properties, interior
    formatting, and fill options.
    """
    @property

    @abc.abstractmethod
    def Border(self)->'ChartBorder':
        """
        Gets line border. Read only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set value axis minor gridLines to visible
            chart.PrimaryValueAxis.HasMinorGridLines = true
            #Get value axis minor gridlines
            gridLine = chart.PrimaryValueAxis.MinorGridLines
            Set minor gridlines broder properties
            gridLine.Border.Color = Color.Red
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property

    @abc.abstractmethod
    def Format3D(self)->'Format3D':
        """
        Gets the chart3 D properties.

        """
        pass


    @property

    @abc.abstractmethod
    def Shadow(self)->'ChartShadow':
        """
        Gets the shadow properties.

        """
        pass


    @property

    @abc.abstractmethod
    def LineProperties(self)->'ChartBorder':
        """
        Returns object, that represents line properties. Read-only.

        """
        pass


    @property

    @abc.abstractmethod
    def Interior(self)->'IChartInterior':
        """
        Returns object, that represents area properties. Read-only.

        """
        pass


    @property

    @abc.abstractmethod
    def Fill(self)->'IShapeFill':
        """
        Represents XlsFill options. Read-only.

        """
        pass


