from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IWorkbook (  IExcelApplication) :
    """

    """
    @dispatch

    @abc.abstractmethod
    def Replace(self ,oldValue:str,newValue:str):
        """
        Replaces specified string by specified value.

        Args:
            oldValue: String value to replace.
            newValue: New value for the range with specified string.
        Example::

            #Create workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Replace the oldValue by newValue
            oldValue = "Find"
            newValue = "NewValue"
            workbook.Replace(oldValue, newValue)
            #Save to file
            workbook.SaveToFile("Replace.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def Replace(self ,oldValue:str,newValue:float):
        """
        Replaces specified string by specified value.

        Args:
            oldValue: String value to replace.
            newValue: New value for the range with specified string.
        Example::

            #Create workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Replace the oldValue by double
            oldValue = "Ten"
            workbook.Replace(oldValue, 10.0)
            #Save to file
            workbook.SaveToFile("Replace.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def Replace(self ,oldValue:str,newValue:DateTime):
        """
        Replaces specified string by specified value.

        Args:
            oldValue: String value to replace.
            newValue: New value for the range with specified string.
        Example::

            #Create workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Replace the oldValue by dateTime
            oldValue = "Find"
            dateTime = DateTime.Now
            workbook.Replace(oldValue, dateTime)
            #Save to file
            workbook.SaveToFile("Replace.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def Replace(self ,oldValue:str,newValues:List[str],isVertical:bool):
        """
        Replaces specified string by data from array.

        Args:
            oldValue: String value to replace.
            newValues: Array of new values.
            isVertical: Indicates whether array should be inserted vertically.
        Example::

            #Create workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Replace the oldValue by array of string values
            oldValue = "Find"
            string[] newValues = { "X values", "Y values" }
            workbook.Replace(oldValue, newValues , true)
            #Save to file
            workbook.SaveToFile("Replace.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def Replace(self ,oldValue:str,newValues:List[int],isVertical:bool):
        """
        Replaces specified string by data from array.

        Args:
            oldValue: String value to replace.
            newValues: Array of new values.
            isVertical: Indicates whether array should be inserted vertically.
        Example::

            #Create workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Replace the oldValue by array of int values
            oldValue = "Find"
            int[] newValues = { 1, 2 }
            workbook.Replace(oldValue, newValues, true)
            #Save to file
            workbook.SaveToFile("Replace.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def Replace(self ,oldValue:str,newValues:List[float],isVertical:bool):
        """
        Replaces specified string by data from array.

        Args:
            oldValue: String value to replace.
            newValues: Array of new values.
            isVertical: Indicates whether array should be inserted vertically.
        Example::

            #Create workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Replace the oldValue by array of double values
            oldValue = "Find"
            double[] newValues = { 1.0, 2.0 }
            workbook.Replace(oldValue, newValues, true)
            #Save to file
            workbook.SaveToFile("Replace.xlsx")

        """
        pass


#    @dispatch
#
#    @abc.abstractmethod
#    def Replace(self ,oldValue:str,newValues:'DataTable',isFieldNamesShown:bool):
#        """
#    <summary>
#         Replaces specified string by data table values.
#        <example>The following code snippet illustrates how to replace the string value with data table:
#        <code>
#        //Create workbook
#        Workbook workbook = new Workbook();
#        workbook.LoadFromFile("Sample.xlsx");
#        //Replace the oldValue by data table
#        string oldValue = "Find";
#        System.Data.DataTable table = new System.Data.DataTable();
#        table.Columns.Add("Dosage", typeof(int));
#        table.Rows.Add(1);
#        workbook.Replace(oldValue, table, true);
#        //Save to file
#        workbook.SaveToFile("Replace.xlsx");
#        </code>
#        </example>
#    </summary>
#    <param name="oldValue">String value to replace.</param>
#    <param name="newValues">Data table with new data.</param>
#    <param name="isFieldNamesShown">Indicates whether field name must be shown.</param>
#        """
#        pass
#


#    @dispatch
#
#    @abc.abstractmethod
#    def Replace(self ,oldValue:str,newValues:'DataColumn',isFieldNamesShown:bool):
#        """
#    <summary>
#         Replaces specified string by data column values.
#        <example>The following code snippet illustrates how to replace the string value with data column:
#        <code>
#        //Create workbook
#        Workbook workbook = new Workbook();
#        workbook.LoadFromFile("Sample.xlsx");
#        //Replace the oldValue by data column
#        string oldValue = "Find";
#        System.Data.DataTable table = new System.Data.DataTable();
#        table.Columns.Add("Dosage", typeof(int));
#        table.Rows.Add(1);
#        System.Data.DataColumn dataColumn = table.Columns[0];
#        workbook.Replace(oldValue, dataColumn, true);
#        //Save to file
#        workbook.SaveToFile("Replace.xlsx");
#        </code>
#        </example>
#    </summary>
#    <param name="oldValue">String value to replace.</param>
#    <param name="newValues">Data table with new data.</param>
#    <param name="isFieldNamesShown">Indicates whether field name must be shown.</param>
#        """
#        pass
#


    @dispatch

    @abc.abstractmethod
    def FindOne(self ,findValue:str,flags:FindType)->IXLSRange:
        """
        This method seraches for the first cell with specified string value.

        Args:
            findValue: Value to search.
            flags: Type of value to search.

        Returns:
            First found cell, or Null if value was not found.
        Example::

            #Create workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Find cell with specified string value
            value = "value"
            result = workbook.FindString(value, false, false)

        """
        pass


    @dispatch

    @abc.abstractmethod
    def FindOne(self ,findValue:float,flags:FindType)->IXLSRange:
        """
        This method seraches for the first cell with specified double value.

        Args:
            findValue: Value to search.
            flags: Type of value to search.

        Returns:
            First found cell, or Null if value was not found.
        Example::

            #Create workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Find cell with specified double value
            value = 9.00
            result = workbook.FindNumber(value, false)

        """
        pass


    @dispatch

    @abc.abstractmethod
    def FindOne(self ,findValue:bool)->IXLSRange:
        """
        This method seraches for the first cell with specified bool value.

        Args:
            findValue: Value to search.

        Returns:
            First found cell, or Null if value was not found.
        Example::

            #Create workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Find cell with specified bool value
            result = workbook.FindBool(true)

        """
        pass


    @dispatch

    @abc.abstractmethod
    def FindOne(self ,findValue:DateTime)->IXLSRange:
        """
        This method seraches for the first cell with specified DateTime value.

        Args:
            findValue: Value to search.

        Returns:
            First found cell, or Null if value was not found.
        Example::

            #Create workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Find cell with specified DateTime value
            dateTime = DateTime.Now
            result = workbook.FindDateTime(dateTime)

        """
        pass


    @dispatch

    @abc.abstractmethod
    def FindOne(self ,findValue:TimeSpan)->IXLSRange:
        """
        This method seraches for the first cell with specified TimeSpan value.

        Args:
            findValue: Value to search.

        Returns:
            First found cell, or Null if value was not found.
        Example::

            #Create workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Find cell with specified TimeSpan value
            timeSpan = new TimeSpan(2, 30, 30)
            result = workbook.FindTimeSpan(timeSpan)

        """
        pass


#    @dispatch
#
#    @abc.abstractmethod
#    def FindAll(self ,findValue:str,flags:FindType)->ListCellRanges:
#        """
#    <summary>
#         This method seraches for the all cells with specified string value.
#        <example>This sample shows how to find all cells with specified string value:
#        <code>
#        //Create workbook
#        Workbook workbook = new Workbook();
#        workbook.LoadFromFile("Sample.xlsx");
#        //Find cells with specified string value
#        string value = "value";
#        CellRange[] result = workbook.FindAllString(value , false , false);
#        </code>
#        </example>
#    </summary>
#    <param name="findValue">Value to search.</param>
#    <param name="flags">Type of value to search.</param>
#    <returns>All found cells, or Null if value was not found.</returns>
#        """
#        pass
#


#    @dispatch
#
#    @abc.abstractmethod
#    def FindAll(self ,findValue:float,flags:FindType)->ListCellRanges:
#        """
#    <summary>
#         This method seraches for the all cells with specified double value.
#        <example>This sample shows how to find all cells with specified doulbe value:
#        <code>
#        //Create workbook
#        Workbook workbook = new Workbook();
#        workbook.LoadFromFile("Sample.xlsx");
#        //Find cells with specified double value
#        CellRange[] result = workbook.FindAllNumber(100.32 , false);
#        </code>
#        </example>
#    </summary>
#    <param name="findValue">Value to search.</param>
#    <param name="flags">Type of value to search.</param>
#    <returns>All found cells, or Null if value was not found.</returns>
#        """
#        pass
#


#    @dispatch
#
#    @abc.abstractmethod
#    def FindAll(self ,findValue:bool)->ListCellRanges:
#        """
#    <summary>
#         This method seraches for the all cells with specified bool value.
#        <example>This sample shows how to find all cells with specified bool value:
#        <code>
#        //Create workbook
#        Workbook workbook = new Workbook();
#        workbook.LoadFromFile("Sample.xlsx");
#        //Find cells with specified bool value
#        CellRange[] result = workbook.FindAllBool(true);
#        </code>
#        </example>
#    </summary>
#    <param name="findValue">Value to search.</param>
#    <returns>All found cells, or Null if value was not found</returns>
#        """
#        pass
#


#    @dispatch
#
#    @abc.abstractmethod
#    def FindAll(self ,findValue:DateTime)->ListCellRanges:
#        """
#    <summary>
#         This method seraches for the all cells with specified DateTime value.
#        <example>This sample shows how to find all cells with specified DateTime value:
#        <code>
#        //Create workbook
#        Workbook workbook = new Workbook();
#        workbook.LoadFromFile("Sample.xlsx");
#        //Find cells with specified DateTime value
#        CellRange[] result = workbook.FindAllDateTime(DateTime.Now);
#        </code>
#        </example>
#    </summary>
#    <param name="findValue">Value to search.</param>
#    <returns>All found cells, or Null if value was not found.</returns>
#        """
#        pass
#


#    @dispatch
#
#    @abc.abstractmethod
#    def FindAll(self ,findValue:TimeSpan)->ListCellRanges:
#        """
#    <summary>
#         This method seraches for the all cells with specified TimeSpan value.
#        <example>This sample shows how to find all cells with specified TimeSpan value:
#        <code>
#        //Create workbook
#        Workbook workbook = new Workbook();
#        workbook.LoadFromFile("Sample.xlsx");
#        //Find cells with specified TimeSpan value
#        TimeSpan value = new TimeSpan(2, 30, 30);
#        CellRange[] result = workbook.FindAllTimeSpan(value);
#        </code>
#        </example>
#    </summary>
#    <param name="findValue">Value to search.</param>
#    <returns>All found cells, or Null if value was not found.</returns>
#        """
#        pass
#


    @dispatch

    @abc.abstractmethod
    def SaveAs(self ,fileName:str,separator:str):
        """
        Save active WorkSheet using separator.

        Args:
            fileName: Path to save.
            separator: Current separator.
        Example::

            #Create workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Save to file
            workbook.SaveToFile("Result.csv" , ",")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def SaveAs(self ,stream:Stream,separator:str):
        """
        Save active WorkSheet using separator.

        Args:
            stream: Stream to save.
            separator: Current separator.
        Example::

            #Create workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Save to stream
            stream = MemoryStream()
            workbook.SaveToFile(stream , ",")

        """
        pass



    @abc.abstractmethod
    def SetSeparators(self ,argumentsSeparator:int,arrayRowsSeparator:int):
        """
        Sets separators for formula parsing.

        Args:
            argumentsSeparator: Arguments separator to set.
            arrayRowsSeparator: Array rows separator to set.

        """
        pass



    @abc.abstractmethod
    def Protect(self ,bIsProtectWindow:bool,bIsProtectContent:bool):
        """
        Sets protection for workbook.

        Args:
            bIsProtectWindow: Indicates if protect workbook window.
            bIsProtectContent: Indicates if protect workbook content.

        """
        pass


    @abc.abstractmethod
    def Unprotect(self):
        """
        Unprotects workbook.

        """
        pass



    @abc.abstractmethod
    def Clone(self)->'IWorkbook':
        """
        Creates copy of the current instance.

        Returns:
            Copy of the current instance.

        """
        pass



    @abc.abstractmethod
    def SetWriteProtectionPassword(self ,password:str):
        """
        This method sets write protection password.

        Args:
            password: Password to set.

        """
        pass


    @property

    @abc.abstractmethod
    def ActiveSheet(self)->'IWorksheet':
        """
        Returns an object that represents the active sheet (the sheet on top) in the active workbook or in the specified window or workbook. Returns Nothing if no sheet is active. Read-only.

        """
        pass


    @property
    @abc.abstractmethod
    def ActiveSheetIndex(self)->int:
        """
        Gets / sets index of the active sheet.

        """
        pass


    @ActiveSheetIndex.setter
    @abc.abstractmethod
    def ActiveSheetIndex(self, value:int):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def AddInFunctions(self)->'IAddInFunctions':
        """
        Returns collection of all workbook's add-in functions. Read-only.

        """
        pass


    @property

    @abc.abstractmethod
    def Author(self)->str:
        """
        Returns or sets the author of the comment. Read-only String.

        """
        pass


    @Author.setter
    @abc.abstractmethod
    def Author(self, value:str):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def IsHScrollBarVisible(self)->bool:
        """
        Gets or sets a value indicating whether to display horizontal scroll bar.
        Example::

            #Create workbook
            workbook = Workbook()
            #Hide horizontal scroll bar
            workbook.IsHScrollBarVisible = false
            #Save to file
            workbook.SaveToFile("IsHScrollBarVisible.xlsx")

        """
        pass


    @IsHScrollBarVisible.setter
    @abc.abstractmethod
    def IsHScrollBarVisible(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def IsVScrollBarVisible(self)->bool:
        """
        Gets or sets a value indicating whether to display vertical scroll bar.
        Example::

            #Create workbook
            workbook = Workbook()
            #Hide vertical scroll bar
            workbook.IsVScrollBarVisible = false
            #Save to file
            workbook.SaveToFile("IsVScrollBarVisible.xlsx")

        """
        pass


    @IsVScrollBarVisible.setter
    @abc.abstractmethod
    def IsVScrollBarVisible(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def BuiltInDocumentProperties(self)->'IBuiltInDocumentProperties':
        """
        Returns collection that represents all the built-in document properties for the specified workbook. Read-only.
        Example::

            #Create workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Get the built in document properties
            builtInDocumentProperties = workbook.DocumentProperties

        """
        pass


    @property

    @abc.abstractmethod
    def CodeName(self)->str:
        """
        Name which is used by macros to access the workbook items.

        """
        pass


    @CodeName.setter
    @abc.abstractmethod
    def CodeName(self, value:str):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def CustomDocumentProperties(self)->'ICustomDocumentProperties':
        """
        Returns collection that represents all the custom document properties for the specified workbook. Read-only.
        Example::

            #Create workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Get the document properties
            documentProperties = workbook.CustomDocumentProperties

        """
        pass


    @property
    @abc.abstractmethod
    def Date1904(self)->bool:
        """
        True if the workbook uses the 1904 date system. Read / write Boolean.

        """
        pass


    @Date1904.setter
    @abc.abstractmethod
    def Date1904(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def IsDisplayPrecision(self)->bool:
        """
        True if cell is protected.

        """
        pass


    @IsDisplayPrecision.setter
    @abc.abstractmethod
    def IsDisplayPrecision(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def IsCellProtection(self)->bool:
        """
        True if cell is protected.

        """
        pass


    @property
    @abc.abstractmethod
    def IsWindowProtection(self)->bool:
        """
        True if window is protected.

        """
        pass


    @property

    @abc.abstractmethod
    def Names(self)->'INameRanges':
        """
        For an ReservedHandle object, returns a Names collection that represents all the names in the active workbook. For a Workbook object, returns a Names collection that represents all the names in the specified workbook (including all worksheet-specific names).
        Example::

            #Create workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Get names
            names = workbook.NameRanges

        """
        pass


    @property
    @abc.abstractmethod
    def ReadOnly(self)->bool:
        """
        True if the workbook has been opened as Read-only. Read-only Boolean.

        """
        pass


    @property
    @abc.abstractmethod
    def Saved(self)->bool:
        """
        True if no changes have been made to the specified workbook since it was last saved. Read/write Boolean.

        """
        pass


    @Saved.setter
    @abc.abstractmethod
    def Saved(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Styles(self)->'IStyles':
        """
        Returns a Styles collection that represents all the styles in the specified workbook. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set styles
            styles = workbook.Styles

        """
        pass


    @property

    @abc.abstractmethod
    def Worksheets(self)->'IWorksheets':
        """
        Returns a Sheets collection that represents all the worksheets in the specified workbook. Read-only Sheets object.

        """
        pass


    @property
    @abc.abstractmethod
    def HasMacros(self)->bool:
        """
        True indicate that opened workbook contains VBA macros.

        """
        pass


    @property

    @abc.abstractmethod
    def Palette(self)->List['Color']:
        """
        Gets the palette of colors that an Excel document can have. The following table shows the color indexes and their corresponding positions in the Excel color toolbox:

        +------------------+----+----+----+----+----+----+----+----+
        |                  | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  |
        +------------------+----+----+----+----+----+----+----+----+
        | 1                | 00 | 51 | 50 | 49 | 47 | 10 | 53 | 54 |
        | 2                | 08 | 45 | 11 | 09 | 13 | 04 | 46 | 15 |
        | 3                | 02 | 44 | 42 | 48 | 41 | 40 | 12 | 55 |
        | 4                | 06 | 43 | 05 | 03 | 07 | 32 | 52 | 14 |
        | 5                | 37 | 39 | 35 | 34 | 33 | 36 | 38 | 01 |
        +------------------+----+----+----+----+----+----+----+----+
        | 6                | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
        | 7                | 24 | 25 | 26 | 27 | 28 | 29 | 30 | 31 |
        +------------------+----+----+----+----+----+----+----+----+

        Example::

            # Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            # Get colors
            colors = workbook.Colors
            # Get color
            color = colors[2]
            # Set color
            worksheet["B2"].Style.Color = color
            # Save to file
            workbook.SaveToFile("CellFormats.xlsx")
        """
        pass



    @property
    @abc.abstractmethod
    def DisplayedTab(self)->int:
        """
        Index of tab which will be displayed on document open.

        """
        pass


    @DisplayedTab.setter
    @abc.abstractmethod
    def DisplayedTab(self, value:int):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Charts(self)->'ICharts':
        """
        Collection of the chart objects.

        """
        pass


    @property
    @abc.abstractmethod
    def ThrowOnUnknownNames(self)->bool:
        """
        Indicates whether exception should be thrown when unknown name was found in a formula.

        """
        pass


    @ThrowOnUnknownNames.setter
    @abc.abstractmethod
    def ThrowOnUnknownNames(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def DisableMacrosStart(self)->bool:
        """
        This Property allows users to disable load of macros from document. Excel on file open will simply skip macros and will work as if document does not contain them. This options works only when file contains macros (HasMacros property is True).

        """
        pass


    @DisableMacrosStart.setter
    @abc.abstractmethod
    def DisableMacrosStart(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def StandardFontSize(self)->float:
        """
        Returns or sets the standard font size, in points. Read/write.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["B2"].Text = "Text"
            #Set standard font
            workbook.DefaultFontName = "Arial"
            #Set standard font size
            workbook.DefaultFontSize = 18
            #Save to file
            workbook.SaveToFile("CellFormats.xlsx")

        """
        pass


    @StandardFontSize.setter
    @abc.abstractmethod
    def StandardFontSize(self, value:float):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def StandardFont(self)->str:
        """
        Returns or sets the name of the standard font. Read/write String.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["B2"].Text = "Text"
            #Set standard font
            workbook.DefaultFontName = "Arial"
            #Set standard font size
            workbook.DefaultFontSize = 18
            #Save to file
            workbook.SaveToFile("CellFormats.xlsx")

        """
        pass


    @StandardFont.setter
    @abc.abstractmethod
    def StandardFont(self, value:str):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def Allow3DRangesInDataValidation(self)->bool:
        """
        Indicates whether to allow usage of 3D ranges in DataValidation list property (MS Excel doesn't allow).

        """
        pass


    @Allow3DRangesInDataValidation.setter
    @abc.abstractmethod
    def Allow3DRangesInDataValidation(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def RowSeparator(self)->str:
        """
        Gets / sets row separator for array parsing.

        """
        pass


    @property

    @abc.abstractmethod
    def ArgumentsSeparator(self)->str:
        """
        Formula arguments separator.

        """
        pass


    @property
    @abc.abstractmethod
    def IsRightToLeft(self)->bool:
        """
        Indicates whether worksheet is displayed right to left.

        """
        pass


    @IsRightToLeft.setter
    @abc.abstractmethod
    def IsRightToLeft(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def DisplayWorkbookTabs(self)->bool:
        """
        Indicates whether tabs are visible.

        """
        pass


    @DisplayWorkbookTabs.setter
    @abc.abstractmethod
    def DisplayWorkbookTabs(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def TabSheets(self)->'ITabSheets':
        """
        Returns collection of tab sheets. Read-only.

        """
        pass


    @property
    @abc.abstractmethod
    def DetectDateTimeInValue(self)->bool:
        """
        Indicates whether library should try to detect string value passed to Value (and Value2) property as DateTime. Setting this property to false can increase performance greatly for such operations especially on Framework 1.0 and 1.1. Default value is true.

        """
        pass


    @DetectDateTimeInValue.setter
    @abc.abstractmethod
    def DetectDateTimeInValue(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def ReadOnlyRecommended(self)->bool:
        """
        True to display a message when the file is opened, recommending that the file be opened as read-only.

        """
        pass


    @ReadOnlyRecommended.setter
    @abc.abstractmethod
    def ReadOnlyRecommended(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def PasswordToOpen(self)->str:
        """
        Gets / sets password to encrypt document.

        """
        pass


    @PasswordToOpen.setter
    @abc.abstractmethod
    def PasswordToOpen(self, value:str):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def MaxRowCount(self)->int:
        """
        Returns maximum row count for each worksheet in this workbook. Read-only.

        """
        pass


    @property
    @abc.abstractmethod
    def MaxColumnCount(self)->int:
        """
        Returns maximum column count for each worksheet in this workbook. Read-only.

        """
        pass


    @property

    @abc.abstractmethod
    def Version(self)->'ExcelVersion':
        """
        Gets / sets excel version.

        """
        pass


    @Version.setter
    @abc.abstractmethod
    def Version(self, value:'ExcelVersion'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def PivotCaches(self)->'XlsPivotCachesCollection':
        """
        Returns pivot caches collection. Read-only.
        Example::

            #Load workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Gets pivot caches collection
            pivotCaches = workbook.PivotCaches

        """
        pass


    @abc.abstractmethod
    def Activate(self):
        """
        Activates the first window associated with the workbook.

        """
        pass



    @abc.abstractmethod
    def AddFont(self ,fontToAdd:'IFont')->'IFont':
        """
        Adds font to the inner fonts collection and makes this font read-only.

        Args:
            fontToAdd: Font to add.

        Returns:
            Added font.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def Close(self ,SaveChanges:bool,Filename:str):
        """
        Closes the object.

        Args:
            SaveChanges: If True, all changes will be saved.
            Filename: Name of the file.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def Close(self ,saveChanges:bool):
        """
        Closes the object.

        Args:
            saveChanges: If True, all changes will be saved.

        """
        pass


    @dispatch
    @abc.abstractmethod
    def Close(self):
        """
        Closes the object without saving.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def Close(self ,Filename:str):
        """
        Closes the object and saves changes into specified file.

        Args:
            Filename: 

        """
        pass


    @abc.abstractmethod
    def CopyToClipboard(self):
        """
        Copies workbook to the clipboard.

        """
        pass



    @abc.abstractmethod
    def CreateTemplateMarkersProcessor(self)->'IMarkersDesigner':
        """
        Creates object that can be used for template markers processing.

        Returns:
            Object that can be used for template markers processing.

        """
        pass


    @abc.abstractmethod
    def Save(self):
        """
        Saves changes to the specified workbook.
        Example::

            #Load workbook
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            #Save to file
            workbook.Save()

        """
        pass


    @dispatch

    @abc.abstractmethod
    def SaveAs(self ,Filename:str):
        """
        Short variant of SaveAs method.

        Args:
            Filename: 

        """
        pass


    @dispatch

    @abc.abstractmethod
    def SaveAs(self ,Filename:str,saveType:ExcelSaveType):
        """
        Short variant of SaveAs method.

        Args:
            Filename: Name of the file.
            saveType: Excel save type.

        """
        pass



    @abc.abstractmethod
    def SaveAsHtml(self ,filename:str,saveOptions:'HTMLOptions'):
        """
        Saves changes to the specified stream.

        Args:
            filename: Name of the file.
            saveOptions: Save options in html.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def SaveAs(self ,stream:Stream):
        """
        Saves changes to the specified stream.

        Args:
            stream: Stream that will receive workbook data.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def SaveAs(self ,stream:Stream,saveType:ExcelSaveType):
        """
        Saves changes to the specified stream.

        Args:
            stream: Stream that will receive workbook data.
            saveType: Type of the Excel file.

        """
        pass


#    @dispatch
#
#    @abc.abstractmethod
#    def SaveAs(self ,fileName:str,saveType:ExcelSaveType,response:'HttpResponse'):
#        """
#    <summary>
#        Saves changes to the specified HttpResponse.
#    </summary>
#    <param name="fileName">Name of the file in HttpResponse.</param>
#    <param name="saveType">Type of the Excel file.</param>
#    <param name="response">HttpResponse that will receive workbook's data.</param>
#        """
#        pass
#


#    @dispatch
#
#    @abc.abstractmethod
#    def SaveAs(self ,fileName:str,response:'HttpResponse'):
#        """
#    <summary>
#        Saves changes to the specified HttpResponse.
#    </summary>
#    <param name="fileName">Name of the file in HttpResponse.</param>
#    <param name="response">HttpResponse to save in.</param>
#        """
#        pass
#



    @abc.abstractmethod
    def SetPaletteColor(self ,index:int,color:'Color'):
        """
        Set user color for specified element in Color table.

        Args:
            index: Index of Color in array.
            color: New color which must be set.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set palette color
            workbook.ChangePaletteColor(System.Drawing.Color.Red , 10)
            #Set color
            worksheet["B2"].Style.Color = workbook.Colors[10]
            #Save to file
            workbook.SaveToFile("CellFormats.xlsx")

        """
        pass


    @abc.abstractmethod
    def ResetPalette(self):
        """
        Recover palette to default values.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get colors
            System.Drawing.Color[] colors = workbook.Colors
            #Check color
            print(colors[2].Name)
            #Set color
            colors[2] = System.Drawing.Color.Yellow
            #Reset palette
            workbook.ResetPalette()
            #Check color
            print(workbook.Colors[2].Name)
            #Save to file
            workbook.SaveToFile("CellFormats.xlsx")

        """
        pass



    @abc.abstractmethod
    def GetPaletteColor(self ,color:'ExcelColors')->'Color':
        """
        Method return Color object from workbook palette by its index.

        Args:
            color: Index from palette array.

        Returns:
            RGB Color.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get color
            System.Drawing.color = workbook.GetPaletteColor(ExcelColors.Red)
            #Set color
            worksheet["B2"].Style.Color = workbook.Colors[10]
            #Save to file
            workbook.SaveToFile("CellFormats.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def GetNearestColor(self ,color:Color)->ExcelColors:
        """
        Gets the nearest color to the specified Color structure from Workbook palette.

        Args:
            color: System color.

        Returns:
            Color index from workbook palette.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get color
            color = workbook.GetMatchingColor(System.Drawing.Color.Red)
            #Set color
            worksheet["B2"].Style.KnownColor = color
            #Save to file
            workbook.SaveToFile("CellFormats.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def GetNearestColor(self ,r:int,g:int,b:int)->ExcelColors:
        """
        Gets the nearest color to the specified by red, green, and blue values color from Workbook palette.

        Args:
            r: Red component of the color.
            g: Green component of the color.
            b: Blue component of the color.

        Returns:
            Color index from workbook palette.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get color
            color = workbook.GetMatchingColor(255, 0, 0)
            #Set color
            worksheet["B2"].Style.KnownColor = color
            #Save to file
            workbook.SaveToFile("CellFormats.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def SetColorOrGetNearest(self ,color:Color)->ExcelColors:
        """
        If there is at least one free color, define a new color; if not, search for the closest one.

        Args:
            color: 

        Returns:
            Color index from workbook palette.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def SetColorOrGetNearest(self ,r:int,g:int,b:int)->ExcelColors:
        """
        If there is at least one free color, define a new color; if not, search for the closest one.

        Args:
            r: Red component of the color.
            g: Green component of the color.
            b: Blue component of the color.

        Returns:
            Color index from workbook palette.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def CreateFont(self)->IFont:
        """
        Method to create a font object and register it in the workbook.

        Returns:
            Newly created font.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            richText = worksheet["B2"].RichText
            #Create font
            font = workbook.CreateFont()
            #Set color
            font.Color = Color.Red
            #Set text
            richText.Text = "Sample"
            #Set font
            richText.SetFont(0, 5, font)
            #Save to file
            workbook.SaveToFile("CellFormats.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def CreateFont(self ,baseFont:IFont)->IFont:
        """
        Method that creates font object based on another font object and registers it in the workbook.

        Args:
            baseFont: Base font for the new one.

        Returns:
            Newly created font.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def CreateFont(self ,nativeFont:Font)->IFont:
        """
        Method creates a font object based on native font and register it in the workbook.

        Args:
            nativeFont: Native font to get settings from.

        """
        pass


