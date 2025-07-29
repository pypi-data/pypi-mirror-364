from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class Worksheet (  XlsWorksheet) :
    """

    """
    @property

    def AllocatedRange(self)->'CellRange':
        """
        Returns a Range object that represents the used range on the specified worksheet. Read-only.

        """
        GetDllLibXls().Worksheet_get_AllocatedRange.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_AllocatedRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_AllocatedRange, self.Ptr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @dispatch

    def get_Item(self ,row:int,column:int,lastRow:int,lastColumn:int)->CellRange:
        """
        Get cell range.

        Args:
            row: 
            column: 
            lastRow: 
            lastColumn: 

        """
        
        GetDllLibXls().Worksheet_get_Item.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        GetDllLibXls().Worksheet_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_Item, self.Ptr, row,column,lastRow,lastColumn)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @dispatch

    def get_Item(self ,row:int,column:int)->CellRange:
        """
        Get cell range.

        Args:
            row: 
            column: 

        """
        
        GetDllLibXls().Worksheet_get_ItemRC.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().Worksheet_get_ItemRC.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_ItemRC, self.Ptr, row,column)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @dispatch

    def get_Item(self ,name:str)->CellRange:
        """
        Get cell range.

        Args:
            name: 

        """
        
        GetDllLibXls().Worksheet_get_ItemN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().Worksheet_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_ItemN, self.Ptr, name)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @property

    def MergedCells(self)->'ListCellRanges':
        """
        Returns all merged ranges. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Merge cells
            worksheet["C2:D2"].Merge()
            worksheet["F3:G3"].Merge()
            #Get merged ranges
            IXLSRange[] mergedRanges = worksheet.MergedCells
            #Get merged range count . Output will be 2
            Console.Write(mergedRanges.Length)
            #Save to file
            workbook.SaveToFile("MergedCells.xlsx")

        """
        GetDllLibXls().Worksheet_get_MergedCells.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_MergedCells.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_MergedCells, self.Ptr)
        ret = None if intPtr==None else ListCellRanges(intPtr)
        return ret



    def FindAll(self ,findValue:str,flags:'FindType',findOptions:'ExcelFindOptions')->'ListCellRanges':
        """
        Finds the all cells with specified string value.

        Args:
            findValue: Value to search.
            flags: Type of value to search.
            findOptions: Way to search.

        Returns:
            All found cells, or Null if value was not found.

        """
        enumflags:c_int = flags.value
        enumfindOptions:c_int = findOptions.value

        GetDllLibXls().Worksheet_FindAll.argtypes=[c_void_p ,c_void_p,c_int,c_int]
        GetDllLibXls().Worksheet_FindAll.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_FindAll, self.Ptr, findValue,enumflags,enumfindOptions)
        ret = None if intPtr==None else ListCellRanges(intPtr)
        return ret



    def FindAllNumber(self ,doubleValue:float,formulaValue:bool)->'ListCellRanges':
        """
        Finds the cell with the input number.

        Args:
            doubleValue: Double value to search for.
            formulaValue: Indicates if includes formula value.

        Returns:
            Found ranges.

        """
        
        GetDllLibXls().Worksheet_FindAllNumber.argtypes=[c_void_p ,c_double,c_bool]
        GetDllLibXls().Worksheet_FindAllNumber.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_FindAllNumber, self.Ptr, doubleValue,formulaValue)
        ret = None if intPtr==None else ListCellRanges(intPtr)
        return ret


    @dispatch
    def FindAllString(self ,stringValue:str,formula:bool,formulaValue:bool)->ListCellRanges:
        """
        Finds the cell with the input string.

        Args:
            stringValue: String value to search for.
            formula: Indicates if includes formula.
            formulaValue: Indicates if includes formula value.

        Returns:
            Found ranges.

        """
        
        GetDllLibXls().Worksheet_FindAllString.argtypes=[c_void_p ,c_void_p,c_bool,c_bool]
        GetDllLibXls().Worksheet_FindAllString.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_FindAllString, self.Ptr, stringValue,formula,formulaValue)
        ret = None if intPtr==None else ListCellRanges(intPtr)
        return ret

    @dispatch
    def FindAllString(self ,stringValue:str,formula:bool,formulaValue:bool,igRegex:bool)->ListCellRanges:
        """
        Finds the cell with the input string.

        Args:
            stringValue: String value to search for.
            formula: Indicates if includes formula.
            formulaValue: Indicates if includes formula value.
            isRegex: Indicates if stringValue param is regex.

        Returns:
            Found ranges.

        """
        
        GetDllLibXls().Worksheet_FindAllStringSFFI.argtypes=[c_void_p ,c_void_p,c_bool,c_bool,c_bool]
        GetDllLibXls().Worksheet_FindAllStringSFFI.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_FindAllStringSFFI, self.Ptr, stringValue,formula,formulaValue,igRegex)
        ret = None if intPtr==None else ListCellRanges(intPtr)
        return ret

    def FindAllDateTime(self ,dateTimeValue:'DateTime')->'ListCellRanges':
        """
        Finds the cell with the input date time.

        Args:
            dateTimeValue: Datetime value to search for.

        Returns:
            Found ranges.

        """
        intPtrdateTimeValue:c_void_p = dateTimeValue.Ptr

        GetDllLibXls().Worksheet_FindAllDateTime.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().Worksheet_FindAllDateTime.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_FindAllDateTime, self.Ptr, intPtrdateTimeValue)
        ret = None if intPtr==None else ListCellRanges(intPtr)
        return ret



    def FindAllTimeSpan(self ,timeSpanValue:'TimeSpan')->'ListCellRanges':
        """
        Finds the cell with the input time span.

        Args:
            timeSpanValue: Time span value to search for.

        Returns:
            Found ranges.

        """
        intPtrtimeSpanValue:c_void_p = timeSpanValue.Ptr

        GetDllLibXls().Worksheet_FindAllTimeSpan.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().Worksheet_FindAllTimeSpan.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_FindAllTimeSpan, self.Ptr, intPtrtimeSpanValue)
        ret = None if intPtr==None else ListCellRanges(intPtr)
        return ret



    def FindAllBool(self ,boolValue:bool)->'ListCellRanges':
        """
        Finds the cell with the input bool.

        Args:
            boolValue: Bool value to search for.

        Returns:
            Found ranges.

        """
        
        GetDllLibXls().Worksheet_FindAllBool.argtypes=[c_void_p ,c_bool]
        GetDllLibXls().Worksheet_FindAllBool.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_FindAllBool, self.Ptr, boolValue)
        ret = None if intPtr==None else ListCellRanges(intPtr)
        return ret



    def FindBool(self ,boolValue:bool)->'CellRange':
        """
        Finds the cell with the input bool.

        Args:
            boolValue: Bool value to search for.

        Returns:
            Found range.

        """
        
        GetDllLibXls().Worksheet_FindBool.argtypes=[c_void_p ,c_bool]
        GetDllLibXls().Worksheet_FindBool.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_FindBool, self.Ptr, boolValue)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret



    def FindNumber(self ,doubleValue:float,formulaValue:bool)->'CellRange':
        """
        Finds the cell with the input double.

        Args:
            doubleValue: Double value to search for.
            formulaValue: Indicates if includes formula value.

        Returns:
            Found range.

        """
        
        GetDllLibXls().Worksheet_FindNumber.argtypes=[c_void_p ,c_double,c_bool]
        GetDllLibXls().Worksheet_FindNumber.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_FindNumber, self.Ptr, doubleValue,formulaValue)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret



    def FindString(self ,stringValue:str,formula:bool,formulaValue:bool)->'CellRange':
        """
        Finds the cell with the input string.

        Args:
            stringValue: String value to search for.
            formula: Indicates whether includes formula.
            formulaValue: Indicates whether includes formula value.

        Returns:
            Found range.

        """
        
        GetDllLibXls().Worksheet_FindString.argtypes=[c_void_p ,c_void_p,c_bool,c_bool]
        GetDllLibXls().Worksheet_FindString.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_FindString, self.Ptr, stringValue,formula,formulaValue)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret



    def FindDateTime(self ,dateTimeValue:'DateTime')->'CellRange':
        """
        Finds the cell with the input date time.

        Args:
            dateTimeValue: DateTime value to search for.

        Returns:
            Found range.

        """
        intPtrdateTimeValue:c_void_p = dateTimeValue.Ptr

        GetDllLibXls().Worksheet_FindDateTime.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().Worksheet_FindDateTime.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_FindDateTime, self.Ptr, intPtrdateTimeValue)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret



    def FindTimeSpan(self ,timeSpanValue:'TimeSpan')->'CellRange':
        """
        Finds the cell with the input time span.

        Args:
            timeSpanValue: Time span value to search for.

        Returns:
            Found range.

        """
        intPtrtimeSpanValue:c_void_p = timeSpanValue.Ptr

        GetDllLibXls().Worksheet_FindTimeSpan.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().Worksheet_FindTimeSpan.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_FindTimeSpan, self.Ptr, intPtrtimeSpanValue)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret



    def CopyFrom(self ,worksheet:'Worksheet'):
        """
        Copy data from specified worksheet.

        Args:
            worksheet: worksheet object

        """
        intPtrworksheet:c_void_p = worksheet.Ptr

        GetDllLibXls().Worksheet_CopyFrom.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().Worksheet_CopyFrom, self.Ptr, intPtrworksheet)

    @dispatch

    def Copy(self ,sourceRange:CellRange,destRange:CellRange):
        """
        Copys data from a source range to a destination range.

        Args:
            sourceRange: Source range.
            destRange: Destination range.

        """
        intPtrsourceRange:c_void_p = sourceRange.Ptr
        intPtrdestRange:c_void_p = destRange.Ptr

        GetDllLibXls().Worksheet_Copy.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().Worksheet_Copy, self.Ptr, intPtrsourceRange,intPtrdestRange)

    @dispatch

    def Copy(self ,sourceRange:CellRange,destRange:CellRange,copyStyle:bool):
        """
        Copys data from a source range to a destination range.

        Args:
            sourceRange: Source range.
            destRange: Destination range.
            copyStyle: Indicates whether copys styles.

        """
        intPtrsourceRange:c_void_p = sourceRange.Ptr
        intPtrdestRange:c_void_p = destRange.Ptr

        GetDllLibXls().Worksheet_CopySDC.argtypes=[c_void_p ,c_void_p,c_void_p,c_bool]
        CallCFunction(GetDllLibXls().Worksheet_CopySDC, self.Ptr, intPtrsourceRange,intPtrdestRange,copyStyle)

    @dispatch
    def Copy(self ,sourceRange:CellRange,destRange:CellRange,copyStyle:bool,updateReference:bool,ignoreSize:bool):
        """
        Copys data from a source range to a destination range.

        Args:
            sourceRange: Source range.
            destRange: Destination range
            copyStyle: Indicates whether copy styles.
            updateReference: Indicates whether update reference ranges.
            ignoreSize: Indicates whether check range sizes.

        """
        intPtrsourceRange:c_void_p = sourceRange.Ptr
        intPtrdestRange:c_void_p = destRange.Ptr

        GetDllLibXls().Worksheet_CopySDCUI.argtypes=[c_void_p ,c_void_p,c_void_p,c_bool,c_bool,c_bool]
        CallCFunction(GetDllLibXls().Worksheet_CopySDCUI, self.Ptr, intPtrsourceRange,intPtrdestRange,copyStyle,updateReference,ignoreSize)

    @dispatch

    def Copy(self ,sourceRange:CellRange,worksheet:'Worksheet',destRow:int,destColumn:int):
        """
        Copy data from source range to destination worksheet.

        Args:
            sourceRange: Source range.
            worksheet: Destination worksheet
            destRow: Row index of destination worksheet.
            destColumn: Column index of destination worksheet.

        """
        intPtrsourceRange:c_void_p = sourceRange.Ptr
        intPtrworksheet:c_void_p = worksheet.Ptr

        GetDllLibXls().Worksheet_CopySWDD.argtypes=[c_void_p ,c_void_p,c_void_p,c_int,c_int]
        CallCFunction(GetDllLibXls().Worksheet_CopySWDD, self.Ptr, intPtrsourceRange,intPtrworksheet,destRow,destColumn)

    @dispatch

    def Copy(self ,sourceRange:CellRange,worksheet:'Worksheet',destRow:int,destColumn:int,copyStyle:bool):
        """
        Copy data from source range to destination worksheet.

        Args:
            sourceRange: Source range
            worksheet: Destination worksheet.
            destRow: Row index of destination worksheet.
            destColumn: Column index of destination worksheet.
            copyStyle: Indicates whehter copy styles.

        """
        intPtrsourceRange:c_void_p = sourceRange.Ptr
        intPtrworksheet:c_void_p = worksheet.Ptr

        GetDllLibXls().Worksheet_CopySWDDC.argtypes=[c_void_p ,c_void_p,c_void_p,c_int,c_int,c_bool]
        CallCFunction(GetDllLibXls().Worksheet_CopySWDDC, self.Ptr, intPtrsourceRange,intPtrworksheet,destRow,destColumn,copyStyle)

    @dispatch

    def Copy(self ,sourceRange:CellRange,worksheet:'Worksheet',destRow:int,destColumn:int,copyStyle:bool,updateRerence:bool):
        """
        Copy data from source range to destination worksheet.

        Args:
            sourceRange: Source range
            worksheet: Destination worksheet.
            destRow: Row index of destination worksheet.
            destColumn: Column index of destination worksheet.
            copyStyle: Indicates whehter copy styles.
            updateRerence: Indicates whether update reference range.

        """
        intPtrsourceRange:c_void_p = sourceRange.Ptr
        intPtrworksheet:c_void_p = worksheet.Ptr

        GetDllLibXls().Worksheet_CopySWDDCU.argtypes=[c_void_p ,c_void_p,c_void_p,c_int,c_int,c_bool,c_bool]
        CallCFunction(GetDllLibXls().Worksheet_CopySWDDCU, self.Ptr, intPtrsourceRange,intPtrworksheet,destRow,destColumn,copyStyle,updateRerence)

    @dispatch

    def Copy(self ,sourceRange:CellRange,destRange:CellRange,copyStyle:bool,updateReference:bool,ignoreSize:bool,copyShape:bool):
        """
        Copys data from a source range to a destination range.

        Args:
            sourceRange: Source range.
            destRange: Destination range
            copyStyle: Indicates whether copy styles.
            updateReference: Indicates whether update reference ranges.
            ignoreSize: Indicates whether check range sizes.
            copyShape: Indicates whether copy shape.

        """
        intPtrsourceRange:c_void_p = sourceRange.Ptr
        intPtrdestRange:c_void_p = destRange.Ptr

        GetDllLibXls().Worksheet_CopySDCUIC.argtypes=[c_void_p ,c_void_p,c_void_p,c_bool,c_bool,c_bool,c_bool]
        CallCFunction(GetDllLibXls().Worksheet_CopySDCUIC, self.Ptr, intPtrsourceRange,intPtrdestRange,copyStyle,updateReference,ignoreSize,copyShape)

    @dispatch

    def Copy(self ,sourceRange:CellRange,destRange:CellRange,copyOptions:CopyRangeOptions):
        """
        Copys data from a source range to a destination range.

        Args:
            sourceRange: Source range.
            destRange: Destination range
            copyOptions: Copy options.

        """
        intPtrsourceRange:c_void_p = sourceRange.Ptr
        intPtrdestRange:c_void_p = destRange.Ptr
        enumcopyOptions:c_int = copyOptions.value

        GetDllLibXls().Worksheet_CopySDC1.argtypes=[c_void_p ,c_void_p,c_void_p,c_int]
        CallCFunction(GetDllLibXls().Worksheet_CopySDC1, self.Ptr, intPtrsourceRange,intPtrdestRange,enumcopyOptions)


    def CopyRow(self ,sourceRow:'CellRange',destSheet:'Worksheet',destRowIndex:int,copyOptions:'CopyRangeOptions'):
        """
        Copys data from a source row to a destination row.

        Args:
            sourceRow: Source row.
            destSheet: Destination sheet
            destRowIndex: Destination row index
            copyOptions: Copy options.

        """
        intPtrsourceRow:c_void_p = sourceRow.Ptr
        intPtrdestSheet:c_void_p = destSheet.Ptr
        enumcopyOptions:c_int = copyOptions.value

        GetDllLibXls().Worksheet_CopyRow.argtypes=[c_void_p ,c_void_p,c_void_p,c_int,c_int]
        CallCFunction(GetDllLibXls().Worksheet_CopyRow, self.Ptr, intPtrsourceRow,intPtrdestSheet,destRowIndex,enumcopyOptions)


    def CopyColumn(self ,sourceColumn:'CellRange',destSheet:'Worksheet',destColIndex:int,copyOptions:'CopyRangeOptions'):
        """
        Copys data from a source column to a destination column.

        Args:
            sourceColumn: Source column.
            destSheet: Destination sheet
            destColIndex: Destination column index
            copyOptions: Copy options.

        """
        intPtrsourceColumn:c_void_p = sourceColumn.Ptr
        intPtrdestSheet:c_void_p = destSheet.Ptr
        enumcopyOptions:c_int = copyOptions.value

        GetDllLibXls().Worksheet_CopyColumn.argtypes=[c_void_p ,c_void_p,c_void_p,c_int,c_int]
        CallCFunction(GetDllLibXls().Worksheet_CopyColumn, self.Ptr, intPtrsourceColumn,intPtrdestSheet,destColIndex,enumcopyOptions)

    @dispatch

    def Move(self ,sourceRange:CellRange,destRange:CellRange):
        """
        Move data from source range to destination range.

        Args:
            sourceRange: Source range.
            destRange: Destination range.

        """
        intPtrsourceRange:c_void_p = sourceRange.Ptr
        intPtrdestRange:c_void_p = destRange.Ptr

        GetDllLibXls().Worksheet_Move.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().Worksheet_Move, self.Ptr, intPtrsourceRange,intPtrdestRange)

    @dispatch

    def Move(self ,sourceRange:CellRange,destRange:CellRange,updateReference:bool,copyStyle:bool):
        """

        """
        intPtrsourceRange:c_void_p = sourceRange.Ptr
        intPtrdestRange:c_void_p = destRange.Ptr

        GetDllLibXls().Worksheet_MoveSDUC.argtypes=[c_void_p ,c_void_p,c_void_p,c_bool,c_bool]
        CallCFunction(GetDllLibXls().Worksheet_MoveSDUC, self.Ptr, intPtrsourceRange,intPtrdestRange,updateReference,copyStyle)

