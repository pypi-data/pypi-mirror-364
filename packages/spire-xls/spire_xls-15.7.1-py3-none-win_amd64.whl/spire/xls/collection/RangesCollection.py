from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class RangesCollection (  XlsRangesCollection) :
    """
    Represents a collection of cell ranges in an Excel worksheet, providing methods to manipulate and query ranges.
    """

    def Add(self ,range:'CellRange'):
        """
        Adds a range to the collection.

        Args:
            range (CellRange): The range to add.
        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().RangesCollection_Add.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RangesCollection_Add, self.Ptr, intPtrrange)


    def AddComment(self)->'ExcelComment':
        """
        Adds a comment to the range.

        Returns:
            ExcelComment: The added comment.
        """
        GetDllLibXls().RangesCollection_AddComment.argtypes=[c_void_p]
        GetDllLibXls().RangesCollection_AddComment.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_AddComment, self.Ptr)
        ret = None if intPtr==None else ExcelComment(intPtr)
        return ret



    def AddRange(self ,range:'CellRange'):
        """
        Adds a range to the collection.

        Args:
            range (CellRange): The range to add.
        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().RangesCollection_AddRange.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RangesCollection_AddRange, self.Ptr, intPtrrange)

    @dispatch

    def Copy(self ,destRange:CellRange)->CellRange:
        """
        Copies the range to the specified destination range.

        Args:
            destRange (CellRange): The destination range.

        Returns:
            CellRange: The destination range after copying.
        """
        intPtrdestRange:c_void_p = destRange.Ptr

        GetDllLibXls().RangesCollection_Copy.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().RangesCollection_Copy.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_Copy, self.Ptr, intPtrdestRange)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @dispatch

    def Copy(self ,destRange:CellRange,updateReference:bool)->CellRange:
        """
        Copies the range to the specified destination range, with an option to update reference cells.

        Args:
            destRange (CellRange): The destination range.
            updateReference (bool): Whether to update reference cells.

        Returns:
            CellRange: The destination range after copying.
        """
        intPtrdestRange:c_void_p = destRange.Ptr

        GetDllLibXls().RangesCollection_CopyDU.argtypes=[c_void_p ,c_void_p,c_bool]
        GetDllLibXls().RangesCollection_CopyDU.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_CopyDU, self.Ptr, intPtrdestRange,updateReference)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @dispatch

    def Copy(self ,destRange:CellRange,updateReference:bool,copyStyles:bool)->CellRange:
        """
        Copies the range to the specified destination range, with options to update reference cells and copy styles.

        Args:
            destRange (CellRange): The destination range.
            updateReference (bool): Whether to update reference cells.
            copyStyles (bool): Whether to copy styles.

        Returns:
            CellRange: The destination range after copying.
        """
        intPtrdestRange:c_void_p = destRange.Ptr

        GetDllLibXls().RangesCollection_CopyDUC.argtypes=[c_void_p ,c_void_p,c_bool,c_bool]
        GetDllLibXls().RangesCollection_CopyDUC.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_CopyDUC, self.Ptr, intPtrdestRange,updateReference,copyStyles)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


#
#    def FindAllNumber(self ,doubleValue:float,formulaValue:bool)->'ListCellRanges':
#        """
#    <summary>
#        Finds the cell with the input double.
#    </summary>
#    <param name="doubleValue">Double value to search for</param>
#    <param name="formulaValue">Indicates whether to find formula value</param>
#    <returns>Found ranges</returns>
#        """
#        
#        GetDllLibXls().RangesCollection_FindAllNumber.argtypes=[c_void_p ,c_double,c_bool]
#        GetDllLibXls().RangesCollection_FindAllNumber.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().RangesCollection_FindAllNumber, self.Ptr, doubleValue,formulaValue)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret


#
#    def FindAllString(self ,stringValue:str,formula:bool,formulaValue:bool)->'ListCellRanges':
#        """
#    <summary>
#        Finds the cell with the input string.
#    </summary>
#    <param name="stringValue">String value to search for</param>
#    <param name="formula">Indicates whether include formula</param>
#    <param name="formulaValue">Indicates whether include formula value</param>
#    <returns>Found ranges</returns>
#        """
#        
#        GetDllLibXls().RangesCollection_FindAllString.argtypes=[c_void_p ,c_void_p,c_bool,c_bool]
#        GetDllLibXls().RangesCollection_FindAllString.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().RangesCollection_FindAllString, self.Ptr, stringValue,formula,formulaValue)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret


#
#    def FindAllDateTime(self ,dateTimeValue:'DateTime')->'ListCellRanges':
#        """
#    <summary>
#        Finds the cell with the input datetime.
#    </summary>
#    <param name="dateTimeValue">DateTime value to search for</param>
#    <returns>Found ranges</returns>
#        """
#        intPtrdateTimeValue:c_void_p = dateTimeValue.Ptr
#
#        GetDllLibXls().RangesCollection_FindAllDateTime.argtypes=[c_void_p ,c_void_p]
#        GetDllLibXls().RangesCollection_FindAllDateTime.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().RangesCollection_FindAllDateTime, self.Ptr, intPtrdateTimeValue)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret


