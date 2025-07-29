from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartBorder (abc.ABC) :
    """
    Represents chart border. Provides Border options for Chart Area and Plot Area.

    """
    @property

    @abc.abstractmethod
    def Color(self)->'Color':
        """
        Color of line.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set line color for chart area border
            chart.ChartArea.Border.Color = Color.DarkOrange
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @Color.setter
    @abc.abstractmethod
    def Color(self, value:'Color'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Pattern(self)->'ChartLinePatternType':
        """
        Line pattern.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set line pattern for plot area border
            chart.ChartArea.Border.Pattern = ChartLinePatternType.DashDotDot
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @Pattern.setter
    @abc.abstractmethod
    def Pattern(self, value:'ChartLinePatternType'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Weight(self)->'ChartLineWeightType':
        """
        Weight of line.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set line weight for plot area border
            chart.ChartArea.Border.Weight = ChartLineWeightType.Wide
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @Weight.setter
    @abc.abstractmethod
    def Weight(self, value:'ChartLineWeightType'):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def UseDefaultFormat(self)->bool:
        """
        If true - default format; otherwise custom.

        """
        pass


    @UseDefaultFormat.setter
    @abc.abstractmethod
    def UseDefaultFormat(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def UseDefaultLineColor(self)->bool:
        """
        Custom format for line color.

        """
        pass


    @UseDefaultLineColor.setter
    @abc.abstractmethod
    def UseDefaultLineColor(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def KnownColor(self)->'ExcelColors':
        """
        Line color index.

        """
        pass


    @KnownColor.setter
    @abc.abstractmethod
    def KnownColor(self, value:'ExcelColors'):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def Transparency(self)->float:
        """
        Returns the transparency level of the specified Solid color shaded XlsFill as a floating-point value from 0.0 (Clear) through 1.0(Opaque).
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["B2:C6"]
            #Set the transparency level of the solid color
            chart.ChartArea.Border.Transparency =0.85
            chart.ChartArea.Border.Color = Color.Red
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @Transparency.setter
    @abc.abstractmethod
    def Transparency(self, value:float):
        """

        """
        pass