#    @dispatch
#
#    def ExportDataTable(self ,range:CellRange,exportColumnNames:bool)->DataTable:
#        """
#    <summary>
#        Exports worksheet data into a DataTable.
#    </summary>
#    <param name="range">Range to export.</param>
#    <param name="exportColumnNames">Indicates if export column name.</param>
#    <returns>exported datatable</returns>
#        """
#        intPtrrange:c_void_p = range.Ptr
#
#        GetDllLibXls().Worksheet_ExportDataTable.argtypes=[c_void_p ,c_void_p,c_bool]
#        GetDllLibXls().Worksheet_ExportDataTable.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().Worksheet_ExportDataTable, self.Ptr, intPtrrange,exportColumnNames)
#        ret = None if intPtr==None else DataTable(intPtr)
#        return ret
#


#    @dispatch
#
#    def ExportDataTable(self ,range:CellRange,options:ExportTableOptions)->DataTable:
#        """
#
#        """
#        intPtrrange:c_void_p = range.Ptr
#        intPtroptions:c_void_p = options.Ptr
#
#        GetDllLibXls().Worksheet_ExportDataTableRO.argtypes=[c_void_p ,c_void_p,c_void_p]
#        GetDllLibXls().Worksheet_ExportDataTableRO.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().Worksheet_ExportDataTableRO, self.Ptr, intPtrrange,intPtroptions)
#        ret = None if intPtr==None else DataTable(intPtr)
#        return ret
#


