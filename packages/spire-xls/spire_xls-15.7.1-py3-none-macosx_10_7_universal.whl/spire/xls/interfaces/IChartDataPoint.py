from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartDataPoint (  IExcelApplication) :
    """
    Represents data point in the chart.

    """
    @property

    @abc.abstractmethod
    def DataLabels(self)->'IChartDataLabels':
        """
        Returns data labels object for the data point. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Get the chart serie
            serie = chart.Series[0]
            #Set data labels value visibility
            serie.DataPoints.DefaultDataPoint.DataLabels.HasValue = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property
    @abc.abstractmethod
    def Index(self)->int:
        """
        Gets index of the point in the points collection.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set serie
            serie = chart.Series[0]
            #Get index
            print(serie.DataPoints[0].Index)

        """
        pass


    @property

    @abc.abstractmethod
    def DataFormat(self)->'IChartSerieDataFormat':
        """
        Gets / sets data format.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart type
            chart.ChartType = ExcelChartType.Line
            #Set serie format
            format = chart.Series[0].DataFormat
            #Set marker style
            format.MarkerStyle = ChartMarkerType.Star
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        pass


    @property
    @abc.abstractmethod
    def IsDefault(self)->bool:
        """
        Indicates whether this data point is default data point. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set serie format
            dataPoints = chart.Series[0].DataPoints
            #Check default Datapoint
            print(dataPoints.DefaultDataPoint.IsDefault)
            print(dataPoints[0].IsDefault)

        """
        pass


