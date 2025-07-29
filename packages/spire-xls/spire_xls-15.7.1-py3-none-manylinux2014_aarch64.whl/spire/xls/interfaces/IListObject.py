from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IListObject (SpireObject) :
    """
    Represents a table on a worksheet.

    """
    @property

    def Name(self)->str:
        """
        Gets or sets name of the list object.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Set Table Name
            table1.Name = "Products"
            #Get Table Name
            print(table1.Name)
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObject_get_Name.argtypes=[c_void_p]
        GetDllLibXls().IListObject_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().IListObject_get_Name, self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        GetDllLibXls().IListObject_set_Name.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().IListObject_set_Name, self.Ptr, value)

    @property

    def Location(self)->'IXLSRange':
        """
        Gets or sets list object's location.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Set Table Range
            table1.Location = worksheet.Range["A1:C7"]
            #Get Table Range
            print(table1.Location.RangeAddressLocal.ToString())
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObject_get_Location.argtypes=[c_void_p]
        GetDllLibXls().IListObject_get_Location.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IListObject_get_Location, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @Location.setter
    def Location(self, value:'IXLSRange'):
        GetDllLibXls().IListObject_set_Location.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().IListObject_set_Location, self.Ptr, value.Ptr)

    @property

    def Columns(self)->'ListObjectColumns':
        """
        Gets collection of all columns of the list object.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Total row
            table1.DisplayTotalRow = true
            table1.Columns[0].TotalsRowLabel = "Total"
            table1.Columns[1].TotalsCalculation = ExcelTotalsCalculation.Sum
            table1.Columns[2].TotalsCalculation = ExcelTotalsCalculation.Sum
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObject_get_Columns.argtypes=[c_void_p]
        GetDllLibXls().IListObject_get_Columns.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IListObject_get_Columns, self.Ptr)
        ret = None if intPtr==None else ListObjectColumns(intPtr)
        return ret



    @property
    def Index(self)->int:
        """
        Gets index of the current list object.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Print Table index
            print(table1.Index)
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObject_get_Index.argtypes=[c_void_p]
        GetDllLibXls().IListObject_get_Index.restype=c_int
        ret = CallCFunction(GetDllLibXls().IListObject_get_Index, self.Ptr)
        return ret

    @property

    def BuiltInTableStyle(self)->'TableBuiltInStyles':
        """
        Gets or sets the built-in table style for the specified ListObject object.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Apply builtin style
            table1.BuiltInTableStyle = TableBuiltInStyles.TableStyleMedium9
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObject_get_BuiltInTableStyle.argtypes=[c_void_p]
        GetDllLibXls().IListObject_get_BuiltInTableStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().IListObject_get_BuiltInTableStyle, self.Ptr)
        objwraped = TableBuiltInStyles(ret)
        return objwraped

    @BuiltInTableStyle.setter
    def BuiltInTableStyle(self, value:'TableBuiltInStyles'):
        GetDllLibXls().IListObject_set_BuiltInTableStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().IListObject_set_BuiltInTableStyle, self.Ptr, value.value)

    @property

    def Worksheet(self)->'IWorksheet':
        """
        Gets parent worksheet object.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Get parent worksheet's name
            print(table1.Worksheet.Name)
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObject_get_Worksheet.argtypes=[c_void_p]
        GetDllLibXls().IListObject_get_Worksheet.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IListObject_get_Worksheet, self.Ptr)
        ret = None if intPtr==None else XlsWorksheet(intPtr)
        return ret


    @property

    def DisplayName(self)->str:
        """
        Gets or sets list object name.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Get Table display name
            print(table1.DisplayName)
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObject_get_DisplayName.argtypes=[c_void_p]
        GetDllLibXls().IListObject_get_DisplayName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().IListObject_get_DisplayName, self.Ptr))
        return ret


    @DisplayName.setter
    def DisplayName(self, value:str):
        GetDllLibXls().IListObject_set_DisplayName.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().IListObject_set_DisplayName, self.Ptr, value)

    @property
    def TotalsRowCount(self)->int:
        """
        Gets number of totals rows.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Check totals row count
            print(table1.TotalsRowCount)
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObject_get_TotalsRowCount.argtypes=[c_void_p]
        GetDllLibXls().IListObject_get_TotalsRowCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().IListObject_get_TotalsRowCount, self.Ptr)
        return ret

    @property
    def DisplayTotalRow(self)->bool:
        """
        Gets or sets a value indicating whether the Total row is visible.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Show total row
            table1.DisplayTotalRow = true
            table1.Columns[0].TotalsRowLabel = "Total"
            table1.Columns[1].TotalsCalculation = ExcelTotalsCalculation.Sum
            table1.Columns[2].TotalsCalculation = ExcelTotalsCalculation.Sum
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObject_get_DisplayTotalRow.argtypes=[c_void_p]
        GetDllLibXls().IListObject_get_DisplayTotalRow.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IListObject_get_DisplayTotalRow, self.Ptr)
        return ret

    @DisplayTotalRow.setter
    def DisplayTotalRow(self, value:bool):
        GetDllLibXls().IListObject_set_DisplayTotalRow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IListObject_set_DisplayTotalRow, self.Ptr, value)

    @property
    def ShowTableStyleRowStripes(self)->bool:
        """
        Gets or sets a value indicating whether row stripes should be present.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Set Row Column Stripe Visiblity
            table1.ShowTableStyleRowStripes = false
            table1.ShowTableStyleColumnStripes = true
            #Apply builtin style
            table1.BuiltInTableStyle = TableBuiltInStyles.TableStyleMedium9
            #Create style for table number format
            style1 = workbook.Styles.Add("CurrencyFormat")
            style1.NumberFormat = "_($* #,#0.00_);_($* (#,#0.00);_($* \" - \"??_);_(@_)"
            #Apply number format
            worksheet["B2:C6"].CellStyleName = "CurrencyFormat"
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObject_get_ShowTableStyleRowStripes.argtypes=[c_void_p]
        GetDllLibXls().IListObject_get_ShowTableStyleRowStripes.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IListObject_get_ShowTableStyleRowStripes, self.Ptr)
        return ret

    @ShowTableStyleRowStripes.setter
    def ShowTableStyleRowStripes(self, value:bool):
        GetDllLibXls().IListObject_set_ShowTableStyleRowStripes.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IListObject_set_ShowTableStyleRowStripes, self.Ptr, value)

    @property
    def ShowTableStyleColumnStripes(self)->bool:
        """
        Gets or sets a value indicating whether column stripes should be present.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Set Row Column Stripe Visiblity
            table1.ShowTableStyleRowStripes = false
            table1.ShowTableStyleColumnStripes = true
            #Apply builtin style
            table1.BuiltInTableStyle = TableBuiltInStyles.TableStyleMedium9
            #Create style for table number format
            style1 = workbook.Styles.Add("CurrencyFormat")
            style1.NumberFormat = "_($* #,#0.00_);_($* (#,#0.00);_($* \" - \"??_);_(@_)"
            #Apply number format
            worksheet["B2:C6"].CellStyleName = "CurrencyFormat"
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObject_get_ShowTableStyleColumnStripes.argtypes=[c_void_p]
        GetDllLibXls().IListObject_get_ShowTableStyleColumnStripes.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IListObject_get_ShowTableStyleColumnStripes, self.Ptr)
        return ret

    @ShowTableStyleColumnStripes.setter
    def ShowTableStyleColumnStripes(self, value:bool):
        GetDllLibXls().IListObject_set_ShowTableStyleColumnStripes.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IListObject_set_ShowTableStyleColumnStripes, self.Ptr, value)

    @property
    def DisplayLastColumn(self)->bool:
        """
        Gets or sets a value indicating whether last column is present.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Set Column Visiblity
            table1.DisplayFirstColumn = true
            table1.DisplayLastColumn = true
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObject_get_DisplayLastColumn.argtypes=[c_void_p]
        GetDllLibXls().IListObject_get_DisplayLastColumn.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IListObject_get_DisplayLastColumn, self.Ptr)
        return ret

    @DisplayLastColumn.setter
    def DisplayLastColumn(self, value:bool):
        GetDllLibXls().IListObject_set_DisplayLastColumn.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IListObject_set_DisplayLastColumn, self.Ptr, value)

    @property
    def DisplayFirstColumn(self)->bool:
        """
        Gets or sets a value indicating whether first column is present.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Set Column Visiblity
            table1.DisplayFirstColumn = true
            table1.DisplayLastColumn = true
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObject_get_DisplayFirstColumn.argtypes=[c_void_p]
        GetDllLibXls().IListObject_get_DisplayFirstColumn.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IListObject_get_DisplayFirstColumn, self.Ptr)
        return ret

    @DisplayFirstColumn.setter
    def DisplayFirstColumn(self, value:bool):
        GetDllLibXls().IListObject_set_DisplayFirstColumn.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IListObject_set_DisplayFirstColumn, self.Ptr, value)

    @property
    def DisplayHeaderRow(self)->bool:
        """
        Gets or sets a Boolean value indicating whether to hide/display header row.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create table
            table1 = worksheet.ListObjects.Create("Table1", worksheet["A1:C6"])
            #Set Header Visiblity
            table1.DisplayHeaderRow = true
            #Save to file
            workbook.SaveToFile("Table.xlsx")

        """
        GetDllLibXls().IListObject_get_DisplayHeaderRow.argtypes=[c_void_p]
        GetDllLibXls().IListObject_get_DisplayHeaderRow.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IListObject_get_DisplayHeaderRow, self.Ptr)
        return ret

    @DisplayHeaderRow.setter
    def DisplayHeaderRow(self, value:bool):
        GetDllLibXls().IListObject_set_DisplayHeaderRow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IListObject_set_DisplayHeaderRow, self.Ptr, value)

    @property

    def AutoFilters(self)->'AutoFiltersCollection':
        """
        Gets the AutoFiltersCollection collection in the table. Read-only.

        """
        GetDllLibXls().IListObject_get_AutoFilters.argtypes=[c_void_p]
        GetDllLibXls().IListObject_get_AutoFilters.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IListObject_get_AutoFilters, self.Ptr)
        ret = None if intPtr==None else AutoFiltersCollection(intPtr)
        return ret


