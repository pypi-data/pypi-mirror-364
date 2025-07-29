from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsWorksheet (  XlsWorksheetBase, IInternalWorksheet) :
    """Represents a worksheet in an Excel workbook.
    
    This class provides properties and methods for manipulating worksheets in Excel,
    including cell operations, formatting, ranges, rows, columns, and other worksheet-specific
    functionality. It extends XlsWorksheetBase and implements the IInternalWorksheet interface.
    """
    def GetActiveSelectionRange(self)->List['CellRange']:
        """Gets the currently selected ranges in the worksheet.
        
        Returns:
            List[CellRange]: A list of CellRange objects representing the selected ranges.
        """
        GetDllLibXls().XlsWorksheet_get_ActiveSelectionRange.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_ActiveSelectionRange.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().XlsWorksheet_get_ActiveSelectionRange, self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, CellRange)
        return ret


    def GroupByColumns(self ,firstColumn:int,lastColumn:int,isCollapsed:bool)->'CellRange':
        """Groups a range of columns in the worksheet.
        
        Args:
            firstColumn (int): The index of the first column to be grouped.
            lastColumn (int): The index of the last column to be grouped.
            isCollapsed (bool): Indicates whether the group should be collapsed initially.
            
        Returns:
            CellRange: A CellRange object representing the grouped columns.
        """
        
        GetDllLibXls().XlsWorksheet_GroupByColumns.argtypes=[c_void_p ,c_int,c_int,c_bool]
        GetDllLibXls().XlsWorksheet_GroupByColumns.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_GroupByColumns, self.Ptr, firstColumn,lastColumn,isCollapsed)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret



    def GroupByRows(self ,firstRow:int,lastRow:int,isCollapsed:bool)->'CellRange':
        """Groups a range of rows in the worksheet.
        
        Args:
            firstRow (int): The index of the first row to be grouped.
            lastRow (int): The index of the last row to be grouped.
            isCollapsed (bool): Indicates whether the group should be collapsed initially.
            
        Returns:
            CellRange: A CellRange object representing the grouped rows.
        """
        
        GetDllLibXls().XlsWorksheet_GroupByRows.argtypes=[c_void_p ,c_int,c_int,c_bool]
        GetDllLibXls().XlsWorksheet_GroupByRows.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_GroupByRows, self.Ptr, firstRow,lastRow,isCollapsed)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret



    def UngroupByColumns(self ,firstColumn:int,lastColumn:int)->'CellRange':
        """Ungroups a range of previously grouped columns in the worksheet.
        
        Args:
            firstColumn (int): The index of the first column to be ungrouped.
            lastColumn (int): The index of the last column to be ungrouped.
            
        Returns:
            CellRange: A CellRange object representing the ungrouped columns.
        """
        
        GetDllLibXls().XlsWorksheet_UngroupByColumns.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_UngroupByColumns.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_UngroupByColumns, self.Ptr, firstColumn,lastColumn)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret



    def UngroupByRows(self ,firstRow:int,lastRow:int)->'CellRange':
        """Ungroups a range of previously grouped rows in the worksheet.
        
        Args:
            firstRow (int): The index of the first row to be ungrouped.
            lastRow (int): The index of the last row to be ungrouped.
            
        Returns:
            CellRange: A CellRange object representing the ungrouped rows.
        """
        
        GetDllLibXls().XlsWorksheet_UngroupByRows.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_UngroupByRows.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_UngroupByRows, self.Ptr, firstRow,lastRow)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret



    def SaveShapesToImage(self ,option:'SaveShapeTypeOption')->List['Stream']:
        """Saves all shapes in the worksheet to images.
        
        This method converts all shapes in the worksheet to images according to the
        specified options.
        
        Args:
            option (SaveShapeTypeOption): The options for saving shapes as images, including
                format settings and other parameters.
                
        Returns:
            List[Stream]: A list of Stream objects containing the image data for each shape.
        """
        GetDllLibXls().XlsWorksheet_SaveShapesToImage.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsWorksheet_SaveShapesToImage.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().XlsWorksheet_SaveShapesToImage, self.Ptr,option.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, Stream)
        return ret



    @dispatch
    def ApplyStyle(self ,style:CellStyle):
        """Applies a cell style to the entire worksheet.
        
        This method applies the specified cell style to all cells in the worksheet.
        
        Args:
            style (CellStyle): The cell style to apply to the entire worksheet.
        """
        intPtrstyle:c_void_p = style.Ptr
        GetDllLibXls().XlsWorksheet_ApplyStyle.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_ApplyStyle, self.Ptr, intPtrstyle)

    @dispatch

    def ApplyStyle(self ,style:CellStyle,applyRowStyle:bool,applyColumnStyle:bool):
        """Applies a cell style to the worksheet with options for rows and columns.
        
        This method applies the specified cell style to the worksheet with options to
        control whether the style is applied to rows, columns, or both.
        
        Args:
            style (CellStyle): The cell style to apply.
            applyRowStyle (bool): True to apply the style to all rows; otherwise, False.
            applyColumnStyle (bool): True to apply the style to all columns; otherwise, False.
        """
        intPtrstyle:c_void_p = style.Ptr

        GetDllLibXls().XlsWorksheet_ApplyStyleSAA.argtypes=[c_void_p ,c_void_p,c_bool,c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_ApplyStyleSAA, self.Ptr, intPtrstyle,applyRowStyle,applyColumnStyle)

    @dispatch

    def Subtotal(self ,range:IXLSRange,groupByIndex:int,totalFields:List[int],subtotalType:SubtotalTypes):
        """Creates subtotals for the specified range.
        
        This method creates subtotals for the specified range using the given grouping field,
        total fields, and subtotal type.
        
        Args:
            range (IXLSRange): The range to create subtotals for.
            groupByIndex (int): The zero-based index of the field to group by.
            totalFields (List[int]): A list of zero-based field indices indicating the fields
                to which the subtotals are added.
            subtotalType (SubtotalTypes): The type of subtotal to calculate (e.g., sum, average, count).
        """
        intPtrrange:c_void_p = range.Ptr
        #arraytotalFields:ArrayTypetotalFields = ""
        counttotalFields = len(totalFields)
        ArrayTypetotalFields = c_int * counttotalFields
        arraytotalFields = ArrayTypetotalFields()
        for i in range(0, counttotalFields):
            arraytotalFields[i] = totalFields[i]

        enumsubtotalType:c_int = subtotalType.value

        GetDllLibXls().XlsWorksheet_Subtotal.argtypes=[c_void_p ,c_void_p,c_int,ArrayTypetotalFields,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_Subtotal, self.Ptr, intPtrrange,groupByIndex,arraytotalFields,counttotalFields,enumsubtotalType)

    @dispatch

    def Subtotal(self ,r:IXLSRange,groupByIndex:int,totalFields:List[int],subtotalType:SubtotalTypes,replace:bool,addPageBreak:bool,addsummaryBelowData:bool):
        """Creates subtotals for the specified range with additional options.
        
        This method creates subtotals for the specified range using the given grouping field,
        total fields, subtotal type, and additional formatting options.
        
        Args:
            r (IXLSRange): The range to create subtotals for.
            groupByIndex (int): The zero-based index of the field to group by.
            totalFields (List[int]): A list of zero-based field indices indicating the fields
                to which the subtotals are added.
            subtotalType (SubtotalTypes): The type of subtotal to calculate (e.g., sum, average, count).
            replace (bool): True to replace existing subtotals; otherwise, False.
            addPageBreak (bool): True to add page breaks between groups; otherwise, False.
            addsummaryBelowData (bool): True to add summary rows below the data; otherwise, False
                to add summary rows above the data.
        """
        intPtrrange:c_void_p = r.Ptr
        #arraytotalFields:ArrayTypetotalFields = ""
        counttotalFields = len(totalFields)
        ArrayTypetotalFields = c_int * counttotalFields
        arraytotalFields = ArrayTypetotalFields()
        for i in range(0, counttotalFields):
            arraytotalFields[i] = totalFields[i]

        enumsubtotalType:c_int = subtotalType.value

        GetDllLibXls().XlsWorksheet_SubtotalRGTSRAA.argtypes=[c_void_p ,c_void_p,c_int,ArrayTypetotalFields,c_int,c_int,c_bool,c_bool,c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_SubtotalRGTSRAA, self.Ptr, intPtrrange,groupByIndex,arraytotalFields,counttotalFields,enumsubtotalType,replace,addPageBreak,addsummaryBelowData)


    def GetRowIsAutoFit(self ,rowIndex:int)->bool:
        """
        Get GetRowIsAutoFit By rowIndex

        Args:
            rowIndex: 

        Returns:
            If the row is null Return false,else if the row height is Autofit Return true, the row height is CustomHeight Return false

        """
        
        GetDllLibXls().XlsWorksheet_GetRowIsAutoFit.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsWorksheet_GetRowIsAutoFit.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_GetRowIsAutoFit, self.Ptr, rowIndex)
        return ret


    def GetColumnIsAutoFit(self ,columnIndex:int)->bool:
        """
        Get ColumnIsAutofit By columnIndex

        Args:
            columnIndex: 

        Returns:
            If the column is null Return false,else if the column width is Autofit Return true, the column width is CustomWidth Return false

        """
        
        GetDllLibXls().XlsWorksheet_GetColumnIsAutoFit.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsWorksheet_GetColumnIsAutoFit.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_GetColumnIsAutoFit, self.Ptr, columnIndex)
        return ret


    def GetDefaultRowStyle(self ,rowIndex:int)->'IStyle':
        """
        Get the default row style for a given row index.

        Args:
            rowIndex (int): The row index.

        Returns:
            IStyle: The default style of the row.
        """
        GetDllLibXls().XlsWorksheet_GetDefaultRowStyle.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsWorksheet_GetDefaultRowStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_GetDefaultRowStyle, self.Ptr, rowIndex)
        ret = None if intPtr==None else CellStyle(intPtr)
        return ret



    def GetError(self ,row:int,column:int)->str:
        """
        Gets error value from cell.

        Args:
            row: Row index.
            column: Column index.

        Returns:
            Returns error value or null.

        """
        
        GetDllLibXls().XlsWorksheet_GetError.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_GetError.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorksheet_GetError, self.Ptr, row,column))
        return ret



    def GetFormulaErrorValue(self ,row:int,column:int)->str:
        """
        Gets formula error value from cell.

        Args:
            row: Row index.
            column: Column index.

        Returns:
            Returns error value or null.

        """
        
        GetDllLibXls().XlsWorksheet_GetFormulaErrorValue.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_GetFormulaErrorValue.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorksheet_GetFormulaErrorValue, self.Ptr, row,column))
        return ret



    def GetFormulaNumberValue(self ,row:int,column:int)->float:
        """
        Returns formula number value corresponding to the cell.

        Args:
            row: One-based row index of the cell to get value from.
            column: One-based column index of the cell to get value from.

        Returns:
            Number contained by the cell.

        """
        
        GetDllLibXls().XlsWorksheet_GetFormulaNumberValue.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_GetFormulaNumberValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_GetFormulaNumberValue, self.Ptr, row,column)
        return ret


    def GetFormulaStringValue(self ,row:int,column:int)->str:
        """
        Returns formula string value corresponding to the cell.

        Args:
            row: One-based row index of the cell to get value from.
            column: One-based column index of the cell to get value from.

        Returns:
            String contained by the cell.

        """
        
        GetDllLibXls().XlsWorksheet_GetFormulaStringValue.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_GetFormulaStringValue.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorksheet_GetFormulaStringValue, self.Ptr, row,column))
        return ret


    @dispatch

    def GetFormula(self ,row:int,column:int,bR1C1:bool)->str:
        """
        Get the formula from a cell.

        Args:
            row (int): Row index.
            column (int): Column index.
            bR1C1 (bool): Whether to use R1C1 notation.

        Returns:
            str: The formula string.
        """
        GetDllLibXls().XlsWorksheet_GetFormula.argtypes=[c_void_p ,c_int,c_int,c_bool]
        GetDllLibXls().XlsWorksheet_GetFormula.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorksheet_GetFormula, self.Ptr, row,column,bR1C1))
        return ret


    @dispatch

    def GetFormula(self ,row:int,column:int,bR1C1:bool,isForSerialization:bool)->str:
        """
        Get the formula from a cell, with serialization option.

        Args:
            row (int): Row index.
            column (int): Column index.
            bR1C1 (bool): Whether to use R1C1 notation.
            isForSerialization (bool): Whether for serialization.

        Returns:
            str: The formula string.
        """
        GetDllLibXls().XlsWorksheet_GetFormulaRCBI.argtypes=[c_void_p ,c_int,c_int,c_bool,c_bool]
        GetDllLibXls().XlsWorksheet_GetFormulaRCBI.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorksheet_GetFormulaRCBI, self.Ptr, row,column,bR1C1,isForSerialization))
        return ret



    def GetFormulaBoolValue(self ,row:int,column:int)->bool:
        """
        Gets formula bool value from cell.

        Args:
            row: Represents row index.
            column: Represents column index.

        Returns:
            Returns found bool value. If cannot found returns false.

        """
        
        GetDllLibXls().XlsWorksheet_GetFormulaBoolValue.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_GetFormulaBoolValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_GetFormulaBoolValue, self.Ptr, row,column)
        return ret


    def GetNumber(self ,row:int,column:int)->float:
        """
        Returns number value corresponding to the cell.

        Args:
            row: One-based row index of the cell to get value from.
            column: One-based column index of the cell to get value from.

        Returns:
            Number contained by the cell.

        """
        
        GetDllLibXls().XlsWorksheet_GetNumber.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_GetNumber.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_GetNumber, self.Ptr, row,column)
        return ret


    def GetRowHeight(self ,row:int)->float:
        """
        Gets the height of a specified row.

        Args:
            row: Row index.

        Returns:
            Height of row

        """
        
        GetDllLibXls().XlsWorksheet_GetRowHeight.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsWorksheet_GetRowHeight.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_GetRowHeight, self.Ptr, row)
        return ret


    def GetColumnIsHide(self ,columnIndex:int)->bool:
        """
        Indicates whether the column is hidden.

        Args:
            columnIndex: Column index.

        """
        
        GetDllLibXls().XlsWorksheet_GetColumnIsHide.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsWorksheet_GetColumnIsHide.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_GetColumnIsHide, self.Ptr, columnIndex)
        return ret


    def GetRowIsHide(self ,rowIndex:int)->bool:
        """
        Indicates whether the row is hidden.

        Args:
            rowIndex: Row index.

        """
        
        GetDllLibXls().XlsWorksheet_GetRowIsHide.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsWorksheet_GetRowIsHide.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_GetRowIsHide, self.Ptr, rowIndex)
        return ret


    def HideColumn(self ,columnIndex:int):
        """
        Hides a column.

        Args:
            columnIndex: Column index.

        """
        
        GetDllLibXls().XlsWorksheet_HideColumn.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_HideColumn, self.Ptr, columnIndex)


    def HideColumns(self ,columnIndex:int,columnCount:int):
        """
        Hides columns.

        Args:
            columnIndex: Column index.
            columnCount: Column count.

        """
        
        GetDllLibXls().XlsWorksheet_HideColumns.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_HideColumns, self.Ptr, columnIndex,columnCount)


    def HideRow(self ,rowIndex:int):
        """
        Hides a row.

        Args:
            rowIndex: Row index.

        """
        
        GetDllLibXls().XlsWorksheet_HideRow.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_HideRow, self.Ptr, rowIndex)


    def HideRows(self ,rowIndex:int,rowCount:int):
        """
        Hides a row.

        Args:
            rowIndex: Row index.
            rowCount: Row count.

        """
        
        GetDllLibXls().XlsWorksheet_HideRows.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_HideRows, self.Ptr, rowIndex,rowCount)


    def GetRowHeightPixels(self ,rowIndex:int)->int:
        """
        Gets the height of a specified row in unit of pixel.

        Args:
            rowIndex: Row index.

        Returns:
            Height of row
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["C2"].Text = "Sample text"
            #Set auto fit
            worksheet.AutoFitRow(2)
            #Get row height
            print(worksheet.GetRowHeightPixels(2))
            #Save to file
            workbook.SaveToFile("UsedRange.xlsx")

        """
        
        GetDllLibXls().XlsWorksheet_GetRowHeightPixels.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsWorksheet_GetRowHeightPixels.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_GetRowHeightPixels, self.Ptr, rowIndex)
        return ret


    def GetText(self ,row:int,column:int)->str:
        """
        Returns string value corresponding to the cell.

        Args:
            row: One-based row index of the cell to get value from.
            column: One-based column index of the cell to get value from.

        Returns:
            String contained by the cell.

        """
        
        GetDllLibXls().XlsWorksheet_GetText.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_GetText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorksheet_GetText, self.Ptr, row,column))
        return ret



    def DeleteRange(self ,range:'CellRange',deleteOption:'DeleteOption'):
        """
        delete a range in worksheet

        Args:
            range: the range to be deleted
            deleteOption: Choose to move the right range to left or move the below range to above

        """
        intPtrrange:c_void_p = range.Ptr
        enumdeleteOption:c_int = deleteOption.value

        GetDllLibXls().XlsWorksheet_DeleteRange.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_DeleteRange, self.Ptr, intPtrrange,enumdeleteOption)


    def MoveWorksheet(self ,destIndex:int):
        """
        Moves worksheet into new position.

        Args:
            destIndex: Destination index.

        """
        
        GetDllLibXls().XlsWorksheet_MoveWorksheet.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_MoveWorksheet, self.Ptr, destIndex)


    def PixelsToColumnWidth(self ,pixels:float)->float:
        """

        """

        GetDllLibXls().XlsWorksheet_PixelsToColumnWidth.argtypes=[c_void_p ,c_double]
        GetDllLibXls().XlsWorksheet_PixelsToColumnWidth.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_PixelsToColumnWidth, self.Ptr, pixels)
        return ret

    def Remove(self):
        """
        Removes worksheet from parernt worksheets collection.

        """
        GetDllLibXls().XlsWorksheet_Remove.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_Remove, self.Ptr)


    def RemoveMergedCells(self ,range:'IXLSRange'):
        """

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().XlsWorksheet_RemoveMergedCells.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_RemoveMergedCells, self.Ptr, intPtrrange)

    def RemovePanes(self):
        """
        Removes panes from a worksheet.

        """
        GetDllLibXls().XlsWorksheet_RemovePanes.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_RemovePanes, self.Ptr)

#    @dispatch
#
#    def Replace(self ,oldValue:str,column:'DataColumn',columnHeaders:bool):
#        """
#    <summary>
#          Replaces cells' values with new data.
#        <example>The following code snippet illustrates how to replace the string value with data column:
#        <code>
#        //Create worksheet
#        Workbook workbook = new Workbook();
#        workbook.LoadFromFile("Sample.xlsx");
#        Worksheet worksheet = workbook.Worksheets[0];
#        //Replace the oldValue by data column
#        string oldValue = "Find";
#        System.Data.DataTable table = new System.Data.DataTable();
#        table.Columns.Add("Dosage", typeof(int));
#        table.Rows.Add(1);
#        System.Data.DataColumn dataColumn = table.Columns[0];
#        worksheet.Replace(oldValue, dataColumn, true);
#        //Save to file
#        workbook.SaveToFile("Replace.xlsx");
#        </code>
#        </example>
#    </summary>
#    <param name="oldValue">String value to replace.</param>
#    <param name="column">Data table with new data.</param>
#    <param name="columnHeaders">Indicates whether to import field names.</param>
#<remarks>
#             This can be long operation (needs iteration through all cells
#             in the worksheet). Better use named ranges instead and call
#             Import function instead of placeholders.
#             </remarks>
#        """
#        intPtrcolumn:c_void_p = column.Ptr
#
#        GetDllLibXls().XlsWorksheet_Replace.argtypes=[c_void_p ,c_void_p,c_void_p,c_bool]
#        CallCFunction(GetDllLibXls().XlsWorksheet_Replace, self.Ptr, oldValue,intPtrcolumn,columnHeaders)


