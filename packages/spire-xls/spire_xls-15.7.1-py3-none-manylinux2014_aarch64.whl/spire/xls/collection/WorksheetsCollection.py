from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class WorksheetsCollection (  XlsWorksheetsCollection) :
    """
    Represents a collection of worksheets in a workbook, providing methods to add, copy, create, and access worksheets.
    """

    def Add(self ,name:str)->'Worksheet':
        """
        Adds a new worksheet.

        Args:
            name (str): Worksheet name.

        Returns:
            Worksheet: The added worksheet.
        """
        
        GetDllLibXls().WorksheetsCollection_Add.argtypes=[c_void_p ,c_wchar_p]
        GetDllLibXls().WorksheetsCollection_Add.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().WorksheetsCollection_Add, self.Ptr, name)
        ret = None if intPtr==None else Worksheet(intPtr)
        return ret


    @dispatch

    def AddCopy(self ,sheetIndex:int)->Worksheet:
        """
        Adds a copy of a worksheet by index.

        Args:
            sheetIndex (int): Sheet index.

        Returns:
            Worksheet: The added worksheet.
        """
        
        GetDllLibXls().WorksheetsCollection_AddCopy.argtypes=[c_void_p ,c_int]
        GetDllLibXls().WorksheetsCollection_AddCopy.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().WorksheetsCollection_AddCopy, self.Ptr, sheetIndex)
        ret = None if intPtr==None else Worksheet(intPtr)
        return ret


    @dispatch

    def AddCopy(self ,sheet:Worksheet)->Worksheet:
        """
        Adds a copy of the specified worksheet.

        Args:
            sheet (Worksheet): Worksheet to copy.

        Returns:
            Worksheet: The added worksheet.
        """
        intPtrsheet:c_void_p = sheet.Ptr

        GetDllLibXls().WorksheetsCollection_AddCopySheet.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().WorksheetsCollection_AddCopySheet.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().WorksheetsCollection_AddCopySheet, self.Ptr, intPtrsheet)
        ret = None if intPtr==None else Worksheet(intPtr)
        return ret


    @dispatch

    def AddCopy(self ,sheets:'WorksheetsCollection'):
        """
        Adds a collection of worksheets to the workbook.

        Args:
            sheets (WorksheetsCollection): Source worksheets collection.
        """
        intPtrsheets:c_void_p = sheets.Ptr

        GetDllLibXls().WorksheetsCollection_AddCopySheets.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().WorksheetsCollection_AddCopySheets, self.Ptr, intPtrsheets)

    @dispatch

    def Create(self ,name:str)->Worksheet:
        """
        Creates a new worksheet with the specified name.

        Args:
            name (str): Worksheet name.

        Returns:
            Worksheet: The created worksheet.
        """
        
        GetDllLibXls().WorksheetsCollection_Create.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().WorksheetsCollection_Create.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().WorksheetsCollection_Create, self.Ptr, name)
        ret = None if intPtr==None else Worksheet(intPtr)
        return ret


    @dispatch

    def Create(self)->Worksheet:
        """
        Creates a new worksheet.

        Returns:
            Worksheet: The created worksheet.
        """
        GetDllLibXls().WorksheetsCollection_Create1.argtypes=[c_void_p]
        GetDllLibXls().WorksheetsCollection_Create1.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().WorksheetsCollection_Create1, self.Ptr)
        ret = None if intPtr==None else Worksheet(intPtr)
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
#        GetDllLibXls().WorksheetsCollection_FindAllNumber.argtypes=[c_void_p ,c_double,c_bool]
#        GetDllLibXls().WorksheetsCollection_FindAllNumber.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().WorksheetsCollection_FindAllNumber, self.Ptr, doubleValue,formulaValue)
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
#        GetDllLibXls().WorksheetsCollection_FindAllString.argtypes=[c_void_p ,c_void_p,c_bool,c_bool]
#        GetDllLibXls().WorksheetsCollection_FindAllString.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().WorksheetsCollection_FindAllString, self.Ptr, stringValue,formula,formulaValue)
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
#        GetDllLibXls().WorksheetsCollection_FindAllDateTime.argtypes=[c_void_p ,c_void_p]
#        GetDllLibXls().WorksheetsCollection_FindAllDateTime.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().WorksheetsCollection_FindAllDateTime, self.Ptr, intPtrdateTimeValue)
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
#        GetDllLibXls().WorksheetsCollection_FindAllTimeSpan.argtypes=[c_void_p ,c_void_p]
#        GetDllLibXls().WorksheetsCollection_FindAllTimeSpan.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().WorksheetsCollection_FindAllTimeSpan, self.Ptr, intPtrtimeSpanValue)
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
#        GetDllLibXls().WorksheetsCollection_FindAllBool.argtypes=[c_void_p ,c_bool]
#        GetDllLibXls().WorksheetsCollection_FindAllBool.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().WorksheetsCollection_FindAllBool, self.Ptr, boolValue)
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
        
        GetDllLibXls().WorksheetsCollection_FindBool.argtypes=[c_void_p ,c_bool]
        GetDllLibXls().WorksheetsCollection_FindBool.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().WorksheetsCollection_FindBool, self.Ptr, boolValue)
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
        
        GetDllLibXls().WorksheetsCollection_FindNumber.argtypes=[c_void_p ,c_double,c_bool]
        GetDllLibXls().WorksheetsCollection_FindNumber.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().WorksheetsCollection_FindNumber, self.Ptr, doubleValue,formulaValue)
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
        
        GetDllLibXls().WorksheetsCollection_FindString.argtypes=[c_void_p ,c_void_p,c_bool,c_bool]
        GetDllLibXls().WorksheetsCollection_FindString.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().WorksheetsCollection_FindString, self.Ptr, stringValue,formula,formulaValue)
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

        GetDllLibXls().WorksheetsCollection_FindDateTime.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().WorksheetsCollection_FindDateTime.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().WorksheetsCollection_FindDateTime, self.Ptr, intPtrdateTimeValue)
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

        GetDllLibXls().WorksheetsCollection_FindTimeSpan.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().WorksheetsCollection_FindTimeSpan.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().WorksheetsCollection_FindTimeSpan, self.Ptr, intPtrtimeSpanValue)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret



    def Remove(self ,sheet:'Worksheet'):
        """
        Remove worksheet from collection.

        Args:
            sheet: Worksheet object.

        """
        intPtrsheet:c_void_p = sheet.Ptr

        GetDllLibXls().WorksheetsCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().WorksheetsCollection_Remove, self.Ptr, intPtrsheet)

    @dispatch

    def get_Item(self ,Index:int)->Worksheet:
        """
        Returns a single object from a collection. Read-only.

        """
        if Index >= self.Count:
            raise StopIteration()
        
        GetDllLibXls().WorksheetsCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().WorksheetsCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().WorksheetsCollection_get_Item, self.Ptr, Index)
        ret = None if intPtr==None else Worksheet(intPtr)
        return ret


    @dispatch

    def get_Item(self ,sheetName:str)->Worksheet:
        """
        Returns a single object from a collection. Read-only.

        """
        
        GetDllLibXls().WorksheetsCollection_get_ItemN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().WorksheetsCollection_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().WorksheetsCollection_get_ItemN, self.Ptr, sheetName)
        ret = None if intPtr==None else Worksheet(intPtr)
        return ret


