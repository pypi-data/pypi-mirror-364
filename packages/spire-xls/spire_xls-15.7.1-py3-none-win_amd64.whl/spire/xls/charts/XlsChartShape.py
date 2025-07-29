from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsChartShape (  XlsShape, IChartShape) :
    """
    Represents a chart shape in Excel worksheet.
    Provides access to chart properties and methods.
    """
    @property
    def CategoryAxisTitle(self)->str:
        """
        Gets or sets the title of the category axis.

        Returns:
            str: The title of the category axis.
        """
        GetDllLibXls().XlsChartShape_get_CategoryAxisTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_CategoryAxisTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartShape_get_CategoryAxisTitle, self.Ptr))
        return ret


    @CategoryAxisTitle.setter
    def CategoryAxisTitle(self, value:str):
        GetDllLibXls().XlsChartShape_set_CategoryAxisTitle.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChartShape_set_CategoryAxisTitle, self.Ptr, value)

    @property

    def ValueAxisTitle(self)->str:
        """
        Title of the value axis.

        """
        GetDllLibXls().XlsChartShape_get_ValueAxisTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_ValueAxisTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartShape_get_ValueAxisTitle, self.Ptr))
        return ret


    @ValueAxisTitle.setter
    def ValueAxisTitle(self, value:str):
        GetDllLibXls().XlsChartShape_set_ValueAxisTitle.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChartShape_set_ValueAxisTitle, self.Ptr, value)

    @property

    def SecondaryCategoryAxisTitle(self)->str:
        """
        Gets or sets the title of the secondary category axis.

        Returns:
            str: The title of the secondary category axis.
        """
        GetDllLibXls().XlsChartShape_get_SecondaryCategoryAxisTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_SecondaryCategoryAxisTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartShape_get_SecondaryCategoryAxisTitle, self.Ptr))
        return ret


    @SecondaryCategoryAxisTitle.setter
    def SecondaryCategoryAxisTitle(self, value:str):
        GetDllLibXls().XlsChartShape_set_SecondaryCategoryAxisTitle.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChartShape_set_SecondaryCategoryAxisTitle, self.Ptr, value)

    @property

    def SecondaryValueAxisTitle(self)->str:
        """
        Title of the secondary value axis.

        """
        GetDllLibXls().XlsChartShape_get_SecondaryValueAxisTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_SecondaryValueAxisTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartShape_get_SecondaryValueAxisTitle, self.Ptr))
        return ret


    @SecondaryValueAxisTitle.setter
    def SecondaryValueAxisTitle(self, value:str):
        GetDllLibXls().XlsChartShape_set_SecondaryValueAxisTitle.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChartShape_set_SecondaryValueAxisTitle, self.Ptr, value)

    @property

    def SeriesAxisTitle(self)->str:
        """
        Title of the series axis.

        """
        GetDllLibXls().XlsChartShape_get_SeriesAxisTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_SeriesAxisTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartShape_get_SeriesAxisTitle, self.Ptr))
        return ret


    @SeriesAxisTitle.setter
    def SeriesAxisTitle(self, value:str):
        GetDllLibXls().XlsChartShape_set_SeriesAxisTitle.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChartShape_set_SeriesAxisTitle, self.Ptr, value)

    @property

    def Shapes(self)->'IShapes':
        """
        Gets the collection of shapes in the chart.

        Returns:
            IShapes: The collection of shapes.
        """
        GetDllLibXls().XlsChartShape_get_Shapes.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_Shapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_Shapes, self.Ptr)
        ret = None if intPtr==None else IShapes(intPtr)
        return ret


    @property

    def TextBoxes(self)->'ITextBoxes':
        """
        Gets the collection of text boxes in the chart.

        Returns:
            ITextBoxes: The collection of text boxes.
        """
        GetDllLibXls().XlsChartShape_get_TextBoxes.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_TextBoxes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_TextBoxes, self.Ptr)
        ret = None if intPtr==None else TextBoxCollection(intPtr)
        return ret


    @property

    def CheckBoxes(self)->'ICheckBoxes':
        """
        Gets the collection of check boxes in the chart.

        Returns:
            ICheckBoxes: The collection of check boxes.
        """
        GetDllLibXls().XlsChartShape_get_CheckBoxes.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_CheckBoxes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_CheckBoxes, self.Ptr)
        ret = None if intPtr==None else CheckBoxCollection(intPtr)
        return ret


    @property

    def ComboBoxes(self)->'IComboBoxes':
        """
        Gets the collection of combo boxes in the chart.

        Returns:
            IComboBoxes: The collection of combo boxes.
        """
        GetDllLibXls().XlsChartShape_get_ComboBoxes.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_ComboBoxes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_ComboBoxes, self.Ptr)
        ret = None if intPtr==None else ComboBoxCollection(intPtr)
        return ret


    @property

    def CodeName(self)->str:
        """
        Gets or sets the code name of the chart.

        Returns:
            str: The code name of the chart.
        """
        GetDllLibXls().XlsChartShape_get_CodeName.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_CodeName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartShape_get_CodeName, self.Ptr))
        return ret


    @property
    def IsRightToLeft(self)->bool:
        """
        Indicates whether chart is displayed right to left.

        """
        GetDllLibXls().XlsChartShape_get_IsRightToLeft.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_IsRightToLeft.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_IsRightToLeft, self.Ptr)
        return ret

    @IsRightToLeft.setter
    def IsRightToLeft(self, value:bool):
        GetDllLibXls().XlsChartShape_set_IsRightToLeft.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartShape_set_IsRightToLeft, self.Ptr, value)

    @property

    def PrimaryFormats(self)->'XlsChartFormatCollection':
        """
        Returns chart format collection in primary axis.

        """
        GetDllLibXls().XlsChartShape_get_PrimaryFormats.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_PrimaryFormats.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_PrimaryFormats, self.Ptr)
        ret = None if intPtr==None else XlsChartFormatCollection(intPtr)
        return ret


    @property

    def SecondaryFormats(self)->'XlsChartFormatCollection':
        """
        Returns chart format collection in secondary axis.

        """
        GetDllLibXls().XlsChartShape_get_SecondaryFormats.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_SecondaryFormats.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_SecondaryFormats, self.Ptr)
        ret = None if intPtr==None else XlsChartFormatCollection(intPtr)
        return ret



    def AddShapeInChart(self ,type:'ExcelShapeType',placement:'ResizeBehaveType',left:int,top:int,height:int,width:int)->'IShape':
        """
        Adds a shape to the chart.

        Args:
            type (ExcelShapeType): The type of the shape.
            placement (ResizeBehaveType): The placement behavior of the shape.
            left (int): The left position of the shape.
            top (int): The top position of the shape.
            height (int): The height of the shape.
            width (int): The width of the shape.

        Returns:
            IShape: The added shape.
        """
        enumtype:c_int = type.value
        enumplacement:c_int = placement.value

        GetDllLibXls().XlsChartShape_AddShapeInChart.argtypes=[c_void_p ,c_int,c_int,c_int,c_int,c_int,c_int]
        GetDllLibXls().XlsChartShape_AddShapeInChart.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_AddShapeInChart, self.Ptr, enumtype,enumplacement,left,top,height,width)
        ret = None if intPtr==None else IShape(intPtr)
        return ret


    def RefreshChart(self):
        """
        Refreshes the chart to reflect any changes made to its data or properties.
        """
        GetDllLibXls().XlsChartShape_RefreshChart.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsChartShape_RefreshChart, self.Ptr)