#    @dispatch
#
#    def Replace(self ,oldValue:str,newValues:'DataTable',columnHeaders:bool):
#        """
#    <summary>
#         Replaces cells' values with new data.
#        <example>The following code snippet illustrates how to replace the string value with data table:
#        <code>
#        //Create worksheet
#        Workbook workbook = new Workbook();
#        workbook.LoadFromFile("Sample.xlsx");
#        Worksheet worksheet = workbook.Worksheets[0];
#        //Replace the oldValue by data table
#        string oldValue = "Find";
#        System.Data.DataTable table = new System.Data.DataTable();
#        table.Columns.Add("Dosage", typeof(int));
#        table.Rows.Add(1);
#        worksheet.Replace(oldValue, table, true);
#        //Save to file
#        workbook.SaveToFile("Replace.xlsx");
#        </code>
#        </example>
#    </summary>
#    <param name="oldValue">String value to replace.</param>
#    <param name="newValues">Data table with new data.</param>
#    <param name="columnHeaders">Indicates whether to import field names.</param>
#<remarks>
#             This can be long operation (needs iteration through all cells
#             in the worksheet). Better use named ranges instead and call
#             Import function instead of placeholders.
#             </remarks>
#        """
#        intPtrnewValues:c_void_p = newValues.Ptr
#
#        GetDllLibXls().XlsWorksheet_ReplaceONC.argtypes=[c_void_p ,c_void_p,c_void_p,c_bool]
#        CallCFunction(GetDllLibXls().XlsWorksheet_ReplaceONC, self.Ptr, oldValue,intPtrnewValues,columnHeaders)


    @dispatch

    def Replace(self ,oldValue:str,newValue:DateTime):
        """
        Replaces cells' values with new data.

        Args:
            oldValue: String value to replace.
            newValue: New value for the range with specified string.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Replace the oldValue by dateTime
            oldValue = "Find"
            dateTime = DateTime.Now
            worksheet.Replace(oldValue, dateTime)
            #Save to file
            workbook.SaveToFile("Replace.xlsx")

        """
        intPtrnewValue:c_void_p = newValue.Ptr

        GetDllLibXls().XlsWorksheet_ReplaceON.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_ReplaceON, self.Ptr, oldValue,intPtrnewValue)

    @dispatch

    def Replace(self ,oldValue:str,newValue:float):
        """
        Replaces cells' values with new data.

        Args:
            oldValue: String value to replace.
            newValue: New value for the range with specified string.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Replace the oldValue by double
            oldValue = "Ten"
            worksheet.Replace(oldValue, 10.0)
            #Save to file
            workbook.SaveToFile("Replace.xlsx")

        """
        
        GetDllLibXls().XlsWorksheet_ReplaceON1.argtypes=[c_void_p ,c_void_p,c_double]
        CallCFunction(GetDllLibXls().XlsWorksheet_ReplaceON1, self.Ptr, oldValue,newValue)

    @dispatch

    def Replace(self ,oldValue:str,newValues:List[float],isVertical:bool):
        """
        Replaces cells' values with new data.

        Args:
            oldValue: String value to replace.
            newValues: Array of new values.
            isVertical: Indicates whether array should be inserted vertically.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Replace the oldValue by array of double values
            oldValue = "Find"
            double[] newValues = { 1.0, 2.0 }
            worksheet.Replace(oldValue, newValues, true)
            #Save to file
            workbook.SaveToFile("Replace.xlsx")

        """
        #arraynewValues:ArrayTypenewValues = ""
        countnewValues = len(newValues)
        ArrayTypenewValues = c_double * countnewValues
        arraynewValues = ArrayTypenewValues()
        for i in range(0, countnewValues):
            arraynewValues[i] = newValues[i]


        GetDllLibXls().XlsWorksheet_ReplaceONI.argtypes=[c_void_p ,c_void_p,ArrayTypenewValues,c_int,c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_ReplaceONI, self.Ptr, oldValue,arraynewValues,countnewValues,isVertical)

    @dispatch

    def Replace(self ,oldValue:str,newValues:List[int],isVertical:bool):
        """
        Replaces cells' values with new data.

        Args:
            oldValue: String value to replace.
            newValues: Array of new values.
            isVertical: Indicates whether array should be inserted vertically.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Replace the oldValue by array of int values
            oldValue = "Find"
            int[] newValues = { 1, 2 }
            worksheet.Replace(oldValue, newValues, true)
            #Save to file
            workbook.SaveToFile("Replace.xlsx")

        """
        #arraynewValues:ArrayTypenewValues = ""
        countnewValues = len(newValues)
        ArrayTypenewValues = c_int * countnewValues
        arraynewValues = ArrayTypenewValues()
        for i in range(0, countnewValues):
            arraynewValues[i] = newValues[i]


        GetDllLibXls().XlsWorksheet_ReplaceONI1.argtypes=[c_void_p ,c_void_p,ArrayTypenewValues,c_int,c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_ReplaceONI1, self.Ptr, oldValue,arraynewValues,countnewValues,isVertical)

    @dispatch

    def Replace(self ,oldValue:str,newValue:str):
        """
        Replaces cells' values with new data.

        Args:
            oldValue: String value to replace.
            newValue: New value for the range with specified string.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Replace the oldValue by newValue
            oldValue = "Find"
            newValue = "NewValue"
            worksheet.Replace(oldValue, newValue)
            #Save to file
            workbook.SaveToFile("Replace.xlsx")

        """
        
        GetDllLibXls().XlsWorksheet_ReplaceON11.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_ReplaceON11, self.Ptr, oldValue,newValue)

    @dispatch
    def ReplaceAll(self ,oldValue:str,newValue:str,matchCase:bool)->int:
        """

        """
        
        GetDllLibXls().XlsWorksheet_ReplaceAll.argtypes=[c_void_p ,c_void_p,c_void_p,c_bool]
        GetDllLibXls().XlsWorksheet_ReplaceAll.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_ReplaceAll, self.Ptr, oldValue,newValue,matchCase)
        return ret

    @dispatch
    def ReplaceAll(self ,oldValue:str,oldStyle:CellStyle,newValue:str,newStyle:CellStyle)->int:
        """

        """
        intPtrOldStyle:c_void_p = oldStyle.Ptr
        intPtrNewStyle:c_void_p = newStyle.Ptr
        GetDllLibXls().XlsWorksheet_ReplaceAllOONN.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_void_p]
        GetDllLibXls().XlsWorksheet_ReplaceAllOONN.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_ReplaceAllOONN, self.Ptr, oldValue,intPtrOldStyle,newValue,intPtrNewStyle)
        return ret

    @dispatch

    def Replace(self ,oldValue:str,newValues:List[str],isVertical:bool):
        """
        Replaces cells' values with new data.

        Args:
            oldValue: String value to replace.
            newValues: Array of new values.
            isVertical: Indicates whether array should be inserted vertically.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Replace the oldValue by array of string values
            oldValue = "Find"
            string[] newValues = { "X values", "Y values" }
            worksheet.Replace(oldValue, newValues , true)
            #Save to file
            workbook.SaveToFile("Replace.xlsx")

        """
        #arraynewValues:ArrayTypenewValues = ""
        countnewValues = len(newValues)
        ArrayTypenewValues = c_wchar_p * countnewValues
        arraynewValues = ArrayTypenewValues()
        for i in range(0, countnewValues):
            arraynewValues[i] = newValues[i]


        GetDllLibXls().XlsWorksheet_ReplaceONI11.argtypes=[c_void_p ,c_void_p,ArrayTypenewValues,c_int,c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_ReplaceONI11, self.Ptr, oldValue,arraynewValues,countnewValues,isVertical)

    @dispatch

    def SaveToImage(self ,firstRow:int,firstColumn:int,lastRow:int,lastColumn:int)->Stream:
        """

        """
        
        GetDllLibXls().XlsWorksheet_SaveToImage.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        GetDllLibXls().XlsWorksheet_SaveToImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_SaveToImage, self.Ptr, firstRow,firstColumn,lastRow,lastColumn)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    @dispatch

    def SaveToImage(self ,fileName:str,firstRow:int,firstColumn:int,lastRow:int,lastColumn:int):
        """
        Save worksheet to image.

        Args:
            fileName: file Name
            firstRow: 
            firstColumn: 
            lastRow: 
            lastColumn: 

        """
        
        GetDllLibXls().XlsWorksheet_SaveToImageFFFLL.argtypes=[c_void_p ,c_void_p,c_int,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToImageFFFLL, self.Ptr, fileName,firstRow,firstColumn,lastRow,lastColumn)

    @dispatch

    def SaveToImage(self ,fileName:str):
        """
        Save worksheet to image.

        Args:
            fileName: file Name

        """
        
        GetDllLibXls().XlsWorksheet_SaveToImageF.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToImageF, self.Ptr, fileName)

#    @dispatch

#    def SaveToImage(self ,fileName:str,format:ImageFormat):
#        """
#<summary></summary>
#    <param name="fileName">file name</param>
#    <param name="format">file format</param>
#        """
#        intPtrformat:c_void_p = format.Ptr