#    @dispatch
#
#    def ExportDataTable(self ,firstRow:int,firstColumn:int,maxRows:int,maxColumns:int,options:ExportTableOptions)->DataTable:
#        """
#
#        """
#        intPtroptions:c_void_p = options.Ptr
#
#        GetDllLibXls().Worksheet_ExportDataTableFFMMO.argtypes=[c_void_p ,c_int,c_int,c_int,c_int,c_void_p]
#        GetDllLibXls().Worksheet_ExportDataTableFFMMO.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().Worksheet_ExportDataTableFFMMO, self.Ptr, firstRow,firstColumn,maxRows,maxColumns,intPtroptions)
#        ret = None if intPtr==None else DataTable(intPtr)
#        return ret
#


#    @dispatch
#
#    def ExportDataTable(self ,range:CellRange,exportColumnNames:bool,computedFormulaValue:bool)->DataTable:
#        """
#    <summary>
#        Exports worksheet data into a DataTable.
#    </summary>
#    <param name="range">Range to export.</param>
#    <param name="exportColumnNames">Indicates if export column name.</param>
#    <param name="computedFormulaValue">Indicates wheter compute formula value.</param>
#    <returns>exported datatable</returns>
#        """
#        intPtrrange:c_void_p = range.Ptr
#
#        GetDllLibXls().Worksheet_ExportDataTableREC.argtypes=[c_void_p ,c_void_p,c_bool,c_bool]
#        GetDllLibXls().Worksheet_ExportDataTableREC.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().Worksheet_ExportDataTableREC, self.Ptr, intPtrrange,exportColumnNames,computedFormulaValue)
#        ret = None if intPtr==None else DataTable(intPtr)
#        return ret
#