#
#    def Clone(self ,parent:'SpireObject',hashNewNames:'Dictionary2',dicFontIndexes:'Dictionary2',addToCollections:bool)->'IShape':
#        """
#    <summary>
#        Creates a clone of the current shape.
#    </summary>
#    <param name="parent">New parent for the shape object.</param>
#    <param name="hashNewNames">Hashtable with new worksheet names.</param>
#    <param name="dicFontIndexes">Dictionary with new font indexes.</param>
#    <returns>A copy of the current shape.</returns>
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrhashNewNames:c_void_p = hashNewNames.Ptr
#        intPtrdicFontIndexes:c_void_p = dicFontIndexes.Ptr
#
#        GetDllLibXls().XlsChartShape_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsChartShape_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_Clone, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollections)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


    @property

    def ChartType(self)->'ExcelChartType':
        """
        Gets or sets the type of the chart.

        Returns:
            ExcelChartType: The type of the chart.
        """
        GetDllLibXls().XlsChartShape_get_ChartType.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_ChartType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_ChartType, self.Ptr)
        objwraped = ExcelChartType(ret)
        return objwraped

    @ChartType.setter
    def ChartType(self, value:'ExcelChartType'):
        GetDllLibXls().XlsChartShape_set_ChartType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartShape_set_ChartType, self.Ptr, value.value)

    @property

    def DataRange(self)->'IXLSRange':
        """
        DataRange for the chart series.

        """
        GetDllLibXls().XlsChartShape_get_DataRange.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_DataRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_DataRange, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @DataRange.setter
    def DataRange(self, value:'IXLSRange'):
        GetDllLibXls().XlsChartShape_set_DataRange.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChartShape_set_DataRange, self.Ptr, value.Ptr)

    @property
    def SeriesDataFromRange(self)->bool:
        """
        Gets or sets whether the series data is from range.

        Returns:
            bool: True if series data is from range; otherwise, False.
        """
        GetDllLibXls().XlsChartShape_get_SeriesDataFromRange.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_SeriesDataFromRange.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_SeriesDataFromRange, self.Ptr)
        return ret

    @SeriesDataFromRange.setter
    def SeriesDataFromRange(self, value:bool):
        GetDllLibXls().XlsChartShape_set_SeriesDataFromRange.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartShape_set_SeriesDataFromRange, self.Ptr, value)

    @property

    def PageSetup(self)->'IChartPageSetup':
        """
        Gets the page setup for the chart.

        Returns:
            IChartPageSetup: The page setup for the chart.
        """
        GetDllLibXls().XlsChartShape_get_PageSetup.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_PageSetup.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_PageSetup, self.Ptr)
        ret = None if intPtr==None else IChartPageSetup(intPtr)
        return ret


    @property
    def XPos(self)->float:
        """
        Gets or sets the X position of the chart.

        Returns:
            float: The X position of the chart.
        """
        GetDllLibXls().XlsChartShape_get_XPos.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_XPos.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_XPos, self.Ptr)
        return ret

    @XPos.setter
    def XPos(self, value:float):
        GetDllLibXls().XlsChartShape_set_XPos.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartShape_set_XPos, self.Ptr, value)

    @property
    def YPos(self)->float:
        """
        Gets or sets the Y position of the chart.

        Returns:
            float: The Y position of the chart.
        """
        GetDllLibXls().XlsChartShape_get_YPos.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_YPos.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_YPos, self.Ptr)
        return ret

    @YPos.setter
    def YPos(self, value:float):
        GetDllLibXls().XlsChartShape_set_YPos.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsChartShape_set_YPos, self.Ptr, value)

    @property

    def PrimaryCategoryAxis(self)->'IChartCategoryAxis':
        """
        Gets the primary category axis of the chart.

        Returns:
            IChartCategoryAxis: The primary category axis.
        """
        GetDllLibXls().XlsChartShape_get_PrimaryCategoryAxis.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_PrimaryCategoryAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_PrimaryCategoryAxis, self.Ptr)
        ret = None if intPtr==None else IChartCategoryAxis(intPtr)
        return ret


    @property

    def PrimaryValueAxis(self)->'IChartValueAxis':
        """
        Gets the primary value axis of the chart.

        Returns:
            IChartValueAxis: The primary value axis.
        """
        GetDllLibXls().XlsChartShape_get_PrimaryValueAxis.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_PrimaryValueAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_PrimaryValueAxis, self.Ptr)
        ret = None if intPtr==None else IChartValueAxis(intPtr)
        return ret


    @property

    def PrimarySerieAxis(self)->'IChartSeriesAxis':
        """
        Gets the primary series axis of the chart.

        Returns:
            IChartSeriesAxis: The primary series axis.
        """
        GetDllLibXls().XlsChartShape_get_PrimarySerieAxis.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_PrimarySerieAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_PrimarySerieAxis, self.Ptr)
        ret = None if intPtr==None else IChartSeriesAxis(intPtr)
        return ret


    @property

    def SecondaryCategoryAxis(self)->'IChartCategoryAxis':
        """
        Gets the secondary category axis of the chart.

        Returns:
            IChartCategoryAxis: The secondary category axis.
        """
        GetDllLibXls().XlsChartShape_get_SecondaryCategoryAxis.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_SecondaryCategoryAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_SecondaryCategoryAxis, self.Ptr)
        ret = None if intPtr==None else IChartCategoryAxis(intPtr)
        return ret


    @property

    def SecondaryValueAxis(self)->'IChartValueAxis':
        """
        Gets the secondary value axis of the chart.

        Returns:
            IChartValueAxis: The secondary value axis.
        """
        GetDllLibXls().XlsChartShape_get_SecondaryValueAxis.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_SecondaryValueAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_SecondaryValueAxis, self.Ptr)
        ret = None if intPtr==None else IChartValueAxis(intPtr)
        return ret


    @property

    def ChartArea(self)->'IChartFrameFormat':
        """
        Gets the chart area format.

        Returns:
            IChartFrameFormat: The chart area format.
        """
        GetDllLibXls().XlsChartShape_get_ChartArea.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_ChartArea.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_ChartArea, self.Ptr)
        ret = None if intPtr==None else XlsChartFrameFormat(intPtr)
        return ret


    @property

    def PlotArea(self)->'IChartFrameFormat':
        """
        Gets the plot area format.

        Returns:
            IChartFrameFormat: The plot area format.
        """
        GetDllLibXls().XlsChartShape_get_PlotArea.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_PlotArea.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_PlotArea, self.Ptr)
        ret = None if intPtr==None else XlsChartFrameFormat(intPtr)
        return ret


    @property

    def Walls(self)->'IChartWallOrFloor':
        """
        Gets the walls of the chart.

        Returns:
            IChartWallOrFloor: The walls of the chart.
        """
        GetDllLibXls().XlsChartShape_get_Walls.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_Walls.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_Walls, self.Ptr)
        ret = None if intPtr==None else IChartWallOrFloor(intPtr)
        return ret


    @property
    def SupportWallsAndFloor(self)->bool:
        """
        Indicates whether this chart supports walls and floor. Read-only.

        """
        GetDllLibXls().XlsChartShape_get_SupportWallsAndFloor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_SupportWallsAndFloor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_SupportWallsAndFloor, self.Ptr)
        return ret

    @property

    def Floor(self)->'IChartWallOrFloor':
        """
        Gets the floor of the chart.

        Returns:
            IChartWallOrFloor: The floor of the chart.
        """
        GetDllLibXls().XlsChartShape_get_Floor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_Floor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_Floor, self.Ptr)
        ret = None if intPtr==None else IChartWallOrFloor(intPtr)
        return ret


    @property

    def DataTable(self)->'IChartDataTable':
        """
        Gets the data table of the chart.

        Returns:
            IChartDataTable: The data table of the chart.
        """
        GetDllLibXls().XlsChartShape_get_DataTable.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_DataTable.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_DataTable, self.Ptr)
        ret = None if intPtr==None else IChartDataTable(intPtr)
        return ret


    @property
    def HasChartTitle(self)->bool:
        """
        Indicates wheather the chart has title

        """
        GetDllLibXls().XlsChartShape_get_HasChartTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_HasChartTitle.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_HasChartTitle, self.Ptr)
        return ret

    @HasChartTitle.setter
    def HasChartTitle(self, value:bool):
        GetDllLibXls().XlsChartShape_set_HasChartTitle.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartShape_set_HasChartTitle, self.Ptr, value)

    @property
    def HasChartArea(self)->bool:
        """
        Indicates whether chart has chart area.

        """
        GetDllLibXls().XlsChartShape_get_HasChartArea.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_HasChartArea.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_HasChartArea, self.Ptr)
        return ret

    @HasChartArea.setter
    def HasChartArea(self, value:bool):
        GetDllLibXls().XlsChartShape_set_HasChartArea.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartShape_set_HasChartArea, self.Ptr, value)

    @property
    def HasDataTable(self)->bool:
        """
        True if the chart has a data table.
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

        """
        GetDllLibXls().XlsChartShape_get_HasDataTable.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_HasDataTable.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_HasDataTable, self.Ptr)
        return ret

    @HasDataTable.setter
    def HasDataTable(self, value:bool):
        GetDllLibXls().XlsChartShape_set_HasDataTable.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartShape_set_HasDataTable, self.Ptr, value)

    @property
    def HasFloor(self)->bool:
        """
        Gets value indicating whether floor object was created.

        """
        GetDllLibXls().XlsChartShape_get_HasFloor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_HasFloor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_HasFloor, self.Ptr)
        return ret

    @property
    def HasWalls(self)->bool:
        """
        Gets value indicating whether floor object was created.

        """
        GetDllLibXls().XlsChartShape_get_HasWalls.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_HasWalls.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_HasWalls, self.Ptr)
        return ret

    @property

    def Legend(self)->'IChartLegend':
        """

        """
        GetDllLibXls().XlsChartShape_get_Legend.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_Legend.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_Legend, self.Ptr)
        ret = None if intPtr==None else IChartLegend(intPtr)
        return ret


    @property
    def HasLegend(self)->bool:
        """
        True if the chart has a legend object.
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

        """
        GetDllLibXls().XlsChartShape_get_HasLegend.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_HasLegend.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_HasLegend, self.Ptr)
        return ret

    @HasLegend.setter
    def HasLegend(self, value:bool):
        GetDllLibXls().XlsChartShape_set_HasLegend.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartShape_set_HasLegend, self.Ptr, value)

    @property
    def HasPivotTable(self)->bool:
        """
        Indicates whether contains pivot table.

        """
        GetDllLibXls().XlsChartShape_get_HasPivotTable.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_HasPivotTable.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_HasPivotTable, self.Ptr)
        return ret

    @property
    def Rotation(self)->int:
        """
        Returns or sets the rotation of the 3-D chart view (the rotation of the plot area around the z-axis, in degrees).(0 to 360 degrees).
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

        """
        GetDllLibXls().XlsChartShape_get_Rotation.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_Rotation.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_Rotation, self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:int):
        GetDllLibXls().XlsChartShape_set_Rotation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartShape_set_Rotation, self.Ptr, value)

    @property
    def Elevation(self)->int:
        """
        Returns or sets the elevation of the 3-D chart view, in degrees (?0 to +90 degrees).
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

        """
        GetDllLibXls().XlsChartShape_get_Elevation.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_Elevation.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_Elevation, self.Ptr)
        return ret

    @Elevation.setter
    def Elevation(self, value:int):
        GetDllLibXls().XlsChartShape_set_Elevation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartShape_set_Elevation, self.Ptr, value)

    @property
    def Perspective(self)->int:
        """
        Returns or sets the perspective for the 3-D chart view (0 to 100).
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

        """
        GetDllLibXls().XlsChartShape_get_Perspective.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_Perspective.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_Perspective, self.Ptr)
        return ret

    @Perspective.setter
    def Perspective(self, value:int):
        GetDllLibXls().XlsChartShape_set_Perspective.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartShape_set_Perspective, self.Ptr, value)

    @property
    def HeightPercent(self)->int:
        """
        Gets or sets the height of a 3-D chart as a percentage of the chart width (5 to 500 percent).

        Returns:
            int: The height percentage.
        """
        GetDllLibXls().XlsChartShape_get_HeightPercent.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_HeightPercent.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_HeightPercent, self.Ptr)
        return ret

    @HeightPercent.setter
    def HeightPercent(self, value:int):
        GetDllLibXls().XlsChartShape_set_HeightPercent.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartShape_set_HeightPercent, self.Ptr, value)

    @property
    def DepthPercent(self)->int:
        """
        Gets or sets the depth of a 3-D chart as a percentage of the chart width (20 to 2000 percent).

        Returns:
            int: The depth percentage.
        """
        GetDllLibXls().XlsChartShape_get_DepthPercent.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_DepthPercent.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_DepthPercent, self.Ptr)
        return ret

    @DepthPercent.setter
    def DepthPercent(self, value:int):
        GetDllLibXls().XlsChartShape_set_DepthPercent.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartShape_set_DepthPercent, self.Ptr, value)

    @property
    def GapDepth(self)->int:
        """
        Gets or sets the distance between the data series in a 3-D chart, as a percentage of the marker width.

        Returns:
            int: The gap depth percentage.
        """
        GetDllLibXls().XlsChartShape_get_GapDepth.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_GapDepth.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_GapDepth, self.Ptr)
        return ret

    @GapDepth.setter
    def GapDepth(self, value:int):
        GetDllLibXls().XlsChartShape_set_GapDepth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartShape_set_GapDepth, self.Ptr, value)

    @property
    def RightAngleAxes(self)->bool:
        """
        Gets or sets whether the chart axes are at right angles, independent of chart rotation or elevation.

        Returns:
            bool: True if the axes are at right angles; otherwise, False.
        """
        GetDllLibXls().XlsChartShape_get_RightAngleAxes.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_RightAngleAxes.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_RightAngleAxes, self.Ptr)
        return ret

    @RightAngleAxes.setter
    def RightAngleAxes(self, value:bool):
        GetDllLibXls().XlsChartShape_set_RightAngleAxes.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartShape_set_RightAngleAxes, self.Ptr, value)

    @property
    def AutoScaling(self)->bool:
        """
        Gets or sets whether Microsoft Excel scales a 3-D chart so that it's closer in size to the equivalent 2-D chart.

        Returns:
            bool: True if auto scaling is enabled; otherwise, False.
        """
        GetDllLibXls().XlsChartShape_get_AutoScaling.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_AutoScaling.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_AutoScaling, self.Ptr)
        return ret

    @AutoScaling.setter
    def AutoScaling(self, value:bool):
        GetDllLibXls().XlsChartShape_set_AutoScaling.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartShape_set_AutoScaling, self.Ptr, value)

    @property
    def WallsAndGridlines2D(self)->bool:
        """
        Gets or sets whether gridlines are drawn two-dimensionally on a 3-D chart.

        Returns:
            bool: True if gridlines are drawn two-dimensionally; otherwise, False.
        """
        GetDllLibXls().XlsChartShape_get_WallsAndGridlines2D.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_WallsAndGridlines2D.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_WallsAndGridlines2D, self.Ptr)
        return ret

    @WallsAndGridlines2D.setter
    def WallsAndGridlines2D(self, value:bool):
        GetDllLibXls().XlsChartShape_set_WallsAndGridlines2D.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartShape_set_WallsAndGridlines2D, self.Ptr, value)

    @property
    def HasPlotArea(self)->bool:
        """
        Gets or sets whether the chart has a plot area.

        Returns:
            bool: True if the chart has a plot area; otherwise, False.
        """
        GetDllLibXls().XlsChartShape_get_HasPlotArea.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_HasPlotArea.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_HasPlotArea, self.Ptr)
        return ret

    @HasPlotArea.setter
    def HasPlotArea(self, value:bool):
        GetDllLibXls().XlsChartShape_set_HasPlotArea.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartShape_set_HasPlotArea, self.Ptr, value)

    @property

    def DisplayBlanksAs(self)->'ChartPlotEmptyType':
        """
        Gets or sets how blank cells are plotted on a chart.

        Returns:
            ChartPlotEmptyType: The way blank cells are plotted.
        """
        GetDllLibXls().XlsChartShape_get_DisplayBlanksAs.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_DisplayBlanksAs.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_DisplayBlanksAs, self.Ptr)
        objwraped = ChartPlotEmptyType(ret)
        return objwraped

    @DisplayBlanksAs.setter
    def DisplayBlanksAs(self, value:'ChartPlotEmptyType'):
        GetDllLibXls().XlsChartShape_set_DisplayBlanksAs.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartShape_set_DisplayBlanksAs, self.Ptr, value.value)

    @property
    def PlotVisibleOnly(self)->bool:
        """
        Gets or sets whether only visible cells are plotted.

        Returns:
            bool: True if only visible cells are plotted; otherwise, False.
        """
        GetDllLibXls().XlsChartShape_get_PlotVisibleOnly.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_PlotVisibleOnly.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_PlotVisibleOnly, self.Ptr)
        return ret

    @PlotVisibleOnly.setter
    def PlotVisibleOnly(self, value:bool):
        GetDllLibXls().XlsChartShape_set_PlotVisibleOnly.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartShape_set_PlotVisibleOnly, self.Ptr, value)

    @property
    def SizeWithWindow(self)->bool:
        """
        Gets or sets whether the chart should be sized with the window.

        Returns:
            bool: True if the chart should be sized with the window; otherwise, False.
        """
        GetDllLibXls().XlsChartShape_get_SizeWithWindow.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_SizeWithWindow.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_SizeWithWindow, self.Ptr)
        return ret

    @SizeWithWindow.setter
    def SizeWithWindow(self, value:bool):
        GetDllLibXls().XlsChartShape_set_SizeWithWindow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartShape_set_SizeWithWindow, self.Ptr, value)

    @property

    def PivotTable(self)->'PivotTable':
        """
        Gets the pivot table associated with the chart.

        Returns:
            PivotTable: The associated pivot table.
        """
        GetDllLibXls().XlsChartShape_get_PivotTable.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_PivotTable.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_PivotTable, self.Ptr)
        ret = None if intPtr==None else PivotTable(intPtr)
        return ret


    @PivotTable.setter
    def PivotTable(self, value:'PivotTable'):
        GetDllLibXls().XlsChartShape_set_PivotTable.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChartShape_set_PivotTable, self.Ptr, value.Ptr)

    @property

    def PivotChartType(self)->'ExcelChartType':
        """
        Gets or sets the chart type for the pivot chart.

        Returns:
            ExcelChartType: The chart type for the pivot chart.
        """
        GetDllLibXls().XlsChartShape_get_PivotChartType.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_PivotChartType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_PivotChartType, self.Ptr)
        objwraped = ExcelChartType(ret)
        return objwraped

    @PivotChartType.setter
    def PivotChartType(self, value:'ExcelChartType'):
        GetDllLibXls().XlsChartShape_set_PivotChartType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartShape_set_PivotChartType, self.Ptr, value.value)

    @property
    def DisplayEntireFieldButtons(self)->bool:
        """
        Gets or sets whether to display all field buttons on the pivot chart.

        Returns:
            bool: True if all field buttons should be displayed; otherwise, False.
        """
        GetDllLibXls().XlsChartShape_get_DisplayEntireFieldButtons.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_DisplayEntireFieldButtons.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_DisplayEntireFieldButtons, self.Ptr)
        return ret

    @DisplayEntireFieldButtons.setter
    def DisplayEntireFieldButtons(self, value:bool):
        GetDllLibXls().XlsChartShape_set_DisplayEntireFieldButtons.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartShape_set_DisplayEntireFieldButtons, self.Ptr, value)

    @property
    def DisplayValueFieldButtons(self)->bool:
        """
        Gets or sets whether to display value field buttons on the pivot chart.

        Returns:
            bool: True if value field buttons should be displayed; otherwise, False.
        """
        GetDllLibXls().XlsChartShape_get_DisplayValueFieldButtons.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_DisplayValueFieldButtons.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_DisplayValueFieldButtons, self.Ptr)
        return ret

    @DisplayValueFieldButtons.setter
    def DisplayValueFieldButtons(self, value:bool):
        GetDllLibXls().XlsChartShape_set_DisplayValueFieldButtons.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartShape_set_DisplayValueFieldButtons, self.Ptr, value)

    @property
    def DisplayAxisFieldButtons(self)->bool:
        """
        Gets or sets whether to display axis field buttons on the pivot chart.

        Returns:
            bool: True if axis field buttons should be displayed; otherwise, False.
        """
        GetDllLibXls().XlsChartShape_get_DisplayAxisFieldButtons.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_DisplayAxisFieldButtons.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_DisplayAxisFieldButtons, self.Ptr)
        return ret

    @DisplayAxisFieldButtons.setter
    def DisplayAxisFieldButtons(self, value:bool):
        GetDllLibXls().XlsChartShape_set_DisplayAxisFieldButtons.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartShape_set_DisplayAxisFieldButtons, self.Ptr, value)

    @property
    def DisplayLegendFieldButtons(self)->bool:
        """
        Gets or sets whether to display legend field buttons on the pivot chart.

        Returns:
            bool: True if legend field buttons should be displayed; otherwise, False.
        """
        GetDllLibXls().XlsChartShape_get_DisplayLegendFieldButtons.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_DisplayLegendFieldButtons.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_DisplayLegendFieldButtons, self.Ptr)
        return ret

    @DisplayLegendFieldButtons.setter
    def DisplayLegendFieldButtons(self, value:bool):
        GetDllLibXls().XlsChartShape_set_DisplayLegendFieldButtons.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartShape_set_DisplayLegendFieldButtons, self.Ptr, value)

    @property
    def ShowReportFilterFieldButtons(self)->bool:
        """
        Gets or sets whether to display report filter field buttons on the pivot chart.

        Returns:
            bool: True if report filter field buttons should be displayed; otherwise, False.
        """
        GetDllLibXls().XlsChartShape_get_ShowReportFilterFieldButtons.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_ShowReportFilterFieldButtons.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_ShowReportFilterFieldButtons, self.Ptr)
        return ret

    @ShowReportFilterFieldButtons.setter
    def ShowReportFilterFieldButtons(self, value:bool):
        GetDllLibXls().XlsChartShape_set_ShowReportFilterFieldButtons.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartShape_set_ShowReportFilterFieldButtons, self.Ptr, value)

    @property
    def TopRow(self)->int:
        """
        Gets or sets the top row of the chart.

        Returns:
            int: The top row index.
        """
        GetDllLibXls().XlsChartShape_get_TopRow.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_TopRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_TopRow, self.Ptr)
        return ret

    @TopRow.setter
    def TopRow(self, value:int):
        GetDllLibXls().XlsChartShape_set_TopRow.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartShape_set_TopRow, self.Ptr, value)

    @property
    def BottomRow(self)->int:
        """
        Gets or sets the bottom row of the chart.

        Returns:
            int: The bottom row index.
        """
        GetDllLibXls().XlsChartShape_get_BottomRow.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_BottomRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_BottomRow, self.Ptr)
        return ret

    @BottomRow.setter
    def BottomRow(self, value:int):
        GetDllLibXls().XlsChartShape_set_BottomRow.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartShape_set_BottomRow, self.Ptr, value)

    @property
    def LeftColumn(self)->int:
        """
        Gets or sets the left column of the chart.

        Returns:
            int: The left column index.
        """
        GetDllLibXls().XlsChartShape_get_LeftColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_LeftColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_LeftColumn, self.Ptr)
        return ret

    @LeftColumn.setter
    def LeftColumn(self, value:int):
        GetDllLibXls().XlsChartShape_set_LeftColumn.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartShape_set_LeftColumn, self.Ptr, value)

    @property
    def RightColumn(self)->int:
        """
        Gets or sets the right column of the chart.

        Returns:
            int: The right column index.
        """
        GetDllLibXls().XlsChartShape_get_RightColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_RightColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartShape_get_RightColumn, self.Ptr)
        return ret

    @RightColumn.setter
    def RightColumn(self, value:int):
        GetDllLibXls().XlsChartShape_set_RightColumn.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartShape_set_RightColumn, self.Ptr, value)

    @property

    def ChartTitleArea(self)->'IChartTextArea':
        """
        Gets the chart title area.

        Returns:
            IChartTextArea: The chart title area.
        """
        GetDllLibXls().XlsChartShape_get_ChartTitleArea.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_ChartTitleArea.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartShape_get_ChartTitleArea, self.Ptr)
        ret = None if intPtr==None else IChartTextArea(intPtr)
        return ret


    @property

    def ChartSubTitle(self)->str:
        """
        Gets or sets the chart subtitle.

        Returns:
            str: The chart subtitle.
        """
        GetDllLibXls().XlsChartShape_get_ChartSubTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_ChartSubTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartShape_get_ChartSubTitle, self.Ptr))
        return ret


    @property

    def ChartTitle(self)->str:
        """
        Gets or sets the chart title.

        Returns:
            str: The chart title.
        """
        GetDllLibXls().XlsChartShape_get_ChartTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsChartShape_get_ChartTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsChartShape_get_ChartTitle, self.Ptr))
        return ret

    @ChartTitle.setter
    def ChartTitle(self, value:str):
        GetDllLibXls().XlsChartShape_set_ChartTitle.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsChartShape_set_ChartTitle, self.Ptr, value)