#        GetDllLibXls().XlsWorksheet_SaveToImageFF.argtypes=[c_void_p ,c_void_p,c_void_p]
#        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToImageFF, self.Ptr, fileName,intPtrformat)


    def ToImage(self ,firstRow:int,firstColumn:int,lastRow:int,lastColumn:int)->'Stream':
        """
        Args:
            firstRow: One-based index of the first row to convert.
            firstColumn: One-based index of the first column to convert.
            lastRow: One-based index of the last row to convert.
            lastColumn: One-based index of the last column to convert.

        """
        
        GetDllLibXls().XlsWorksheet_ToImage.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        GetDllLibXls().XlsWorksheet_ToImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_ToImage, self.Ptr, firstRow,firstColumn,lastRow,lastColumn)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    @dispatch

    def SaveToImage(self ,stream:Stream,firstRow:int,firstColumn:int,lastRow:int,lastColumn:int,imageType:ImageType)->Stream:
        """
        Save worksheet into image.

        Args:
            stream: Output stream. It is ignored if null.
            firstRow: One-based index of the first row to convert.
            firstColumn: One-based index of the first column to convert.
            lastRow: One-based index of the last row to convert.
            lastColumn: One-based index of the last column to convert.
            imageType: Type of the image to create.

        Returns:
            Created image.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Creat stream
            stream = MemoryStream()
            #Save to image
            System.Drawing.image = worksheet.SaveToImage(stream,1, 1, 10, 20, Spire.Xls.ImageType.Bitmap)
            image.Save("Sample.png", System.Drawing.Imaging.ImageFormat.Png)

        """
        intPtrstream:c_void_p = stream.Ptr
        enumimageType:c_int = imageType.value

        GetDllLibXls().XlsWorksheet_SaveToImageSFFLLI.argtypes=[c_void_p ,c_void_p,c_int,c_int,c_int,c_int,c_int]
        GetDllLibXls().XlsWorksheet_SaveToImageSFFLLI.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_SaveToImageSFFLLI, self.Ptr, intPtrstream,firstRow,firstColumn,lastRow,lastColumn,enumimageType)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    @dispatch

    def SaveToImage(self ,stream:Stream,firstRow:int,firstColumn:int,lastRow:int,lastColumn:int,emfType:EmfType)->Stream:
        """
        Converts range into image.

        Args:
            outputStream: Output stream. It is ignored if null.
            firstRow: One-based index of the first row to convert.
            firstColumn: One-based index of the first column to convert.
            lastRow: One-based index of the last row to convert.
            lastColumn: One-based index of the last column to convert.
            emfType: Metafile EmfType.

        Returns:
            Created image.

        """
        intPtrstream:c_void_p = stream.Ptr
        enumemfType:c_int = emfType.value

        GetDllLibXls().XlsWorksheet_SaveToImageSFFLLE.argtypes=[c_void_p ,c_void_p,c_int,c_int,c_int,c_int,c_int]
        GetDllLibXls().XlsWorksheet_SaveToImageSFFLLE.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_SaveToImageSFFLLE, self.Ptr, intPtrstream,firstRow,firstColumn,lastRow,lastColumn,enumemfType)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    @dispatch

    def SaveToImage(self ,stream:Stream,firstRow:int,firstColumn:int,lastRow:int,lastColumn:int,imageType:ImageType,emfType:EmfType)->Stream:
        """
        Converts range into image.

        Args:
            firstRow: One-based index of the first row to convert.
            firstColumn: One-based index of the first column to convert.
            lastRow: One-based index of the last row to convert.
            lastColumn: One-based index of the last column to convert.
            imageType: Type of the image to create.
            outputStream: Output stream. It is ignored if null.
            emfType: Metafile EmfType.

        Returns:
            Created image.

        """
        intPtrstream:c_void_p = stream.Ptr
        enumimageType:c_int = imageType.value
        enumemfType:c_int = emfType.value

        GetDllLibXls().XlsWorksheet_SaveToImageSFFLLIE.argtypes=[c_void_p ,c_void_p,c_int,c_int,c_int,c_int,c_int,c_int]
        GetDllLibXls().XlsWorksheet_SaveToImageSFFLLIE.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_SaveToImageSFFLLIE, self.Ptr, intPtrstream,firstRow,firstColumn,lastRow,lastColumn,enumimageType,enumemfType)
        ret = None if intPtr==None else Stream(intPtr)
        return ret



    def SaveToEMFImage(self ,FilePath:str,firstRow:int,firstColumn:int,lastRow:int,lastColumn:int,emfType:'EmfType'):
        """

        """
        enumemfType:c_int = emfType.value

        GetDllLibXls().XlsWorksheet_SaveToEMFImage.argtypes=[c_void_p ,c_void_p,c_int,c_int,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToEMFImage, self.Ptr, FilePath,firstRow,firstColumn,lastRow,lastColumn,enumemfType)

    @dispatch

    def SaveToHtml(self ,stream:Stream):
        """
        Save to HTML stream.

        Args:
            stream: Stream object
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Creat stream
            stream = MemoryStream()
            #Save to HTML stream
            worksheet.SaveToHtml(stream)

        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibXls().XlsWorksheet_SaveToHtml.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToHtml, self.Ptr, intPtrstream)

    @dispatch

    def SaveToHtml(self ,stream:Stream,saveOption:HTMLOptions):
        """
        Saves work sheet to HTML.

        Args:
            stream: The stream
            saveOption: The option
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Creat stream
            stream = MemoryStream()
            #Save to HTML stream
            worksheet.SaveToHtml(stream, Spire.Xls.Core.Spreadsheet.HTMLOptions.Default)

        """
        intPtrstream:c_void_p = stream.Ptr
        intPtrsaveOption:c_void_p = saveOption.Ptr

        GetDllLibXls().XlsWorksheet_SaveToHtmlSS.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToHtmlSS, self.Ptr, intPtrstream,intPtrsaveOption)

    @dispatch

    def SaveToHtml(self ,filename:str):
        """
        Save to HTML file.

        Args:
            filename: File name
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Save to HTML file
            worksheet.SaveToHtml("Output.html")

        """
        
        GetDllLibXls().XlsWorksheet_SaveToHtmlF.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToHtmlF, self.Ptr, filename)

    @dispatch

    def SaveToHtml(self ,fileName:str,saveOption:HTMLOptions):
        """
        Saves as HTML.

        Args:
            fileName: The filename
            saveOption: The option
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Save to HTML file
            worksheet.SaveToHtml("Sample.html" , Spire.Xls.Core.Spreadsheet.HTMLOptions.Default)

        """
        intPtrsaveOption:c_void_p = saveOption.Ptr

        GetDllLibXls().XlsWorksheet_SaveToHtmlFS.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToHtmlFS, self.Ptr, fileName,intPtrsaveOption)

    @dispatch

    def SaveToFile(self ,fileName:str,separator:str):
        """
        Save worksheet to file.

        Args:
            fileName: File name.
            separator: Seperator.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Save to file
            worksheet.SaveToFile("SaveToFile.csv" , ",")

        """
        
        GetDllLibXls().XlsWorksheet_SaveToFile.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToFile, self.Ptr, fileName,separator)

    @dispatch

    def SaveToFile(self ,fileName:str,separator:str,retainHiddenData:bool):
        """
        Save worksheet to file.

        Args:
            fileName: File name.
            separator: Seperator.
            retainHiddenData: retain hidden data

        """
        
        GetDllLibXls().XlsWorksheet_SaveToFileFSR.argtypes=[c_void_p ,c_void_p,c_void_p,c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToFileFSR, self.Ptr, fileName,separator,retainHiddenData)

    @dispatch

    def SaveToFile(self ,fileName:str,separator:str,encoding:Encoding):
        """
        Save worksheet to file..

        Args:
            fileName: File name.
            separator: Seperator.
            encoding: Encoding to use.

        """
        intPtrencoding:c_void_p = encoding.Ptr

        GetDllLibXls().XlsWorksheet_SaveToFileFSE.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToFileFSE, self.Ptr, fileName,separator,intPtrencoding)

    @dispatch

    def SaveToStream(self ,stream:Stream,separator:str):
        """
        Save worksheet to stream.

        Args:
            stream: Stream object.
            separator: Seperator.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create stream
            stream = MemoryStream()
            #Save to stream
            worksheet.SaveToStream(stream , ",")

        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibXls().XlsWorksheet_SaveToStream.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToStream, self.Ptr, intPtrstream,separator)

    @dispatch

    def SaveToStream(self ,stream:Stream,separator:str,retainHiddenData:bool):
        """
        Save worksheet to stream.

        Args:
            stream: Stream object.
            separator: Seperator.
            retainHiddenData: retain hidden data

        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibXls().XlsWorksheet_SaveToStreamSSR.argtypes=[c_void_p ,c_void_p,c_void_p,c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToStreamSSR, self.Ptr, intPtrstream,separator,retainHiddenData)

    @dispatch

    def SaveToStream(self ,stream:Stream,separator:str,encoding:Encoding):
        """
        Save worksheet to stream.

        Args:
            stream: Stream to save.
            separator: Current seperator.
            encoding: Encoding to use.

        """
        intPtrstream:c_void_p = stream.Ptr
        intPtrencoding:c_void_p = encoding.Ptr

        GetDllLibXls().XlsWorksheet_SaveToStreamSSE.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToStreamSSE, self.Ptr, intPtrstream,separator,intPtrencoding)


    def SaveToXps(self ,fileName:str):
        """
        Saves specific worksheet to xps.

        Args:
            fileName: File name.

        """
        
        GetDllLibXls().XlsWorksheet_SaveToXps.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToXps, self.Ptr, fileName)

    @dispatch

    def SaveToPdf(self ,fileName:str,fileFormat:FileFormat):
        """
        Save worksheet to pdf.

        Args:
            fileName: File name.

        """
        enumfileFormat:c_int = fileFormat.value

        GetDllLibXls().XlsWorksheet_SaveToPdf.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToPdf, self.Ptr, fileName,enumfileFormat)

    @dispatch

    def SaveToPdf(self ,fileName:str):
        """
        Save worksheet to pdf.

        Args:
            fileName: File name.

        """
        
        GetDllLibXls().XlsWorksheet_SaveToPdfF.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToPdfF, self.Ptr, fileName)

    @dispatch

    def SaveToPdfStream(self ,stream:Stream,fileFormat:FileFormat):
        """

        """
        intPtrstream:c_void_p = stream.Ptr
        enumfileFormat:c_int = fileFormat.value

        GetDllLibXls().XlsWorksheet_SaveToPdfStream.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToPdfStream, self.Ptr, intPtrstream,enumfileFormat)

    @dispatch

    def SaveToPdfStream(self ,stream:Stream):
        """
        Save worksheet to pdf Stream.

        Args:
            stream: Stream.

        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibXls().XlsWorksheet_SaveToPdfStreamS.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SaveToPdfStreamS, self.Ptr, intPtrstream)


    def ToSVGStream(self ,stream:'Stream',firstRow:int,firstColumn:int,lastRow:int,lastColumn:int):
        """
        Convert CellRange to Svg stream

        Args:
            stream: stream.
            firstRow: One-based index of the first row to convert.
            firstColumn: One-based index of the first column to convert.
            lastRow: One-based index of the last row to convert.
            lastColumn: One-based index of the last column to convert.

        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibXls().XlsWorksheet_ToSVGStream.argtypes=[c_void_p ,c_void_p,c_int,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_ToSVGStream, self.Ptr, intPtrstream,firstRow,firstColumn,lastRow,lastColumn)


    def SetBlank(self ,iRow:int,iColumn:int):
        """
        Sets blank in specified cell.

        Args:
            iRow: One-based row index  of the cell to set value.
            iColumn: One-based column index of the cell to set value.

        """
        
        GetDllLibXls().XlsWorksheet_SetBlank.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetBlank, self.Ptr, iRow,iColumn)


    def SetBoolean(self ,iRow:int,iColumn:int,value:bool):
        """
        Sets value in the specified cell.

        Args:
            iRow: One-based row index  of the cell to set value.
            iColumn: One-based column index of the cell to set value.
            value: Value to set.

        """
        
        GetDllLibXls().XlsWorksheet_SetBoolean.argtypes=[c_void_p ,c_int,c_int,c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetBoolean, self.Ptr, iRow,iColumn,value)

    @dispatch

    def SetColumnWidthInPixels(self ,iColumn:int,value:int):
        """
        Sets column width in pixels.

        Args:
            iColumn: One-based column index.
            value: Width in pixels to set.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set column width
            worksheet.SetColumnWidthInPixels(2, 160)
            #Save to file
            workbook.SaveToFile("SetColumnWidthInPixels.xlsx")

        """
        
        GetDllLibXls().XlsWorksheet_SetColumnWidthInPixels.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetColumnWidthInPixels, self.Ptr, iColumn,value)


    def SetColumnWidth(self ,columnIndex:int,width:float):
        """
        Set solumn width

        Args:
            columnIndex: Column index.
            width: Width to set.

        """
        
        GetDllLibXls().XlsWorksheet_SetColumnWidth.argtypes=[c_void_p ,c_int,c_double]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetColumnWidth, self.Ptr, columnIndex,width)

    @dispatch

    def SetColumnWidthInPixels(self ,columnIndex:int,count:int,value:int):
        """
        Sets the width of the specified columns.

        Args:
            columnIndex: Column index
            count: count
            value: Value

        """
        
        GetDllLibXls().XlsWorksheet_SetColumnWidthInPixelsCCV.argtypes=[c_void_p ,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetColumnWidthInPixelsCCV, self.Ptr, columnIndex,count,value)

    @dispatch

    def SetDefaultColumnStyle(self ,columnIndex:int,defaultStyle:IStyle):
        """
        Sets default style for column.

        Args:
            columnIndex: Column index.
            defaultStyle: Default style.

        """
        intPtrdefaultStyle:c_void_p = defaultStyle.Ptr

        GetDllLibXls().XlsWorksheet_SetDefaultColumnStyle.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetDefaultColumnStyle, self.Ptr, columnIndex,intPtrdefaultStyle)

    @dispatch

    def SetDefaultColumnStyle(self ,firstColumnIndex:int,lastColumnIndex:int,defaultStyle:IStyle):
        """

        """
        intPtrdefaultStyle:c_void_p = defaultStyle.Ptr

        GetDllLibXls().XlsWorksheet_SetDefaultColumnStyleFLD.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetDefaultColumnStyleFLD, self.Ptr, firstColumnIndex,lastColumnIndex,intPtrdefaultStyle)

    @dispatch

    def SetDefaultRowStyle(self ,rowIndex:int,defaultStyle:IStyle):
        """

        """
        intPtrdefaultStyle:c_void_p = defaultStyle.Ptr

        GetDllLibXls().XlsWorksheet_SetDefaultRowStyle.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetDefaultRowStyle, self.Ptr, rowIndex,intPtrdefaultStyle)

    @dispatch

    def SetDefaultRowStyle(self ,firstRowIndex:int,lastRowIndex:int,defaultStyle:IStyle):
        """

        """
        intPtrdefaultStyle:c_void_p = defaultStyle.Ptr

        GetDllLibXls().XlsWorksheet_SetDefaultRowStyleFLD.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetDefaultRowStyleFLD, self.Ptr, firstRowIndex,lastRowIndex,intPtrdefaultStyle)

    @dispatch

    def SetError(self ,iRow:int,iColumn:int,value:str):
        """
        Sets error in the specified cell.

        Args:
            iRow: One-based row index  of the cell to set value.
            iColumn: One-based column index of the cell to set value.
            value: Error to set.

        """
        
        GetDllLibXls().XlsWorksheet_SetError.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetError, self.Ptr, iRow,iColumn,value)

    @dispatch

    def SetError(self ,iRow:int,iColumn:int,value:str,isSetText:bool):
        """
        Args:
            iRow: 
            iColumn: 
            value: 
            isSetText: 

        """
        
        GetDllLibXls().XlsWorksheet_SetErrorIIVI.argtypes=[c_void_p ,c_int,c_int,c_void_p,c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetErrorIIVI, self.Ptr, iRow,iColumn,value,isSetText)

    @dispatch

    def SetFormula(self ,iRow:int,iColumn:int,value:str):
        """
        Sets formula in the specified cell.

        Args:
            iRow: One-based row index  of the cell to set value.
            iColumn: One-based column index of the cell to set value.
            value: Formula to set.

        """
        
        GetDllLibXls().XlsWorksheet_SetFormula.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetFormula, self.Ptr, iRow,iColumn,value)

    @dispatch

    def SetFormula(self ,iRow:int,iColumn:int,value:str,bIsR1C1:bool):
        """
        Sets formula in the specified cell.

        Args:
            iRow: One-based row index  of the cell to set value.
            iColumn: One-based column index of the cell to set value.
            value: Formula to set.
            bIsR1C1: Indicates is formula in R1C1 notation.

        """
        
        GetDllLibXls().XlsWorksheet_SetFormulaIIVB.argtypes=[c_void_p ,c_int,c_int,c_void_p,c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetFormulaIIVB, self.Ptr, iRow,iColumn,value,bIsR1C1)


    def SetFormulaBoolValue(self ,iRow:int,iColumn:int,value:bool):
        """
        Sets formula bool value.

        Args:
            iRow: One based row index.
            iColumn: One based column index.
            value: Represents formula bool value for set.

        """
        
        GetDllLibXls().XlsWorksheet_SetFormulaBoolValue.argtypes=[c_void_p ,c_int,c_int,c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetFormulaBoolValue, self.Ptr, iRow,iColumn,value)


    def SetFormulaErrorValue(self ,iRow:int,iColumn:int,value:str):
        """
        Sets formula error value.

        Args:
            iRow: One based row index.
            iColumn: One based column index.
            value: Represents formula error value for set.

        """
        
        GetDllLibXls().XlsWorksheet_SetFormulaErrorValue.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetFormulaErrorValue, self.Ptr, iRow,iColumn,value)


    def SetFormulaNumberValue(self ,iRow:int,iColumn:int,value:float):
        """
        Sets formula number value.

        Args:
            iRow: One based row index.
            iColumn: One based column index.
            value: Represents formula number value for set.

        """
        
        GetDllLibXls().XlsWorksheet_SetFormulaNumberValue.argtypes=[c_void_p ,c_int,c_int,c_double]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetFormulaNumberValue, self.Ptr, iRow,iColumn,value)


    def SetFormulaStringValue(self ,iRow:int,iColumn:int,value:str):
        """
        Sets formula string value.

        Args:
            iRow: One based row index.
            iColumn: One based column index.
            value: Represents formula string value for set.

        """
        
        GetDllLibXls().XlsWorksheet_SetFormulaStringValue.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetFormulaStringValue, self.Ptr, iRow,iColumn,value)


    def SetNumber(self ,iRow:int,iColumn:int,value:float):
        """
        Sets value in the specified cell.

        Args:
            iRow: One-based row index  of the cell to set value.
            iColumn: One-based column index of the cell to set value.
            value: Value to set.

        """
        
        GetDllLibXls().XlsWorksheet_SetNumber.argtypes=[c_void_p ,c_int,c_int,c_double]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetNumber, self.Ptr, iRow,iColumn,value)


    def SetRowHeightInPixels(self ,rowIndex:int,count:int,value:float):
        """
        Set Row height from Start Row index

        Args:
            rowIndex: Row index
            Count: count
            value: Value

        """
        
        GetDllLibXls().XlsWorksheet_SetRowHeightInPixels.argtypes=[c_void_p ,c_int,c_int,c_double]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetRowHeightInPixels, self.Ptr, rowIndex,count,value)


    def SetRowHeight(self ,rowIndex:int,height:float):
        """
        Sets the height of the specified row.

        Args:
            rowIndex: Row index.
            height: Height.

        """
        
        GetDllLibXls().XlsWorksheet_SetRowHeight.argtypes=[c_void_p ,c_int,c_double]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetRowHeight, self.Ptr, rowIndex,height)


    def SetRowHeightPixels(self ,rowIndex:int,height:float):
        """
        Sets the height of the specified row.

        Args:
            rowIndex: Row index.
            height: Height.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set row height
            worksheet.SetRowHeightPixels(3, 150)
            #Save to file
            workbook.SaveToFile("SetRowHeightPixels.xlsx")

        """
        
        GetDllLibXls().XlsWorksheet_SetRowHeightPixels.argtypes=[c_void_p ,c_int,c_double]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetRowHeightPixels, self.Ptr, rowIndex,height)


    def SetText(self ,iRow:int,iColumn:int,value:str):
        """
        Sets text in the specified cell.

        Args:
            iRow: One-based row index  of the cell to set value.
            iColumn: One-based column index of the cell to set value.
            value: Text to set.

        """
        
        GetDllLibXls().XlsWorksheet_SetText.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetText, self.Ptr, iRow,iColumn,value)


    def SetValue(self ,rowIndex:int,columnIndex:int,stringValue:str):
        """

        """
        
        GetDllLibXls().XlsWorksheet_SetValue.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetValue, self.Ptr, rowIndex,columnIndex,stringValue)

    @dispatch

    def SetCellValue(self ,rowIndex:int,columnIndex:int,boolValue:bool):
        """
        Sets value in the specified cell.

        Args:
            rowIndex: Row index.
            columnIndex: Column index.
            boolValue: Value to set.

        """
        
        GetDllLibXls().XlsWorksheet_SetCellValue.argtypes=[c_void_p ,c_int,c_int,c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetCellValue, self.Ptr, rowIndex,columnIndex,boolValue)

    @dispatch

    def SetCellValue(self ,rowIndex:int,columnIndex:int,stringValue:str):
        """
        Sets value in the specified cell.

        Args:
            rowIndex: Row index
            columnIndex: Column index.
            stringValue: Value to set.

        """
        
        GetDllLibXls().XlsWorksheet_SetCellValueRCS.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetCellValueRCS, self.Ptr, rowIndex,columnIndex,stringValue)

    @property
    def HasMergedCells(self)->bool:
        """
        Indicates whether worksheet has merged cells.

        """
        GetDllLibXls().XlsWorksheet_get_HasMergedCells.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_HasMergedCells.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_HasMergedCells, self.Ptr)
        return ret

    @property
    def HasOleObjects(self)->bool:
        """
        Indicats whether there is OLE object.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Create image stream
            System.Drawing.image = System.Drawing.Image.FromFile("image.png")
            #Add ole object
            oleObject = worksheet.OleObjects.Add("Shapes.xlsx", image, OleLinkType.Embed)
            #Check HasOleObject.Output will be true.</para>
            Console.Write(worksheet.HasOleObjects)
            
                             <para>#Save to file
                    workbook.SaveToFile("HasOleObjects.xlsx");

        """
        GetDllLibXls().XlsWorksheet_get_HasOleObjects.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_HasOleObjects.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_HasOleObjects, self.Ptr)
        return ret

    @property
    def HorizontalSplit(self)->int:
        """

        """
        GetDllLibXls().XlsWorksheet_get_HorizontalSplit.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_HorizontalSplit.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_HorizontalSplit, self.Ptr)
        return ret

    @HorizontalSplit.setter
    def HorizontalSplit(self, value:int):
        GetDllLibXls().XlsWorksheet_set_HorizontalSplit.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_HorizontalSplit, self.Ptr, value)

    @property

    def HPageBreaks(self)->'IHPageBreaks':
        """

        """
        GetDllLibXls().XlsWorksheet_get_HPageBreaks.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_HPageBreaks.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_HPageBreaks, self.Ptr)
        ret = None if intPtr==None else IHPageBreaks(intPtr)
        return ret


    @property

    def HyperLinks(self)->'IHyperLinks':
        """

        """
        GetDllLibXls().XlsWorksheet_get_HyperLinks.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_HyperLinks.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_HyperLinks, self.Ptr)
        ret = None if intPtr==None else IHyperLinks(intPtr)
        return ret


    @property
    def IsDisplayZeros(self)->bool:
        """
        Indicates whether zero values to be displayed

        """
        GetDllLibXls().XlsWorksheet_get_IsDisplayZeros.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_IsDisplayZeros.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_IsDisplayZeros, self.Ptr)
        return ret

    @IsDisplayZeros.setter
    def IsDisplayZeros(self, value:bool):
        GetDllLibXls().XlsWorksheet_set_IsDisplayZeros.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_IsDisplayZeros, self.Ptr, value)

    @property
    def IsEmpty(self)->bool:
        """
        Indicates whether worksheet is empty. Read-only.

        """
        GetDllLibXls().XlsWorksheet_get_IsEmpty.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_IsEmpty.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_IsEmpty, self.Ptr)
        return ret

    @property
    def IsFreezePanes(self)->bool:
        """
        Indicates whether freezed panes are applied.

        """
        GetDllLibXls().XlsWorksheet_get_IsFreezePanes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_IsFreezePanes.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_IsFreezePanes, self.Ptr)
        return ret

    @property
    def IsStringsPreserved(self)->bool:
        """
        Indicates if all values in the workbook are preserved as strings.

        """
        GetDllLibXls().XlsWorksheet_get_IsStringsPreserved.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_IsStringsPreserved.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_IsStringsPreserved, self.Ptr)
        return ret

    @IsStringsPreserved.setter
    def IsStringsPreserved(self, value:bool):
        GetDllLibXls().XlsWorksheet_set_IsStringsPreserved.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_IsStringsPreserved, self.Ptr, value)

    @dispatch

    def AddAllowEditRange(self ,title:str,range:CellRange,password:str)->bool:
        """
        AddAllowEditRange : add a range of cells that allow editing

        Args:
            title: title
            range: range
            password: password

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().XlsWorksheet_AddAllowEditRange.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p]
        GetDllLibXls().XlsWorksheet_AddAllowEditRange.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_AddAllowEditRange, self.Ptr, title,intPtrrange,password)
        return ret

    @dispatch

    def AddAllowEditRange(self ,title:str,range:CellRange)->bool:
        """
        AddAllowEditRange : add a range of cells that allow editing

        Args:
            title: title
            range: range

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().XlsWorksheet_AddAllowEditRangeTR.argtypes=[c_void_p ,c_void_p,c_void_p]
        GetDllLibXls().XlsWorksheet_AddAllowEditRangeTR.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_AddAllowEditRangeTR, self.Ptr, title,intPtrrange)
        return ret

    @property

    def ListObjects(self)->'IListObjects':
        """
        Returns all list objects in the worksheet.

        """
        GetDllLibXls().XlsWorksheet_get_ListObjects.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_ListObjects.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_ListObjects, self.Ptr)
        ret = None if intPtr==None else ListObjectCollection(intPtr)
        return ret


    @property
    def FormulasVisible(self)->bool:
        """

        """
        GetDllLibXls().XlsWorksheet_get_FormulasVisible.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_FormulasVisible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_FormulasVisible, self.Ptr)
        return ret

    @FormulasVisible.setter
    def FormulasVisible(self, value:bool):
        GetDllLibXls().XlsWorksheet_set_FormulasVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_FormulasVisible, self.Ptr, value)

    @property
    def RowColumnHeadersVisible(self)->bool:
        """
        True if row and column headers are visible. False otherwise.

        """
        GetDllLibXls().XlsWorksheet_get_RowColumnHeadersVisible.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_RowColumnHeadersVisible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_RowColumnHeadersVisible, self.Ptr)
        return ret

    @RowColumnHeadersVisible.setter
    def RowColumnHeadersVisible(self, value:bool):
        GetDllLibXls().XlsWorksheet_set_RowColumnHeadersVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_RowColumnHeadersVisible, self.Ptr, value)

    @property
    def ProtectContents(self)->bool:
        """
        Indicates whether current sheet is protected.

        """
        GetDllLibXls().XlsWorksheet_get_ProtectContents.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_ProtectContents.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_ProtectContents, self.Ptr)
        return ret

    @property

    def PivotTables(self)->'PivotTablesCollection':
        """
        Returns charts collection. Read-only.

        """
        GetDllLibXls().XlsWorksheet_get_PivotTables.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_PivotTables.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_PivotTables, self.Ptr)
        ret = None if intPtr==None else PivotTablesCollection(intPtr)
        return ret


    @property

    def QuotedName(self)->str:
        """
        Returns quoted name of the worksheet.

        """
        GetDllLibXls().XlsWorksheet_get_QuotedName.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_QuotedName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorksheet_get_QuotedName, self.Ptr))
        return ret


    @property

    def DVTable(self)->'IDataValidationTable':
        """

        """
        GetDllLibXls().XlsWorksheet_get_DVTable.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_DVTable.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_DVTable, self.Ptr)
        ret = None if intPtr==None else XlsDataValidationTable(intPtr)
        return ret


    def CalculateAllValue(self):
        """
        Caculate all formula for the specified worksheet

        """
        GetDllLibXls().XlsWorksheet_CalculateAllValue.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_CalculateAllValue, self.Ptr)


    def GetCaculateValue(self ,row:int,col:int)->'str':
        """

        """
        
        GetDllLibXls().XlsWorksheet_GetCaculateValue.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_GetCaculateValue.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_GetCaculateValue, self.Ptr, row,col)
        ret = None if intPtr==None else PtrToStr(intPtr)
        return ret



    def SetCaculateValue(self ,value:'SpireObject',row:int,col:int):
        """

        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibXls().XlsWorksheet_SetCaculateValue.argtypes=[c_void_p ,c_void_p,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetCaculateValue, self.Ptr, intPtrvalue,row,col)

