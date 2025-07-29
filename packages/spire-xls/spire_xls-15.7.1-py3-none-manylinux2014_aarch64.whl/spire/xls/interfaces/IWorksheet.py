from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IWorksheet (  ITabSheet, IExcelApplication) :
    """

    """

    @abc.abstractmethod
    def Protect(self ,password:str):
        """
        Protects worksheet's content with password.

        Args:
            password: Password to protect with.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Protects the first worksheet's content with password
            worksheet.Protect("123456")
            #Save to file
            workbook.SaveToFile("Protect.xlsx")

        """
        pass



    @abc.abstractmethod
    def Unprotect(self ,password:str):
        """
        Unprotects worksheet's content with password.

        Args:
            password: Password to unprotect.

        """
        pass



    @abc.abstractmethod
    def AutoFitRow(self ,rowIndex:int):
        """
        Autofits specified row.

        Args:
            rowIndex: One-based row index.
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
        pass



    @abc.abstractmethod
    def AutoFitColumn(self ,columnIndex:int):
        """
        Autofits specified column.

        Args:
            columnIndex: One-based column index.
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
        pass


    @dispatch

    @abc.abstractmethod
    def Replace(self ,oldValue:str,newValue:str):
        """
        Replaces specified string by specified value.

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
#    <param name="isFieldNamesShown">Indicates wheter field name must be shown.</param>
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
#    <param name="newValues">Data table with new data.</param>
#    <param name="isFieldNamesShown">Indicates whether field name must be shown.</param>
#        """
#        pass
#


    @abc.abstractmethod
    def Remove(self):
        """
        Removes worksheet from parent worksheets collection.

        """
        pass



    @abc.abstractmethod
    def MoveWorksheet(self ,iNewIndex:int):
        """
        Moves worksheet.

        Args:
            iNewIndex: New index of the worksheet.

        """
        pass



    @abc.abstractmethod
    def ColumnWidthToPixels(self ,widthInChars:float)->int:
        """
        Converts column width into pixels.

        Args:
            widthInChars: Width in characters.

        Returns:
            Width in pixels

        """
        pass



    @abc.abstractmethod
    def PixelsToColumnWidth(self ,pixels:float)->float:
        """
        Converts pixels into column width (in characters).

        Args:
            pixels: Width in pixels

        Returns:
            Widht in characters.

        """
        pass



    @abc.abstractmethod
    def SetColumnWidthInPixels(self ,columnIndex:int,value:int):
        """
        Sets column width in pixels.

        Args:
            columnIndex: One-based column index.
            value: Width to set.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set column width
            worksheet.SetColumnWidthInPixels(2, 160)
            #Save to file
            workbook.SaveToFile("SetColumnWidthInPixels.xlsx")

        """
        pass



    @abc.abstractmethod
    def SetRowHeightPixels(self ,Row:int,value:float):
        """
        Sets row height in pixels.

        Args:
            Row: One-based row index to set height.
            value: Value in pixels to set.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set row height
            worksheet.SetRowHeightPixels(3, 150)
            #Save to file
            workbook.SaveToFile("SetRowHeightPixels.xlsx")

        """
        pass



    @abc.abstractmethod
    def GetColumnWidthPixels(self ,Column:int)->int:
        """
        Returns width in pixels from ColumnInfoRecord if there is corresponding ColumnInfoRecord or StandardWidth if not.

        Args:
            Column: One-based index of the column.

        Returns:
            Width in pixels of the specified column.
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
        pass



    @abc.abstractmethod
    def GetRowHeightPixels(self ,Row:int)->int:
        """
        Returns height from RowRecord if there is a corresponding RowRecord. Otherwise returns StandardHeight.

        Args:
            Row: One-bazed index of the row.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["C2"].Text = "Sample text"
            worksheet["C2"].Style.Font.Size = 18
            #Set auto fit
            worksheet.AutoFitRow(2)
            #Get row height
            print(worksheet.GetRowHeightPixels(2))
            #Save to file
            workbook.SaveToFile("UsedRange.xlsx")

        """
        pass



    @abc.abstractmethod
    def SaveToFile(self ,fileName:str,separator:str):
        """
        Save tabsheet using separator.

        Args:
            fileName: File to save.
            separator: Current seperator.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Save to file

        """
        pass



    @abc.abstractmethod
    def SaveToStream(self ,stream:'Stream',separator:str):
        """
        Save tabsheet using separator.

        Args:
            stream: Stream to save.
            separator: Current seperator.
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
        pass


    @dispatch

    @abc.abstractmethod
    def SetDefaultColumnStyle(self ,iColumnIndex:int,defaultStyle:IStyle):
        """
        Sets by column index default style for column.

        Args:
            iColumnIndex: Column index.
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
        pass


    @dispatch

    @abc.abstractmethod
    def SetDefaultColumnStyle(self ,iStartColumnIndex:int,iEndColumnIndex:int,defaultStyle:IStyle):
        """
        Sets by column index default style for column.

        Args:
            iStartColumnIndex: Start column index.
            iEndColumnIndex: End column index.
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
        pass


    @dispatch

    @abc.abstractmethod
    def SetDefaultRowStyle(self ,rowIndex:int,defaultStyle:IStyle):
        """
        Sets by column index default style for row.

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
        pass


    @dispatch

    @abc.abstractmethod
    def SetDefaultRowStyle(self ,iStartRowIndex:int,iEndRowIndex:int,defaultStyle:IStyle):
        """
        Sets by column index default style for row.

        Args:
            iStartRowIndex: Start row index.
            iEndRowIndex: End row index.
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
        pass



    @abc.abstractmethod
    def GetDefaultColumnStyle(self ,iColumnIndex:int)->'IStyle':
        """
        Returns default column style.

        Args:
            iColumnIndex: Column index.

        Returns:
            Default column style or null if style wasn't set.
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
        pass



    @abc.abstractmethod
    def GetDefaultRowStyle(self ,rowIndex:int)->'IStyle':
        """
        Returns default row style.

        Args:
            rowIndex: Row index.

        Returns:
            Default row style or null if style wasn't set.
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
        pass



    @abc.abstractmethod
    def SetValue(self ,iRow:int,iColumn:int,value:str):
        """
        Sets value in the specified cell.

        Args:
            iRow: One-based row index  of the cell to set value.
            iColumn: One-based column index of the cell to set value.
            value: Value to set.

        """
        pass



    @abc.abstractmethod
    def SetNumber(self ,iRow:int,iColumn:int,value:float):
        """
        Sets value in the specified cell.

        Args:
            iRow: One-based row index  of the cell to set value.
            iColumn: One-based column index of the cell to set value.
            value: Value to set.

        """
        pass



    @abc.abstractmethod
    def SetBoolean(self ,iRow:int,iColumn:int,value:bool):
        """
        Sets value in the specified cell.

        Args:
            iRow: One-based row index  of the cell to set value.
            iColumn: One-based column index of the cell to set value.
            value: Value to set.

        """
        pass



    @abc.abstractmethod
    def SetText(self ,iRow:int,iColumn:int,value:str):
        """
        Sets text in the specified cell.

        Args:
            iRow: One-based row index  of the cell to set value.
            iColumn: One-based column index of the cell to set value.
            value: Text to set.

        """
        pass



    @abc.abstractmethod
    def SetFormula(self ,iRow:int,iColumn:int,value:str):
        """
        Sets formula in the specified cell.

        Args:
            iRow: One-based row index  of the cell to set value.
            iColumn: One-based column index of the cell to set value.
            value: Formula to set.

        """
        pass



    @abc.abstractmethod
    def SetError(self ,iRow:int,iColumn:int,value:str):
        """
        Sets error in the specified cell.

        Args:
            iRow: One-based row index  of the cell to set value.
            iColumn: One-based column index of the cell to set value.
            value: Error to set.

        """
        pass



    @abc.abstractmethod
    def SetBlank(self ,iRow:int,iColumn:int):
        """
        Sets blank in specified cell.

        Args:
            iRow: One-based row index  of the cell to set value.
            iColumn: One-based column index of the cell to set value.

        """
        pass



    @abc.abstractmethod
    def SetFormulaNumberValue(self ,iRow:int,iColumn:int,value:float):
        """
        Sets formula number value.

        Args:
            iRow: One based row index.
            iColumn: One based column index.
            value: Represents formula number value for set.

        """
        pass



    @abc.abstractmethod
    def SetFormulaErrorValue(self ,iRow:int,iColumn:int,value:str):
        """
        Sets formula error value.

        Args:
            iRow: One based row index.
            iColumn: One based column index.
            value: Represents formula error value for set.

        """
        pass



    @abc.abstractmethod
    def SetFormulaBoolValue(self ,iRow:int,iColumn:int,value:bool):
        """
        Sets formula bool value.

        Args:
            iRow: One based row index.
            iColumn: One based column index.
            value: Represents formula bool value for set.

        """
        pass



    @abc.abstractmethod
    def SetFormulaStringValue(self ,iRow:int,iColumn:int,value:str):
        """
        Sets formula string value.

        Args:
            iRow: One based row index.
            iColumn: One based column index.
            value: Represents formula string value for set.

        """
        pass



    @abc.abstractmethod
    def GetText(self ,row:int,column:int)->str:
        """
        Returns string value corresponding to the cell.

        Args:
            row: One-based row index of the cell to get value from.
            column: One-based column index of the cell to get value from.

        Returns:
            String contained by the cell.

        """
        pass



    @abc.abstractmethod
    def GetNumber(self ,row:int,column:int)->float:
        """
        Returns number value corresponding to the cell.

        Args:
            row: One-based row index of the cell to get value from.
            column: One-based column index of the cell to get value from.

        Returns:
            Number contained by the cell.

        """
        pass



    @abc.abstractmethod
    def GetFormula(self ,row:int,column:int,bR1C1:bool)->str:
        """
        Returns formula value corresponding to the cell.

        Args:
            row: One-based row index of the cell to get value from.
            column: One-based column index of the cell to get value from.
            bR1C1: Indicates whether R1C1 notation should be used.

        Returns:
            Formula contained by the cell.

        """
        pass



    @abc.abstractmethod
    def GetError(self ,row:int,column:int)->str:
        """
        Gets error value from cell.

        Args:
            row: Row index.
            column: Column index.

        Returns:
            Returns error value or null.

        """
        pass



    @abc.abstractmethod
    def GetBoolean(self ,row:int,column:int)->bool:
        """
        Gets bool value from cell.

        Args:
            row: Represents row index.
            column: Represents column index.

        Returns:
            Returns found bool value. If cannot found returns false.

        """
        pass



    @abc.abstractmethod
    def GetFormulaBoolValue(self ,row:int,column:int)->bool:
        """
        Gets formula bool value from cell.

        Args:
            row: Represents row index.
            column: Represents column index.

        Returns:
            Returns found bool value. If cannot found returns false.

        """
        pass



    @abc.abstractmethod
    def GetFormulaErrorValue(self ,row:int,column:int)->str:
        """
        Gets formula error value from cell.

        Args:
            row: Row index.
            column: Column index.

        Returns:
            Returns error value or null.

        """
        pass



    @abc.abstractmethod
    def GetFormulaNumberValue(self ,row:int,column:int)->float:
        """
        Returns formula number value corresponding to the cell.

        Args:
            row: One-based row index of the cell to get value from.
            column: One-based column index of the cell to get value from.

        Returns:
            Number contained by the cell.

        """
        pass



    @abc.abstractmethod
    def GetFormulaStringValue(self ,row:int,column:int)->str:
        """
        Returns formula string value corresponding to the cell.

        Args:
            row: One-based row index of the cell to get value from.
            column: One-based column index of the cell to get value from.

        Returns:
            String contained by the cell.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def SaveToImage(self ,firstRow:int,firstColumn:int,lastRow:int,lastColumn:int)->Stream:
        """
        Converts range into image (Bitmap).

        Args:
            firstRow: One-based index of the first row to convert.
            firstColumn: One-based index of the first column to convert.
            lastRow: One-based index of the last row to convert.
            lastColumn: One-based index of the last column to convert.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def SaveToImage(self ,stream:Stream,firstRow:int,firstColumn:int,lastRow:int,lastColumn:int,imageType:ImageType)->Stream:
        """
        Converts range into image.

        Args:
            firstRow: One-based index of the first row to convert.
            firstColumn: One-based index of the first column to convert.
            lastRow: One-based index of the last row to convert.
            lastColumn: One-based index of the last column to convert.
            imageType: Type of the image to create.
            stream: Output stream. It is ignored if null.

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
        pass


    @dispatch

    @abc.abstractmethod
    def SaveToHtml(self ,filename:str):
        """
        Saves worksheet with specified filename.

        Args:
            filename: File to save.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Save to HTML file
            worksheet.SaveToHtml("Output.html")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def SaveToHtml(self ,stream:Stream):
        """
        Save to HTML stream.

        Args:
            stream: Stream object.
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
        pass


    @dispatch

    @abc.abstractmethod
    def SaveToHtml(self ,filename:str,saveOptions:HTMLOptions):
        """
        Saves as HTML.

        Args:
            filename: The filename.
            saveOptions: The option.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Save to HTML file
            worksheet.SaveToHtml("Sample.html" , Spire.Xls.Core.Spreadsheet.HTMLOptions.Default)

        """
        pass


    @dispatch

    @abc.abstractmethod
    def SaveToHtml(self ,stream:Stream,saveOptions:HTMLOptions):
        """
        Saves work sheet to HTML.

        Args:
            stream: Stream to save.
            saveOptions: Save Options.
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
        pass


    @dispatch

    @abc.abstractmethod
    def SaveToImage(self ,outputStream:Stream,firstRow:int,firstColumn:int,lastRow:int,lastColumn:int,emfType:EmfType)->Stream:
        """
        Converts range into metafile image.

        Args:
            firstRow: One-based index of the first row to convert.
            firstColumn: One-based index of the first column to convert.
            lastRow: One-based index of the last row to convert.
            lastColumn: One-based index of the last column to convert.
            emfType: Metafile EmfType.
            outputStream: Output stream. It is ignored if null.

        Returns:
            Created image.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def SaveToImage(self ,outputStream:Stream,firstRow:int,firstColumn:int,lastRow:int,lastColumn:int,imageType:ImageType,emfType:EmfType)->Stream:
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
        pass



    @abc.abstractmethod
    def add_CellValueChanged(self ,value:'CellValueChangedEventHandler'):
        """

        """
        pass



    @abc.abstractmethod
    def remove_CellValueChanged(self ,value:'CellValueChangedEventHandler'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def AutoFilters(self)->'IAutoFilters':
        """
        Returns collection of worksheet's autofilters. Read-only.

        """
        pass


    @property

    @abc.abstractmethod
    def Cells(self)->'ListXlsRanges':
        """
        Returns all used cells in the worksheet. Read-only.

        """
        pass



    @property
    @abc.abstractmethod
    def DisplayPageBreaks(self)->bool:
        """
        True if page breaks (both automatic and manual) on the specified worksheet are displayed. Read / write Boolean.

        """
        pass


    @DisplayPageBreaks.setter
    @abc.abstractmethod
    def DisplayPageBreaks(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def Index(self)->int:
        """
        Returns the index number of the object within the collection of similar objects. Read-only.

        """
        pass


    @property

    @abc.abstractmethod
    def MergedCells(self)->'ListXlsRanges':
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
        pass



    @property

    @abc.abstractmethod
    def Names(self)->'INameRanges':
        """
        For a Worksheet object, returns a Names collection that represents all the worksheet-specific names (names defined with the "WorksheetName!" prefix). Read-only Names object.

        """
        pass


    @property

    @abc.abstractmethod
    def CodeName(self)->str:
        """
        Name that is used by macros to access the workbook items.

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
    def PageSetup(self)->'IPageSetup':
        """
        Returns a PageSetup object that contains all the page setup settings for the specified object. Read-only.

        """
        pass


    @property

    @abc.abstractmethod
    def AllocatedRange(self)->'IXLSRange':
        """
        Returns a Range object that represents a cell or a range of cells.

        """
        pass


    @property

    @abc.abstractmethod
    def Rows(self)->'ListXlsRanges':
        """
        For a Worksheet object, returns an array of Range objects that represents all the rows on the specified worksheet. Read-only Range object.

        """
        pass



    @property
    @abc.abstractmethod
    def Columns(self)->'ListXlsRanges':
        """
        For a Worksheet object, returns an array of Range objects that represents all the columns on the specified worksheet. Read-only Range object.

        """
        pass



    @property
    @abc.abstractmethod
    def DefaultRowHeight(self)->float:
        """
        Returns the standard (default) height of all the rows in the worksheet, in points. Read/write Double.
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
        pass


    @DefaultRowHeight.setter
    @abc.abstractmethod
    def DefaultRowHeight(self, value:float):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def DefaultColumnWidth(self)->float:
        """
        Returns or sets the standard (default) width of all the columns in the worksheet. Read/write Double.
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
        pass


    @DefaultColumnWidth.setter
    @abc.abstractmethod
    def DefaultColumnWidth(self, value:float):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Type(self)->'ExcelSheetType':
        """
        Returns or sets the worksheet type. Read-only ExcelSheetType.

        """
        pass


    @property

    @abc.abstractmethod
    def Range(self)->'XlsRange':
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
        pass


    @property
    @abc.abstractmethod
    def Zoom(self)->int:
        """
        Zoom factor of document. Value must be in range from 10 till 400.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set zoom
            worksheet.Zoom = 200
            #Save to file
            workbook.SaveToFile("Zoom.xlsx")

        """
        pass


    @Zoom.setter
    @abc.abstractmethod
    def Zoom(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def VerticalSplit(self)->int:
        """
        Gets or sets the position of vertical split in the worksheet.

        """
        pass


    @VerticalSplit.setter
    @abc.abstractmethod
    def VerticalSplit(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def HorizontalSplit(self)->int:
        """
        Gets or sets the position of horizontal split in the worksheet.

        """
        pass


    @HorizontalSplit.setter
    @abc.abstractmethod
    def HorizontalSplit(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def FirstVisibleRow(self)->int:
        """
        Index to first visible row in bottom pane(s).

        """
        pass


    @FirstVisibleRow.setter
    @abc.abstractmethod
    def FirstVisibleRow(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def FirstVisibleColumn(self)->int:
        """
        Index to first visible column in right pane(s).

        """
        pass


    @FirstVisibleColumn.setter
    @abc.abstractmethod
    def FirstVisibleColumn(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def ActivePane(self)->int:
        """
        Identifier of pane with active cell cursor.

        """
        pass


    @ActivePane.setter
    @abc.abstractmethod
    def ActivePane(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def IsDisplayZeros(self)->bool:
        """
        True if zero values to be displayed False otherwise.

        """
        pass


    @IsDisplayZeros.setter
    @abc.abstractmethod
    def IsDisplayZeros(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
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
        pass


    @GridLinesVisible.setter
    @abc.abstractmethod
    def GridLinesVisible(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def GridLineColor(self)->'ExcelColors':
        """
        Gets / sets Grid line color.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set grid lines color
            worksheet.GridLineColor = ExcelColors.Red
            #Save to file
            workbook.SaveToFile("GridLineColor.xlsx")

        """
        pass


    @GridLineColor.setter
    @abc.abstractmethod
    def GridLineColor(self, value:'ExcelColors'):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def RowColumnHeadersVisible(self)->bool:
        """
        True if row and column headers are visible; False otherwise.

        """
        pass


    @RowColumnHeadersVisible.setter
    @abc.abstractmethod
    def RowColumnHeadersVisible(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def FormulasVisible(self)->bool:
        """

        """
        pass


    @FormulasVisible.setter
    @abc.abstractmethod
    def FormulasVisible(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def VPageBreaks(self)->'IVPageBreaks':
        """
        Returns a VPageBreaks collection that represents the vertical page breaks on the sheet. Read-only.

        """
        pass


    @property

    @abc.abstractmethod
    def HPageBreaks(self)->'IHPageBreaks':
        """
        Returns an HPageBreaks collection that represents the horizontal page breaks on the sheet. Read-only.

        """
        pass


    @property
    @abc.abstractmethod
    def IsStringsPreserved(self)->bool:
        """
        Indicates if all values in the workbook are preserved as strings.

        """
        pass


    @IsStringsPreserved.setter
    @abc.abstractmethod
    def IsStringsPreserved(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Comments(self)->'IComments':
        """
        Comments collection.
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
        pass


    @dispatch

    @abc.abstractmethod
    def get_Item(self ,row:int,column:int)->IXLSRange:
        """
        Gets / sets cell by row and index.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def get_Item(self ,row:int,column:int,lastRow:int,lastColumn:int)->IXLSRange:
        """
        Get cells range.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def get_Item(self ,name:str)->IXLSRange:
        """
        Get cell range.

        """
        pass


    @property

    @abc.abstractmethod
    def HyperLinks(self)->'IHyperLinks':
        """
        Collection of all worksheet's hyperlinks.

        """
        pass


    @property
    @abc.abstractmethod
    def UseRangesCache(self)->bool:
        """
        Indicates whether all created range objects should be cached. Default value is false.

        """
        pass


    @UseRangesCache.setter
    @abc.abstractmethod
    def UseRangesCache(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def TopVisibleRow(self)->int:
        """
        Gets/sets top visible row of the worksheet.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set top visible row
            worksheet.TopVisibleRow = 5
            #Get top visible row
            Console.Write(worksheet.TopVisibleRow)
            #Save to file
            workbook.SaveToFile("TopVisibleRow.xlsx")

        """
        pass


    @TopVisibleRow.setter
    @abc.abstractmethod
    def TopVisibleRow(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def LeftVisibleColumn(self)->int:
        """
        Gets/sets left visible column of the worksheet.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set left visible column
            worksheet.LeftVisibleColumn = 3
            #Get left visible column
            Console.Write(worksheet.LeftVisibleColumn)
            #Save to file
            workbook.SaveToFile("LeftVisibleColumn.xlsx")

        """
        pass


    @LeftVisibleColumn.setter
    @abc.abstractmethod
    def LeftVisibleColumn(self, value:int):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def PivotTables(self)->'PivotTablesCollection':
        """
        Returns pivot table collection containing all pivot tables in the worksheet. Read-only.

        """
        pass


    @property

    @abc.abstractmethod
    def ListObjects(self)->'IListObjects':
        """
        Gets collection of all list objects in the worksheet.

        """
        pass


    @property

    @abc.abstractmethod
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
        pass


    @property
    @abc.abstractmethod
    def HasOleObjects(self)->bool:
        """
        Gets or sets a value indicating whether this instance is OLE object.
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
        pass


    @abc.abstractmethod
    def CopyToClipboard(self):
        """
        Copies worksheet into the clipboard.

        """
        pass


    @abc.abstractmethod
    def Clear(self):
        """
        Clears worksheet data. Removes all formatting and merges.

        """
        pass


    @abc.abstractmethod
    def ClearData(self):
        """
        Clears worksheet. Only the data is removed from each cell.

        """
        pass



    @abc.abstractmethod
    def CheckExistence(self ,iRow:int,iColumn:int)->bool:
        """
        Indicates whether a cell was initialized or accessed by the user.

        Args:
            iRow: One-based row index of the cell.
            iColumn: One-based column index of the cell.

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
        pass



    @abc.abstractmethod
    def CreateNamedRanges(self ,namedRange:str,referRange:str,vertical:bool):
        """

        """
        pass



    @abc.abstractmethod
    def IsColumnVisible(self ,columnIndex:int)->bool:
        """
        Method check is Column with specifed index visible to end user or not.

        Args:
            columnIndex: Index of column.

        Returns:
            True - column is visible; otherwise False.

        """
        pass



    @abc.abstractmethod
    def IsRowVisible(self ,rowIndex:int)->bool:
        """
        Method check is Row with specifed index visible to user or not.

        Args:
            rowIndex: Index of row visibility of each must be checked.

        Returns:
            True - row is visible to user, otherwise False.

        """
        pass



    @abc.abstractmethod
    def DeleteRow(self ,index:int):
        """
        Removes specified row (with formulas update).

        Args:
            index: One-based row index to remove.

        """
        pass



    @abc.abstractmethod
    def DeleteColumn(self ,index:int):
        """
        Removes specified column (with formulas update).

        Args:
            index: One-based column index to remove.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def InsertArray(self ,arrObject:List[SpireObject],firstRow:int,firstColumn:int,isVertical:bool)->int:
        """
        Imports an array of objects into a worksheet.

        Args:
            arrObject: Array to import.
            firstRow: Row of the first cell where array should be imported.
            firstColumn: Column of the first cell where array should be imported.
            isVertical: True if array should be imported vertically; False - horizontally.

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
        pass


    @dispatch

    @abc.abstractmethod
    def InsertArray(self ,arrString:List[str],firstRow:int,firstColumn:int,isVertical:bool)->int:
        """
        Imports an array of strings into a worksheet.

        Args:
            arrString: Array to import.
            firstRow: Row of the first cell where array should be imported.
            firstColumn: Column of the first cell where array should be imported.
            isVertical: True if array should be imported vertically; False - horizontally.

        Returns:
            Number of imported elements.
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
        pass


    @dispatch

    @abc.abstractmethod
    def InsertArray(self ,arrInt:List[int],firstRow:int,firstColumn:int,isVertical:bool)->int:
        """
        Imports an array of integers into a worksheet.

        Args:
            arrInt: Array to import.
            firstRow: Row of the first cell where array should be imported.
            firstColumn: Column of the first cell where array should be imported.
            isVertical: True if array should be imported vertically; False - horizontally.

        Returns:
            Number of imported elements.
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
        pass


    @dispatch

    @abc.abstractmethod
    def InsertArray(self ,arrDouble:List[float],firstRow:int,firstColumn:int,isVertical:bool)->int:
        """
        Imports an array of doubles into a worksheet.

        Args:
            arrDouble: Array to import.
            firstRow: Row of the first cell where array should be imported.
            firstColumn: Column of the first cell where array should be imported.
            isVertical: True if array should be imported vertically; False - horizontally.

        Returns:
            Number of imported elements.
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
        pass


#    @dispatch
#
#    @abc.abstractmethod
#    def InsertArray(self ,arrDateTime:'DateTime[]',firstRow:int,firstColumn:int,isVertical:bool)->int:
#        """
#    <summary>
#         Imports an array of DateTimes into worksheet.
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
#    <param name="arrDateTime">Array to import.</param>
#    <param name="firstRow">Row of the first cell where array should be imported.</param>
#    <param name="firstColumn">Column of the first cell where array should be imported.</param>
#    <param name="isVertical">True if array should be imported vertically; False - horizontally.</param>
#    <returns>Number of imported elements.</returns>
#        """
#        pass
#


#    @dispatch
#
#    @abc.abstractmethod
#    def InsertArray(self ,arrObject:'Object[,]',firstRow:int,firstColumn:int)->int:
#        """
#
#        """
#        pass
#


#
#    @abc.abstractmethod
#    def InsertDataColumn(self ,dataColumn:'DataColumn',isFieldNameShown:bool,firstRow:int,firstColumn:int)->int:
#        """
#    <summary>
#         Imports data from a DataColumn into worksheet.
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
#    <param name="dataColumn">DataColumn with desired data.</param>
#    <param name="isFieldNameShown">True if column name must also be imported.</param>
#    <param name="firstRow">Row of the first cell where DataTable should be imported.</param>
#    <param name="firstColumn">Column of the first cell where DataTable should be imported.</param>
#    <returns>Number of imported rows.</returns>
#        """
#        pass
#


#    @dispatch
#
#    @abc.abstractmethod
#    def InsertDataTable(self ,dataTable:'DataTable',isFieldNameShown:bool,firstRow:int,firstColumn:int)->int:
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
#    <param name="dataTable">DataTable with desired data.</param>
#    <param name="isFieldNameShown">True if column names must also be imported.</param>
#    <param name="firstRow">Row of the first cell where DataTable should be imported.</param>
#    <param name="firstColumn">Column of the first cell where DataTable should be imported.</param>
#    <returns>Number of imported rows.</returns>
#        """
#        pass
#


#    @dispatch
#
#    @abc.abstractmethod
#    def InsertDataTable(self ,dataTable:'DataTable',isFieldNameShown:bool,firstRow:int,firstColumn:int,preserveTypes:bool)->int:
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
#    <param name="dataTable">DataTable with desired data.</param>
#    <param name="isFieldNameShown">True if column names must also be imported.</param>
#    <param name="firstRow">Row of the first cell where DataTable should be imported.</param>
#    <param name="firstColumn">Column of the first cell where DataTable should be imported.</param>
#    <param name="preserveTypes">
#             Indicates whether XlsIO should try to preserve types in DataTable,
#             i.e. if it is set to False (default) and in DataTable we have in string column
#             value that contains only numbers, it would be converted to number.
#     </param>
#    <returns>Number of imported rows.</returns>
#        """
#        pass
#


#    @dispatch
#
#    @abc.abstractmethod
#    def InsertDataTable(self ,dataTable:'DataTable',isFieldNameShown:bool,firstRow:int,firstColumn:int,maxRows:int,maxColumns:int)->int:
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
#    <param name="dataTable">DataTable with desired data.</param>
#    <param name="isFieldNameShown">True if column names must also be imported.</param>
#    <param name="firstRow">Row of the first cell where DataTable should be imported.</param>
#    <param name="firstColumn">Column of the first cell where DataTable should be imported.</param>
#    <param name="maxRows">Maximum number of rows to import.</param>
#    <param name="maxColumns">Maximum number of columns to import.</param>
#    <returns>Number of imported rows.</returns>
#        """
#        pass
#


#    @dispatch
#
#    @abc.abstractmethod
#    def InsertDataTable(self ,dataTable:'DataTable',isFieldNameShown:bool,firstRow:int,firstColumn:int,maxRows:int,maxColumns:int,preserveTypes:bool)->int:
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
#    <param name="dataTable">DataTable with desired data.</param>
#    <param name="isFieldNameShown">True if column names must also be imported.</param>
#    <param name="firstRow">Row of the first cell where DataTable should be imported.</param>
#    <param name="firstColumn">Column of the first cell where DataTable should be imported.</param>
#    <param name="maxRows">Maximum number of rows to import.</param>
#    <param name="maxColumns">Maximum number of columns to import.</param>
#    <param name="preserveTypes">
#             Indicates whether XlsIO should try to preserve types in DataTable,
#             i.e. if it is set to False (default) and in DataTable we have in string column
#             value that contains only numbers, it would be converted to number.
#     </param>
#    <returns>Number of imported rows.</returns>
#        """
#        pass
#


#    @dispatch
#
#    @abc.abstractmethod
#    def InsertDataView(self ,dataView:'DataView',isFieldNameShown:bool,firstRow:int,firstColumn:int)->int:
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
#    <param name="dataView">DataView with desired data.</param>
#    <param name="isFieldNameShown">TRUE if column names must also be imported.</param>
#    <param name="firstRow">Row of the first cell where DataView should be imported.</param>
#    <param name="firstColumn">Column of the first cell where DataView should be imported.</param>
#    <returns>Number of imported rows.</returns>
#        """
#        pass
#


#    @dispatch
#
#    @abc.abstractmethod
#    def InsertDataView(self ,dataView:'DataView',isFieldNameShown:bool,firstRow:int,firstColumn:int,bPreserveTypes:bool)->int:
#        """
#    <summary>
#         Imports data from a DataView into worksheet.
#        <example>The following code illustrates how to Imports data from a DataView into a worksheet with the specified specified row and column along with preserve type:
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
#    <param name="dataView">DataView with desired data.</param>
#    <param name="isFieldNameShown">TRUE if column names must also be imported.</param>
#    <param name="firstRow">Row of the first cell where DataView should be imported.</param>
#    <param name="firstColumn">Column of the first cell where DataView should be imported.</param>
#    <param name="bPreserveTypes">Indicates whether to preserve column types.</param>
#    <returns>Number of imported rows.</returns>
#        """
#        pass
#


#    @dispatch
#
#    @abc.abstractmethod
#    def InsertDataView(self ,dataView:'DataView',isFieldNameShown:bool,firstRow:int,firstColumn:int,maxRows:int,maxColumns:int)->int:
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
#    <param name="dataView">DataView with desired data.</param>
#    <param name="isFieldNameShown">TRUE if column names must also be imported.</param>
#    <param name="firstRow">Row of the first cell where DataView should be imported.</param>
#    <param name="firstColumn">Column of the first cell where DataView should be imported.</param>
#    <param name="maxRows">Maximum number of rows to import.</param>
#    <param name="maxColumns">Maximum number of columns to import.</param>
#    <returns>Number of imported rows.</returns>
#        """
#        pass
#


#    @dispatch
#
#    @abc.abstractmethod
#    def InsertDataView(self ,dataView:'DataView',isFieldNameShown:bool,firstRow:int,firstColumn:int,maxRows:int,maxColumns:int,bPreserveTypes:bool)->int:
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
#    <param name="dataView">DataView with desired data.</param>
#    <param name="isFieldNameShown">TRUE if column names must also be imported.</param>
#    <param name="firstRow">Row of the first cell where DataView should be imported.</param>
#    <param name="firstColumn">Column of the first cell where DataView should be imported.</param>
#    <param name="maxRows">Maximum number of rows to import.</param>
#    <param name="maxColumns">Maximum number of columns to import.</param>
#    <param name="bPreserveTypes">Indicates whether to preserve column types.</param>
#    <returns>Number of imported rows</returns>
#        """
#        pass
#


    @abc.abstractmethod
    def RemovePanes(self):
        """
        Removes panes from a worksheet.

        """
        pass


