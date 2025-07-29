from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IListObjectColumn (SpireObject) :
    """
    Represents a column in the table.

    """
    @property

    def Name(self)->str:
        """
        Gets or sets name of the column.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Print Column Name, ID, Index
            print("Column Name " + table1.Columns[0].Name)
            print("Column ID " + table1.Columns[0].Id)
            print("Column Index " + table1.Columns[0].Index)
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObjectColumn_get_Name.argtypes=[c_void_p]
        GetDllLibXls().IListObjectColumn_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().IListObjectColumn_get_Name, self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        GetDllLibXls().IListObjectColumn_set_Name.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().IListObjectColumn_set_Name, self.Ptr, value)

    @property
    def Index(self)->int:
        """
        Gets column index.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Print Column Name, ID, Index
            print("Column Name " + table1.Columns[0].Name)
            print("Column ID " + table1.Columns[0].Id)
            print("Column Index " + table1.Columns[0].Index)
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObjectColumn_get_Index.argtypes=[c_void_p]
        GetDllLibXls().IListObjectColumn_get_Index.restype=c_int
        ret = CallCFunction(GetDllLibXls().IListObjectColumn_get_Index, self.Ptr)
        return ret

    @property
    def Id(self)->int:
        """
        Gets column id of current column. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Print Column Name, ID, Index
            print("Column Name " + table1.Columns[0].Name)
            print("Column ID " + table1.Columns[0].Id)
            print("Column Index " + table1.Columns[0].Index)
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObjectColumn_get_Id.argtypes=[c_void_p]
        GetDllLibXls().IListObjectColumn_get_Id.restype=c_int
        ret = CallCFunction(GetDllLibXls().IListObjectColumn_get_Id, self.Ptr)
        return ret

    @property

    def TotalsCalculation(self)->'ExcelTotalsCalculation':
        """
        Gets or sets function used for totals calculation.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Total row
            table1.ShowTotals = true
            table1.Columns[0].TotalsRowLabel = "Total"
            table1.Columns[1].TotalsCalculation = ExcelTotalsCalculation.Sum
            table1.Columns[2].TotalsCalculation = ExcelTotalsCalculation.Sum
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObjectColumn_get_TotalsCalculation.argtypes=[c_void_p]
        GetDllLibXls().IListObjectColumn_get_TotalsCalculation.restype=c_int
        ret = CallCFunction(GetDllLibXls().IListObjectColumn_get_TotalsCalculation, self.Ptr)
        objwraped = ExcelTotalsCalculation(ret)
        return objwraped

    @TotalsCalculation.setter
    def TotalsCalculation(self, value:'ExcelTotalsCalculation'):
        GetDllLibXls().IListObjectColumn_set_TotalsCalculation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().IListObjectColumn_set_TotalsCalculation, self.Ptr, value.value)

    @property

    def TotalsRowLabel(self)->str:
        """
        Gets or sets label of the totals row.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Total row
            table1.ShowTotals = true
            table1.Columns[0].TotalsRowLabel = "Total"
            table1.Columns[1].TotalsCalculation = ExcelTotalsCalculation.Sum
            table1.Columns[2].TotalsCalculation = ExcelTotalsCalculation.Sum
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObjectColumn_get_TotalsRowLabel.argtypes=[c_void_p]
        GetDllLibXls().IListObjectColumn_get_TotalsRowLabel.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().IListObjectColumn_get_TotalsRowLabel, self.Ptr))
        return ret


    @TotalsRowLabel.setter
    def TotalsRowLabel(self, value:str):
        GetDllLibXls().IListObjectColumn_set_TotalsRowLabel.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().IListObjectColumn_set_TotalsRowLabel, self.Ptr, value)

    @property

    def CalculatedFormula(self)->str:
        """
        Gets or sets calculated formula value.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Total row
            table1.ShowTotals = true
            table1.Columns[0].TotalsRowLabel = "Total"
            table1.Columns[1].TotalsCalculation = ExcelTotalsCalculation.Sum
            table1.Columns[2].TotalsCalculation = ExcelTotalsCalculation.Sum
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObjectColumn_get_CalculatedFormula.argtypes=[c_void_p]
        GetDllLibXls().IListObjectColumn_get_CalculatedFormula.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().IListObjectColumn_get_CalculatedFormula, self.Ptr))
        return ret


    @CalculatedFormula.setter
    def CalculatedFormula(self, value:str):
        GetDllLibXls().IListObjectColumn_set_CalculatedFormula.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().IListObjectColumn_set_CalculatedFormula, self.Ptr, value)

class ListObjectColumns (IList[IListObjectColumn]):
    pass