#    @dispatch
#
#    def InsertArray(self ,dateTimeArray:'DateTime[]',firstRow:int,firstColumn:int,isVertical:bool)->int:
#        """
#    <summary>
#         Imports an array of datetimes into worksheet.
#        <example>The following code illustrates how to Imports an array of DateTime values into a worksheet with the specified row and colum:
#        <code>
#        //Create worksheet
#        Workbook workbook = new Workbook();
#        Worksheet worksheet = workbook.Worksheets[0];
#        //Initialize the DateTime Array
#        DateTime[] arrayDate = new DateTime[4] { DateTime.Parse("06:45"), DateTime.Parse("08:30"), DateTime.Parse("09:40"), DateTime.Parse("10:30") };
#        //Insert the DateTime Array to Sheet
#        worksheet.InsertArray(arrayDate, 1, 1, true);
#        //Save to file
#        workbook.SaveToFile(InsertArray.xlsx");
#        </code>
#        </example>
#    </summary>
#    <param name="dateTimeArray">Datetime array.</param>
#    <param name="firstRow">The row number of the first cell to import in.</param>
#    <param name="firstColumn">The column number of the first cell to import in.</param>
#    <param name="isVertical">Specifies to import data vertically or horizontally.</param>
#    <returns></returns>
#        """
#        #arraydateTimeArray:ArrayTypedateTimeArray = ""
#        countdateTimeArray = len(dateTimeArray)
#        ArrayTypedateTimeArray = c_void_p * countdateTimeArray
#        arraydateTimeArray = ArrayTypedateTimeArray()
#        for i in range(0, countdateTimeArray):
#            arraydateTimeArray[i] = dateTimeArray[i].Ptr
#
#
#        GetDllLibXls().XlsWorksheet_InsertArray.argtypes=[c_void_p ,ArrayTypedateTimeArray,c_int,c_int,c_bool]
#        GetDllLibXls().XlsWorksheet_InsertArray.restype=c_int
#        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertArray, self.Ptr, arraydateTimeArray,firstRow,firstColumn,isVertical)
#        return ret


    @dispatch

    def InsertArray(self ,doubleArray:List[float],firstRow:int,firstColumn:int,isVertical:bool)->int:
        """
        Imports an array of doubles into a worksheet.

        Args:
            doubleArray: Double array
            firstRow: The row number of the first cell to import in.
            firstColumn: The column number of the first cell to import in.
            isVertical: Specifies to import data vertically or horizontally.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Initialize the double Array
            double[] arrayDouble = new double[4] { 344.0045, 345.0045, 346.0045, 347.0045 }
            #Insert the double Array to Sheet
            worksheet.InsertArray(arrayDouble, 1, 1, true)
            #Save to file
            workbook.SaveToFile(InsertArray.xlsx")

        """
        #arraydoubleArray:ArrayTypedoubleArray = ""
        countdoubleArray = len(doubleArray)
        ArrayTypedoubleArray = c_double * countdoubleArray
        arraydoubleArray = ArrayTypedoubleArray()
        for i in range(0, countdoubleArray):
            arraydoubleArray[i] = doubleArray[i]


        GetDllLibXls().XlsWorksheet_InsertArrayDFFI.argtypes=[c_void_p ,ArrayTypedoubleArray,c_int,c_int,c_int,c_bool]
        GetDllLibXls().XlsWorksheet_InsertArrayDFFI.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertArrayDFFI, self.Ptr, arraydoubleArray,countdoubleArray,firstRow,firstColumn,isVertical)
        return ret

#    @dispatch
#
#    def InsertArray(self ,objects:'T',firstRow:int,firstColumn:int,isVertical:bool)->int:
#        """
#
#        """
#        intPtrobjects:c_void_p = objects.Ptr
#
#        GetDllLibXls().XlsWorksheet_InsertArrayOFFI.argtypes=[c_void_p ,c_void_p,c_int,c_int,c_bool]
#        GetDllLibXls().XlsWorksheet_InsertArrayOFFI.restype=c_int
#        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertArrayOFFI, self.Ptr, intPtrobjects,firstRow,firstColumn,isVertical)
#        return ret


    @dispatch

    def InsertArray(self ,intArray:List[int],firstRow:int,firstColumn:int,isVertical:bool)->int:
        """
        Imports an array of integer into a worksheet.

        Args:
            intArray: Integer array.
            firstRow: The row number of the first cell to import in.
            firstColumn: The column number of the first cell to import in.
            isVertical: Specifies to import data vertically or horizontally.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Initialize the integer Array
            int[] arrayInt = new int[4] {1000, 2000, 3000, 4000}
            #Insert the integer Array to Sheet
            worksheet.InsertArray(arrayInt, 1, 1, true)
            #Save to file
            workbook.SaveToFile(InsertArray.xlsx")

        """
        #arrayintArray:ArrayTypeintArray = ""
        countintArray = len(intArray)
        ArrayTypeintArray = c_int * countintArray
        arrayintArray = ArrayTypeintArray()
        for i in range(0, countintArray):
            arrayintArray[i] = intArray[i]


        GetDllLibXls().XlsWorksheet_InsertArrayIFFI.argtypes=[c_void_p ,ArrayTypeintArray,c_int,c_int,c_int,c_bool]
        GetDllLibXls().XlsWorksheet_InsertArrayIFFI.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertArrayIFFI, self.Ptr, arrayintArray,countintArray,firstRow,firstColumn,isVertical)
        return ret

#    @dispatch
#
#    def InsertArray(self ,objectArray:'Object[,]',firstRow:int,firstColumn:int)->int:
#        """
#
#        """
#        #arrayobjectArray:ArrayTypeobjectArray = ""
#        countobjectArray = len(objectArray)
#        ArrayTypeobjectArray = c_void_p * countobjectArray
#        arrayobjectArray = ArrayTypeobjectArray()
#        for i in range(0, countobjectArray):
#            arrayobjectArray[i] = objectArray[i].Ptr
#
#
#        GetDllLibXls().XlsWorksheet_InsertArrayOFF.argtypes=[c_void_p ,ArrayTypeobjectArray,c_int,c_int]
#        GetDllLibXls().XlsWorksheet_InsertArrayOFF.restype=c_int
#        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertArrayOFF, self.Ptr, arrayobjectArray,firstRow,firstColumn)
#        return ret


#    @dispatch
#
#    def InsertArray(self ,objectArray:'Object[,]',firstRow:int,firstColumn:int,needConvert:bool)->int:
#        """
#    <summary>
#         Imports an array of objects into a worksheet.
#        <example>The following code illustrates how to Imports an array of Object into a worksheet with specified alignment:
#        <code>
#        //Create worksheet
#        Workbook workbook = new Workbook();
#        Worksheet worksheet = workbook.Worksheets[0];
#        //Initialize the Object Array
#        object[] array = new object[4] { "Total Income", "Actual Expense", "Expected Expenses", "Profit" };
#        //Insert the Object Array to Sheet
#        worksheet.InsertArray(array, 1, 1, true);
#        //Save to file
#        workbook.SaveToFile(InsertArray.xlsx");
#        </code>
#        </example>
#    </summary>
#    <param name="arrObject">Array to import.</param>
#    <param name="firstRow">The row number of the first cell to import in.</param>
#    <param name="firstColumn">The column number of the first cell to import in.</param>
#    <param name="isVertical">TRUE if array should be imported vertically; FALSE - horizontally.</param>
#    <returns>Number of imported elements.</returns>
#        """
#        #arrayobjectArray:ArrayTypeobjectArray = ""
#        countobjectArray = len(objectArray)
#        ArrayTypeobjectArray = c_void_p * countobjectArray
#        arrayobjectArray = ArrayTypeobjectArray()
#        for i in range(0, countobjectArray):
#            arrayobjectArray[i] = objectArray[i].Ptr
#
#
#        GetDllLibXls().XlsWorksheet_InsertArrayOFFN.argtypes=[c_void_p ,ArrayTypeobjectArray,c_int,c_int,c_bool]
#        GetDllLibXls().XlsWorksheet_InsertArrayOFFN.restype=c_int
#        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertArrayOFFN, self.Ptr, arrayobjectArray,firstRow,firstColumn,needConvert)
#        return ret


    @dispatch

    def InsertArray(self ,stringArray:List[str],firstRow:int,firstColumn:int,isVertical:bool)->int:
        """
        Imports an array of strings into a worksheet.

        Args:
            stringArray: String array.
            firstRow: The row number of the first cell to import in.
            firstColumn: The column number of the first cell to import in.
            isVertical: Specifies to import data vertically or horizontally.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Initialize the string Array
            string[] arrayString = new string[4] { "Total Income", "Actual Expense", "Expected Expenses", "Profit" }
            #Insert the string Array to Sheet
            worksheet.InsertArray(arrayString, 1, 1, true)
            #Save to file
            workbook.SaveToFile(InsertArray.xlsx")

        """
        #arraystringArray:ArrayTypestringArray = ""
        countstringArray = len(stringArray)
        ArrayTypestringArray = c_wchar_p * countstringArray
        arraystringArray = ArrayTypestringArray()
        for i in range(0, countstringArray):
            arraystringArray[i] = stringArray[i]


        GetDllLibXls().XlsWorksheet_InsertArraySFFI.argtypes=[c_void_p ,ArrayTypestringArray,c_int,c_int,c_int,c_bool]
        GetDllLibXls().XlsWorksheet_InsertArraySFFI.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertArraySFFI, self.Ptr, arraystringArray,countstringArray,firstRow,firstColumn,isVertical)
        return ret

    @dispatch

    def InsertArray(self ,arrObject:List[SpireObject],firstRow:int,firstColumn:int,isVertical:bool)->int:
        """
        Imports an array of objects into a worksheet.

        Args:
            arrObject: Array to import.
            firstRow: The row number of the first cell to import in.
            firstColumn: The column number of the first cell to import in.
            isVertical: TRUE if array should be imported vertically; FALSE - horizontally.

        Returns:
            Number of imported elements.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Initialize the Object Array
            object[] array = new object[4] { "Total Income", "Actual Expense", "Expected Expenses", "Profit" }
            #Insert the Object Array to Sheet
            worksheet.InsertArray(array, 1, 1, true)
            #Save to file
            workbook.SaveToFile(InsertArray.xlsx")

        """
        #arrayarrObject:ArrayTypearrObject = ""
        countarrObject = len(arrObject)
        ArrayTypearrObject = c_void_p * countarrObject
        arrayarrObject = ArrayTypearrObject()
        for i in range(0, countarrObject):
            arrayarrObject[i] = arrObject[i].Ptr


        GetDllLibXls().XlsWorksheet_InsertArrayAFFI.argtypes=[c_void_p ,ArrayTypearrObject,c_int,c_int,c_int,c_bool]
        GetDllLibXls().XlsWorksheet_InsertArrayAFFI.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertArrayAFFI, self.Ptr, arrayarrObject,countarrObject,firstRow,firstColumn,isVertical)
        return ret