#
#    def FindAllTimeSpan(self ,timeSpanValue:'TimeSpan')->'ListCellRanges':
#        """
#    <summary>
#        Finds the cell with input timespan
#    </summary>
#    <param name="timeSpanValue">time span value to search for</param>
#    <returns>Found ranges</returns>
#        """
#        intPtrtimeSpanValue:c_void_p = timeSpanValue.Ptr
#
#        GetDllLibXls().RangesCollection_FindAllTimeSpan.argtypes=[c_void_p ,c_void_p]
#        GetDllLibXls().RangesCollection_FindAllTimeSpan.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().RangesCollection_FindAllTimeSpan, self.Ptr, intPtrtimeSpanValue)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret


#
#    def FindAllBool(self ,boolValue:bool)->'ListCellRanges':
#        """
#    <summary>
#        Finds the cell with the input bool. 
#    </summary>
#    <param name="boolValue">Bool value to search for</param>
#    <returns>Found ranges</returns>
#        """
#        
#        GetDllLibXls().RangesCollection_FindAllBool.argtypes=[c_void_p ,c_bool]
#        GetDllLibXls().RangesCollection_FindAllBool.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().RangesCollection_FindAllBool, self.Ptr, boolValue)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret



    def FindBool(self ,boolValue:bool)->'CellRange':
        """
        Finds the cell with the input bool.

        Args:
            boolValue: Bool value to search for

        Returns:
            Found range

        """
        
        GetDllLibXls().RangesCollection_FindBool.argtypes=[c_void_p ,c_bool]
        GetDllLibXls().RangesCollection_FindBool.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_FindBool, self.Ptr, boolValue)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret



    def FindNumber(self ,doubleValue:float,formulaValue:bool)->'CellRange':
        """
        Finds the cell with the input double.

        Args:
            doubleValue: Double value to search for
            formulaValue: Indicates whether includes formula value to search for

        Returns:
            Found range

        """
        
        GetDllLibXls().RangesCollection_FindNumber.argtypes=[c_void_p ,c_double,c_bool]
        GetDllLibXls().RangesCollection_FindNumber.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_FindNumber, self.Ptr, doubleValue,formulaValue)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret



    def FindString(self ,stringValue:str,formula:bool,formulaValue:bool)->'CellRange':
        """
        Finds the cell with the input string.

        Args:
            stringValue: String value to search for
            formula: Indicates whether includes formula to search for
            formulaValue: Indicates whether includes formula value to search for

        Returns:
            Found range

        """
        
        GetDllLibXls().RangesCollection_FindString.argtypes=[c_void_p ,c_void_p,c_bool,c_bool]
        GetDllLibXls().RangesCollection_FindString.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_FindString, self.Ptr, stringValue,formula,formulaValue)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret



    def FindDateTime(self ,dateTimeValue:'DateTime')->'CellRange':
        """
        Finds the cell with the input datetime.

        Args:
            dateTimeValue: Datetime value to search for

        Returns:
            Found range

        """
        intPtrdateTimeValue:c_void_p = dateTimeValue.Ptr

        GetDllLibXls().RangesCollection_FindDateTime.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().RangesCollection_FindDateTime.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_FindDateTime, self.Ptr, intPtrdateTimeValue)
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

        GetDllLibXls().RangesCollection_FindTimeSpan.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().RangesCollection_FindTimeSpan.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_FindTimeSpan, self.Ptr, intPtrtimeSpanValue)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret



    def Intersect(self ,range:'CellRange')->'CellRange':
        """
        Get intersection range with the specified range.

        Args:
            range: Range which to intersect.

        Returns:
            Range intersection.

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().RangesCollection_Intersect.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().RangesCollection_Intersect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_Intersect, self.Ptr, intPtrrange)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @dispatch

    def Move(self ,destRange:CellRange):
        """
        Moves the cells to the specified Range.

        Args:
            destination: Destnation Range.

        """
        intPtrdestRange:c_void_p = destRange.Ptr

        GetDllLibXls().RangesCollection_Move.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RangesCollection_Move, self.Ptr, intPtrdestRange)

    @dispatch

    def Move(self ,destRange:CellRange,updateReference:bool):
        """
        Moves the cells to the specified Range.

        Args:
            destination: Destination Range.
            updateReference: Indicates whether to update reference range.

        """
        intPtrdestRange:c_void_p = destRange.Ptr

        GetDllLibXls().RangesCollection_MoveDU.argtypes=[c_void_p ,c_void_p,c_bool]
        CallCFunction(GetDllLibXls().RangesCollection_MoveDU, self.Ptr, intPtrdestRange,updateReference)


    def Remove(self ,range:'CellRange'):
        """
        Removes range from the collection.

        Args:
            range: Range to remove.

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().RangesCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RangesCollection_Remove, self.Ptr, intPtrrange)

    @property

    def EntireRow(self)->'RangesCollection':
        """
        Returns a Range object that represents the entire row (or rows) that contains the specified range.

        """
        GetDllLibXls().RangesCollection_get_EntireRow.argtypes=[c_void_p]
        GetDllLibXls().RangesCollection_get_EntireRow.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_get_EntireRow, self.Ptr)
        ret = None if intPtr==None else RangesCollection(intPtr)
        return ret


    @property

    def EntireColumn(self)->'RangesCollection':
        """
        Returns a Range object that represents the entire column (or columns) that contains the specified range.

        """
        GetDllLibXls().RangesCollection_get_EntireColumn.argtypes=[c_void_p]
        GetDllLibXls().RangesCollection_get_EntireColumn.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_get_EntireColumn, self.Ptr)
        ret = None if intPtr==None else RangesCollection(intPtr)
        return ret


