from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from spire.xls.charts.XlsChartBorder import *
from ctypes import *
import abc

class IChartErrorBars (SpireObject) :
    """
    Represent error bars on the chart series. Error bars indicate the degree of uncertainty for chart data. Only series in area, bar, column, line, and scatter groups on a 2-D chart can have error bars. Only series in scatter groups can have x and y error bars.

    """
    @property

    def Border(self)->'IChartBorder':
        """
        Represents border object. Read only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnClustered
            #Get chart serie
            serie = chart.Series[0]
            #Enabling the Y Error bars
            serie.ErrorBar(true,ErrorBarIncludeType.Both,ErrorBarType.Percentage,10)
            errorBars = serie.ErrorBarsY
            #Set Error bars border color
            errorBars.Border.Color = Color.Red
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartErrorBars_get_Border.argtypes=[c_void_p]
        GetDllLibXls().IChartErrorBars_get_Border.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IChartErrorBars_get_Border, self.Ptr)
        ret = None if intPtr==None else XlsChartBorder(intPtr)
        return ret


    @property

    def Include(self)->'ErrorBarIncludeType':
        """
        Reprsents error bar include type.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnClustered
            #Get chart serie
            serie = chart.Series[0]
            #Enabling the Y Error bars
            serie.ErrorBar(true,ErrorBarIncludeType.Both,ErrorBarType.Percentage,10)
            errorBars = serie.ErrorBarsY
            #Set negative error only to include
            errorBars.Include = ErrorBarIncludeType.Minus
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartErrorBars_get_Include.argtypes=[c_void_p]
        GetDllLibXls().IChartErrorBars_get_Include.restype=c_int
        ret = CallCFunction(GetDllLibXls().IChartErrorBars_get_Include, self.Ptr)
        objwraped = ErrorBarIncludeType(ret)
        return objwraped

    @Include.setter
    def Include(self, value:'ErrorBarIncludeType'):
        GetDllLibXls().IChartErrorBars_set_Include.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().IChartErrorBars_set_Include, self.Ptr, value.value)

    @property
    def HasCap(self)->bool:
        """
        Indicates if error bar has cap.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnClustered
            #Get chart serie
            serie = chart.Series[0]
            #Enabling the Y Error bars
            serie.ErrorBar(true,ErrorBarIncludeType.Both,ErrorBarType.Percentage,10)
            errorBars = serie.ErrorBarsY
            #Set false to remove the end style
            errorBars.HasCap = false
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartErrorBars_get_HasCap.argtypes=[c_void_p]
        GetDllLibXls().IChartErrorBars_get_HasCap.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IChartErrorBars_get_HasCap, self.Ptr)
        return ret

    @HasCap.setter
    def HasCap(self, value:bool):
        GetDllLibXls().IChartErrorBars_set_HasCap.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IChartErrorBars_set_HasCap, self.Ptr, value)

    @property

    def Type(self)->'ErrorBarType':
        """
        Represents excel error bar type.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnClustered
            #Get chart serie
            serie = chart.Series[0]
            #Enabling the Y Error bars
            serie.ErrorBar(true,ErrorBarIncludeType.Both,ErrorBarType.Percentage,10)
            errorBars = serie.ErrorBarsY
            #Set error amount to standard deviation
            errorBars.Type = ErrorBarType.StandardDeviation
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartErrorBars_get_Type.argtypes=[c_void_p]
        GetDllLibXls().IChartErrorBars_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibXls().IChartErrorBars_get_Type, self.Ptr)
        objwraped = ErrorBarType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'ErrorBarType'):
        GetDllLibXls().IChartErrorBars_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().IChartErrorBars_set_Type, self.Ptr, value.value)

    @property
    def NumberValue(self)->float:
        """
        Represents number value.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnClustered
            #Get chart serie
            serie = chart.Series[0]
            #Enabling the Y Error bars
            serie.ErrorBar(true,ErrorBarIncludeType.Both,ErrorBarType.Percentage,10)
            errorBars = serie.ErrorBarsY
            #Set error value
            errorBars.NumberValue = 3.0
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartErrorBars_get_NumberValue.argtypes=[c_void_p]
        GetDllLibXls().IChartErrorBars_get_NumberValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().IChartErrorBars_get_NumberValue, self.Ptr)
        return ret

    @NumberValue.setter
    def NumberValue(self, value:float):
        GetDllLibXls().IChartErrorBars_set_NumberValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().IChartErrorBars_set_NumberValue, self.Ptr, value)

    @property

    def PlusRange(self)->'IXLSRange':
        """
        Represents custom plus value.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnClustered
            #Get chart serie
            serie = chart.Series[0]
            #Enabling the Y Error bars
            serie.ErrorBar(true,ErrorBarIncludeType.Both,ErrorBarType.Percentage,10)
            errorBars = serie.ErrorBarsY
            #Set plus range
            errorBars.PlusRange = worksheet["D2"]
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartErrorBars_get_PlusRange.argtypes=[c_void_p]
        GetDllLibXls().IChartErrorBars_get_PlusRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IChartErrorBars_get_PlusRange, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @PlusRange.setter
    def PlusRange(self, value:'IXLSRange'):
        GetDllLibXls().IChartErrorBars_set_PlusRange.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().IChartErrorBars_set_PlusRange, self.Ptr, value.Ptr)

    @property

    def MinusRange(self)->'IXLSRange':
        """
        Represents custom minus value.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnClustered
            #Get chart serie
            serie = chart.Series[0]
            #Enabling the Y Error bars
            serie.ErrorBar(true,ErrorBarIncludeType.Both,ErrorBarType.Percentage,10)
            errorBars = serie.ErrorBarsY
            #Set minus range
            errorBars.MinusRange = worksheet["D2"]
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartErrorBars_get_MinusRange.argtypes=[c_void_p]
        GetDllLibXls().IChartErrorBars_get_MinusRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IChartErrorBars_get_MinusRange, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @MinusRange.setter
    def MinusRange(self, value:'IXLSRange'):
        GetDllLibXls().IChartErrorBars_set_MinusRange.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().IChartErrorBars_set_MinusRange, self.Ptr, value.Ptr)

    @property

    def Shadow(self)->'IShadow':
        """
        Gets the shadow.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C3"]
            #Set chart type
            chart.ChartType = ExcelChartType.ColumnClustered
            #Get chart serie
            serie = chart.Series[0]
            #Enabling the Y Error bars
            serie.ErrorBar(true,ErrorBarIncludeType.Both,ErrorBarType.Percentage,10)
            errorBars = serie.ErrorBarsY
            #Set Error bars shadow color
            errorBars.Shadow.Color = Color.Red
            #Set Error bars shadow outer presets
            errorBars.Shadow.ShadowOuterType = XLSXChartShadowOuterType.OffsetDiagonalTopRight
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        """
        GetDllLibXls().IChartErrorBars_get_Shadow.argtypes=[c_void_p]
        GetDllLibXls().IChartErrorBars_get_Shadow.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IChartErrorBars_get_Shadow, self.Ptr)
        ret = None if intPtr==None else ChartShadow(intPtr)
        return ret


    @property

    def Chart3DOptions(self)->'IFormat3D':
        """
        Gets the chart3 D options.

        """
        GetDllLibXls().IChartErrorBars_get_Chart3DOptions.argtypes=[c_void_p]
        GetDllLibXls().IChartErrorBars_get_Chart3DOptions.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IChartErrorBars_get_Chart3DOptions, self.Ptr)
        ret = None if intPtr==None else Format3D(intPtr)
        return ret


    def ClearFormats(self):
        """
        Clears current error bar.

        """
        GetDllLibXls().IChartErrorBars_ClearFormats.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().IChartErrorBars_ClearFormats, self.Ptr)

    def Delete(self):
        """
        Delete current error bar.

        """
        GetDllLibXls().IChartErrorBars_Delete.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().IChartErrorBars_Delete, self.Ptr)