#
#    def InsertArrayList(self ,arrayList:'ArrayList',firstRow:int,firstColumn:int,isVertical:bool)->int:
#        """
#    <summary>
#        Imports an arraylist of data into a worksheet. 
#    </summary>
#    <param name="arrayList">Data arraylist.</param>
#    <param name="firstRow">The row number of the first cell to import in.</param>
#    <param name="firstColumn">The column number of the first cell to import in.</param>
#    <param name="isVertical">Specifies to import data vertically or horizontally.</param>
#    <returns></returns>
#        """
#        intPtrarrayList:c_void_p = arrayList.Ptr
#
#        GetDllLibXls().XlsWorksheet_InsertArrayList.argtypes=[c_void_p ,c_void_p,c_int,c_int,c_bool]
#        GetDllLibXls().XlsWorksheet_InsertArrayList.restype=c_int
#        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertArrayList, self.Ptr, intPtrarrayList,firstRow,firstColumn,isVertical)
#        return ret


#
#    def InsertDataColumn(self ,dataColumn:'DataColumn',columnHeaders:bool,firstRow:int,firstColumn:int)->int:
#        """
#    <summary>
#         Imports data column.
#        <example>The following code illustrates how to Imports data from a DataColumn into a worksheet with the specified row and column:
#        <code>
#        //Create worksheet
#        Workbook workbook = new Workbook();
#        Worksheet worksheet = workbook.Worksheets[0];
#        //Create a DataTable
#        System.Data.DataTable table = new System.Data.DataTable();
#        table.Columns.Add("ID", typeof(int));
#                 table.Columns.Add("Item", typeof(string));
#                 table.Columns.Add("Name", typeof(string));
#        table.Rows.Add(1, "Soap", "David");
#                 table.Rows.Add(2, "Paste", "Sam");
#                 table.Rows.Add(3, "Cream", "Christoff");
#        //Insert the DataColumn to worksheet
#        System.Data.DataColumn column = table.Columns[2];
#        worksheet.InsertDataColumn(column, true, 1, 1);
#        //Save to file
#        workbook.SaveToFile(InsertDataColumn.xlsx");
#        </code>
#        </example>
#    </summary>
#    <param name="dataColumn">Data column to import.</param>
#    <param name="columnHeaders">Indicates whether to import field names.</param>
#    <param name="firstRow">Index of the first row.</param>
#    <param name="firstColumn">Index of the first column</param>
#    <returns></returns>
#        """
#        intPtrdataColumn:c_void_p = dataColumn.Ptr
#
#        GetDllLibXls().XlsWorksheet_InsertDataColumn.argtypes=[c_void_p ,c_void_p,c_bool,c_int,c_int]
#        GetDllLibXls().XlsWorksheet_InsertDataColumn.restype=c_int
#        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertDataColumn, self.Ptr, intPtrdataColumn,columnHeaders,firstRow,firstColumn)
#        return ret


#
#    def InsertDataColumns(self ,dataColumns:'DataColumn[]',columnHeaders:bool,firstRow:int,firstColumn:int)->int:
#        """
#    <summary>
#        Imports array of data columns.
#    </summary>
#    <param name="dataColumns">Data columns to import.</param>
#    <param name="columnHeaders">Indicates whether to import field names.</param>
#    <param name="firstRow">Index to the first row.</param>
#    <param name="firstColumn">Index to the first column.</param>
#    <returns></returns>
#        """
#        #arraydataColumns:ArrayTypedataColumns = ""
#        countdataColumns = len(dataColumns)
#        ArrayTypedataColumns = c_void_p * countdataColumns
#        arraydataColumns = ArrayTypedataColumns()
#        for i in range(0, countdataColumns):
#            arraydataColumns[i] = dataColumns[i].Ptr
#
#
#        GetDllLibXls().XlsWorksheet_InsertDataColumns.argtypes=[c_void_p ,ArrayTypedataColumns,c_bool,c_int,c_int]
#        GetDllLibXls().XlsWorksheet_InsertDataColumns.restype=c_int
#        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertDataColumns, self.Ptr, arraydataColumns,columnHeaders,firstRow,firstColumn)
#        return ret


#    @dispatch
#
#    def InsertDataTable(self ,dataTable:'DataTable',columnHeaders:bool,firstRow:int,firstColumn:int)->int:
#        """
#    <summary>
#         Imports data from a DataTable into worksheet.
#        <example>The following code illustrates how to Imports data from a DataTable into a worksheet with the specified row and column:
#        <code>
#        //Create worksheet
#        Workbook workbook = new Workbook();
#        Worksheet worksheet = workbook.Worksheets[0];
#        //Create a DataTable
#        System.Data.DataTable table = new System.Data.DataTable();
#        table.Columns.Add("ID", typeof(int));
#                 table.Columns.Add("Item", typeof(string));
#                 table.Columns.Add("Name", typeof(string));
#        table.Rows.Add(1, "Soap", "David");
#                 table.Rows.Add(2, "Paste", "Sam");
#                 table.Rows.Add(3, "Cream", "Christoff");
#        //Insert the DataTable to worksheet
#        worksheet.InsertDataTable(table, true, 1, 1);
#        //Save to file
#        workbook.SaveToFile(InsertDataTable.xlsx");
#        </code>
#        </example>
#    </summary>
#    <param name="dataTable">DataTable</param>
#    <param name="columnHeaders">Indicates whether to import field names.</param>
#    <param name="firstRow">The row number of the first cell to import in.</param>
#    <param name="firstColumn">The column number of the first cell to import in.</param>
#    <returns></returns>
#        """
#        intPtrdataTable:c_void_p = dataTable.Ptr
#
#        GetDllLibXls().XlsWorksheet_InsertDataTable.argtypes=[c_void_p ,c_void_p,c_bool,c_int,c_int]
#        GetDllLibXls().XlsWorksheet_InsertDataTable.restype=c_int
#        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertDataTable, self.Ptr, intPtrdataTable,columnHeaders,firstRow,firstColumn)
#        return ret


#    @dispatch
#
#    def InsertDataTable(self ,dataTable:'DataTable',columnHeaders:bool,firstRow:int,firstColumn:int,transTypes:bool)->int:
#        """
#    <summary>
#         Imports data from a DataTable into worksheet.
#        <example>The following code illustrates how to Imports data from a DataTable into a worksheet with the specified row and column along with the preserve type:
#        <code>
#        //Create worksheet
#        Workbook workbook = new Workbook();
#        Worksheet worksheet = workbook.Worksheets[0];
#        //Create a DataTable
#        System.Data.DataTable table = new System.Data.DataTable();
#        table.Columns.Add("ID", typeof(int));
#                 table.Columns.Add("Item", typeof(string));
#                 table.Columns.Add("Name", typeof(string));
#        table.Rows.Add(1, "Soap", "David");
#                 table.Rows.Add(2, "Paste", "Sam");
#                 table.Rows.Add(3, "Cream", "Christoff");
#        //Insert the DataTable to worksheet
#        worksheet.InsertDataTable(table, true, 1, 1 , true);
#        //Save to file
#        workbook.SaveToFile(InsertDataTable.xlsx");
#        </code>
#        </example>
#    </summary>
#    <param name="dataTable">DataTable</param>
#    <param name="columnHeaders">Indicates whether to import field names.</param>
#    <param name="firstRow">The row number of the first cell to import in.</param>
#    <param name="firstColumn">The column number of the first cell to import in.</param>
#    <param name="transTypes">Indicates if preserve types when insert data into worksheet </param>
#    <returns></returns>
#        """
#        intPtrdataTable:c_void_p = dataTable.Ptr
#
#        GetDllLibXls().XlsWorksheet_InsertDataTableDCFFT.argtypes=[c_void_p ,c_void_p,c_bool,c_int,c_int,c_bool]
#        GetDllLibXls().XlsWorksheet_InsertDataTableDCFFT.restype=c_int
#        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertDataTableDCFFT, self.Ptr, intPtrdataTable,columnHeaders,firstRow,firstColumn,transTypes)
#        return ret


#    @dispatch
#
#    def InsertDataTable(self ,dataTable:'DataTable',columnHeaders:bool,firstRow:int,firstColumn:int,maxRows:int,maxColumns:int)->int:
#        """
#    <summary>
#         Imports data from a DataTable into worksheet.
#        <example>The following code illustrates how to Imports data from a DataTable into a worksheet with the specified range:
#        <code>
#        //Create worksheet
#        Workbook workbook = new Workbook();
#        Worksheet worksheet = workbook.Worksheets[0];
#        //Create a DataTable
#        System.Data.DataTable table = new System.Data.DataTable();
#        table.Columns.Add("ID", typeof(int));
#                 table.Columns.Add("Item", typeof(string));
#                 table.Columns.Add("Name", typeof(string));
#        table.Rows.Add(1, "Soap", "David");
#                 table.Rows.Add(2, "Paste", "Sam");
#                 table.Rows.Add(3, "Cream", "Christoff");
#        //Insert the DataTable to worksheet
#        worksheet.InsertDataTable(table, true, 1 , 1 , 2 , 2);
#        //Save to file
#        workbook.SaveToFile(InsertDataTable.xlsx");
#        </code>
#        </example>
#    </summary>
#    <param name="dataTable">DataTable</param>
#    <param name="columnHeaders">Indicates whether to import field names.</param>
#    <param name="firstRow">The row number of the first cell to import in.</param>
#    <param name="firstColumn">The column number of the first cell to import in.</param>
#    <param name="maxRows">Maximum number of rows to import</param>
#    <param name="maxColumns">Maximum number of columns to import</param>
#    <returns></returns>
#        """
#        intPtrdataTable:c_void_p = dataTable.Ptr
#
#        GetDllLibXls().XlsWorksheet_InsertDataTableDCFFMM.argtypes=[c_void_p ,c_void_p,c_bool,c_int,c_int,c_int,c_int]
#        GetDllLibXls().XlsWorksheet_InsertDataTableDCFFMM.restype=c_int
#        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertDataTableDCFFMM, self.Ptr, intPtrdataTable,columnHeaders,firstRow,firstColumn,maxRows,maxColumns)
#        return ret


#    @dispatch
#
#    def InsertDataTable(self ,dataTable:'DataTable',columnHeaders:bool,firstRow:int,firstColumn:int,maxRows:int,maxColumns:int,transTypes:bool)->int:
#        """
#    <summary>
#         Imports data from a DataTable into worksheet.
#        <example>The following code illustrates how to Imports data from a DataTable into a worksheet with specified range along with preserve type:
#        <code>
#        //Create worksheet
#        Workbook workbook = new Workbook();
#        Worksheet worksheet = workbook.Worksheets[0];
#        //Create a DataTable
#        System.Data.DataTable table = new System.Data.DataTable();
#        table.Columns.Add("ID", typeof(int));
#                 table.Columns.Add("Item", typeof(string));
#                 table.Columns.Add("Name", typeof(string));
#        table.Rows.Add(1, "Soap", "David");
#                 table.Rows.Add(2, "Paste", "Sam");
#                 table.Rows.Add(3, "Cream", "Christoff");
#        //Insert the DataTable to worksheet
#        worksheet.InsertDataTable(table, true, 1 , 1 , 2 , 2 , true);
#        //Save to file
#        workbook.SaveToFile(InsertDataTable.xlsx");
#        </code>
#        </example>
#    </summary>
#    <param name="dataTable">Datatable</param>
#    <param name="columnHeaders">Indicates whether to import field names.</param>
#    <param name="firstRow">The row number of the first cell to import in.</param>
#    <param name="firstColumn">The column number of the first cell to import in.</param>
#    <param name="maxRows">Maximum number of rows to import</param>
#    <param name="maxColumns">Maximum number of columns to import</param>
#    <param name="transTypes">Indicates if preserve types when insert data into worksheet </param>
#    <returns></returns>
#        """
#        intPtrdataTable:c_void_p = dataTable.Ptr
#
#        GetDllLibXls().XlsWorksheet_InsertDataTableDCFFMMT.argtypes=[c_void_p ,c_void_p,c_bool,c_int,c_int,c_int,c_int,c_bool]
#        GetDllLibXls().XlsWorksheet_InsertDataTableDCFFMMT.restype=c_int
#        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertDataTableDCFFMMT, self.Ptr, intPtrdataTable,columnHeaders,firstRow,firstColumn,maxRows,maxColumns,transTypes)
#        return ret


#    @dispatch
#
#    def InsertDataTable(self ,dataTable:'DataTable',columnHeaders:bool,firstRow:int,firstColumn:int,maxRows:int,maxColumns:int,columnsArray:'DataColumn[]',transTypes:bool)->int:
#        """
#    <summary>
#        Imports data from a DataTable into worksheet
#    </summary>
#    <param name="dataTable">DataTable</param>
#    <param name="columnHeaders">Indicates whether to import field names.</param>
#    <param name="firstRow">The row number of the first cell to import in.</param>
#    <param name="firstColumn">The column number of the first cell to import in.</param>
#    <param name="maxRows">Maximum number of rows to import</param>
#    <param name="maxColumns">Maximum number of columns to import</param>
#    <param name="columnsArray">Array of columns to import.</param>
#    <param name="transTypes">Indicates if preserve types when insert data into worksheet.true is default</param>
#    <returns></returns>
#        """
#        intPtrdataTable:c_void_p = dataTable.Ptr
#        #arraycolumnsArray:ArrayTypecolumnsArray = ""
#        countcolumnsArray = len(columnsArray)
#        ArrayTypecolumnsArray = c_void_p * countcolumnsArray
#        arraycolumnsArray = ArrayTypecolumnsArray()
#        for i in range(0, countcolumnsArray):
#            arraycolumnsArray[i] = columnsArray[i].Ptr
#
#
#        GetDllLibXls().XlsWorksheet_InsertDataTableDCFFMMCT.argtypes=[c_void_p ,c_void_p,c_bool,c_int,c_int,c_int,c_int,ArrayTypecolumnsArray,c_bool]
#        GetDllLibXls().XlsWorksheet_InsertDataTableDCFFMMCT.restype=c_int
#        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertDataTableDCFFMMCT, self.Ptr, intPtrdataTable,columnHeaders,firstRow,firstColumn,maxRows,maxColumns,arraycolumnsArray,transTypes)
#        return ret


#    @dispatch
#
#    def InsertDataView(self ,dataView:'DataView',columnHeaders:bool,firstRow:int,firstColumn:int)->int:
#        """
#    <summary>
#         Imports data from a DataView into worksheet.
#        <example>The following code illustrates how to Imports data from a DataView into a worksheet with the specified row and column:
#        <code>
#        //Create worksheet
#        Workbook workbook = new Workbook();
#        Worksheet worksheet = workbook.Worksheets[0];
#        //Create a DataTable
#        System.Data.DataTable table = new System.Data.DataTable();
#        table.Columns.Add("ID", typeof(int));
#                 table.Columns.Add("Item", typeof(string));
#                 table.Columns.Add("Name", typeof(string));
#        table.Rows.Add(1, "Soap", "David");
#                 table.Rows.Add(2, "Paste", "Sam");
#                 table.Rows.Add(3, "Cream", "Christoff");
#        //Initialize dataview of datatable
#        System.Data.DataView view = table.DefaultView;
#        //Import data from DataView
#        worksheet.InsertDataView(view, true, 1, 1);
#        //Save to file
#        workbook.SaveToFile(InsertDataView.xlsx");
#        </code>
#        </example>
#    </summary>
#    <param name="dataView">Data view object</param>
#    <param name="columnHeaders">Indicates whether to import field names.</param>
#    <param name="firstRow">The row number of the first cell to import in.</param>
#    <param name="firstColumn">The column number of the first cell to import in.</param>
#    <returns></returns>
#        """
#        intPtrdataView:c_void_p = dataView.Ptr
#
#        GetDllLibXls().XlsWorksheet_InsertDataView.argtypes=[c_void_p ,c_void_p,c_bool,c_int,c_int]
#        GetDllLibXls().XlsWorksheet_InsertDataView.restype=c_int
#        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertDataView, self.Ptr, intPtrdataView,columnHeaders,firstRow,firstColumn)
#        return ret


