from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsChart (  XlsWorksheetBase, ICloneParent, IChart) :
    """
    Represents a chart in a worksheet, providing access to chart properties, axes, series, formatting, and data management.
    """
    def MoveChartsheet(self,destIndex:int):
        """
        Moves the chart sheet to a new position in the workbook.

        Args:
            destIndex (int): The zero-based index to move the chart sheet to.
        """
        GetDllLibXls().XlsChart_MoveChartsheet.argtypes=[c_void_p,c_int]
        CallCFunction(GetDllLibXls().XlsChart_MoveChartsheet, self.Ptr,destIndex)


    @property
    def IsChartPyramid(self)->bool:
        """
        Returns True if the chart is a pyramid shape. Read-only.

        Returns:
            bool: True if the chart is a pyramid shape; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChartPyramid.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChartPyramid.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChartPyramid, self.Ptr)
        return ret

    @property
    def IsChartRadar(self)->bool:
        """
        Returns True if the chart is a radar chart. Read-only.

        Returns:
            bool: True if the chart is a radar chart; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChartRadar.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChartRadar.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChartRadar, self.Ptr)
        return ret

    @property
    def IsChartScatter(self)->bool:
        """
        Returns True if the chart is a scatter chart. Read-only.

        Returns:
            bool: True if the chart is a scatter chart; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChartScatter.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChartScatter.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChartScatter, self.Ptr)
        return ret

    @property
    def IsChartSmoothedLine(self)->bool:
        """
        Returns True if the chart has smoothed lines. Read-only.

        Returns:
            bool: True if the chart has smoothed lines; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChartSmoothedLine.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChartSmoothedLine.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChartSmoothedLine, self.Ptr)
        return ret

    @property
    def IsChartStock(self)->bool:
        """
        Returns True if this is a stock chart. Read-only.

        Returns:
            bool: True if this is a stock chart; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChartStock.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChartStock.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChartStock, self.Ptr)
        return ret

    @property
    def IsChartVeryColor(self)->bool:
        """
        Returns True if the chart should have a different color for each series value. Read-only.

        Returns:
            bool: True if the chart should have a different color for each series value; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChartVeryColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChartVeryColor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChartVeryColor, self.Ptr)
        return ret

    @property
    def IsChartVolume(self)->bool:
        """
        Returns True if the chart is a stock chart with volume. Read-only.

        Returns:
            bool: True if the chart is a stock chart with volume; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChartVolume.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChartVolume.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChartVolume, self.Ptr)
        return ret

    @property
    def IsChartWalls(self)->bool:
        """
        Returns True if the chart has walls. Read-only.

        Returns:
            bool: True if the chart has walls; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChartWalls.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChartWalls.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChartWalls, self.Ptr)
        return ret

    @property
    def IsClustered(self)->bool:
        """
        Returns True if the chart is a clustered chart. Read-only.

        Returns:
            bool: True if the chart is a clustered chart; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsClustered.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsClustered.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsClustered, self.Ptr)
        return ret

    @property
    def IsEmbeded(self)->bool:
        """
        Gets a value indicating whether the chart is embedded into the worksheet.

        Returns:
            bool: True if the chart is embedded; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsEmbeded.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsEmbeded.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsEmbeded, self.Ptr)
        return ret

    @property
    def IsPerspective(self)->bool:
        """
        Returns True if the chart has perspective. Read-only.

        Returns:
            bool: True if the chart has perspective; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsPerspective.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsPerspective.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsPerspective, self.Ptr)
        return ret

    @property
    def IsPivot3DChart(self)->bool:
        """
        Gets a value indicating whether this instance is a pivot 3D chart.

        Returns:
            bool: True if this is a pivot 3D chart; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsPivot3DChart.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsPivot3DChart.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsPivot3DChart, self.Ptr)
        return ret

    @property
    def IsSecondaryAxes(self)->bool:
        """
        Gets or sets a value indicating whether the chart uses secondary axes.

        Returns:
            bool: True if the chart uses secondary axes; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsSecondaryAxes.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsSecondaryAxes.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsSecondaryAxes, self.Ptr)
        return ret

    @IsSecondaryAxes.setter
    def IsSecondaryAxes(self, value:bool):
        GetDllLibXls().XlsChart_set_IsSecondaryAxes.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChart_set_IsSecondaryAxes, self.Ptr, value)

    @property
    def IsSecondaryCategoryAxisAvail(self)->bool:
        """
        Gets a value indicating whether the secondary category axis is available.

        Returns:
            bool: True if the secondary category axis is available; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsSecondaryCategoryAxisAvail.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsSecondaryCategoryAxisAvail.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsSecondaryCategoryAxisAvail, self.Ptr)
        return ret

    @property
    def IsSecondaryValueAxisAvail(self)->bool:
        """
        Gets a value indicating whether the secondary value axis is available.

        Returns:
            bool: True if the secondary value axis is available; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsSecondaryValueAxisAvail.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsSecondaryValueAxisAvail.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsSecondaryValueAxisAvail, self.Ptr)
        return ret

    @property
    def IsSeriesAxisAvail(self)->bool:
        """
        Gets a value indicating whether the series axis is available.

        Returns:
            bool: True if the series axis is available; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsSeriesAxisAvail.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsSeriesAxisAvail.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsSeriesAxisAvail, self.Ptr)
        return ret

    @property
    def IsSeriesLines(self)->bool:
        """
        Returns True if the chart has series lines. Read-only.

        Returns:
            bool: True if the chart has series lines; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsSeriesLines.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsSeriesLines.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsSeriesLines, self.Ptr)
        return ret

    @property
    def IsSpecialDataLabels(self)->bool:
        """
        Returns True if the chart needs special data labels serialization. Read-only.

        Returns:
            bool: True if the chart needs special data labels serialization; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsSpecialDataLabels.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsSpecialDataLabels.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsSpecialDataLabels, self.Ptr)
        return ret

    @property
    def IsStacked(self)->bool:
        """
        Returns True if the chart is stacked. Read-only.

        Returns:
            bool: True if the chart is stacked; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsStacked.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsStacked.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsStacked, self.Ptr)
        return ret

    @property
    def IsValueAxisAvail(self)->bool:
        """
        Indicates whether the chart has a value axis. Read-only.

        Returns:
            bool: True if the chart has a value axis; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsValueAxisAvail.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsValueAxisAvail.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsValueAxisAvail, self.Ptr)
        return ret

    @property
    def NeedDataFormat(self)->bool:
        """
        Returns True if the chart needs data format to be saved. Read-only.

        Returns:
            bool: True if the chart needs data format to be saved; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_NeedDataFormat.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_NeedDataFormat.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_NeedDataFormat, self.Ptr)
        return ret

    @property
    def NeedDropBar(self)->bool:
        """
        Returns True if the chart needs drop bars to be saved. Read-only.

        Returns:
            bool: True if the chart needs drop bars to be saved; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_NeedDropBar.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_NeedDropBar.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_NeedDropBar, self.Ptr)
        return ret

    @property
    def NeedMarkerFormat(self)->bool:
        """
        Returns True if the chart needs marker format to be saved. Read-only.

        Returns:
            bool: True if the chart needs marker format to be saved; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_NeedMarkerFormat.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_NeedMarkerFormat.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_NeedMarkerFormat, self.Ptr)
        return ret

    @property
    def NoPlotArea(self)->bool:
        """
        Returns True if the chart has no plot area. Read-only.

        Returns:
            bool: True if the chart has no plot area; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_NoPlotArea.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_NoPlotArea.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_NoPlotArea, self.Ptr)
        return ret

    @property
    def Style(self)->int:
        """
        Gets or sets the style index for Excel 2007 chart.

        Returns:
            int: The style index.
        """
        GetDllLibXls().XlsChart_get_Style.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_Style.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChart_get_Style, self.Ptr)
        return ret

    @Style.setter
    def Style(self, value:int):
        GetDllLibXls().XlsChart_set_Style.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChart_set_Style, self.Ptr, value)

    @property
    def SupportWallsAndFloor(self)->bool:
        """
        Indicates whether this chart supports walls and floor. Read-only.

        Returns:
            bool: True if the chart supports walls and floor; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_SupportWallsAndFloor.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_SupportWallsAndFloor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_SupportWallsAndFloor, self.Ptr)
        return ret

    @property
    def ZoomToFit(self)->bool:
        """
        Gets or sets the zoomToFit value for the chart.

        Returns:
            bool: True if zoom to fit is enabled; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_ZoomToFit.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_ZoomToFit.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_ZoomToFit, self.Ptr)
        return ret

    @ZoomToFit.setter
    def ZoomToFit(self, value:bool):
        GetDllLibXls().XlsChart_set_ZoomToFit.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChart_set_ZoomToFit, self.Ptr, value)

    @property
    def SecondaryCategoryAxisTitle(self)->str:
        """
        Gets or sets the title of the secondary category axis.

        Returns:
            str: The title of the secondary category axis.
        """
        GetDllLibXls().XlsChart_get_SecondaryCategoryAxisTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_SecondaryCategoryAxisTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChart_get_SecondaryCategoryAxisTitle, self.Ptr))
        return ret


    @SecondaryCategoryAxisTitle.setter
    def SecondaryCategoryAxisTitle(self, value:str):
        GetDllLibXls().XlsChart_set_SecondaryCategoryAxisTitle.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChart_set_SecondaryCategoryAxisTitle, self.Ptr, value)

    @property
    def SecondaryValueAxisTitle(self)->str:
        """
        Gets or sets the title of the secondary value axis.

        Returns:
            str: The title of the secondary value axis.
        """
        GetDllLibXls().XlsChart_get_SecondaryValueAxisTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_SecondaryValueAxisTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChart_get_SecondaryValueAxisTitle, self.Ptr))
        return ret


    @SecondaryValueAxisTitle.setter
    def SecondaryValueAxisTitle(self, value:str):
        GetDllLibXls().XlsChart_set_SecondaryValueAxisTitle.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChart_set_SecondaryValueAxisTitle, self.Ptr, value)

    @property
    def SeriesAxisTitle(self)->str:
        """
        Gets or sets the title of the series axis.

        Returns:
            str: The title of the series axis.
        """
        GetDllLibXls().XlsChart_get_SeriesAxisTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_SeriesAxisTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChart_get_SeriesAxisTitle, self.Ptr))
        return ret


    @SeriesAxisTitle.setter
    def SeriesAxisTitle(self, value:str):
        GetDllLibXls().XlsChart_set_SeriesAxisTitle.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChart_set_SeriesAxisTitle, self.Ptr, value)

    @property
    def ValueAxisTitle(self)->str:
        """
        Gets or sets the title of the value axis.

        Returns:
            str: The title of the value axis.
        """
        GetDllLibXls().XlsChart_get_ValueAxisTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_ValueAxisTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChart_get_ValueAxisTitle, self.Ptr))
        return ret


    @ValueAxisTitle.setter
    def ValueAxisTitle(self, value:str):
        GetDllLibXls().XlsChart_set_ValueAxisTitle.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChart_set_ValueAxisTitle, self.Ptr, value)

    @property
    def HasChartArea(self)->bool:
        """
        Indicates whether the chart has a chart area.

        Returns:
            bool: True if the chart has a chart area; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_HasChartArea.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_HasChartArea.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_HasChartArea, self.Ptr)
        return ret

    @HasChartArea.setter
    def HasChartArea(self, value:bool):
        GetDllLibXls().XlsChart_set_HasChartArea.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChart_set_HasChartArea, self.Ptr, value)

    @property
    def HasChartTitle(self)->bool:
        """
        Indicates whether the chart has a title.

        Returns:
            bool: True if the chart has a title; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_HasChartTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_HasChartTitle.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_HasChartTitle, self.Ptr)
        return ret

    @property
    def HasFloor(self)->bool:
        """
        Gets a value indicating whether the floor object was created.

        Returns:
            bool: True if the floor object was created; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_HasFloor.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_HasFloor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_HasFloor, self.Ptr)
        return ret

    @property
    def HasWalls(self)->bool:
        """
        Gets a value indicating whether the walls object was created.

        Returns:
            bool: True if the walls object was created; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_HasWalls.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_HasWalls.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_HasWalls, self.Ptr)
        return ret

    @property
    def HasPivotTable(self)->bool:
        """
        Indicates whether the chart contains a pivot table.

        Returns:
            bool: True if the chart contains a pivot table; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_HasPivotTable.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_HasPivotTable.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_HasPivotTable, self.Ptr)
        return ret

    @staticmethod
    def CheckDataTablePossibility(startType:str,bThrowException:bool)->bool:
        """
        Checks if a data table can be created for the specified chart type.

        Args:
            startType (str): The start type of the chart.
            bThrowException (bool): Whether to throw an exception if not possible.
        Returns:
            bool: True if a data table can be created; otherwise, False.
        """
        GetDllLibXls().XlsChart_CheckDataTablePossibility.argtypes=[ c_void_p,c_bool]
        GetDllLibXls().XlsChart_CheckDataTablePossibility.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_CheckDataTablePossibility,  startType,bThrowException)
        return ret

    def CheckForSupportGridLine(self)->bool:
        """
        Checks whether the chart supports grid lines.

        Returns:
            bool: True if the chart supports grid lines; otherwise, False.
        """
        GetDllLibXls().XlsChart_CheckForSupportGridLine.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_CheckForSupportGridLine.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_CheckForSupportGridLine, self.Ptr)
        return ret

    @dispatch
    def Clone(self ,parent:SpireObject)->SpireObject:
        """
        Clones the current chart instance.

        Args:
            parent (SpireObject): The parent object for the cloned chart.
        Returns:
            SpireObject: The cloned chart object.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsChart_CloneP.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsChart_CloneP.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChart_CloneP, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret

    def SetToDefaultGridlines(self ,type:'ExcelChartType'):
        """
        Sets the chart to use default gridlines for the specified chart type.

        Args:
            type (ExcelChartType): The chart type to set default gridlines for.
        """
        enumtype:c_int = type.value

        GetDllLibXls().XlsChart_SetToDefaultGridlines.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsChart_SetToDefaultGridlines, self.Ptr, enumtype)

    @property
    def ChartType(self)->'ExcelChartType':
        """
        Gets or sets the type of the chart.

        Returns:
            ExcelChartType: The chart type.
        """
        GetDllLibXls().XlsChart_get_ChartType.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_ChartType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChart_get_ChartType, self.Ptr)
        objwraped = ExcelChartType(ret)
        return objwraped

    @ChartType.setter
    def ChartType(self, value:'ExcelChartType'):
        GetDllLibXls().XlsChart_set_ChartType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChart_set_ChartType, self.Ptr, value.value)

    @property
    def DataRange(self)->'IXLSRange':
        """
        Gets or sets the data range for the chart.

        Returns:
            IXLSRange: The data range used by the chart.
        """
        GetDllLibXls().XlsChart_get_DataRange.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_DataRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChart_get_DataRange, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @DataRange.setter
    def DataRange(self, value:'IXLSRange'):
        GetDllLibXls().XlsChart_set_DataRange.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChart_set_DataRange, self.Ptr, value.Ptr)

    @property
    def SeriesDataFromRange(self)->bool:
        """
        Gets or sets a value indicating whether series are in rows in DataRange; otherwise, in columns.

        Returns:
            bool: True if series are in rows; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_SeriesDataFromRange.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_SeriesDataFromRange.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_SeriesDataFromRange, self.Ptr)
        return ret

    @SeriesDataFromRange.setter
    def SeriesDataFromRange(self, value:bool):
        GetDllLibXls().XlsChart_set_SeriesDataFromRange.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChart_set_SeriesDataFromRange, self.Ptr, value)

    @property
    def PageSetup(self)->'IChartPageSetup':
        """
        Gets the page setup options for the chart.

        Returns:
            IChartPageSetup: The page setup object.
        """
        GetDllLibXls().XlsChart_get_PageSetup.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_PageSetup.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChart_get_PageSetup, self.Ptr)
        ret = None if intPtr==None else IChartPageSetup(intPtr)
        return ret


    @property
    def XPos(self)->float:
        """
        Gets or sets the X position of the chart.

        Returns:
            float: The X position.
        """
        GetDllLibXls().XlsChart_get_XPos.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_XPos.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChart_get_XPos, self.Ptr)
        return ret

    @XPos.setter
    def XPos(self, value:float):
        GetDllLibXls().XlsChart_set_XPos.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChart_set_XPos, self.Ptr, value)

    @property
    def YPos(self)->float:
        """
        Gets or sets the Y position of the chart.

        Returns:
            float: The Y position.
        """
        GetDllLibXls().XlsChart_get_YPos.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_YPos.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChart_get_YPos, self.Ptr)
        return ret

    @YPos.setter
    def YPos(self, value:float):
        GetDllLibXls().XlsChart_set_YPos.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChart_set_YPos, self.Ptr, value)

    @property
    def Width(self)->float:
        """
        Gets or sets the width of the chart.

        Returns:
            float: The width of the chart.
        """
        GetDllLibXls().XlsChart_get_Width.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_Width.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChart_get_Width, self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibXls().XlsChart_set_Width.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChart_set_Width, self.Ptr, value)

    @property
    def Height(self)->float:
        """
        Gets or sets the height of the chart.

        Returns:
            float: The height of the chart.
        """
        GetDllLibXls().XlsChart_get_Height.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_Height.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChart_get_Height, self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibXls().XlsChart_set_Height.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChart_set_Height, self.Ptr, value)

    @property
    def PrimaryCategoryAxis(self)->'IChartCategoryAxis':
        """
        Gets the primary category axis of the chart.

        Returns:
            IChartCategoryAxis: The primary category axis object.
        """
        GetDllLibXls().XlsChart_get_PrimaryCategoryAxis.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_PrimaryCategoryAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChart_get_PrimaryCategoryAxis, self.Ptr)
        ret = None if intPtr==None else IChartCategoryAxis(intPtr)
        return ret


    @property
    def PrimaryValueAxis(self)->'IChartValueAxis':
        """
        Gets the primary value axis of the chart.

        Returns:
            IChartValueAxis: The primary value axis object.
        """
        GetDllLibXls().XlsChart_get_PrimaryValueAxis.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_PrimaryValueAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChart_get_PrimaryValueAxis, self.Ptr)
        ret = None if intPtr==None else IChartValueAxis(intPtr)
        return ret


    @property
    def PrimarySerieAxis(self)->'IChartSeriesAxis':
        """
        Gets the primary series axis of the chart.

        Returns:
            IChartSeriesAxis: The primary series axis object.
        """
        GetDllLibXls().XlsChart_get_PrimarySerieAxis.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_PrimarySerieAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChart_get_PrimarySerieAxis, self.Ptr)
        ret = None if intPtr==None else IChartSeriesAxis(intPtr)
        return ret


    @property
    def SecondaryCategoryAxis(self)->'IChartCategoryAxis':
        """
        Gets the secondary category axis of the chart.

        Returns:
            IChartCategoryAxis: The secondary category axis object.
        """
        GetDllLibXls().XlsChart_get_SecondaryCategoryAxis.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_SecondaryCategoryAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChart_get_SecondaryCategoryAxis, self.Ptr)
        ret = None if intPtr==None else IChartCategoryAxis(intPtr)
        return ret


    @property
    def SecondaryValueAxis(self)->'IChartValueAxis':
        """
        Gets the secondary value axis of the chart.

        Returns:
            IChartValueAxis: The secondary value axis object.
        """
        GetDllLibXls().XlsChart_get_SecondaryValueAxis.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_SecondaryValueAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChart_get_SecondaryValueAxis, self.Ptr)
        ret = None if intPtr==None else IChartValueAxis(intPtr)
        return ret


    @property
    def ChartArea(self)->'IChartFrameFormat':
        """
        Gets the chart area formatting object.

        Returns:
            IChartFrameFormat: The chart area formatting object.
        """
        GetDllLibXls().XlsChart_get_ChartArea.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_ChartArea.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChart_get_ChartArea, self.Ptr)
        ret = None if intPtr==None else XlsChartFrameFormat(intPtr)
        return ret


    @property
    def PlotArea(self)->'IChartFrameFormat':
        """
        Gets the plot area formatting object.

        Returns:
            IChartFrameFormat: The plot area formatting object.
        """
        GetDllLibXls().XlsChart_get_PlotArea.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_PlotArea.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChart_get_PlotArea, self.Ptr)
        ret = None if intPtr==None else XlsChartFrameFormat(intPtr)
        return ret


    @property
    def Walls(self)->'IChartWallOrFloor':
        """
        Gets the walls formatting object of the chart.

        Returns:
            IChartWallOrFloor: The walls formatting object.
        """
        GetDllLibXls().XlsChart_get_Walls.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_Walls.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChart_get_Walls, self.Ptr)
        ret = None if intPtr==None else IChartWallOrFloor(intPtr)
        return ret


    @property
    def Floor(self)->'IChartWallOrFloor':
        """
        Gets the floor formatting object of the chart.

        Returns:
            IChartWallOrFloor: The floor formatting object.
        """
        GetDllLibXls().XlsChart_get_Floor.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_Floor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChart_get_Floor, self.Ptr)
        ret = None if intPtr==None else IChartWallOrFloor(intPtr)
        return ret


    @property
    def DataTable(self)->'IChartDataTable':
        """
        Gets the data table object of the chart.

        Returns:
            IChartDataTable: The data table object.
        """
        GetDllLibXls().XlsChart_get_DataTable.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_DataTable.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChart_get_DataTable, self.Ptr)
        ret = None if intPtr==None else IChartDataTable(intPtr)
        return ret


    @property
    def HasDataTable(self)->bool:
        """
        Gets or sets a value indicating whether the chart has a data table.

        Returns:
            bool: True if the chart has a data table; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_HasDataTable.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_HasDataTable.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_HasDataTable, self.Ptr)
        return ret

    @HasDataTable.setter
    def HasDataTable(self, value:bool):
        GetDllLibXls().XlsChart_set_HasDataTable.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChart_set_HasDataTable, self.Ptr, value)

    @property
    def Legend(self)->'IChartLegend':
        """
        Gets the legend object of the chart.

        Returns:
            IChartLegend: The legend object.
        """
        GetDllLibXls().XlsChart_get_Legend.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_Legend.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChart_get_Legend, self.Ptr)
        ret = None if intPtr==None else IChartLegend(intPtr)
        return ret


    @property
    def HasLegend(self)->bool:
        """
        Gets or sets a value indicating whether the chart has a legend.

        Returns:
            bool: True if the chart has a legend; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_HasLegend.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_HasLegend.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_HasLegend, self.Ptr)
        return ret

    @HasLegend.setter
    def HasLegend(self, value:bool):
        GetDllLibXls().XlsChart_set_HasLegend.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChart_set_HasLegend, self.Ptr, value)

    @property
    def Rotation(self)->int:
        """
        Gets or sets the rotation angle of the 3D chart.

        Returns:
            int: The rotation angle in degrees.
        """
        GetDllLibXls().XlsChart_get_Rotation.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_Rotation.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChart_get_Rotation, self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:int):
        GetDllLibXls().XlsChart_set_Rotation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChart_set_Rotation, self.Ptr, value)

    @property
    def Elevation(self)->int:
        """
        Gets or sets the elevation of the 3D chart.

        Returns:
            int: The elevation value.
        """
        GetDllLibXls().XlsChart_get_Elevation.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_Elevation.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChart_get_Elevation, self.Ptr)
        return ret

    @Elevation.setter
    def Elevation(self, value:int):
        GetDllLibXls().XlsChart_set_Elevation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChart_set_Elevation, self.Ptr, value)

    @property
    def Perspective(self)->int:
        """
        Gets or sets the perspective angle of the 3D chart.

        Returns:
            int: The perspective angle in degrees.
        """
        GetDllLibXls().XlsChart_get_Perspective.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_Perspective.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChart_get_Perspective, self.Ptr)
        return ret

    @Perspective.setter
    def Perspective(self, value:int):
        GetDllLibXls().XlsChart_set_Perspective.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChart_set_Perspective, self.Ptr, value)

    @property
    def HeightPercent(self)->int:
        """
        Gets or sets the height percentage of the chart.

        Returns:
            int: The height percentage.
        """
        GetDllLibXls().XlsChart_get_HeightPercent.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_HeightPercent.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChart_get_HeightPercent, self.Ptr)
        return ret

    @HeightPercent.setter
    def HeightPercent(self, value:int):
        GetDllLibXls().XlsChart_set_HeightPercent.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChart_set_HeightPercent, self.Ptr, value)

    @property
    def DepthPercent(self)->int:
        """
        Gets or sets the depth percentage of the chart.

        Returns:
            int: The depth percentage.
        """
        GetDllLibXls().XlsChart_get_DepthPercent.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_DepthPercent.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChart_get_DepthPercent, self.Ptr)
        return ret

    @DepthPercent.setter
    def DepthPercent(self, value:int):
        GetDllLibXls().XlsChart_set_DepthPercent.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChart_set_DepthPercent, self.Ptr, value)

    @property
    def DestinationType(self)->'ExcelChartType':
        """
        Gets chart type after type change.

        Returns:
            ExcelChartType: The chart type after type change.
        """
        GetDllLibXls().XlsChart_get_DestinationType.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_DestinationType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChart_get_DestinationType, self.Ptr)
        objwraped = ExcelChartType(ret)
        return objwraped

    @DestinationType.setter
    def DestinationType(self, value:'ExcelChartType'):
        GetDllLibXls().XlsChart_set_DestinationType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChart_set_DestinationType, self.Ptr, value.value)

    @property
    def GapDepth(self)->int:
        """
        Gets or sets the gap depth of the chart.

        Returns:
            int: The gap depth.
        """
        GetDllLibXls().XlsChart_get_GapDepth.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_GapDepth.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChart_get_GapDepth, self.Ptr)
        return ret

    @GapDepth.setter
    def GapDepth(self, value:int):
        GetDllLibXls().XlsChart_set_GapDepth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChart_set_GapDepth, self.Ptr, value)

    @property
    def RightAngleAxes(self)->bool:
        """
        Gets or sets a value indicating whether the chart uses right angle axes.

        Returns:
            bool: True if the chart uses right angle axes; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_RightAngleAxes.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_RightAngleAxes.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_RightAngleAxes, self.Ptr)
        return ret

    @RightAngleAxes.setter
    def RightAngleAxes(self, value:bool):
        GetDllLibXls().XlsChart_set_RightAngleAxes.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChart_set_RightAngleAxes, self.Ptr, value)

    @property
    def AutoScaling(self)->bool:
        """
        Gets or sets a value indicating whether the chart uses auto scaling.

        Returns:
            bool: True if the chart uses auto scaling; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_AutoScaling.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_AutoScaling.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_AutoScaling, self.Ptr)
        return ret

    @AutoScaling.setter
    def AutoScaling(self, value:bool):
        GetDllLibXls().XlsChart_set_AutoScaling.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChart_set_AutoScaling, self.Ptr, value)

    @property
    def WallsAndGridlines2D(self)->bool:
        """
        Gets or sets a value indicating whether the chart uses walls and gridlines in 2D mode.

        Returns:
            bool: True if the chart uses walls and gridlines in 2D mode; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_WallsAndGridlines2D.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_WallsAndGridlines2D.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_WallsAndGridlines2D, self.Ptr)
        return ret

    @WallsAndGridlines2D.setter
    def WallsAndGridlines2D(self, value:bool):
        GetDllLibXls().XlsChart_set_WallsAndGridlines2D.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChart_set_WallsAndGridlines2D, self.Ptr, value)

    @property
    def HasPlotArea(self)->bool:
        """
        Gets or sets a value indicating whether the chart has a plot area.

        Returns:
            bool: True if the chart has a plot area; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_HasPlotArea.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_HasPlotArea.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_HasPlotArea, self.Ptr)
        return ret

    @HasPlotArea.setter
    def HasPlotArea(self, value:bool):
        GetDllLibXls().XlsChart_set_HasPlotArea.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChart_set_HasPlotArea, self.Ptr, value)

    @property
    def DisplayBlanksAs(self)->'ChartPlotEmptyType':
        """
        Gets or sets the display blanks as type for the chart.

        Returns:
            ChartPlotEmptyType: The display blanks as type.
        """
        GetDllLibXls().XlsChart_get_DisplayBlanksAs.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_DisplayBlanksAs.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChart_get_DisplayBlanksAs, self.Ptr)
        objwraped = ChartPlotEmptyType(ret)
        return objwraped

    @DisplayBlanksAs.setter
    def DisplayBlanksAs(self, value:'ChartPlotEmptyType'):
        GetDllLibXls().XlsChart_set_DisplayBlanksAs.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChart_set_DisplayBlanksAs, self.Ptr, value.value)

    @property
    def PlotVisibleOnly(self)->bool:
        """
        Gets or sets a value indicating whether the chart plots only visible cells.

        Returns:
            bool: True if the chart plots only visible cells; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_PlotVisibleOnly.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_PlotVisibleOnly.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_PlotVisibleOnly, self.Ptr)
        return ret

    @PlotVisibleOnly.setter
    def PlotVisibleOnly(self, value:bool):
        GetDllLibXls().XlsChart_set_PlotVisibleOnly.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChart_set_PlotVisibleOnly, self.Ptr, value)

    @property
    def SizeWithWindow(self)->bool:
        """
        Gets or sets a value indicating whether the chart size is based on the window size.

        Returns:
            bool: True if the chart size is based on the window size; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_SizeWithWindow.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_SizeWithWindow.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_SizeWithWindow, self.Ptr)
        return ret

    @SizeWithWindow.setter
    def SizeWithWindow(self, value:bool):
        GetDllLibXls().XlsChart_set_SizeWithWindow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChart_set_SizeWithWindow, self.Ptr, value)

    @property
    def PivotTable(self)->'PivotTable':
        """
        Gets or sets the pivot table for the chart.

        Returns:
            PivotTable: The pivot table object.
        """
        GetDllLibXls().XlsChart_get_PivotTable.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_PivotTable.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChart_get_PivotTable, self.Ptr)
        ret = None if intPtr==None else PivotTable(intPtr)
        return ret


    @PivotTable.setter
    def PivotTable(self, value:'PivotTable'):
        GetDllLibXls().XlsChart_set_PivotTable.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChart_set_PivotTable, self.Ptr, value.Ptr)

    @property
    def PivotChartType(self)->'ExcelChartType':
        """
        Gets or sets the pivot chart type for the chart.

        Returns:
            ExcelChartType: The pivot chart type.
        """
        GetDllLibXls().XlsChart_get_PivotChartType.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_PivotChartType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChart_get_PivotChartType, self.Ptr)
        objwraped = ExcelChartType(ret)
        return objwraped

    @PivotChartType.setter
    def PivotChartType(self, value:'ExcelChartType'):
        GetDllLibXls().XlsChart_set_PivotChartType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChart_set_PivotChartType, self.Ptr, value.value)

    @property
    def DisplayEntireFieldButtons(self)->bool:
        """
        Gets or sets a value indicating whether to display entire field buttons.

        Returns:
            bool: True if to display entire field buttons; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_DisplayEntireFieldButtons.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_DisplayEntireFieldButtons.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_DisplayEntireFieldButtons, self.Ptr)
        return ret

    @DisplayEntireFieldButtons.setter
    def DisplayEntireFieldButtons(self, value:bool):
        GetDllLibXls().XlsChart_set_DisplayEntireFieldButtons.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChart_set_DisplayEntireFieldButtons, self.Ptr, value)

    @property
    def DisplayValueFieldButtons(self)->bool:
        """
        Gets or sets a value indicating whether to display value field buttons.

        Returns:
            bool: True if to display value field buttons; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_DisplayValueFieldButtons.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_DisplayValueFieldButtons.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_DisplayValueFieldButtons, self.Ptr)
        return ret

    @DisplayValueFieldButtons.setter
    def DisplayValueFieldButtons(self, value:bool):
        GetDllLibXls().XlsChart_set_DisplayValueFieldButtons.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChart_set_DisplayValueFieldButtons, self.Ptr, value)

    @property
    def DisplayAxisFieldButtons(self)->bool:
        """
        Gets or sets a value indicating whether to display axis field buttons.

        Returns:
            bool: True if to display axis field buttons; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_DisplayAxisFieldButtons.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_DisplayAxisFieldButtons.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_DisplayAxisFieldButtons, self.Ptr)
        return ret

    @DisplayAxisFieldButtons.setter
    def DisplayAxisFieldButtons(self, value:bool):
        GetDllLibXls().XlsChart_set_DisplayAxisFieldButtons.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChart_set_DisplayAxisFieldButtons, self.Ptr, value)

    @property
    def DisplayLegendFieldButtons(self)->bool:
        """
        Gets or sets a value indicating whether to display legend field buttons.

        Returns:
            bool: True if to display legend field buttons; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_DisplayLegendFieldButtons.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_DisplayLegendFieldButtons.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_DisplayLegendFieldButtons, self.Ptr)
        return ret

    @DisplayLegendFieldButtons.setter
    def DisplayLegendFieldButtons(self, value:bool):
        GetDllLibXls().XlsChart_set_DisplayLegendFieldButtons.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChart_set_DisplayLegendFieldButtons, self.Ptr, value)

    @property
    def ShowReportFilterFieldButtons(self)->bool:
        """
        Gets or sets a value indicating whether to show report filter field buttons.

        Returns:
            bool: True if to show report filter field buttons; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_ShowReportFilterFieldButtons.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_ShowReportFilterFieldButtons.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_ShowReportFilterFieldButtons, self.Ptr)
        return ret

    @ShowReportFilterFieldButtons.setter
    def ShowReportFilterFieldButtons(self, value:bool):
        GetDllLibXls().XlsChart_set_ShowReportFilterFieldButtons.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChart_set_ShowReportFilterFieldButtons, self.Ptr, value)

    @property
    def CanChartBubbleLabel(self)->bool:
        """
        Gets a value indicating whether the chart can have bubble data labels.

        Returns:
            bool: True if the chart can have bubble data labels; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_CanChartBubbleLabel.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_CanChartBubbleLabel.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_CanChartBubbleLabel, self.Ptr)
        return ret

    @property
    def CanChartHaveSeriesLines(self)->bool:
        """
        Gets a value indicating whether the chart can have series lines.

        Returns:
            bool: True if the chart can have series lines; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_CanChartHaveSeriesLines.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_CanChartHaveSeriesLines.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_CanChartHaveSeriesLines, self.Ptr)
        return ret

    @property
    def CanChartPercentageLabel(self)->bool:
        """
        Gets a value indicating whether the chart can have percentage data labels.

        Returns:
            bool: True if the chart can have percentage data labels; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_CanChartPercentageLabel.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_CanChartPercentageLabel.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_CanChartPercentageLabel, self.Ptr)
        return ret

    @property
    def CategoryAxisTitle(self)->str:
        """
        Gets or sets the title of the category axis.

        Returns:
            str: The title of the category axis.
        """
        GetDllLibXls().XlsChart_get_CategoryAxisTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_CategoryAxisTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChart_get_CategoryAxisTitle, self.Ptr))
        return ret


    @CategoryAxisTitle.setter
    def CategoryAxisTitle(self, value:str):
        GetDllLibXls().XlsChart_set_CategoryAxisTitle.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChart_set_CategoryAxisTitle, self.Ptr, value)

    @property
    def ChartStartType(self)->str:
        """
        Gets the start type of the chart.

        Returns:
            str: The start type of the chart.
        """
        GetDllLibXls().XlsChart_get_ChartStartType.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_ChartStartType.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChart_get_ChartStartType, self.Ptr))
        return ret


    @property
    def ChartTitle(self)->str:
        """
        Gets or sets the title of the chart.

        Returns:
            str: The title of the chart.
        """
        GetDllLibXls().XlsChart_get_ChartTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_ChartTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChart_get_ChartTitle, self.Ptr))
        return ret


    @ChartTitle.setter
    def ChartTitle(self, value:str):
        GetDllLibXls().XlsChart_set_ChartTitle.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChart_set_ChartTitle, self.Ptr, value)

    @property
    def ChartTitleFont(self)->'IFont':
        """
        Gets the font for the chart title.

        Returns:
            IFont: The font for the chart title.
        """
        GetDllLibXls().XlsChart_get_ChartTitleFont.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_ChartTitleFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChart_get_ChartTitleFont, self.Ptr)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret


    @property
    def DefaultLinePattern(self)->'ChartLinePatternType':
        """
        Gets the default line pattern for the chart.

        Returns:
            ChartLinePatternType: The default line pattern for the chart.
        """
        GetDllLibXls().XlsChart_get_DefaultLinePattern.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_DefaultLinePattern.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChart_get_DefaultLinePattern, self.Ptr)
        objwraped = ChartLinePatternType(ret)
        return objwraped

    @property
    def DefaultTextIndex(self)->int:
        """
        Gets the default text index for the chart.

        Returns:
            int: The default text index for the chart.
        """
        GetDllLibXls().XlsChart_get_DefaultTextIndex.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_DefaultTextIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChart_get_DefaultTextIndex, self.Ptr)
        return ret

    @property
    def Font(self)->'FontWrapper':
        """
        Gets the font for the chart.

        Returns:
            FontWrapper: The font for the chart.
        """
        GetDllLibXls().XlsChart_get_Font.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_Font.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChart_get_Font, self.Ptr)
        ret = None if intPtr==None else FontWrapper(intPtr)
        return ret


    @property
    def IsCategoryAxisAvail(self)->bool:
        """
        Gets a value indicating whether the chart has a category axis.

        Returns:
            bool: True if the chart has a category axis; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsCategoryAxisAvail.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsCategoryAxisAvail.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsCategoryAxisAvail, self.Ptr)
        return ret

    @property
    def IsChart_100(self)->bool:
        """
        Gets a value indicating whether the chart is 100%.

        Returns:
            bool: True if the chart is 100%; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChart_100.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChart_100.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChart_100, self.Ptr)
        return ret

    @property
    def IsChart3D(self)->bool:
        """
        Gets a value indicating whether the chart is 3D.

        Returns:
            bool: True if the chart is 3D; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChart3D.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChart3D.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChart3D, self.Ptr)
        return ret

    @property
    def IsChartBar(self)->bool:
        """
        Gets a value indicating whether the chart is a bar chart.

        Returns:
            bool: True if the chart is a bar chart; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChartBar.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChartBar.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChartBar, self.Ptr)
        return ret

    @property
    def IsChartBubble(self)->bool:
        """
        Gets a value indicating whether the chart is a bubble chart.

        Returns:
            bool: True if the chart is a bubble chart; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChartBubble.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChartBubble.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChartBubble, self.Ptr)
        return ret

    @property
    def IsChartCone(self)->bool:
        """
        Gets a value indicating whether the chart is a conical shape.

        Returns:
            bool: True if the chart is a conical shape; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChartCone.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChartCone.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChartCone, self.Ptr)
        return ret

    @property
    def IsChartCylinder(self)->bool:
        """
        Gets a value indicating whether the chart is a cylinder shape.

        Returns:
            bool: True if the chart is a cylinder shape; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChartCylinder.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChartCylinder.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChartCylinder, self.Ptr)
        return ret

    @property
    def IsChartDoughnut(self)->bool:
        """
        Gets a value indicating whether the chart is a doughnut chart.

        Returns:
            bool: True if the chart is a doughnut chart; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChartDoughnut.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChartDoughnut.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChartDoughnut, self.Ptr)
        return ret

    @property
    def IsChartExploded(self)->bool:
        """
        Gets a value indicating whether the chart is exploded.

        Returns:
            bool: True if the chart is exploded; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChartExploded.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChartExploded.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChartExploded, self.Ptr)
        return ret

    @property
    def IsChartFloor(self)->bool:
        """
        Gets a value indicating whether the chart has a floor.

        Returns:
            bool: True if the chart has a floor; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChartFloor.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChartFloor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChartFloor, self.Ptr)
        return ret

    @property
    def IsChartLine(self)->bool:
        """
        Gets a value indicating whether the chart is a line chart.

        Returns:
            bool: True if the chart is a line chart; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChartLine.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChartLine.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChartLine, self.Ptr)
        return ret

    @property
    def IsChartPie(self)->bool:
        """
        Gets a value indicating whether the chart is a pie chart.

        Returns:
            bool: True if the chart is a pie chart; otherwise, False.
        """
        GetDllLibXls().XlsChart_get_IsChartPie.argtypes=[c_void_p]
        GetDllLibXls().XlsChart_get_IsChartPie.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChart_get_IsChartPie, self.Ptr)
        return ret

    @staticmethod
    def DEF_SUPPORT_SERIES_AXIS()->List['ExcelChartType']:
        """
        Gets the default support series axis for the chart.

        Returns:
            List[ExcelChartType]: The default support series axis for the chart.
        """
        #GetDllLibXls().XlsChart_DEF_SUPPORT_SERIES_AXIS.argtypes=[]
        GetDllLibXls().XlsChart_DEF_SUPPORT_SERIES_AXIS.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().XlsChart_DEF_SUPPORT_SERIES_AXIS)
        ret = GetVectorFromArray(intPtrArray, ExcelChartType)
        return ret


    @staticmethod
    def DEF_SUPPORT_ERROR_BARS()->List[str]:
        """
        Gets the default support error bars for the chart.

        Returns:
            List[str]: The default support error bars for the chart.
        """
        GetDllLibXls().XlsChart_DEF_SUPPORT_ERROR_BARS.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().XlsChart_DEF_SUPPORT_ERROR_BARS)
        ret = GetVectorFromArray(intPtrArray, c_wchar_p)
        return ret

    @staticmethod
    def DEF_SUPPORT_TREND_LINES()->List['ExcelChartType']:
        """
        Gets the default support trend lines for the chart.

        Returns:
            List[ExcelChartType]: The default support trend lines for the chart.
        """
        GetDllLibXls().XlsChart_DEF_SUPPORT_TREND_LINES.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().XlsChart_DEF_SUPPORT_TREND_LINES)
        ret = GetVectorFromArray(intPtrArray, ExcelChartType)
        return ret