#    @property
#
#    def Cells(self)->'ListCellRanges':
#        """
#    <summary>
#        Returns a Range object that represents the cells in the specified range.
#    </summary>
#        """
#        GetDllLibXls().RangesCollection_get_Cells.argtypes=[c_void_p]
#        GetDllLibXls().RangesCollection_get_Cells.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().RangesCollection_get_Cells, self.Ptr)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret


#    @property
#
#    def Rows(self)->'ListCellRanges':
#        """
#    <summary>
#        Returns the number of the first row of the first area in the range.
#    </summary>
#        """
#        GetDllLibXls().RangesCollection_get_Rows.argtypes=[c_void_p]
#        GetDllLibXls().RangesCollection_get_Rows.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().RangesCollection_get_Rows, self.Ptr)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret


#    @property
#
#    def Columns(self)->'ListCellRanges':
#        """
#    <summary>
#        Returns a Range object that represents the columns in the specified range
#    </summary>
#        """
#        GetDllLibXls().RangesCollection_get_Columns.argtypes=[c_void_p]
#        GetDllLibXls().RangesCollection_get_Columns.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().RangesCollection_get_Columns, self.Ptr)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret


    @property

    def Comment(self)->'ExcelComment':
        """
        Returns a Comment object that represents the comment associated with the cell in the upper-left corner of the range.

        """
        GetDllLibXls().RangesCollection_get_Comment.argtypes=[c_void_p]
        GetDllLibXls().RangesCollection_get_Comment.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_get_Comment, self.Ptr)
        ret = None if intPtr==None else ExcelComment(intPtr)
        return ret


    @property

    def EndCell(self)->'CellRange':
        """
        Returns a Range object that represents the cell at the end of the region that contains the source range.

        """
        GetDllLibXls().RangesCollection_get_EndCell.argtypes=[c_void_p]
        GetDllLibXls().RangesCollection_get_EndCell.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_get_EndCell, self.Ptr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @property

    def Borders(self)->'BordersCollection':
        """
        Returns a Borders collection that represents the borders of a style or a range of cells (including a range defined as part of a conditional format).

        """
        GetDllLibXls().RangesCollection_get_Borders.argtypes=[c_void_p]
        GetDllLibXls().RangesCollection_get_Borders.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_get_Borders, self.Ptr)
        ret = None if intPtr==None else BordersCollection(intPtr)
        return ret


    @property

    def MergeArea(self)->'RangesCollection':
        """
        Returns a Range object that represents the merged range containing the specified cell.

        """
        GetDllLibXls().RangesCollection_get_MergeArea.argtypes=[c_void_p]
        GetDllLibXls().RangesCollection_get_MergeArea.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_get_MergeArea, self.Ptr)
        ret = None if intPtr==None else RangesCollection(intPtr)
        return ret


    @property

    def RichText(self)->'RichText':
        """
        Returns a RichTextString object that represents the rich text style.

        """
        GetDllLibXls().RangesCollection_get_RichText.argtypes=[c_void_p]
        GetDllLibXls().RangesCollection_get_RichText.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_get_RichText, self.Ptr)
        ret = None if intPtr==None else RichText(intPtr)
        return ret


    @property

    def Style(self)->'CellStyle':
        """
        Returns a Style object that represents the style of the specified range

        """
        GetDllLibXls().RangesCollection_get_Style.argtypes=[c_void_p]
        GetDllLibXls().RangesCollection_get_Style.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_get_Style, self.Ptr)
        ret = None if intPtr==None else CellStyle(intPtr)
        return ret


    @Style.setter
    def Style(self, value:'CellStyle'):
        GetDllLibXls().RangesCollection_set_Style.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().RangesCollection_set_Style, self.Ptr, value.Ptr)

    @property

    def Worksheet(self)->'Worksheet':
        """

        """
        GetDllLibXls().RangesCollection_get_Worksheet.argtypes=[c_void_p]
        GetDllLibXls().RangesCollection_get_Worksheet.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RangesCollection_get_Worksheet, self.Ptr)
        ret = None if intPtr==None else Worksheet(intPtr)
        return ret