#    @dispatch
#
#    def InsertDataView(self ,dataView:'DataView',columnHeaders:bool,firstRow:int,firstColumn:int,transTypes:bool)->int:
#        """
#    <summary>
#         Imports data from a DataView into worksheet.
#        <example>The following code illustrates how to Imports data from a DataView into a worksheet with the specified row and column along with preserve type:
#        <code>
#        //Create worksheet
#        Workbook workbook = new Workbook();
#        Worksheet worksheet = workbook.Worksheets[0];
#        //Create a DataTable
#        System.Data.DataTable table = new System.Data.DataTable();
#        table.Columns.Add("ID", typeof(int));
#                 table.Columns.Add("Item", typeof(string));
#                 table.Columns.Add("Name", typeof(string));
#        table.Rows.Add(1, "Soap", "David");
#                 table.Rows.Add(2, "Paste", "Sam");
#                 table.Rows.Add(3, "Cream", "Christoff");
#        //Initialize dataview of datatable
#        System.Data.DataView view = table.DefaultView;
#        //Import data from DataView
#        worksheet.InsertDataView(view, true, 1, 1 , true);
#        //Save to file
#        workbook.SaveToFile(InsertDataView.xlsx");
#        </code>
#        </example>
#    </summary>
#    <param name="dataView">Dataview object.</param>
#    <param name="columnHeaders">Indicates whether to import field names.</param>
#    <param name="firstRow">The row number of the first cell to import in.</param>
#    <param name="firstColumn">The column number of the first cell to import in.</param>
#    <param name="transTypes">Indicates if preserve types when insert data into worksheet.</param>
#    <returns></returns>
#        """
#        intPtrdataView:c_void_p = dataView.Ptr
#
#        GetDllLibXls().XlsWorksheet_InsertDataViewDCFFT.argtypes=[c_void_p ,c_void_p,c_bool,c_int,c_int,c_bool]
#        GetDllLibXls().XlsWorksheet_InsertDataViewDCFFT.restype=c_int
#        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertDataViewDCFFT, self.Ptr, intPtrdataView,columnHeaders,firstRow,firstColumn,transTypes)
#        return ret


#    @dispatch
#
#    def InsertDataView(self ,dataView:'DataView',columnHeaders:bool,firstRow:int,firstColumn:int,maxRows:int,maxColumns:int)->int:
#        """
#    <summary>
#         Imports data from a DataView into worksheet.
#        <example>The following code illustrates how to Imports data from a DataView into a worksheet with the specified range:
#        <code>
#        //Create worksheet
#        Workbook workbook = new Workbook();
#        Worksheet worksheet = workbook.Worksheets[0];
#        //Create a DataTable
#        System.Data.DataTable table = new System.Data.DataTable();
#        table.Columns.Add("ID", typeof(int));
#                 table.Columns.Add("Item", typeof(string));
#                 table.Columns.Add("Name", typeof(string));
#        table.Rows.Add(1, "Soap", "David");
#                 table.Rows.Add(2, "Paste", "Sam");
#                 table.Rows.Add(3, "Cream", "Christoff");
#        //Initialize dataview of datatable
#        System.Data.DataView view = table.DefaultView;
#        //Import data from DataView
#        worksheet.InsertDataView(view, true, 1, 1 , 2 , 2);
#        //Save to file
#        workbook.SaveToFile(InsertDataView.xlsx");
#        </code>
#        </example>
#    </summary>
#    <param name="dataView">Dataview object.</param>
#    <param name="columnHeaders">Indicates whether to import field names.</param>
#    <param name="firstRow">The row number of the first cell to import in.</param>
#    <param name="firstColumn">The column number of the first cell to import in.</param>
#    <param name="maxRows">Maximum number of rows to import.</param>
#    <param name="maxColumns">Maximum number of columns to import.</param>
#    <returns></returns>
#        """
#        intPtrdataView:c_void_p = dataView.Ptr
#
#        GetDllLibXls().XlsWorksheet_InsertDataViewDCFFMM.argtypes=[c_void_p ,c_void_p,c_bool,c_int,c_int,c_int,c_int]
#        GetDllLibXls().XlsWorksheet_InsertDataViewDCFFMM.restype=c_int
#        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertDataViewDCFFMM, self.Ptr, intPtrdataView,columnHeaders,firstRow,firstColumn,maxRows,maxColumns)
#        return ret


#    @dispatch
#
#    def InsertDataView(self ,dataView:'DataView',columnHeaders:bool,firstRow:int,firstColumn:int,maxRows:int,maxColumns:int,transTypes:bool)->int:
#        """
#    <summary>
#         Imports data from a DataView into worksheet.
#        <example>The following code illustrates how to Imports data from a DataView into a worksheet with the specified range along with preserve type:
#        <code>
#        //Create worksheet
#        Workbook workbook = new Workbook();
#        Worksheet worksheet = workbook.Worksheets[0];
#        //Create a DataTable
#        System.Data.DataTable table = new System.Data.DataTable();
#        table.Columns.Add("ID", typeof(int));
#                 table.Columns.Add("Item", typeof(string));
#                 table.Columns.Add("Name", typeof(string));
#        table.Rows.Add(1, "Soap", "David");
#                 table.Rows.Add(2, "Paste", "Sam");
#                 table.Rows.Add(3, "Cream", "Christoff");
#        //Initialize dataview of datatable
#        System.Data.DataView view = table.DefaultView;
#        //Import data from DataView
#        worksheet.InsertDataView(view, true, 1, 1 , 2 , 2 , true);
#        //Save to file
#        workbook.SaveToFile(InsertDataView.xlsx");
#        </code>
#        </example>
#    </summary>
#    <param name="dataView">Dataview object.</param>
#    <param name="columnHeaders">Indicates whether to import field names.</param>
#    <param name="firstRow">The row number of the first cell to import in.</param>
#    <param name="firstColumn">The column number of the first cell to import in.</param>
#    <param name="maxRows">Maximum number of rows to import.</param>
#    <param name="maxColumns">Maximum number of columns to import.</param>
#    <param name="transTypes">Indicates if preserve types when insert data into worksheet.</param>
#    <returns></returns>
#        """
#        intPtrdataView:c_void_p = dataView.Ptr
#
#        GetDllLibXls().XlsWorksheet_InsertDataViewDCFFMMT.argtypes=[c_void_p ,c_void_p,c_bool,c_int,c_int,c_int,c_int,c_bool]
#        GetDllLibXls().XlsWorksheet_InsertDataViewDCFFMMT.restype=c_int
#        ret = CallCFunction(GetDllLibXls().XlsWorksheet_InsertDataViewDCFFMMT, self.Ptr, intPtrdataView,columnHeaders,firstRow,firstColumn,maxRows,maxColumns,transTypes)
#        return ret


    @dispatch

    def ImportCustomObjects(self ,list:ICollection,firstRow:int,firstColumn:int,options:ImportObjectOptions)->int:
        """

        """
        intPtrlist:c_void_p = list.Ptr
        intPtroptions:c_void_p = options.Ptr

        GetDllLibXls().XlsWorksheet_ImportCustomObjects.argtypes=[c_void_p ,c_void_p,c_int,c_int,c_void_p]
        GetDllLibXls().XlsWorksheet_ImportCustomObjects.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_ImportCustomObjects, self.Ptr, intPtrlist,firstRow,firstColumn,intPtroptions)
        return ret

    @dispatch

    def ImportCustomObjects(self ,list:ICollection,propertyNames:List[str],isPropertyNameShown:bool,firstRow:int,firstColumn:int,rowNumber:int,insertRows:bool,dateFormatString:str,convertStringToNumber:bool)->int:
        """

        """
        intPtrlist:c_void_p = list.Ptr
        #arraypropertyNames:ArrayTypepropertyNames = ""
        countpropertyNames = len(propertyNames)
        ArrayTypepropertyNames = c_wchar_p * countpropertyNames
        arraypropertyNames = ArrayTypepropertyNames()
        for i in range(0, countpropertyNames):
            arraypropertyNames[i] = propertyNames[i]


        GetDllLibXls().XlsWorksheet_ImportCustomObjectsLPIFFRIDC.argtypes=[c_void_p ,c_void_p,ArrayTypepropertyNames,c_int,c_bool,c_int,c_int,c_int,c_bool,c_void_p,c_bool]
        GetDllLibXls().XlsWorksheet_ImportCustomObjectsLPIFFRIDC.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_ImportCustomObjectsLPIFFRIDC, self.Ptr, intPtrlist,arraypropertyNames,countpropertyNames,isPropertyNameShown,firstRow,firstColumn,rowNumber,insertRows,dateFormatString,convertStringToNumber)
        return ret


    def IsColumnVisible(self ,columnIndex:int)->bool:
        """
        Indicates whether column is visible.

        Args:
            columnIndex: Column index.

        Returns:
            true - visible, otherwise false.

        """
        
        GetDllLibXls().XlsWorksheet_IsColumnVisible.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsWorksheet_IsColumnVisible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_IsColumnVisible, self.Ptr, columnIndex)
        return ret


    def IsExternalFormula(self ,row:int,column:int)->bool:
        """
        Indicates is formula in cell is formula to external workbook.

        Args:
            row: Represents row index.
            column: Represents column index.

        Returns:
            If contain extern formula returns true; otherwise false.

        """
        
        GetDllLibXls().XlsWorksheet_IsExternalFormula.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_IsExternalFormula.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_IsExternalFormula, self.Ptr, row,column)
        return ret


    def IsRowVisible(self ,rowIndex:int)->bool:
        """
        Indicates whether row is visible.

        Args:
            rowIndex: Row index.

        Returns:
            true - visible, otherwise false.

        """
        
        GetDllLibXls().XlsWorksheet_IsRowVisible.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsWorksheet_IsRowVisible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_IsRowVisible, self.Ptr, rowIndex)
        return ret

    @dispatch

    def AutoFitColumn(self ,columnIndex:int):
        """
        Autofit the column width.

        Args:
            columnIndex: Column index.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["A1"].Text = "Sample text in cell"
            #Set auto fit
            worksheet.AutoFitColumn(1)
            #Save to file
            workbook.SaveToFile("AutoFitColumn.xlsx")

        """
        
        GetDllLibXls().XlsWorksheet_AutoFitColumn.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_AutoFitColumn, self.Ptr, columnIndex)

    @dispatch

    def AutoFitColumn(self ,columnIndex:int,options:AutoFitterOptions):
        """
        Autofit the column width.

        Args:
            columnIndex: Column index.
            options: auto fit options

        """
        intPtroptions:c_void_p = options.Ptr

        GetDllLibXls().XlsWorksheet_AutoFitColumnCO.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_AutoFitColumnCO, self.Ptr, columnIndex,intPtroptions)

    @dispatch

    def AutoFitColumn(self ,columnIndex:int,firstRow:int,lastRow:int):
        """
        Autofit the column width.

        Args:
            columnIndex: Column index.
            firstRow: One-based index of the first row to be used for autofit operation.
            lastRow: One-based index of the last row to be used for autofit operation.

        """
        
        GetDllLibXls().XlsWorksheet_AutoFitColumnCFL.argtypes=[c_void_p ,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_AutoFitColumnCFL, self.Ptr, columnIndex,firstRow,lastRow)

    @dispatch

    def AutoFitColumn(self ,columnIndex:int,firstRow:int,lastRow:int,options:AutoFitterOptions):
        """
        Autofit the column width.

        Args:
            columnIndex: Column index.
            firstRow: One-based index of the first row to be used for autofit operation.
            lastRow: One-based index of the last row to be used for autofit operation.
            options: auto fit options

        """
        intPtroptions:c_void_p = options.Ptr

        GetDllLibXls().XlsWorksheet_AutoFitColumnCFLO.argtypes=[c_void_p ,c_int,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_AutoFitColumnCFLO, self.Ptr, columnIndex,firstRow,lastRow,intPtroptions)

    @dispatch

    def AutoFitRow(self ,rowIndex:int):
        """
        Autofit the row height.

        Args:
            rowIndex: Row index
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["C2"].Value = "Sample text"
            #Set Style
            style = workbook.Styles.Add("CustomStyle")
            font = style.Font
            font.Size = 18
            worksheet["C2"].Style = style
            #Set auto fit
            worksheet.AutoFitRow(2)
            #Save to file
            workbook.SaveToFile("AutoFitRow.xlsx")

        """
        
        GetDllLibXls().XlsWorksheet_AutoFitRow.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_AutoFitRow, self.Ptr, rowIndex)

    @dispatch

    def AutoFitRow(self ,rowIndex:int,firstColumn:int,lastColumn:int,options:AutoFitterOptions):
        """
        Autofit the row height.

        Args:
            rowIndex: Row index
            firstColumn: One-based index of the first column to be used for autofit operation.
            lastColumn: One-based index of the last column to be used for autofit operation.
            options: auto fit options

        """
        intPtroptions:c_void_p = options.Ptr

        GetDllLibXls().XlsWorksheet_AutoFitRowRFLO.argtypes=[c_void_p ,c_int,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_AutoFitRowRFLO, self.Ptr, rowIndex,firstColumn,lastColumn,intPtroptions)

    @dispatch

    def AutoFitRow(self ,rowIndex:int,firstColumn:int,lastColumn:int,bRaiseEvents:bool):
        """
        Autofit the row height.

        Args:
            rowIndex: Row index
            firstColumn: One-based index of the first column to be used for autofit operation.
            lastColumn: One-based index of the last column to be used for autofit operation.
            bRaiseEvents: If true then raise events.

        """
        
        GetDllLibXls().XlsWorksheet_AutoFitRowRFLB.argtypes=[c_void_p ,c_int,c_int,c_int,c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_AutoFitRowRFLB, self.Ptr, rowIndex,firstColumn,lastColumn,bRaiseEvents)

    @dispatch

    def AutoFitRow(self ,rowIndex:int,firstColumn:int,lastColumn:int,bRaiseEvents:bool,options:AutoFitterOptions):
        """
        Autofit the row height.

        Args:
            rowIndex: Row index
            firstColumn: One-based index of the first column to be used for autofit operation.
            lastColumn: One-based index of the last column to be used for autofit operation.
            bRaiseEvents: If true then raise events.
            options: auto fit options

        """
        intPtroptions:c_void_p = options.Ptr

        GetDllLibXls().XlsWorksheet_AutoFitRowRFLBO.argtypes=[c_void_p ,c_int,c_int,c_int,c_bool,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_AutoFitRowRFLBO, self.Ptr, rowIndex,firstColumn,lastColumn,bRaiseEvents,intPtroptions)


    def CheckExistence(self ,row:int,column:int)->bool:
        """
        Indicates whether cell has been initialized.

        Args:
            row: Row index.
            column: Column index.

        Returns:
            Value indicating whether the cell was initialized or accessed by the user.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet.Range["A1"].Text = "Hello"
            #Check the cell.Output will be true.
            Console.Write(worksheet.CheckExistence(1, 1))
            #Save to file
            workbook.SaveToFile("CheckExistence.xlsx")

        """
        
        GetDllLibXls().XlsWorksheet_CheckExistence.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_CheckExistence.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_CheckExistence, self.Ptr, row,column)
        return ret

    def Clear(self):
        """
        Clears data the worksheet.

        """
        GetDllLibXls().XlsWorksheet_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_Clear, self.Ptr)

    def ClearData(self):
        """
        Clears contents of a range.

        """
        GetDllLibXls().XlsWorksheet_ClearData.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_ClearData, self.Ptr)


    def ColumnWidthToPixels(self ,widthInChars:float)->int:
        """

        """
        
        GetDllLibXls().XlsWorksheet_ColumnWidthToPixels.argtypes=[c_void_p ,c_double]
        GetDllLibXls().XlsWorksheet_ColumnWidthToPixels.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_ColumnWidthToPixels, self.Ptr, widthInChars)
        return ret

#
#    def CopyFrom(self ,worksheet:'XlsWorksheet',hashStyleNames:'Dictionary2',hashWorksheetNames:'Dictionary2',dicFontIndexes:'Dictionary2',flags:'WorksheetCopyType',hashExtFormatIndexes:'Dictionary2',hashNameIndexes:'Dictionary2',hashExternSheets:'Dictionary2'):
#        """
#
#        """
#        intPtrworksheet:c_void_p = worksheet.Ptr
#        intPtrhashStyleNames:c_void_p = hashStyleNames.Ptr
#        intPtrhashWorksheetNames:c_void_p = hashWorksheetNames.Ptr
#        intPtrdicFontIndexes:c_void_p = dicFontIndexes.Ptr
#        enumflags:c_int = flags.value
#        intPtrhashExtFormatIndexes:c_void_p = hashExtFormatIndexes.Ptr
#        intPtrhashNameIndexes:c_void_p = hashNameIndexes.Ptr
#        intPtrhashExternSheets:c_void_p = hashExternSheets.Ptr
#
#        GetDllLibXls().XlsWorksheet_CopyFrom.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_void_p,c_int,c_void_p,c_void_p,c_void_p]
#        CallCFunction(GetDllLibXls().XlsWorksheet_CopyFrom, self.Ptr, intPtrworksheet,intPtrhashStyleNames,intPtrhashWorksheetNames,intPtrdicFontIndexes,enumflags,intPtrhashExtFormatIndexes,intPtrhashNameIndexes,intPtrhashExternSheets)



    def GetCellType(self ,row:int,column:int,bNeedFormulaSubType:bool)->'TRangeValueType':
        """
        Gets cell type from current column.

        Args:
            row: Indicates row.
            column: Indicates column.
            bNeedFormulaSubType: Indicates is need to indified formula sub type.

        Returns:
            Returns cell type.

        """
        
        GetDllLibXls().XlsWorksheet_GetCellType.argtypes=[c_void_p ,c_int,c_int,c_bool]
        GetDllLibXls().XlsWorksheet_GetCellType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_GetCellType, self.Ptr, row,column,bNeedFormulaSubType)
        objwraped = TRangeValueType(ret)
        return objwraped

