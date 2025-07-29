from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ChartArea (  XlsChartFrameFormat) :
    """

    """
    @property

    def Border(self)->'ChartBorder':
        """
        Represents chart border. Read only.

        """
        GetDllLibXls().ChartArea_get_Border.argtypes=[c_void_p]
        GetDllLibXls().ChartArea_get_Border.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartArea_get_Border, self.Ptr)
        ret = None if intPtr==None else ChartBorder(intPtr)
        return ret


    @property

    def Interior(self)->'ChartInterior':
        """
        Represents chart interior. Read only.
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
        GetDllLibXls().ChartArea_get_Interior.argtypes=[c_void_p]
        GetDllLibXls().ChartArea_get_Interior.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartArea_get_Interior, self.Ptr)
        ret = None if intPtr==None else ChartInterior(intPtr)
        return ret