#    @dispatch
#
#    def ExportDataTable(self ,firstRow:int,firstColumn:int,maxRows:int,maxColumns:int,exportColumnNames:bool)->DataTable:
#        """
#    <summary>
#        Exports worksheet data into a DataTable
#    </summary>
#    <param name="firstRow">Row of first cell.</param>
#    <param name="firstColumn">Column of first cell.</param>
#    <param name="maxRows">Maximun rows to export.</param>
#    <param name="maxColumns">Maximun columns to export.</param>
#    <param name="exportColumnNames">Indicates if export column name.</param>
#    <returns>Exported datatable.</returns>
#        """
#        
#        GetDllLibXls().Worksheet_ExportDataTableFFMME.argtypes=[c_void_p ,c_int,c_int,c_int,c_int,c_bool]
#        GetDllLibXls().Worksheet_ExportDataTableFFMME.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().Worksheet_ExportDataTableFFMME, self.Ptr, firstRow,firstColumn,maxRows,maxColumns,exportColumnNames)
#        ret = None if intPtr==None else DataTable(intPtr)
#        return ret
#



    def GetIntersectRanges(self ,range1:'CellRange',range2:'CellRange')->'CellRange':
        """
        Intersects two ranges.

        Args:
            range1: First range.
            range2: Second range.

        Returns:
            Intersection of two ranges

        """
        intPtrrange1:c_void_p = range1.Ptr
        intPtrrange2:c_void_p = range2.Ptr

        GetDllLibXls().Worksheet_GetIntersectRanges.argtypes=[c_void_p ,c_void_p,c_void_p]
        GetDllLibXls().Worksheet_GetIntersectRanges.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_GetIntersectRanges, self.Ptr, intPtrrange1,intPtrrange2)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    #@property

    #def GroupShapeCollection(self)->'GroupShapeCollection':
    #    """
    #<summary>
    #    Get group shapes in worksheet.
    #</summary>
    #    """
    #    GetDllLibXls().Worksheet_get_GroupShapeCollection.argtypes=[c_void_p]
    #    GetDllLibXls().Worksheet_get_GroupShapeCollection.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibXls().Worksheet_get_GroupShapeCollection, self.Ptr)
    #    ret = None if intPtr==None else GroupShapeCollection(intPtr)
    #    return ret



    def Merge(self ,range1:'CellRange',range2:'CellRange')->'CellRange':
        """
        Combines a range of cells into a single cell.

        Args:
            range1: First range.
            range2: Second range.

        Returns:
            Merged ranges

        """
        intPtrrange1:c_void_p = range1.Ptr
        intPtrrange2:c_void_p = range2.Ptr

        GetDllLibXls().Worksheet_Merge.argtypes=[c_void_p ,c_void_p,c_void_p]
        GetDllLibXls().Worksheet_Merge.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_Merge, self.Ptr, intPtrrange1,intPtrrange2)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @dispatch

    def SetDefaultColumnStyle(self ,columnIndex:int,defaultStyle:CellStyle):
        """
        Sets default style for column.

        Args:
            columnIndex: Column index.
            defaultStyle: Default style.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Create style
            style = workbook.Styles.Add("CustomStyle")
            #Set Color
            style.Color = Color.Red
            #Set default style
            worksheet.SetDefaultColumnStyle(2, style)
            #Save to file
            workbook.SaveToFile("SetDefaultColumnStyle.xlsx")

        """
        intPtrdefaultStyle:c_void_p = defaultStyle.Ptr

        GetDllLibXls().Worksheet_SetDefaultColumnStyle.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibXls().Worksheet_SetDefaultColumnStyle, self.Ptr, columnIndex,intPtrdefaultStyle)

    @dispatch

    def SetDefaultColumnStyle(self ,firstColumnIndex:int,lastColumnIndex:int,defaultStyle:CellStyle):
        """
        Sets default style for column.

        Args:
            firstColumnIndex: First column index.
            lastColumnIndex: Last column index.
            defaultStyle: Default style.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Create style
            style = workbook.Styles.Add("CustomStyle")
            #Set Color
            style.Color = Color.Red
            #Set default style
            worksheet.SetDefaultColumnStyle(2, 5, style)
            #Save to file
            workbook.SaveToFile("SetDefaultColumnStyle.xlsx")

        """
        intPtrdefaultStyle:c_void_p = defaultStyle.Ptr

        GetDllLibXls().Worksheet_SetDefaultColumnStyleFLD.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().Worksheet_SetDefaultColumnStyleFLD, self.Ptr, firstColumnIndex,lastColumnIndex,intPtrdefaultStyle)

    @dispatch

    def SetDefaultRowStyle(self ,rowIndex:int,defaultStyle:CellStyle):
        """
        Sets default style for row.

        Args:
            rowIndex: Row index.
            defaultStyle: Default style.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Create style
            style = workbook.Styles.Add("CustomStyle")
            #Set Color
            style.Color = Color.Red
            #Set default style
            worksheet.SetDefaultRowStyle(2, style)
            #Save to file
            workbook.SaveToFile("SetDefaultRowStyle.xlsx")

        """
        intPtrdefaultStyle:c_void_p = defaultStyle.Ptr

        GetDllLibXls().Worksheet_SetDefaultRowStyle.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibXls().Worksheet_SetDefaultRowStyle, self.Ptr, rowIndex,intPtrdefaultStyle)

    @dispatch

    def SetDefaultRowStyle(self ,firstRowIndex:int,lastRowIndex:int,defaultStyle:CellStyle):
        """
        Sets default style for row.

        Args:
            firstRowIndex: First row index.
            lastRowIndex: Last row index.
            defaultStyle: Default style.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Create style
            style = workbook.Styles.Add("CustomStyle")
            #Set Color
            style.Color = Color.Red
            #Set default style
            worksheet.SetDefaultRowStyle(2, 5, style)
            #Save to file
            workbook.SaveToFile("SetDefaultRowStyle.xlsx")

        """
        intPtrdefaultStyle:c_void_p = defaultStyle.Ptr

        GetDllLibXls().Worksheet_SetDefaultRowStyleFLD.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().Worksheet_SetDefaultRowStyleFLD, self.Ptr, firstRowIndex,lastRowIndex,intPtrdefaultStyle)


    def GetDefaultColumnStyle(self ,columnIndex:int)->'CellStyle':
        """
        Returns default column style.

        Args:
            columnIndex: Column index.

        Returns:
            Default column style or null if default style is not exists.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Create style
            style = workbook.Styles.Add("CustomStyle")
            #Set Color
            style.Color = Color.Red
            #Set default style
            worksheet.SetDefaultColumnStyle(2,style)
            #Get default style
            defaultStyle = worksheet.GetDefaultColumnStyle(2)
            #Set color
            defaultStyle.Color = Color.Blue
            worksheet.SetDefaultColumnStyle(3, defaultStyle)
            #Save to file
            workbook.SaveToFile("GetDefaultColumnStyle.xlsx")

        """
        
        GetDllLibXls().Worksheet_GetDefaultColumnStyle.argtypes=[c_void_p ,c_int]
        GetDllLibXls().Worksheet_GetDefaultColumnStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_GetDefaultColumnStyle, self.Ptr, columnIndex)
        ret = None if intPtr==None else CellStyle(intPtr)
        return ret



    def GetDefaultRowStyle(self ,rowIndex:int)->'CellStyle':
        """
        Returns default row style.

        Args:
            rowIndex: Row index.

        Returns:
            Default row style or null if default style is not set.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Create style
            style = workbook.Styles.Add("CustomStyle")
            #Set Color
            style.Color = Color.Red
            #Set default style
            worksheet.SetDefaultRowStyle(2,style)
            #Get default style
            defaultStyle = worksheet.GetDefaultRowStyle(2)
            #Set color
            defaultStyle.Color = Color.Blue
            worksheet.SetDefaultRowStyle(3, defaultStyle)
            #Save to file
            workbook.SaveToFile("GetDefaultColumnStyle.xlsx")

        """
        
        GetDllLibXls().Worksheet_GetDefaultRowStyle.argtypes=[c_void_p ,c_int]
        GetDllLibXls().Worksheet_GetDefaultRowStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_GetDefaultRowStyle, self.Ptr, rowIndex)
        ret = None if intPtr==None else CellStyle(intPtr)
        return ret



    def RemoveMergedCells(self ,range:'CellRange'):
        """

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().Worksheet_RemoveMergedCells.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().Worksheet_RemoveMergedCells, self.Ptr, intPtrrange)

    @dispatch

    def RemoveRange(self ,range:CellRange):
        """
        Removes range from list.

        Args:
            range: Specified range.

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().Worksheet_RemoveRange.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().Worksheet_RemoveRange, self.Ptr, intPtrrange)

    @dispatch

    def RemoveRange(self ,rowIndex:int,columnIndex:int):
        """
        Removes range from list.

        Args:
            rowIndex: Row index.
            columnIndex: Column index.

        """
        
        GetDllLibXls().Worksheet_RemoveRangeRC.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().Worksheet_RemoveRangeRC, self.Ptr, rowIndex,columnIndex)

    @dispatch

    def RemovePicture(self ,index:int):
        """
        Remove picture from this worksheet.

        Args:
            index: Picture ID

        """
        
        GetDllLibXls().Worksheet_RemovePicture.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().Worksheet_RemovePicture, self.Ptr, index)

    @dispatch

    def RemovePicture(self ,picturename:str):
        """
        Remove picture from this worksheet.

        Args:
            picturename: Picture name

        """
        
        GetDllLibXls().Worksheet_RemovePictureP.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().Worksheet_RemovePictureP, self.Ptr, picturename)

    @dispatch

    def RemovePicture(self ,picture:IPictureShape):
        """
        Remove picture from this worksheet.

        Args:
            picture: A pictureshape

        """
        intPtrpicture:c_void_p = picture.Ptr

        GetDllLibXls().Worksheet_RemovePictureP.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().Worksheet_RemovePictureP, self.Ptr, intPtrpicture)


    def ApplyStyle(self ,style:'CellStyle'):
        """
        Apply style to whole sheet.

        Args:
            style: style to apply

        """
        intPtrstyle:c_void_p = style.Ptr

        GetDllLibXls().Worksheet_ApplyStyle.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().Worksheet_ApplyStyle, self.Ptr, intPtrstyle)


    def FreezePanes(self ,rowIndex:int,columnIndex:int):
        """
        Freezes panes at the specified cell in the worksheet.

        Args:
            rowIndex: Row index.
            columnIndex: Column index.

        """
        
        GetDllLibXls().Worksheet_FreezePanes.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().Worksheet_FreezePanes, self.Ptr, rowIndex,columnIndex)


    def GetFreezePanes(self )->List[int]:
        """

        """
        GetDllLibXls().Worksheet_GetFreezePanes.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_GetFreezePanes.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().Worksheet_GetFreezePanes, self.Ptr)
        ret =[]
        ret.append(intPtrArray.data[0])
        ret.append(intPtrArray.data[2])
        return ret


    def SetActiveCell(self ,range:'CellRange'):
        """
        Sets active cell

        Args:
            range: Cell to activate.

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().Worksheet_SetActiveCell.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().Worksheet_SetActiveCell, self.Ptr, intPtrrange)

    @property

    def Cells(self)->'ListCellRanges':
        """
        Returns all used cells in the worksheet. Read-only.

        """
        GetDllLibXls().Worksheet_get_Cells.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_Cells.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_Cells, self.Ptr)
        ret = None if intPtr==None else ListCellRanges(intPtr)
        return ret


    @property

    def Columns(self)->'ListCellRanges':
        """
        Rrepresents all used columns on the specified worksheet. Read-only Range object.

        """
        GetDllLibXls().Worksheet_get_Columns.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_Columns.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_Columns, self.Ptr)
        ret = None if intPtr==None else ListCellRanges(intPtr)
        return ret


    @property

    def PageSetup(self)->'PageSetup':
        """
        Returns a PageSetup object that contains all the page setup settings for the specified object. Read-only.

        """
        GetDllLibXls().Worksheet_get_PageSetup.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_PageSetup.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_PageSetup, self.Ptr)
        ret = None if intPtr==None else PageSetup(intPtr)
        return ret


    @property

    def AutoFilters(self)->'AutoFiltersCollection':
        """

        """
        GetDllLibXls().Worksheet_get_AutoFilters.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_AutoFilters.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_AutoFilters, self.Ptr)
        ret = None if intPtr==None else AutoFiltersCollection(intPtr)
        return ret


    @property

    def Charts(self)->'WorksheetChartsCollection':
        """
        Returns charts collection. Read-only.

        """
        GetDllLibXls().Worksheet_get_Charts.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_Charts.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_Charts, self.Ptr)
        ret = None if intPtr==None else WorksheetChartsCollection(intPtr)
        return ret


    @property

    def QueryTables(self)->'QueryTableCollection':
        """

        """
        GetDllLibXls().Worksheet_get_QueryTables.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_QueryTables.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_QueryTables, self.Ptr)
        ret = None if intPtr==None else QueryTableCollection(intPtr)
        return ret


    @property

    def Comments(self)->'CommentsCollection':
        """
        Returns comments collection for this worksheet. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Adding comments to a cell.
            comment1 = worksheet.Range["A1"].AddComment()
            comment2 = worksheet.Range["B1"].AddComment()
            #Set comment text
            comment1.Text = "Comment1"
            comment2.Text = "Comment2"
            #Check count
            Console.Write(worksheet.Comments.Count)
            #Save to file
            workbook.SaveToFile("Comments.xlsx")

        """
        GetDllLibXls().Worksheet_get_Comments.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_Comments.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_Comments, self.Ptr)
        ret = None if intPtr==None else CommentsCollection(intPtr)
        return ret


    @property

    def HPageBreaks(self)->'HPageBreaksCollection':
        """
        Returns an HPageBreaks collection that represents the horizontal page breaks on the sheet.

        """
        GetDllLibXls().Worksheet_get_HPageBreaks.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_HPageBreaks.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_HPageBreaks, self.Ptr)
        ret = None if intPtr==None else HPageBreaksCollection(intPtr)
        return ret


    @property

    def HyperLinks(self)->'HyperLinksCollection':
        """
        Collection of all worksheet's hyperlinks.

        """
        GetDllLibXls().Worksheet_get_HyperLinks.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_HyperLinks.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_HyperLinks, self.Ptr)
        ret = None if intPtr==None else HyperLinksCollection(intPtr)
        return ret


    @property

    def Pictures(self)->'PicturesCollection':
        """
        Pictures collection. Read-only.

        """
        GetDllLibXls().Worksheet_get_Pictures.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_Pictures.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_Pictures, self.Ptr)
        ret = None if intPtr==None else PicturesCollection(intPtr)
        return ret


    @property

    def PrintRange(self)->'CellRange':
        """
        Print area of worksheet.

        """
        GetDllLibXls().Worksheet_get_PrintRange.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_PrintRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_PrintRange, self.Ptr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @property

    def VPageBreaks(self)->'VPageBreaksCollection':
        """
        Returns a VPageBreaks collection that represents the vertical page breaks on the sheet. Read-only.

        """
        GetDllLibXls().Worksheet_get_VPageBreaks.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_VPageBreaks.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_VPageBreaks, self.Ptr)
        ret = None if intPtr==None else VPageBreaksCollection(intPtr)
        return ret


    @property

    def Range(self)->'CellRange':
        """
        Returns a Range object that represents the used range on the specified worksheet. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["B2"].Text = "Text"
            #Set Color
            worksheet["J3"].Style.Color = Color.Red
            #Get used range . Output will be B2:J3
            Console.Write(worksheet.Range.RangeAddressLocal)
            #Save to file
            workbook.SaveToFile("UsedRange.xlsx")

        """
        GetDllLibXls().Worksheet_get_Range.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_Range.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_Range, self.Ptr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret



    def CalculateAndGetRowHeight(self ,rowIndex:int)->float:
        """

        """
        
        GetDllLibXls().Worksheet_CalculateAndGetRowHeight.argtypes=[c_void_p ,c_int]
        GetDllLibXls().Worksheet_CalculateAndGetRowHeight.restype=c_double
        ret = CallCFunction(GetDllLibXls().Worksheet_CalculateAndGetRowHeight, self.Ptr, rowIndex)
        return ret

    @property

    def Rows(self)->'ListCellRanges':
        """
        Represents all the rows on the specified worksheet. Read-only Range object.

        """
        GetDllLibXls().Worksheet_get_Rows.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_Rows.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_Rows, self.Ptr)
        ret = None if intPtr==None else ListCellRanges(intPtr)
        return ret


    @property

    def Workbook(self)->'Workbook':
        """

        """
        GetDllLibXls().Worksheet_get_Workbook.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_Workbook.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_Workbook, self.Ptr)
        from spire.xls.Workbook import Workbook
        ret = None if intPtr==None else Workbook(intPtr)
        return ret


    @property

    def ParentWorkbook(self)->'Workbook':
        """

        """
        GetDllLibXls().Worksheet_get_ParentWorkbook.argtypes=[c_void_p]
        GetDllLibXls().Worksheet_get_ParentWorkbook.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().Worksheet_get_ParentWorkbook, self.Ptr)
        from spire.xls.Workbook import Workbook
        ret = None if intPtr==None else Workbook(intPtr)
        return ret