#
#    def GetClonedObject(self ,hashNewNames:'Dictionary2',book:'XlsWorkbook')->'IInternalWorksheet':
#        """
#
#        """
#        intPtrhashNewNames:c_void_p = hashNewNames.Ptr
#        intPtrbook:c_void_p = book.Ptr
#
#        GetDllLibXls().XlsWorksheet_GetClonedObject.argtypes=[c_void_p ,c_void_p,c_void_p]
#        GetDllLibXls().XlsWorksheet_GetClonedObject.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_GetClonedObject, self.Ptr, intPtrhashNewNames,intPtrbook)
#        ret = None if intPtr==None else IInternalWorksheet(intPtr)
#        return ret
#


    @dispatch

    def GetStringValue(self ,cellIndex:int)->str:
        """
        Returns string value corresponding to the cell.

        Args:
            iCellIndex: Cell index to get value from.

        Returns:
            String contained by the cell.

        """
        
        GetDllLibXls().XlsWorksheet_GetStringValue.argtypes=[c_void_p ,c_long]
        GetDllLibXls().XlsWorksheet_GetStringValue.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorksheet_GetStringValue, self.Ptr, cellIndex))
        return ret


    @dispatch

    def GetStringValue(self ,row:int,column:int)->str:
        """
        Returns string value corresponding to the cell.

        Args:
            row: Represents row index.
            column: Represents column index.

        Returns:
            String contained by the cell.

        """
        
        GetDllLibXls().XlsWorksheet_GetStringValueRC.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_GetStringValueRC.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorksheet_GetStringValueRC, self.Ptr, row,column))
        return ret


    @dispatch

    def GetTextObject(self ,cellIndex:int)->SpireObject:
        """
        Returns TextWithFormat object corresponding to the specified cell.

        Args:
            cellIndex: Cell index.

        Returns:
            Object corresponding to the specified cell.

        """
        
        GetDllLibXls().XlsWorksheet_GetTextObject.argtypes=[c_void_p ,c_long]
        GetDllLibXls().XlsWorksheet_GetTextObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_GetTextObject, self.Ptr, cellIndex)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @dispatch

    def GetTextObject(self ,row:int,column:int)->SpireObject:
        """
        Returns TextWithFormat object corresponding to the specified cell.

        Args:
            row: Represents row index.
            column: Represents column index.

        Returns:
            Object corresponding to the specified cell.

        """
        
        GetDllLibXls().XlsWorksheet_GetTextObjectRC.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_GetTextObjectRC.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_GetTextObjectRC, self.Ptr, row,column)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def HasArrayFormula(self ,cellIndex:int)->bool:
        """
        Indicates whether cell contains array-entered formula.

        Args:
            cellIndex: cell index.

        """
        
        GetDllLibXls().XlsWorksheet_HasArrayFormula.argtypes=[c_void_p ,c_long]
        GetDllLibXls().XlsWorksheet_HasArrayFormula.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_HasArrayFormula, self.Ptr, cellIndex)
        return ret


    def HasArrayFormulaRecord(self ,row:int,column:int)->bool:
        """
        Indicates is has array formula.

        Args:
            row: Represents row index.
            column: Represents column index.

        Returns:
            Indicates is contain array formula record.

        """
        
        GetDllLibXls().XlsWorksheet_HasArrayFormulaRecord.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_HasArrayFormulaRecord.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_HasArrayFormulaRecord, self.Ptr, row,column)
        return ret


    def InsertRange(self ,rowIndex:int,columnIndex:int,rowCount:int,columnCount:int,moveOptions:'InsertMoveOption',insertOptions:'InsertOptionsType')->'IXLSRange':
        """
        Insert a cell range into worksheet

        Args:
            rowIndex: the cell range first row index
            columnIndex: the cell range first column index
            rowCount: the number of rows
            columnCount: the number of columns
            moveOptions: Insert options.
            insertOptions: Move the cell on the right to right or Move the cell below down

        Returns:
            return the range that insert into worksheet

        """
        enummoveOptions:c_int = moveOptions.value
        enuminsertOptions:c_int = insertOptions.value

        GetDllLibXls().XlsWorksheet_InsertRange.argtypes=[c_void_p ,c_int,c_int,c_int,c_int,c_int,c_int]
        GetDllLibXls().XlsWorksheet_InsertRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_InsertRange, self.Ptr, rowIndex,columnIndex,rowCount,columnCount,enummoveOptions,enuminsertOptions)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret



    def InsertCutRange(self ,cutRange:'IXLSRange',rowIndex:int,colIndex:int,moveOptions:'InsertMoveOption'):
        """
        Insert cut range into worksheet at specified position.

        Args:
            cutRange: the cut range
            rowIndex: the dest range first row index
            colIndex: the dest range first column index
            moveOptions: insert options.

        """
        intPtrcutRange:c_void_p = cutRange.Ptr
        enummoveOptions:c_int = moveOptions.value

        GetDllLibXls().XlsWorksheet_InsertCutRange.argtypes=[c_void_p ,c_void_p,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_InsertCutRange, self.Ptr, intPtrcutRange,rowIndex,colIndex,enummoveOptions)

    @dispatch

    def IsArrayFormula(self ,cellIndex:int)->bool:
        """

        """
        
        GetDllLibXls().XlsWorksheet_IsArrayFormula.argtypes=[c_void_p ,c_long]
        GetDllLibXls().XlsWorksheet_IsArrayFormula.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_IsArrayFormula, self.Ptr, cellIndex)
        return ret

    @dispatch

    def IsArrayFormula(self ,row:int,column:int)->bool:
        """
        Indicates whether cell contains array-entered formula.

        Args:
            row: Represents row index.
            column: Represents column index.

        Returns:
            True if cell contains array-entered formula.

        """
        
        GetDllLibXls().XlsWorksheet_IsArrayFormulaRC.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_IsArrayFormulaRC.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_IsArrayFormulaRC, self.Ptr, row,column)
        return ret

    def ReparseFormula(self):
        """

        """
        GetDllLibXls().XlsWorksheet_ReparseFormula.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_ReparseFormula, self.Ptr)

    def CopyToClipboard(self):
        """

        """
        GetDllLibXls().XlsWorksheet_CopyToClipboard.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_CopyToClipboard, self.Ptr)


    def CreateRanges(self ,ranges:'ListCellRanges')->'XlsRangesCollection':
        """

        """
        #arrayranges:ArrayTyperanges = ""
        countranges = len(ranges)
        ArrayTyperanges = c_void_p * countranges
        arrayranges = ArrayTyperanges()
        for i in range(0, countranges):
            arrayranges[i] = ranges[i].Ptr


        GetDllLibXls().XlsWorksheet_CreateRanges.argtypes=[c_void_p ,ArrayTyperanges, c_int]
        GetDllLibXls().XlsWorksheet_CreateRanges.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_CreateRanges, self.Ptr, arrayranges, countranges)
        ret = None if intPtr==None else XlsRangesCollection(intPtr)
        return ret




    def CreateNamedRanges(self ,namedRange:str,referRange:str,vertical:bool):
        """

        """
        
        GetDllLibXls().XlsWorksheet_CreateNamedRanges.argtypes=[c_void_p ,c_void_p,c_void_p,c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_CreateNamedRanges, self.Ptr, namedRange,referRange,vertical)

    @dispatch

    def DeleteColumn(self ,index:int):
        """
        Deletes a column.

        Args:
            columnIndex: Column index to remove..

        """
        
        GetDllLibXls().XlsWorksheet_DeleteColumn.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_DeleteColumn, self.Ptr, index)

    @dispatch

    def DeleteColumn(self ,index:int,count:int):
        """
        Removes specified column.

        Args:
            index: One-based column index to remove.
            count: Number of columns to remove.

        """
        
        GetDllLibXls().XlsWorksheet_DeleteColumnIC.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_DeleteColumnIC, self.Ptr, index,count)

    @dispatch

    def DeleteRow(self ,index:int):
        """
        Delete a row.

        Args:
            index: Row index to remove

        """
        
        GetDllLibXls().XlsWorksheet_DeleteRow.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_DeleteRow, self.Ptr, index)

    @dispatch

    def DeleteRow(self ,index:int,count:int):
        """
        Removes specified row.

        Args:
            index: One-based row index to remove
            count: Number of rows to delete.

        """
        
        GetDllLibXls().XlsWorksheet_DeleteRowIC.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_DeleteRowIC, self.Ptr, index,count)

    @dispatch

    def InsertColumn(self ,columnIndex:int):
        """
        Inserts a new column into the worksheet.

        Args:
            columnIndex: Column index

        """
        
        GetDllLibXls().XlsWorksheet_InsertColumn.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_InsertColumn, self.Ptr, columnIndex)

    @dispatch

    def InsertColumn(self ,columnIndex:int,columnCount:int,insertOptions:InsertOptionsType):
        """

        """
        enuminsertOptions:c_int = insertOptions.value

        GetDllLibXls().XlsWorksheet_InsertColumnCCI.argtypes=[c_void_p ,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_InsertColumnCCI, self.Ptr, columnIndex,columnCount,enuminsertOptions)

    @dispatch

    def InsertColumn(self ,columnIndex:int,columnCount:int):
        """
        Inserts specified number column into the worksheet.

        Args:
            columnIndex: Column index
            columnCount: Number of columns to insert.

        """
        
        GetDllLibXls().XlsWorksheet_InsertColumnCC.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_InsertColumnCC, self.Ptr, columnIndex,columnCount)

    @dispatch

    def InsertRow(self ,rowIndex:int):
        """
        Inserts a new row into the worksheet.

        Args:
            rowIndex: Index at which new row should be inserted

        """
        
        GetDllLibXls().XlsWorksheet_InsertRow.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_InsertRow, self.Ptr, rowIndex)

#
#    def ExportDataTable(self)->'DataTable':
#        """
#
#        """
#        GetDllLibXls().XlsWorksheet_ExportDataTable.argtypes=[c_void_p]
#        GetDllLibXls().XlsWorksheet_ExportDataTable.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_ExportDataTable, self.Ptr)
#        ret = None if intPtr==None else DataTable(intPtr)
#        return ret
#


    @dispatch

    def InsertRow(self ,rowIndex:int,rowCount:int,insertOptions:InsertOptionsType):
        """

        """
        enuminsertOptions:c_int = insertOptions.value

        GetDllLibXls().XlsWorksheet_InsertRowRRI.argtypes=[c_void_p ,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_InsertRowRRI, self.Ptr, rowIndex,rowCount,enuminsertOptions)

    @dispatch

    def InsertRow(self ,rowIndex:int,rowCount:int):
        """
        Inserts multiple rows into the worksheet.

        Args:
            rowIndex: Index at which new row should be inserted
            rowCount: Number of rows to be inserted.

        """
        
        GetDllLibXls().XlsWorksheet_InsertRowRR.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_InsertRowRR, self.Ptr, rowIndex,rowCount)


    def GetBoolean(self ,row:int,column:int)->bool:
        """
        Gets bool value from cell.

        Args:
            row: Represents row index.
            column: Represents column index.

        Returns:
            Returns found bool value. If cannot found returns false.

        """
        
        GetDllLibXls().XlsWorksheet_GetBoolean.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_GetBoolean.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_GetBoolean, self.Ptr, row,column)
        return ret


    def GetColumnWidth(self ,columnIndex:int)->float:
        """
        Gets the width of the specified column

        Args:
            columnIndex: Column index

        Returns:
            Width of column

        """
        
        GetDllLibXls().XlsWorksheet_GetColumnWidth.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsWorksheet_GetColumnWidth.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_GetColumnWidth, self.Ptr, columnIndex)
        return ret


    def GetColumnWidthPixels(self ,columnIndex:int)->int:
        """
        Gets the width of the specified column, in units of pixel.

        Args:
            columnIndex: Column index.

        Returns:
            Width of column
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["A1"].Text = "Sample text in cell"
            #Set auto fit
            worksheet.AutoFitColumn(1)
            #Get column width
            print(worksheet.GetColumnWidthPixels(1))
            #Save to file
            workbook.SaveToFile("UsedRange.xlsx")

        """
        
        GetDllLibXls().XlsWorksheet_GetColumnWidthPixels.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsWorksheet_GetColumnWidthPixels.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_GetColumnWidthPixels, self.Ptr, columnIndex)
        return ret


    def GetDefaultColumnStyle(self ,columnIndex:int)->'IStyle':
        """

        """
        
        GetDllLibXls().XlsWorksheet_GetDefaultColumnStyle.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsWorksheet_GetDefaultColumnStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_GetDefaultColumnStyle, self.Ptr, columnIndex)
        ret = None if intPtr==None else CellStyle(intPtr)
        return ret



    def add_CellValueChanged(self ,value:'CellValueChangedEventHandler'):
        """

        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibXls().XlsWorksheet_add_CellValueChanged.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_add_CellValueChanged, self.Ptr, intPtrvalue)


    def remove_CellValueChanged(self ,value:'CellValueChangedEventHandler'):
        """

        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibXls().XlsWorksheet_remove_CellValueChanged.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_remove_CellValueChanged, self.Ptr, intPtrvalue)

    @property
    def Copying(self)->bool:
        """

        """
        GetDllLibXls().XlsWorksheet_get_Copying.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_Copying.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_Copying, self.Ptr)
        return ret

    @Copying.setter
    def Copying(self, value:bool):
        GetDllLibXls().XlsWorksheet_set_Copying.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_Copying, self.Ptr, value)

    @property

    def OleObjects(self)->'IOleObjects':
        """
        Gets the OLE objects.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Create image stream
            System.Drawing.image = System.Drawing.Image.FromFile("image.png")
            #Add ole object
            oleObject = worksheet.OleObjects.Add("Shapes.xlsx", image, OleLinkType.Embed)
            #Save to file
            workbook.SaveToFile("OLEObjects.xlsx")

        """
        GetDllLibXls().XlsWorksheet_get_OleObjects.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_OleObjects.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_OleObjects, self.Ptr)
        ret = None if intPtr==None else IOleObjects(intPtr)
        return ret


    @property

    def AutoFilters(self)->'IAutoFilters':
        """

        """
        GetDllLibXls().XlsWorksheet_get_AutoFilters.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_AutoFilters.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_AutoFilters, self.Ptr)
        ret = None if intPtr==None else IAutoFilters(intPtr)
        return ret


    @property

    def Cells(self)->ListXlsRanges:
        """Gets a collection of all cells in the worksheet.
        
        Returns:
            ListXlsRanges: A collection of XlsRange objects representing all cells in the worksheet.
        """
        GetDllLibXls().XlsWorksheet_get_Cells.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_Cells.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_Cells, self.Ptr)
        ret = None if intPtr==None else ListXlsRanges(intPtr)
        return ret


