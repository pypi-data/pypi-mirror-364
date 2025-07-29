from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsDataValidationTable (  SpireObject, IDataValidationTable) :
    """Represents a table of data validations in an Excel worksheet.
    
    This class provides properties and methods for accessing and manipulating data validations
    in an Excel worksheet, including finding, removing, and cloning validations.
    It extends SpireObject and implements the IDataValidationTable interface.
    """
    @property

    def Worksheet(self)->'Worksheet':
        """Gets the worksheet containing this data validation table.
        
        Returns:
            Worksheet: The worksheet object containing this data validation table.
        """
        GetDllLibXls().XlsDataValidationTable_get_Worksheet.argtypes=[c_void_p]
        GetDllLibXls().XlsDataValidationTable_get_Worksheet.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsDataValidationTable_get_Worksheet, self.Ptr)
        ret = None if intPtr==None else Worksheet(intPtr)
        return ret


    @property

    def Workbook(self)->'Workbook':
        """Gets the workbook containing this data validation table.
        
        Returns:
            Workbook: The workbook object containing this data validation table.
        """
        GetDllLibXls().XlsDataValidationTable_get_Workbook.argtypes=[c_void_p]
        GetDllLibXls().XlsDataValidationTable_get_Workbook.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsDataValidationTable_get_Workbook, self.Ptr)
        ret = None if intPtr==None else Workbook(intPtr)
        return ret



    def get_Item(self ,index:int)->'XlsDataValidationCollection':
        """Gets the data validation collection at the specified index.
        
        Args:
            index (int): The zero-based index of the data validation collection.
            
        Returns:
            XlsDataValidationCollection: The data validation collection at the specified index.
        """
        
        GetDllLibXls().XlsDataValidationTable_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsDataValidationTable_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsDataValidationTable_get_Item, self.Ptr, index)
        ret = None if intPtr==None else XlsDataValidationCollection(intPtr)
        return ret


    @property
    def ShapesCount(self)->int:
        """Gets the number of data validation shapes in the table.
        
        Returns:
            int: The number of data validation shapes.
        """
        GetDllLibXls().XlsDataValidationTable_get_ShapesCount.argtypes=[c_void_p]
        GetDllLibXls().XlsDataValidationTable_get_ShapesCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsDataValidationTable_get_ShapesCount, self.Ptr)
        return ret


    def FindDataValidation(self ,iCellIndex:int)->'IDataValidation':
        """Finds the data validation for a cell with the specified index.
        
        Args:
            iCellIndex (int): The index of the cell.
            
        Returns:
            IDataValidation: The data validation object for the specified cell, or None if not found.
        """
        
        GetDllLibXls().XlsDataValidationTable_FindDataValidation.argtypes=[c_void_p ,c_long]
        GetDllLibXls().XlsDataValidationTable_FindDataValidation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsDataValidationTable_FindDataValidation, self.Ptr, iCellIndex)
        ret = None if intPtr==None else XlsValidation(intPtr)
        return ret



    def Remove(self ,rectangles:List[Rectangle]):
        """Removes data validations from the specified rectangular regions.
        
        Args:
            rectangles (List[Rectangle]): A list of Rectangle objects representing the regions
                from which to remove data validations.
        """
        #arrayrectangles:ArrayTyperectangles = ""
        countrectangles = len(rectangles)
        ArrayTyperectangles = c_void_p * countrectangles
        arrayrectangles = ArrayTyperectangles()
        for i in range(0, countrectangles):
            arrayrectangles[i] = rectangles[i].Ptr


        GetDllLibXls().XlsDataValidationTable_Remove.argtypes=[c_void_p ,ArrayTyperectangles,c_int]
        CallCFunction(GetDllLibXls().XlsDataValidationTable_Remove, self.Ptr, arrayrectangles, countrectangles)



    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """Creates a clone of this data validation table.
        
        Args:
            parent (SpireObject): The parent object for the cloned table.
            
        Returns:
            SpireObject: A new instance of the data validation table with the same validations.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsDataValidationTable_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsDataValidationTable_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsDataValidationTable_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


