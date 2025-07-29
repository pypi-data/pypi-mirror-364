from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsPivotTable (  XlsObject, IPivotTable) :
    """Implementation of the PivotTable interface.
    
    This class provides functionality for managing PivotTables in Excel worksheets,
    including formatting options, data calculation, and source management.
    """
    @property
    def ShowRowStripes(self)->bool:
        """Gets whether row stripe formatting is shown for the table.
        
        Returns:
            bool: True if row stripe formatting is shown; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_ShowRowStripes.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_ShowRowStripes.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_ShowRowStripes, self.Ptr)
        return ret

    @ShowRowStripes.setter
    def ShowRowStripes(self, value:bool):
        """Sets whether row stripe formatting is shown for the table.
        
        Args:
            value (bool): True to show row stripe formatting; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_ShowRowStripes.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_ShowRowStripes, self.Ptr, value)

    @property
    def ShowDataFieldInRow(self)->bool:
        """Gets whether the calculated data field is added in rows.
        
        Returns:
            bool: True if the calculated data field is added in rows; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_ShowDataFieldInRow.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_ShowDataFieldInRow.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_ShowDataFieldInRow, self.Ptr)
        return ret

    @ShowDataFieldInRow.setter
    def ShowDataFieldInRow(self, value:bool):
        """Sets whether the calculated data field is added in rows.
        
        Args:
            value (bool): True to add the calculated data field in rows; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_ShowDataFieldInRow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_ShowDataFieldInRow, self.Ptr, value)

    @property

    def ReportFilters(self)->'PivotReportFilters':
        """Gets the report filter collection for the PivotTable.
        
        Returns:
            PivotReportFilters: The collection of report filters.
        """
        GetDllLibXls().XlsPivotTable_get_ReportFilters.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_ReportFilters.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotTable_get_ReportFilters, self.Ptr)
        ret = None if intPtr==None else PivotReportFilters(intPtr)
        return ret


    @ReportFilters.setter
    def ReportFilters(self, value:'PivotReportFilters'):
        """Sets the report filter collection for the PivotTable.
        
        Args:
            value (PivotReportFilters): The collection of report filters to set.
        """
        GetDllLibXls().XlsPivotTable_set_ReportFilters.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_ReportFilters, self.Ptr, value.Ptr)

    @property
    def AllSubTotalTop(self)->bool:
        """Gets whether all subtotals are displayed at the top of each group.
        
        Changes to this property will affect every field's setting.
        
        Returns:
            bool: True if all subtotals are displayed at the top; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_AllSubTotalTop.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_AllSubTotalTop.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_AllSubTotalTop, self.Ptr)
        return ret

    @AllSubTotalTop.setter
    def AllSubTotalTop(self, value:bool):
        """Sets whether all subtotals are displayed at the top of each group.
        
        Changes to this property will affect every field's setting.
        
        Args:
            value (bool): True to display all subtotals at the top; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_AllSubTotalTop.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_AllSubTotalTop, self.Ptr, value)

    @property

    def CustomTableStyleName(self)->str:
        """Gets the name of the custom table style for the PivotTable.
        
        Returns:
            str: The name of the custom table style.
        """
        GetDllLibXls().XlsPivotTable_get_CustomTableStyleName.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_CustomTableStyleName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPivotTable_get_CustomTableStyleName, self.Ptr))
        return ret


    @CustomTableStyleName.setter
    def CustomTableStyleName(self, value:str):
        """Sets the name of the custom table style for the PivotTable.
        
        Args:
            value (str): The name of the custom table style.
        """
        GetDllLibXls().XlsPivotTable_set_CustomTableStyleName.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_CustomTableStyleName, self.Ptr, value)

    def CalculateData(self):
        """Calculates the data in the PivotTable.
        
        This method refreshes the PivotTable and recalculates all values.
        """
        GetDllLibXls().XlsPivotTable_CalculateData.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsPivotTable_CalculateData, self.Ptr)


    def ChangeDataSource(self ,dataSource:'IXLSRange'):
        """Changes the data source of the PivotTable.
        
        Args:
            dataSource (IXLSRange): The new data source range.
        """
        intPtrdataSource:c_void_p = dataSource.Ptr

        GetDllLibXls().XlsPivotTable_ChangeDataSource.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsPivotTable_ChangeDataSource, self.Ptr, intPtrdataSource)

    @dispatch

    def Clone(self ,parent:SpireObject)->SpireObject:
        """Creates a clone of this PivotTable.
        
        Args:
            parent (SpireObject): The parent object for the cloned PivotTable.
            
        Returns:
            SpireObject: The cloned PivotTable.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsPivotTable_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsPivotTable_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotTable_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


#    @dispatch
#
#    def Clone(self ,parent:SpireObject,cacheIndex:int,hashWorksheetNames:'Dictionary2')->SpireObject:
#        """
#
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrhashWorksheetNames:c_void_p = hashWorksheetNames.Ptr
#
#        GetDllLibXls().XlsPivotTable_ClonePCH.argtypes=[c_void_p ,c_void_p,c_int,c_void_p]
#        GetDllLibXls().XlsPivotTable_ClonePCH.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsPivotTable_ClonePCH, self.Ptr, intPtrparent,cacheIndex,intPtrhashWorksheetNames)
#        ret = None if intPtr==None else SpireObject(intPtr)
#        return ret
#


    @property

    def Name(self)->str:
        """Gets the name of the PivotTable.
        
        Returns:
            str: The name of the PivotTable.
        """
        GetDllLibXls().XlsPivotTable_get_Name.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPivotTable_get_Name, self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        """Sets the name of the PivotTable.
        
        Args:
            value (str): The name to set for the PivotTable.
        """
        GetDllLibXls().XlsPivotTable_set_Name.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_Name, self.Ptr, value)

    @property

    def PivotFields(self)->'PivotTableFields':
        """Gets the collection of fields in the PivotTable.
        
        Returns:
            PivotTableFields: The collection of PivotTable fields.
        """
        GetDllLibXls().XlsPivotTable_get_PivotFields.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_PivotFields.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotTable_get_PivotFields, self.Ptr)
        ret = None if intPtr==None else PivotTableFields(intPtr)
        return ret


    @property

    def DataFields(self)->'PivotDataFields':
        """Gets the collection of data fields in the PivotTable.
        
        Returns:
            PivotDataFields: The collection of PivotTable data fields.
        """
        GetDllLibXls().XlsPivotTable_get_DataFields.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_DataFields.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotTable_get_DataFields, self.Ptr)
        ret = None if intPtr==None else PivotDataFields(intPtr)
        return ret


    @property
    def IsRowGrand(self)->bool:
        """Gets whether grand totals are displayed for rows.
        
        Returns:
            bool: True if grand totals are displayed for rows; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_IsRowGrand.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_IsRowGrand.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_IsRowGrand, self.Ptr)
        return ret

    @IsRowGrand.setter
    def IsRowGrand(self, value:bool):
        """Sets whether grand totals are displayed for rows.
        
        Args:
            value (bool): True to display grand totals for rows; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_IsRowGrand.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_IsRowGrand, self.Ptr, value)

    @property
    def IsColumnGrand(self)->bool:
        """Gets whether grand totals are displayed for columns.
        
        Returns:
            bool: True if grand totals are displayed for columns; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_IsColumnGrand.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_IsColumnGrand.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_IsColumnGrand, self.Ptr)
        return ret

    @IsColumnGrand.setter
    def IsColumnGrand(self, value:bool):
        """Sets whether grand totals are displayed for columns.
        
        Args:
            value (bool): True to display grand totals for columns; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_IsColumnGrand.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_IsColumnGrand, self.Ptr, value)

    @property
    def ShowDrillIndicators(self)->bool:
        """Gets whether drill indicators are shown in the PivotTable.
        
        Returns:
            bool: True if drill indicators are shown; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_ShowDrillIndicators.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_ShowDrillIndicators.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_ShowDrillIndicators, self.Ptr)
        return ret

    @ShowDrillIndicators.setter
    def ShowDrillIndicators(self, value:bool):
        """Sets whether drill indicators are shown in the PivotTable.
        
        Args:
            value (bool): True to show drill indicators; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_ShowDrillIndicators.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_ShowDrillIndicators, self.Ptr, value)

    @property
    def DisplayFieldCaptions(self)->bool:
        """Gets whether field captions are displayed in the PivotTable.
        
        Returns:
            bool: True if field captions are displayed; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_DisplayFieldCaptions.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_DisplayFieldCaptions.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_DisplayFieldCaptions, self.Ptr)
        return ret

    @DisplayFieldCaptions.setter
    def DisplayFieldCaptions(self, value:bool):
        """Sets whether field captions are displayed in the PivotTable.
        
        Args:
            value (bool): True to display field captions; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_DisplayFieldCaptions.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_DisplayFieldCaptions, self.Ptr, value)

    @property
    def RepeatItemsOnEachPrintedPage(self)->bool:
        """Gets whether items are repeated on each printed page.
        
        Returns:
            bool: True if items are repeated on each printed page; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_RepeatItemsOnEachPrintedPage.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_RepeatItemsOnEachPrintedPage.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_RepeatItemsOnEachPrintedPage, self.Ptr)
        return ret

    @RepeatItemsOnEachPrintedPage.setter
    def RepeatItemsOnEachPrintedPage(self, value:bool):
        """Sets whether items are repeated on each printed page.
        
        Args:
            value (bool): True to repeat items on each printed page; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_RepeatItemsOnEachPrintedPage.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_RepeatItemsOnEachPrintedPage, self.Ptr, value)

    @property

    def BuiltInStyle(self)->PivotBuiltInStyles:
        """Gets the built-in style used for the PivotTable.
        
        Returns:
            PivotBuiltInStyles: An enumeration value representing the built-in style.
        """
        GetDllLibXls().XlsPivotTable_get_BuiltInStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_BuiltInStyle.restype=c_int
        intPtr = CallCFunction(GetDllLibXls().XlsPivotTable_get_BuiltInStyle, self.Ptr)
        ret = None if intPtr==None else PivotBuiltInStyles(intPtr)
        return ret



    @BuiltInStyle.setter
    def BuiltInStyle(self, value:PivotBuiltInStyles):
        """Sets the built-in style used for the PivotTable.
        
        Args:
            value (PivotBuiltInStyles): An enumeration value representing the built-in style to set.
        """
        GetDllLibXls().XlsPivotTable_set_BuiltInStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_BuiltInStyle, self.Ptr, value.value)


    @property
    def ShowRowGrand(self)->bool:
        """Gets whether grand totals are shown for rows.
        
        Returns:
            bool: True if grand totals are shown for rows; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_ShowRowGrand.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_ShowRowGrand.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_ShowRowGrand, self.Ptr)
        return ret

    @ShowRowGrand.setter
    def ShowRowGrand(self, value:bool):
        """Sets whether grand totals are shown for rows.
        
        Args:
            value (bool): True to show grand totals for rows; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_ShowRowGrand.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_ShowRowGrand, self.Ptr, value)

    @property
    def ShowColumnGrand(self)->bool:
        """Gets whether grand totals are shown for columns.
        
        Returns:
            bool: True if grand totals are shown for columns; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_ShowColumnGrand.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_ShowColumnGrand.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_ShowColumnGrand, self.Ptr)
        return ret

    @ShowColumnGrand.setter
    def ShowColumnGrand(self, value:bool):
        """Sets whether grand totals are shown for columns.
        
        Args:
            value (bool): True to show grand totals for columns; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_ShowColumnGrand.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_ShowColumnGrand, self.Ptr, value)

    @property
    def CacheIndex(self)->int:
        """Gets the index of the PivotCache used by this PivotTable.
        
        Returns:
            int: The index of the PivotCache.
        """
        GetDllLibXls().XlsPivotTable_get_CacheIndex.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_CacheIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_CacheIndex, self.Ptr)
        return ret

    @property

    def AutoFormatType(self)->'PivotAutoFomatTypes':
        """Gets the auto-format type used for the PivotTable.
        
        Returns:
            PivotAutoFomatTypes: An enumeration value representing the auto-format type.
        """
        GetDllLibXls().XlsPivotTable_get_AutoFormatType.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_AutoFormatType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_AutoFormatType, self.Ptr)
        objwraped = PivotAutoFomatTypes(ret)
        return objwraped

    @AutoFormatType.setter
    def AutoFormatType(self, value:'PivotAutoFomatTypes'):
        """Sets the auto-format type used for the PivotTable.
        
        Args:
            value (PivotAutoFomatTypes): An enumeration value representing the auto-format type to set.
        """
        GetDllLibXls().XlsPivotTable_set_AutoFormatType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_AutoFormatType, self.Ptr, value.value)

    @property
    def IsCompatibleWithExcel2003(self)->bool:
        """Gets whether the PivotTable is compatible with Excel 2003.
        
        Returns:
            bool: True if the PivotTable is compatible with Excel 2003; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_IsCompatibleWithExcel2003.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_IsCompatibleWithExcel2003.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_IsCompatibleWithExcel2003, self.Ptr)
        return ret

    @IsCompatibleWithExcel2003.setter
    def IsCompatibleWithExcel2003(self, value:bool):
        """Sets whether the PivotTable is compatible with Excel 2003.
        
        Args:
            value (bool): True to make the PivotTable compatible with Excel 2003; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_IsCompatibleWithExcel2003.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_IsCompatibleWithExcel2003, self.Ptr, value)

    @property

    def Location(self)->'CellRange':
        """Gets the location of the PivotTable on the worksheet.
        
        Returns:
            CellRange: The cell range representing the PivotTable's location.
        """
        GetDllLibXls().XlsPivotTable_get_Location.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_Location.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotTable_get_Location, self.Ptr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @Location.setter
    def Location(self, value:'CellRange'):
        """Sets the location of the PivotTable on the worksheet.
        
        Args:
            value (CellRange): The cell range representing the PivotTable's location.
        """
        GetDllLibXls().XlsPivotTable_set_Location.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_Location, self.Ptr, value.Ptr)

    @property

    def Options(self)->'IPivotTableOptions':
        """Gets the options for the PivotTable.
        
        Returns:
            IPivotTableOptions: The object containing PivotTable options.
        """
        GetDllLibXls().XlsPivotTable_get_Options.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_Options.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotTable_get_Options, self.Ptr)
        ret = None if intPtr==None else IPivotTableOptions(intPtr)
        return ret


    @property
    def RowsPerPage(self)->int:
        """Gets the number of rows shown per page in the PivotTable.
        
        Returns:
            int: The number of rows per page.
        """
        GetDllLibXls().XlsPivotTable_get_RowsPerPage.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_RowsPerPage.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_RowsPerPage, self.Ptr)
        return ret

    @RowsPerPage.setter
    def RowsPerPage(self, value:int):
        """Sets the number of rows shown per page in the PivotTable.
        
        Args:
            value (int): The number of rows per page.
        """
        GetDllLibXls().XlsPivotTable_set_RowsPerPage.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_RowsPerPage, self.Ptr, value)

    @property
    def ColumnsPerPage(self)->int:
        """Gets the number of columns shown per page in the PivotTable.
        
        Returns:
            int: The number of columns per page.
        """
        GetDllLibXls().XlsPivotTable_get_ColumnsPerPage.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_ColumnsPerPage.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_ColumnsPerPage, self.Ptr)
        return ret

    @ColumnsPerPage.setter
    def ColumnsPerPage(self, value:int):
        """Sets the number of columns shown per page in the PivotTable.
        
        Args:
            value (int): The number of columns per page.
        """
        GetDllLibXls().XlsPivotTable_set_ColumnsPerPage.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_ColumnsPerPage, self.Ptr, value)

    @property

    def CalculatedFields(self)->'IPivotCalculatedFields':
        """Gets the collection of calculated fields in the PivotTable.
        
        Returns:
            IPivotCalculatedFields: The collection of calculated fields.
        """
        GetDllLibXls().XlsPivotTable_get_CalculatedFields.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_CalculatedFields.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotTable_get_CalculatedFields, self.Ptr)
        ret = None if intPtr==None else PivotCalculatedFieldsCollection(intPtr)
        return ret


    @property

    def PageFields(self)->'IPivotFields':
        """Gets the collection of page fields in the PivotTable.
        
        Returns:
            IPivotFields: The collection of page fields.
        """
        GetDllLibXls().XlsPivotTable_get_PageFields.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_PageFields.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotTable_get_PageFields, self.Ptr)
        ret = None if intPtr==None else PivotTableFields(intPtr)
        return ret


    @property

    def RowFields(self)->'IPivotFields':
        """Gets the collection of row fields in the PivotTable.
        
        Returns:
            IPivotFields: The collection of row fields.
        """
        GetDllLibXls().XlsPivotTable_get_RowFields.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_RowFields.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotTable_get_RowFields, self.Ptr)
        ret = None if intPtr==None else PivotTableFields(intPtr)
        return ret


    @property

    def ColumnFields(self)->'IPivotFields':
        """Gets the collection of column fields in the PivotTable.
        
        Returns:
            IPivotFields: The collection of column fields.
        """
        GetDllLibXls().XlsPivotTable_get_ColumnFields.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_ColumnFields.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotTable_get_ColumnFields, self.Ptr)
        ret = None if intPtr==None else PivotTableFields(intPtr)
        return ret


    @property
    def ShowSubtotals(self)->bool:
        """Gets whether subtotals are shown in the PivotTable.
        
        Returns:
            bool: True if subtotals are shown; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_ShowSubtotals.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_ShowSubtotals.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_ShowSubtotals, self.Ptr)
        return ret

    @ShowSubtotals.setter
    def ShowSubtotals(self, value:bool):
        """Sets whether subtotals are shown in the PivotTable.
        
        Args:
            value (bool): True to show subtotals; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_ShowSubtotals.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_ShowSubtotals, self.Ptr, value)

    def Clear(self):
        """Clears the PivotTable, removing all fields and data.
        """
        GetDllLibXls().XlsPivotTable_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsPivotTable_Clear, self.Ptr)


    def ClearRowFieldFilter(self ,fieldName:str):
        """Clears the filter applied to a row field.
        
        Args:
            fieldName (str): The name of the field to clear the filter from.
        """
        
        GetDllLibXls().XlsPivotTable_ClearRowFieldFilter.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsPivotTable_ClearRowFieldFilter, self.Ptr, fieldName)


    def ClearColumnFieldFilter(self ,fieldName:str):
        """Clears the filter applied to a column field.
        
        Args:
            fieldName (str): The name of the field to clear the filter from.
        """
        
        GetDllLibXls().XlsPivotTable_ClearColumnFieldFilter.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsPivotTable_ClearColumnFieldFilter, self.Ptr, fieldName)


    def ClearFilter(self ,fieldName:str):
        """Clears all filters applied to a field.
        
        Args:
            fieldName (str): The name of the field to clear all filters from.
        """
        
        GetDllLibXls().XlsPivotTable_ClearFilter.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsPivotTable_ClearFilter, self.Ptr, fieldName)

    @property

    def Parent(self)->'XlsPivotTablesCollection':
        """Gets the parent collection of the PivotTable.
        
        Returns:
            XlsPivotTablesCollection: The parent collection object.
        """
        GetDllLibXls().XlsPivotTable_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotTable_get_Parent, self.Ptr)
        ret = None if intPtr==None else XlsPivotTablesCollection(intPtr)
        return ret


    @property
    def DisplayErrorString(self)->bool:
        """Gets whether error values are displayed as error strings in the PivotTable.
        
        Returns:
            bool: True if error values are displayed as strings; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_DisplayErrorString.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_DisplayErrorString.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_DisplayErrorString, self.Ptr)
        return ret

    @DisplayErrorString.setter
    def DisplayErrorString(self, value:bool):
        """Sets whether error values are displayed as error strings in the PivotTable.
        
        Args:
            value (bool): True to display error values as strings; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_DisplayErrorString.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_DisplayErrorString, self.Ptr, value)

    @property
    def DisplayNullString(self)->bool:
        """Gets whether null values are displayed as null strings in the PivotTable.
        
        Returns:
            bool: True if null values are displayed as strings; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_DisplayNullString.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_DisplayNullString.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_DisplayNullString, self.Ptr)
        return ret

    @DisplayNullString.setter
    def DisplayNullString(self, value:bool):
        """Sets whether null values are displayed as null strings in the PivotTable.
        
        Args:
            value (bool): True to display null values as strings; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_DisplayNullString.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_DisplayNullString, self.Ptr, value)

    @property
    def EnableDrilldown(self)->bool:
        """Gets whether drill-down functionality is enabled for the PivotTable.
        
        Returns:
            bool: True if drill-down is enabled; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_EnableDrilldown.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_EnableDrilldown.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_EnableDrilldown, self.Ptr)
        return ret

    @EnableDrilldown.setter
    def EnableDrilldown(self, value:bool):
        """Sets whether drill-down functionality is enabled for the PivotTable.
        
        Args:
            value (bool): True to enable drill-down; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_EnableDrilldown.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_EnableDrilldown, self.Ptr, value)

    @property
    def EnableFieldDialog(self)->bool:
        """Gets whether the field dialog is enabled for the PivotTable.
        
        Returns:
            bool: True if the field dialog is enabled; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_EnableFieldDialog.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_EnableFieldDialog.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_EnableFieldDialog, self.Ptr)
        return ret

    @EnableFieldDialog.setter
    def EnableFieldDialog(self, value:bool):
        """Sets whether the field dialog is enabled for the PivotTable.
        
        Args:
            value (bool): True to enable the field dialog; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_EnableFieldDialog.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_EnableFieldDialog, self.Ptr, value)

    @property
    def EnableWizard(self)->bool:
        """Gets whether the PivotTable wizard is enabled.
        
        Returns:
            bool: True if the wizard is enabled; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_EnableWizard.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_EnableWizard.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_EnableWizard, self.Ptr)
        return ret

    @EnableWizard.setter
    def EnableWizard(self, value:bool):
        """Sets whether the PivotTable wizard is enabled.
        
        Args:
            value (bool): True to enable the wizard; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_EnableWizard.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_EnableWizard, self.Ptr, value)

    @property

    def ErrorString(self)->str:
        """Gets the string displayed in cells that contain errors.
        
        Returns:
            str: The string displayed for error values.
        """
        GetDllLibXls().XlsPivotTable_get_ErrorString.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_ErrorString.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPivotTable_get_ErrorString, self.Ptr))
        return ret


    @ErrorString.setter
    def ErrorString(self, value:str):
        """Sets the string displayed in cells that contain errors.
        
        Args:
            value (str): The string to display for error values.
        """
        GetDllLibXls().XlsPivotTable_set_ErrorString.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_ErrorString, self.Ptr, value)

    @property
    def ManualUpdate(self)->bool:
        """Gets whether the PivotTable is updated manually.
        
        Returns:
            bool: True if manual update is enabled; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_ManualUpdate.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_ManualUpdate.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_ManualUpdate, self.Ptr)
        return ret

    @ManualUpdate.setter
    def ManualUpdate(self, value:bool):
        """Sets whether the PivotTable is updated manually.
        
        Args:
            value (bool): True to enable manual update; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_ManualUpdate.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_ManualUpdate, self.Ptr, value)

    @property
    def MergeLabels(self)->bool:
        """Gets whether labels are merged in the PivotTable.
        
        Returns:
            bool: True if labels are merged; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_MergeLabels.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_MergeLabels.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_MergeLabels, self.Ptr)
        return ret

    @MergeLabels.setter
    def MergeLabels(self, value:bool):
        """Sets whether labels are merged in the PivotTable.
        
        Args:
            value (bool): True to merge labels; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_MergeLabels.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_MergeLabels, self.Ptr, value)

    @property

    def NullString(self)->str:
        """Gets the string displayed in cells that contain null values.
        
        Returns:
            str: The string displayed for null values.
        """
        GetDllLibXls().XlsPivotTable_get_NullString.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_NullString.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPivotTable_get_NullString, self.Ptr))
        return ret


    @NullString.setter
    def NullString(self, value:str):
        """Sets the string displayed in cells that contain null values.
        
        Args:
            value (str): The string to display for null values.
        """
        GetDllLibXls().XlsPivotTable_set_NullString.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_NullString, self.Ptr, value)

    @property

    def PageFieldOrder(self)->'PagesOrderType':
        """Gets the order of page fields in the PivotTable.
        
        Returns:
            PagesOrderType: An enumeration value representing the page field order.
        """
        GetDllLibXls().XlsPivotTable_get_PageFieldOrder.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_PageFieldOrder.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_PageFieldOrder, self.Ptr)
        objwraped = PagesOrderType(ret)
        return objwraped

    @PageFieldOrder.setter
    def PageFieldOrder(self, value:'PagesOrderType'):
        """Sets the order of page fields in the PivotTable.
        
        Args:
            value (PagesOrderType): An enumeration value representing the page field order to set.
        """
        GetDllLibXls().XlsPivotTable_set_PageFieldOrder.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_PageFieldOrder, self.Ptr, value.value)

    @property

    def PageFieldStyle(self)->str:
        """Gets the style applied to page fields in the PivotTable.
        
        Returns:
            str: The name of the style applied to page fields.
        """
        GetDllLibXls().XlsPivotTable_get_PageFieldStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_PageFieldStyle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPivotTable_get_PageFieldStyle, self.Ptr))
        return ret


    @PageFieldStyle.setter
    def PageFieldStyle(self, value:str):
        """Sets the style applied to page fields in the PivotTable.
        
        Args:
            value (str): The name of the style to apply to page fields.
        """
        GetDllLibXls().XlsPivotTable_set_PageFieldStyle.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_PageFieldStyle, self.Ptr, value)

    @property
    def PageFieldWrapCount(self)->int:
        """Gets the number of page fields in a column before wrapping to a new row.
        
        Returns:
            int: The number of page fields per row.
        """
        GetDllLibXls().XlsPivotTable_get_PageFieldWrapCount.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_PageFieldWrapCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_PageFieldWrapCount, self.Ptr)
        return ret

    @PageFieldWrapCount.setter
    def PageFieldWrapCount(self, value:int):
        """Sets the number of page fields in a column before wrapping to a new row.
        
        Args:
            value (int): The number of page fields per row.
        """
        GetDllLibXls().XlsPivotTable_set_PageFieldWrapCount.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_PageFieldWrapCount, self.Ptr, value)

    @property

    def Cache(self)->'PivotCache':
        """Gets the PivotCache object associated with this PivotTable.
        
        Returns:
            PivotCache: The PivotCache object.
        """
        GetDllLibXls().XlsPivotTable_get_Cache.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_Cache.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotTable_get_Cache, self.Ptr)
        ret = None if intPtr==None else PivotCache(intPtr)
        return ret


    @property

    def PivotConditionalFormats(self)->'PivotConditionalFormatCollection':
        """Gets the collection of conditional formats applied to the PivotTable.
        
        Returns:
            PivotConditionalFormatCollection: The collection of conditional formats.
        """
        GetDllLibXls().XlsPivotTable_get_PivotConditionalFormats.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_PivotConditionalFormats.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotTable_get_PivotConditionalFormats, self.Ptr)
        ret = None if intPtr==None else PivotConditionalFormatCollection(intPtr)
        return ret


    @property

    def Workbook(self)->'XlsWorkbook':
        """Gets the workbook containing this PivotTable.
        
        Returns:
            XlsWorkbook: The workbook object.
        """
        GetDllLibXls().XlsPivotTable_get_Workbook.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_Workbook.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotTable_get_Workbook, self.Ptr)
        ret = None if intPtr==None else XlsWorkbook(intPtr)
        return ret


    @property

    def Worksheet(self)->'XlsWorksheet':
        """Gets the worksheet containing this PivotTable.
        
        Returns:
            XlsWorksheet: The worksheet object.
        """
        GetDllLibXls().XlsPivotTable_get_Worksheet.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_Worksheet.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotTable_get_Worksheet, self.Ptr)
        ret = None if intPtr==None else XlsWorksheet(intPtr)
        return ret


    @property
    def FirstDataCol(self)->int:
        """Gets the first column of the PivotTable data, relative to the top left cell.
        
        Returns:
            int: The index of the first data column.
        """
        GetDllLibXls().XlsPivotTable_get_FirstDataCol.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_FirstDataCol.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_FirstDataCol, self.Ptr)
        return ret

    @FirstDataCol.setter
    def FirstDataCol(self, value:int):
        """Sets the first column of the PivotTable data, relative to the top left cell.
        
        Args:
            value (int): The index of the first data column.
        """
        GetDllLibXls().XlsPivotTable_set_FirstDataCol.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_FirstDataCol, self.Ptr, value)

    @property
    def FirstDataRow(self)->int:
        """Gets the first row of the PivotTable data, relative to the top left cell.
        
        Returns:
            int: The index of the first data row.
        """
        GetDllLibXls().XlsPivotTable_get_FirstDataRow.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_FirstDataRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_FirstDataRow, self.Ptr)
        return ret

    @FirstDataRow.setter
    def FirstDataRow(self, value:int):
        """Sets the first row of the PivotTable data, relative to the top left cell.
        
        Args:
            value (int): The index of the first data row.
        """
        GetDllLibXls().XlsPivotTable_set_FirstDataRow.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_FirstDataRow, self.Ptr, value)

    @property
    def FirstHeaderRow(self)->int:
        """Gets the first row of the PivotTable header, relative to the top left cell.
        
        Returns:
            int: The index of the first header row.
        """
        GetDllLibXls().XlsPivotTable_get_FirstHeaderRow.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_FirstHeaderRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_FirstHeaderRow, self.Ptr)
        return ret

    @FirstHeaderRow.setter
    def FirstHeaderRow(self, value:int):
        """Sets the first row of the PivotTable header, relative to the top left cell.
        
        Args:
            value (int): The index of the first header row.
        """
        GetDllLibXls().XlsPivotTable_set_FirstHeaderRow.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_FirstHeaderRow, self.Ptr, value)

    @property
    def ShowColHeaderStyle(self)->bool:
        """Gets whether column headers are shown with a style in the PivotTable.
        
        Returns:
            bool: True if column headers are shown with a style; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_ShowColHeaderStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_ShowColHeaderStyle.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_ShowColHeaderStyle, self.Ptr)
        return ret

    @ShowColHeaderStyle.setter
    def ShowColHeaderStyle(self, value:bool):
        """Sets whether column headers are shown with a style in the PivotTable.
        
        Args:
            value (bool): True to show column headers with a style; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_ShowColHeaderStyle.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_ShowColHeaderStyle, self.Ptr, value)

    @property
    def ShowColStripes(self)->bool:
        """Gets whether column stripe formatting is shown for the PivotTable.
        
        Returns:
            bool: True if column stripe formatting is shown; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_ShowColStripes.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_ShowColStripes.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_ShowColStripes, self.Ptr)
        return ret

    @ShowColStripes.setter
    def ShowColStripes(self, value:bool):
        """Sets whether column stripe formatting is shown for the PivotTable.
        
        Args:
            value (bool): True to show column stripe formatting; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_ShowColStripes.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_ShowColStripes, self.Ptr, value)

    @property
    def ShowLastCol(self)->bool:
        """Gets whether the last column is shown in the PivotTable.
        
        Returns:
            bool: True if the last column is shown; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_ShowLastCol.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_ShowLastCol.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_ShowLastCol, self.Ptr)
        return ret

    @ShowLastCol.setter
    def ShowLastCol(self, value:bool):
        """Sets whether the last column is shown in the PivotTable.
        
        Args:
            value (bool): True to show the last column; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_ShowLastCol.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_ShowLastCol, self.Ptr, value)

    @property
    def ShowRowHeaderStyle(self)->bool:
        """Gets whether row headers are shown with a style in the PivotTable.
        
        Returns:
            bool: True if row headers are shown with a style; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_get_ShowRowHeaderStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotTable_get_ShowRowHeaderStyle.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotTable_get_ShowRowHeaderStyle, self.Ptr)
        return ret

    @ShowRowHeaderStyle.setter
    def ShowRowHeaderStyle(self, value:bool):
        """Sets whether row headers are shown with a style in the PivotTable.
        
        Args:
            value (bool): True to show row headers with a style; otherwise, False.
        """
        GetDllLibXls().XlsPivotTable_set_ShowRowHeaderStyle.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotTable_set_ShowRowHeaderStyle, self.Ptr, value)