#    @property
#
#    def CellList(self)->'List1':
#        """
#
#        """
#        GetDllLibXls().XlsWorksheet_get_CellList.argtypes=[c_void_p]
#        GetDllLibXls().XlsWorksheet_get_CellList.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_CellList, self.Ptr)
#        ret = None if intPtr==None else List1(intPtr)
#        return ret
#


    @property
    def DisplayPageBreaks(self)->bool:
        """
        True if page breaks (both automatic and manual) on the specified worksheet are displayed.

        """
        GetDllLibXls().XlsWorksheet_get_DisplayPageBreaks.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_DisplayPageBreaks.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_DisplayPageBreaks, self.Ptr)
        return ret

    @DisplayPageBreaks.setter
    def DisplayPageBreaks(self, value:bool):
        GetDllLibXls().XlsWorksheet_set_DisplayPageBreaks.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_DisplayPageBreaks, self.Ptr, value)

    @property

    def MergedCells(self)->ListXlsRanges:
        """

        """
        GetDllLibXls().XlsWorksheet_get_MergedCells.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_MergedCells.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_MergedCells, self.Ptr)
        ret = None if intPtr==None else ListXlsRanges(intPtr)
        return ret


    @property

    def Names(self)->'INameRanges':
        """
        Name range used by macros to access to workbook items.

        """
        GetDllLibXls().XlsWorksheet_get_Names.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_Names.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_Names, self.Ptr)
        ret = None if intPtr==None else INameRanges(intPtr)
        return ret


    @property

    def PageSetup(self)->'IPageSetup':
        """

        """
        GetDllLibXls().XlsWorksheet_get_PageSetup.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_PageSetup.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_PageSetup, self.Ptr)
        ret = None if intPtr==None else XlsPageSetup(intPtr)
        return ret


    @property

    def MaxDisplayRange(self)->'IXLSRange':
        """

        """
        GetDllLibXls().XlsWorksheet_get_MaxDisplayRange.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_MaxDisplayRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_MaxDisplayRange, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @property

    def AllocatedRange(self)->'IXLSRange':
        """

        """
        GetDllLibXls().XlsWorksheet_get_AllocatedRange.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_AllocatedRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_AllocatedRange, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @property
    def AllocatedRangeIncludesFormatting(self)->bool:
        """

        """
        GetDllLibXls().XlsWorksheet_get_AllocatedRangeIncludesFormatting.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_AllocatedRangeIncludesFormatting.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_AllocatedRangeIncludesFormatting, self.Ptr)
        return ret

    @AllocatedRangeIncludesFormatting.setter
    def AllocatedRangeIncludesFormatting(self, value:bool):
        GetDllLibXls().XlsWorksheet_set_AllocatedRangeIncludesFormatting.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_AllocatedRangeIncludesFormatting, self.Ptr, value)

    @property

    def Rows(self)->ListXlsRanges:
        """Gets a collection of all rows in the worksheet.
        
        Returns:
            ListXlsRanges: A collection of XlsRange objects representing all rows in the worksheet.
        """
        GetDllLibXls().XlsWorksheet_get_Rows.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_Rows.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_Rows, self.Ptr)
        ret = None if intPtr==None else ListXlsRanges(intPtr)
        return ret


    @property

    def Columns(self)->ListXlsRanges:
        """Gets a collection of all columns in the worksheet.
        
        Returns:
            ListXlsRanges: A collection of XlsRange objects representing all columns in the worksheet.
        """
        GetDllLibXls().XlsWorksheet_get_Columns.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_Columns.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_Columns, self.Ptr)
        ret = None if intPtr==None else ListXlsRanges(intPtr)
        return ret


    @property

    def ConditionalFormats(self)->'IConditionalFormatsCollection':
        """
        Returns collection with all conditional formats in the worksheet. Read-only.

        """
        GetDllLibXls().XlsWorksheet_get_ConditionalFormats.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_ConditionalFormats.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_ConditionalFormats, self.Ptr)
        ret = None if intPtr==None else XlsWorksheetConditionalFormats(intPtr)
        return ret


    @property
    def DefaultRowHeight(self)->float:
        """
        Gets or sets default height of all the rows in the worksheet, in points.Read/write Double.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get row height
            Console.Write(worksheet.DefaultRowHeight)
            #Set default height
            worksheet.DefaultRowHeight = 40
            #Save to file
            workbook.SaveToFile("DefaultRowHeight.xlsx")

        """
        GetDllLibXls().XlsWorksheet_get_DefaultRowHeight.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_DefaultRowHeight.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_DefaultRowHeight, self.Ptr)
        return ret

    @DefaultRowHeight.setter
    def DefaultRowHeight(self, value:float):
        GetDllLibXls().XlsWorksheet_set_DefaultRowHeight.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_DefaultRowHeight, self.Ptr, value)

    @property
    def DefaultPrintRowHeight(self)->int:
        """
        Return default row height.

        """
        GetDllLibXls().XlsWorksheet_get_DefaultPrintRowHeight.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_DefaultPrintRowHeight.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_DefaultPrintRowHeight, self.Ptr)
        return ret

    @DefaultPrintRowHeight.setter
    def DefaultPrintRowHeight(self, value:int):
        GetDllLibXls().XlsWorksheet_set_DefaultPrintRowHeight.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_DefaultPrintRowHeight, self.Ptr, value)

    @property

    def ViewMode(self)->'ViewMode':
        """
        Gets or sets the view mode of the sheet.

        """
        GetDllLibXls().XlsWorksheet_get_ViewMode.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_ViewMode.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_ViewMode, self.Ptr)
        objwraped = ViewMode(ret)
        return objwraped

    @ViewMode.setter
    def ViewMode(self, value:'ViewMode'):
        GetDllLibXls().XlsWorksheet_set_ViewMode.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_ViewMode, self.Ptr, value.value)

    @property
    def DefaultColumnWidth(self)->float:
        """
        Returns or sets the default  width of all the columns in the worksheet. Read/write Double.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get column width
            Console.Write(worksheet.DefaultColumnWidth)
            #Set default width
            worksheet.DefaultColumnWidth = 40
            #Save to file
            workbook.SaveToFile("DefaultColumnWidth.xlsx")

        """
        GetDllLibXls().XlsWorksheet_get_DefaultColumnWidth.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_DefaultColumnWidth.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_DefaultColumnWidth, self.Ptr)
        return ret

    @DefaultColumnWidth.setter
    def DefaultColumnWidth(self, value:float):
        GetDllLibXls().XlsWorksheet_set_DefaultColumnWidth.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_DefaultColumnWidth, self.Ptr, value)

    @property
    def Zoom(self)->int:
        """
        Zoom factor of document.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set zoom
            worksheet.Zoom = 200
            #Save to file
            workbook.SaveToFile("Zoom.xlsx")

        """
        GetDllLibXls().XlsWorksheet_get_Zoom.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_Zoom.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_Zoom, self.Ptr)
        return ret

    @Zoom.setter
    def Zoom(self, value:int):
        GetDllLibXls().XlsWorksheet_set_Zoom.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_Zoom, self.Ptr, value)

    @property
    def ZoomScaleNormal(self)->int:
        """
        Gets or sets the zoom scale of normal view of the sheet.

        """
        GetDllLibXls().XlsWorksheet_get_ZoomScaleNormal.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_ZoomScaleNormal.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_ZoomScaleNormal, self.Ptr)
        return ret

    @ZoomScaleNormal.setter
    def ZoomScaleNormal(self, value:int):
        GetDllLibXls().XlsWorksheet_set_ZoomScaleNormal.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_ZoomScaleNormal, self.Ptr, value)

    @property
    def ZoomScalePageBreakView(self)->int:
        """
        Gets or sets the zoom scale of page break preview of the sheet.

        """
        GetDllLibXls().XlsWorksheet_get_ZoomScalePageBreakView.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_ZoomScalePageBreakView.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_ZoomScalePageBreakView, self.Ptr)
        return ret

    @ZoomScalePageBreakView.setter
    def ZoomScalePageBreakView(self, value:int):
        GetDllLibXls().XlsWorksheet_set_ZoomScalePageBreakView.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_ZoomScalePageBreakView, self.Ptr, value)

    @property
    def ZoomScalePageLayoutView(self)->int:
        """
        Gets or sets the zoom scale of page layout view of the sheet.

        """
        GetDllLibXls().XlsWorksheet_get_ZoomScalePageLayoutView.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_ZoomScalePageLayoutView.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_ZoomScalePageLayoutView, self.Ptr)
        return ret

    @ZoomScalePageLayoutView.setter
    def ZoomScalePageLayoutView(self, value:int):
        GetDllLibXls().XlsWorksheet_set_ZoomScalePageLayoutView.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_ZoomScalePageLayoutView, self.Ptr, value)

    @property
    def SelectionCount(self)->int:
        """

        """
        GetDllLibXls().XlsWorksheet_get_SelectionCount.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_SelectionCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_SelectionCount, self.Ptr)
        return ret

    @property

    def Version(self)->'ExcelVersion':
        """
        Gets or sets excel file version.

        """
        GetDllLibXls().XlsWorksheet_get_Version.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_Version.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_Version, self.Ptr)
        objwraped = ExcelVersion(ret)
        return objwraped

    @Version.setter
    def Version(self, value:'ExcelVersion'):
        GetDllLibXls().XlsWorksheet_set_Version.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_Version, self.Ptr, value.value)

    @property

    def SparklineGroups(self)->'SparklineGroupCollection':
        """

        """
        GetDllLibXls().XlsWorksheet_get_SparklineGroups.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_SparklineGroups.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_SparklineGroups, self.Ptr)
        ret = None if intPtr==None else SparklineGroupCollection(intPtr)
        return ret


    @property
    def StandardHeightFlag(self)->bool:
        """
        Gets or sets the standard (default) height option flag, which defines that standard (default) row height and book default font height do not match. Bool.

        """
        GetDllLibXls().XlsWorksheet_get_StandardHeightFlag.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_StandardHeightFlag.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_StandardHeightFlag, self.Ptr)
        return ret

    @StandardHeightFlag.setter
    def StandardHeightFlag(self, value:bool):
        GetDllLibXls().XlsWorksheet_set_StandardHeightFlag.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_StandardHeightFlag, self.Ptr, value)

    @property

    def Type(self)->'ExcelSheetType':
        """

        """
        GetDllLibXls().XlsWorksheet_get_Type.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_Type, self.Ptr)
        objwraped = ExcelSheetType(ret)
        return objwraped

    @property

    def Range(self)->'XlsRange':
        """Gets the range object representing the entire worksheet.
        
        Returns:
            XlsRange: A range object representing the entire worksheet.
        """
        GetDllLibXls().XlsWorksheet_get_Range.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_Range.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_Range, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def get_Item(self ,row:int,column:int)->IXLSRange:
        """

        """
        
        GetDllLibXls().XlsWorksheet_get_Item.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsWorksheet_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_Item, self.Ptr, row,column)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def get_Item(self ,row:int,column:int,lastRow:int,lastColumn:int)->IXLSRange:
        """

        """
        
        GetDllLibXls().XlsWorksheet_get_ItemRCLL.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        GetDllLibXls().XlsWorksheet_get_ItemRCLL.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_ItemRCLL, self.Ptr, row,column,lastRow,lastColumn)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def get_Item(self ,name:str)->IXLSRange:
        """

        """
        
        GetDllLibXls().XlsWorksheet_get_ItemN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsWorksheet_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_ItemN, self.Ptr, name)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @property

    def TopLeftCell(self)->'CellRange':
        """
        Gets top left cell of the worksheet.

        """
        GetDllLibXls().XlsWorksheet_get_TopLeftCell.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_TopLeftCell.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_TopLeftCell, self.Ptr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @TopLeftCell.setter
    def TopLeftCell(self, value:'CellRange'):
        GetDllLibXls().XlsWorksheet_set_TopLeftCell.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_TopLeftCell, self.Ptr, value.Ptr)

    @property
    def UseRangesCache(self)->bool:
        """
        Indicates whether all created range objects should be cached. Default value is true.

        """
        GetDllLibXls().XlsWorksheet_get_UseRangesCache.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_UseRangesCache.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_UseRangesCache, self.Ptr)
        return ret

    @UseRangesCache.setter
    def UseRangesCache(self, value:bool):
        GetDllLibXls().XlsWorksheet_set_UseRangesCache.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_UseRangesCache, self.Ptr, value)

    @property
    def VerticalSplit(self)->int:
        """

        """
        GetDllLibXls().XlsWorksheet_get_VerticalSplit.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_VerticalSplit.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_VerticalSplit, self.Ptr)
        return ret

    @VerticalSplit.setter
    def VerticalSplit(self, value:int):
        GetDllLibXls().XlsWorksheet_set_VerticalSplit.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_VerticalSplit, self.Ptr, value)

    @property

    def VPageBreaks(self)->'IVPageBreaks':
        """

        """
        GetDllLibXls().XlsWorksheet_get_VPageBreaks.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_VPageBreaks.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheet_get_VPageBreaks, self.Ptr)
        ret = None if intPtr==None else IVPageBreaks(intPtr)
        return ret


    @property
    def ActivePane(self)->int:
        """
        Gets or sets index of the active pane.

        """
        GetDllLibXls().XlsWorksheet_get_ActivePane.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_ActivePane.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_ActivePane, self.Ptr)
        return ret

    @ActivePane.setter
    def ActivePane(self, value:int):
        GetDllLibXls().XlsWorksheet_set_ActivePane.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_ActivePane, self.Ptr, value)


    def SetFirstColumn(self ,columnIndex:int):
        """

        """
        
        GetDllLibXls().XlsWorksheet_SetFirstColumn.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetFirstColumn, self.Ptr, columnIndex)


    def SetLastColumn(self ,columnIndex:int):
        """
        Updates last column index.

        Args:
            columnIndex: Column index.

        """
        
        GetDllLibXls().XlsWorksheet_SetLastColumn.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetLastColumn, self.Ptr, columnIndex)


    def SetFirstRow(self ,rowIndex:int):
        """
        Updates first row index.

        Args:
            rowIndex: Row index.

        """
        
        GetDllLibXls().XlsWorksheet_SetFirstRow.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetFirstRow, self.Ptr, rowIndex)


    def SetLastRow(self ,rowIndex:int):
        """
        Updates last row index.

        Args:
            rowIndex: Row index.

        """
        
        GetDllLibXls().XlsWorksheet_SetLastRow.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetLastRow, self.Ptr, rowIndex)


    def ShowColumn(self ,columnIndex:int):
        """
        Shows a column.

        Args:
            columnIndex: Column index.

        """
        
        GetDllLibXls().XlsWorksheet_ShowColumn.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_ShowColumn, self.Ptr, columnIndex)


    def ShowRow(self ,rowIndex:int):
        """

        """
        
        GetDllLibXls().XlsWorksheet_ShowRow.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_ShowRow, self.Ptr, rowIndex)

#    @dispatch

#    def ToEMFStream(self ,stream:Stream,firstRow:int,firstColumn:int,lastRow:int,lastColumn:int,emfType:EmfType):
#        """

#        """
#        intPtrstream:c_void_p = stream.Ptr
#        enumemfType:c_int = emfType.value

#        GetDllLibXls().XlsWorksheet_ToEMFStream.argtypes=[c_void_p ,c_void_p,c_int,c_int,c_int,c_int,c_int]
#        CallCFunction(GetDllLibXls().XlsWorksheet_ToEMFStream, self.Ptr, intPtrstream,firstRow,firstColumn,lastRow,lastColumn,enumemfType)

#    @dispatch

#    def ToEMFStream(self ,stream:Stream,firstRow:int,firstColumn:int,lastRow:int,lastColumn:int):
#        """
#<summary></summary>
#    <param name="stream">stream.</param>
#    <param name="firstRow">One-based index of the first row to convert.</param>
#    <param name="firstColumn">One-based index of the first column to convert.</param>
#    <param name="lastRow">One-based index of the last row to convert.</param>
#    <param name="lastColumn">One-based index of the last column to convert.</param>
#        """
#        intPtrstream:c_void_p = stream.Ptr

#        GetDllLibXls().XlsWorksheet_ToEMFStreamSFFLL.argtypes=[c_void_p ,c_void_p,c_int,c_int,c_int,c_int]
#        CallCFunction(GetDllLibXls().XlsWorksheet_ToEMFStreamSFFLL, self.Ptr, intPtrstream,firstRow,firstColumn,lastRow,lastColumn)

    @dispatch

    def SetActiveCell(self ,range:IXLSRange):
        """

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().XlsWorksheet_SetActiveCell.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetActiveCell, self.Ptr, intPtrrange)

    @dispatch

    def SetActiveCell(self ,range:IXLSRange,updateApplication:bool):
        """

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().XlsWorksheet_SetActiveCellRU.argtypes=[c_void_p ,c_void_p,c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_SetActiveCellRU, self.Ptr, intPtrrange,updateApplication)

    @property
    def FirstVisibleColumn(self)->int:
        """

        """
        GetDllLibXls().XlsWorksheet_get_FirstVisibleColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_FirstVisibleColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_FirstVisibleColumn, self.Ptr)
        return ret

    @FirstVisibleColumn.setter
    def FirstVisibleColumn(self, value:int):
        GetDllLibXls().XlsWorksheet_set_FirstVisibleColumn.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_FirstVisibleColumn, self.Ptr, value)

    @property
    def FirstVisibleRow(self)->int:
        """

        """
        GetDllLibXls().XlsWorksheet_get_FirstVisibleRow.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_FirstVisibleRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_FirstVisibleRow, self.Ptr)
        return ret

    @FirstVisibleRow.setter
    def FirstVisibleRow(self, value:int):
        GetDllLibXls().XlsWorksheet_set_FirstVisibleRow.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_FirstVisibleRow, self.Ptr, value)

    @property
    def GridLinesVisible(self)->bool:
        """
        True if gridlines are visible; False otherwise.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set grid line visibility
            worksheet.GridLinesVisible = false
            #Save to file
            workbook.SaveToFile("GridLinesVisible.xlsx")

        """
        GetDllLibXls().XlsWorksheet_get_GridLinesVisible.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheet_get_GridLinesVisible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheet_get_GridLinesVisible, self.Ptr)
        return ret

    @GridLinesVisible.setter
    def GridLinesVisible(self, value:bool):
        GetDllLibXls().XlsWorksheet_set_GridLinesVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheet_set_GridLinesVisible, self.Ptr, value)


        