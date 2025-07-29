from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IXLSRange (  IExcelApplication) :
    """
    Represents a cell, row, column, selection of cells containing one or more contiguous blocks of cells, or a 3-D range.

    """
    #@property

    #@abc.abstractmethod
    #def Value2(self)->'SpireObject':
    #    """
    #<summary>
    #     Returns or sets the cell value. Read/write Variant.
    #         The only difference between this property and the Value property is
    #         that the Value2 property doesn't use the Currency and Date data types.
    #    <example>The following code illustrates how to access Value2 property of the Range:
    #    <code>
    #    //Create worksheet
    #    Workbook workbook = new Workbook();
    #    Worksheet worksheet = workbook.Worksheets[0];
    #    //Assigning Value2 property of the Range
    #    worksheet["A1"].Value2 = DateTime.Now;
    #    worksheet["A3"].Value2 = false;
    #    //Checking Range types
    #    Console.WriteLine(worksheet["A1"].HasDateTime);
    #    Console.WriteLine(worksheet["A3"].HasBoolean);
    #    </code>
    #    </example>
    #</summary>
    #    """
    #    pass


    #@Value2.setter
    #@abc.abstractmethod
    #def Value2(self, value:'SpireObject'):
    #    """

    #    """
    #    pass


    @property

    @abc.abstractmethod
    def VerticalAlignment(self)->'VerticalAlignType':
        """
        Returns or sets the vertical alignment of the specified object. Read/write VerticalAlignType.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["A1"].Text = "Test"
            #Set alignment
            worksheet["A1"].VerticalAlignment = VerticalAlignType.Top
            #Save to file
            workbook.SaveToFile("VerticalAlignment.xlsx")

        """
        pass


    @VerticalAlignment.setter
    @abc.abstractmethod
    def VerticalAlignment(self, value:'VerticalAlignType'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Worksheet(self)->'IWorksheet':
        """
        Returns a Worksheet object that represents the worksheet containing the specified range. Read-only.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def get_Item(self ,row:int,column:int)->'IXLSRange':
        """
        Gets / sets cell by row and column index. Row and column indexes are one-based.

        """
        pass



    @abc.abstractmethod
    def set_Item(self ,row:int,column:int,value:'IXLSRange'):
        """

        """
        pass


    @dispatch

    @abc.abstractmethod
    def get_Item(self ,row:int,column:int,lastRow:int,lastColumn:int)->'IXLSRange':
        """
        Get cell range. Row and column indexes are one-based. Read-only.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def get_Item(self ,name:str)->'IXLSRange':
        """
        Get cell range. Read-only.

        """
        pass


    @dispatch

    @abc.abstractmethod
    def get_Item(self ,name:str,IsR1C1Notation:bool)->'IXLSRange':
        """
        Gets cell range. Read-only.

        """
        pass


    @property

    @abc.abstractmethod
    def ConditionalFormats(self)->'ConditionalFormats':
        """
        Collection of conditional formats.

        """
        pass


    @property

    @abc.abstractmethod
    def DataValidation(self)->'Validation':
        """
        Data validation for the range.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Data validation for number
            validation = worksheet.Range["A3"].DataValidation
            validation.AllowType = CellDataType.Integer
            #Value between 0 to 10
            validation.CompareOperator = ValidationComparisonOperator.Between
            validation.Formula1 = "0"
            validation.Formula2 = "10"
            #Save to file
            workbook.SaveToFile("DataValidation.xlsx")

        """
        pass


    @property

    @abc.abstractmethod
    def FormulaStringValue(self)->str:
        """
        Gets / sets string value evaluated by formula.

        """
        pass


    @FormulaStringValue.setter
    @abc.abstractmethod
    def FormulaStringValue(self, value:str):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def FormulaNumberValue(self)->float:
        """
        Gets / sets number value evaluated by formula.

        """
        pass


    @FormulaNumberValue.setter
    @abc.abstractmethod
    def FormulaNumberValue(self, value:float):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def HasFormulaBoolValue(self)->bool:
        """
        Indicates if current range has formula bool value. Read only.

        """
        pass


    @property
    @abc.abstractmethod
    def HasFormulaErrorValue(self)->bool:
        """
        Indicates if current range has formula error value. Read only.

        """
        pass


    @property

    @abc.abstractmethod
    def Comment(self)->'ICommentShape':
        """
        Comment assigned to the range. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Adding comments to a cell
            worksheet.Range["A1"].AddComment().Text = "Comments"
            #Add Rich Text Comments
            range = worksheet.Range["A6"]
            range.AddComment().RichText.Text = "RichText"
            rtf = range.Comment.RichText
            #Formatting first 4 characters
            redFont = workbook.CreateFont()
            redFont.IsBold = true
            redFont.Color = Color.Red
            rtf.SetFont(0, 3, redFont)
            #Save to file
            workbook.SaveToFile("DataValidation.xlsx")

        """
        pass


    @property

    @abc.abstractmethod
    def RichText(self)->'IRichTextString':
        """
        String with rich text formatting. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Create style
            style = workbook.Styles.Add("CustomStyle")
            #Set rich text
            richText = worksheet["C2"].RichText
            richText.Text = "Sample text"
            #Set rich text font
            font = style.Font
            font.IsBold = true
            richText.SetFont(0, 5, font)
            #Save to file
            workbook.SaveToFile("RichText.xlsx")

        """
        pass


    @property

    @abc.abstractmethod
    def HtmlString(self)->str:
        """
        Gets and sets the html string which contains data and some formattings in this cell.

        """
        pass


    @HtmlString.setter
    @abc.abstractmethod
    def HtmlString(self, value:str):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def HasMerged(self)->bool:
        """
        Indicates whether this range is part of merged range. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["A1"].Text = "Sample text in cell"
            #Set merge
            worksheet["A1:B1"].Merge()
            #Check merge
            Console.Write(worksheet["A1:B1"].HasMerged)

        """
        pass


    @property

    @abc.abstractmethod
    def MergeArea(self)->'IXLSRange':
        """
        Returns a Range object that represents the merged range containing the specified cell. If the specified cell is not in a merged range, this property returns NULL. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["C2"].Text = "Sample text in cell"
            #Set merge
            worksheet["C2:D3"].Merge()
            #Check merge area
            Console.Write(worksheet["C2"].MergeArea.AddressLocal)

        """
        pass


    @property
    @abc.abstractmethod
    def IsWrapText(self)->bool:
        """
        True if Microsoft Excel wraps the text in the object. Read/write Boolean.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["A1"].Text = "This cell contains sample text"
            #Set wrap text
            worksheet["A1"].IsWrapText = true
            #Save to file
            workbook.SaveToFile("IsWrapText.xlsx")

        """
        pass


    @IsWrapText.setter
    @abc.abstractmethod
    def IsWrapText(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def HasExternalFormula(self)->bool:
        """
        Indicates is current range has external formula. Read-only.

        """
        pass


    @property

    @abc.abstractmethod
    def IgnoreErrorOptions(self)->'IgnoreErrorType':
        """
        Represents ignore error options.

        """
        pass


    @IgnoreErrorOptions.setter
    @abc.abstractmethod
    def IgnoreErrorOptions(self, value:'IgnoreErrorType'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def IsStringsPreserved(self)->bool:
        """
        Indicates whether all values in the range are preserved as strings.

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
    def BuiltInStyle(self)->BuiltInStyles:
        """
        Gets/sets built in style.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["C2"].Text = "Sample"
            #Set built in style
            worksheet["C2"].BuiltInStyle = BuiltInStyles.Accent3
            #Save to file
            workbook.SaveToFile("BuiltInStyle.xlsx")

        """
        pass



    @BuiltInStyle.setter
    @abc.abstractmethod
    def BuiltInStyle(self, value:BuiltInStyles):
        """

        """
        pass



    @property

    @abc.abstractmethod
    def Hyperlinks(self)->'IHyperLinks':
        """
        Returns hyperlinks for this range.

        """
        pass



    @abc.abstractmethod
    def Activate(self ,scroll:bool)->'IXLSRange':
        """
        Activates a single cell, scroll to it and activates the corresponding sheet. To select a range of cells, use the Select method.

        Args:
            scroll: True to scroll to the cell

        Returns:
            Returns the active cell.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Activates 'F1' cell.
            worksheet.Range["F1"].Activate(true)
            #Save to file
            workbook.SaveToFile("Activate.xlsx")

        """
        pass


    @dispatch
    @abc.abstractmethod
    def Merge(self):
        """
        Creates a merged cell from the specified Range object.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["A1"].Text = "Merged cell"
            #Merge cells
            worksheet["A1:B1"].Merge()
            #Save to file
            workbook.SaveToFile("Merge.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def Merge(self ,clearCells:bool):
        """
        Creates a merged cell from the specified Range object.

        Args:
            clearCells: Indicates whether to clear unnecessary cells.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["A1"].Text = "Merged cell"
            worksheet["B1"].Text = "sample"
            #Merge cells
            worksheet["A1:B1"].Merge(true)
            #Save to file
            workbook.SaveToFile("Merge.xlsx")

        """
        pass


    @abc.abstractmethod
    def UnMerge(self):
        """
        Separates a merged area into individual cells.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["A1"].Text = "Merged cell"
            #Merge cells
            worksheet["A1:B1"].Merge(true)
            #Unmerge cells
            worksheet["A1:B1"].UnMerge()
            #Save to file
            workbook.SaveToFile("UnMerge.xlsx")

        """
        pass


    @abc.abstractmethod
    def FreezePanes(self):
        """
        Freezes pane at the current range.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Applying Freeze Pane to the sheet by specifying a cell
            worksheet.Range["B2"].FreezePanes()
            #Save to file
            workbook.SaveToFile("FreezePanes.xlsx")

        """
        pass


    @abc.abstractmethod
    def ClearContents(self):
        """
        Clear the contents of the Range.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Clears the Range C2
            worksheet.Range["C2"].ClearContents()
            #Save to file
            workbook.SaveToFile("ClearContents.xlsx")

        """
        pass



    @abc.abstractmethod
    def Clear(self ,option:'ExcelClearOptions'):
        """
        Clears the cell content, formats, comments based on clear option.

        Args:
            option: Represents the clear options.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Clears the Range C2 with its clear options
            worksheet.Range["C2"].Clear(ExcelClearOptions.ClearAll)
            #Save to file
            workbook.SaveToFile("ClearContents.xlsx")

        """
        pass



    @abc.abstractmethod
    def Intersect(self ,range:'IXLSRange')->'IXLSRange':
        """
        Returns intersection of this range with the specified one.

        Args:
            range: The Range with which to intersect.

        Returns:
            Range intersection; if there is no intersection, NULL is returned.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get intersect range
            range = worksheet.Range["A16:C16"]
            commonRange = worksheet.Range["B16:D16"].Intersect(range)
            #Save to file
            workbook.SaveToFile("Intersect.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def Merge(self ,range:'IXLSRange')->'IXLSRange':
        """
        Returns merge of this range with the specified one.

        Args:
            range: The Range to merge with.

        Returns:
            Merged ranges or NULL if wasn't able to merge ranges.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Merge range
            worksheet["A2:B2"].Merge()
            #Get mergable range
            mergableRange = worksheet["A2"].MergeArea.Merge(worksheet["C2"])
            #Check mergable Area
            Console.Write(mergableRange.RangeAddressLocal)
            #Save to file
            workbook.SaveToFile("Intersect.xlsx")

        """
        pass


    @abc.abstractmethod
    def AutoFitRows(self):
        """
        Autofits all rows in the range.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Auto-fit rows
            worksheet.Range["A2"].Text = "Fit the content to row"
            worksheet.Range["A2"].IsWrapText = true
            worksheet.Range["A2"].AutoFitRows()
            #Save to file
            workbook.SaveToFile("AutoFitRows.xlsx")

        """
        pass


    @abc.abstractmethod
    def AutoFitColumns(self):
        """
        Autofits all columns in the range.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Auto-fit columns
            worksheet.Range["B4"].Text = "Fit the content to column"
            worksheet.Range["B4"].AutoFitColumns()
            #Save to file
            workbook.SaveToFile("AutoFitRows.xlsx")

        """
        pass



    @abc.abstractmethod
    def AddComment(self)->'ICommentShape':
        """
        Adds comment to the range.

        Returns:
            Range's comment.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Adding comments to a cell
            comment = worksheet.Range["A1"].AddComment()
            comment.Text= "Comments"
            #Save to file
            workbook.SaveToFile("AddComment.xlsx")

        """
        pass


    @dispatch
    @abc.abstractmethod
    def BorderAround(self):
        """
        Sets around border for current range.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["C2"].Text = "Sample"
            worksheet["D2"].Text = "text"
            worksheet["C3"].Text = "in"
            worksheet["D3"].Text = "cell"
            #Set border
            worksheet["C2:D3"].BorderAround()
            #Save to file
            workbook.SaveToFile("BorderAround.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def BorderAround(self ,borderLine:LineStyleType):
        """
        Sets around border for current range.

        Args:
            borderLine: Represents border line.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["C2"].Text = "Sample"
            worksheet["D2"].Text = "text"
            worksheet["C3"].Text = "in"
            worksheet["D3"].Text = "cell"
            #Set border
            worksheet["C2:D3"].BorderAround(LineStyleType.Thick)
            #Save to file
            workbook.SaveToFile("BorderAround.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def BorderAround(self ,borderLine:LineStyleType,borderColor:Color):
        """
        Sets around border for current range.

        Args:
            borderLine: Represents border line.
            borderColor: Represents border color.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["C2"].Text = "Sample"
            worksheet["D2"].Text = "text"
            worksheet["C3"].Text = "in"
            worksheet["D3"].Text = "cell"
            #Set border
            worksheet["C2:D3"].BorderAround(LineStyleType.Thick , Color.Red)
            #Save to file
            workbook.SaveToFile("BorderAround.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def BorderAround(self ,borderLine:LineStyleType,borderColor:ExcelColors):
        """
        Sets around border for current range.

        Args:
            borderLine: Represents border line.
            borderColor: Represents border color as ExcelColors.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["C2"].Text = "Sample"
            worksheet["D2"].Text = "text"
            worksheet["C3"].Text = "in"
            worksheet["D3"].Text = "cell"
            #Set border
            worksheet["C2:D3"].BorderAround(LineStyleType.Thick , ExcelColors.Red)
            #Save to file
            workbook.SaveToFile("BorderAround.xlsx")

        """
        pass


    @dispatch
    @abc.abstractmethod
    def BorderInside(self):
        """
        Sets inside border for current range.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["C2"].Text = "Sample"
            worksheet["D2"].Text = "text"
            worksheet["C3"].Text = "in"
            worksheet["D3"].Text = "cell"
            #Set border
            worksheet["C2:D3"].BorderInside()
            #Save to file
            workbook.SaveToFile("BorderInside.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def BorderInside(self ,borderLine:LineStyleType):
        """
        Sets inside border for current range.

        Args:
            borderLine: Represents border line.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["C2"].Text = "Sample"
            worksheet["D2"].Text = "text"
            worksheet["C3"].Text = "in"
            worksheet["D3"].Text = "cell"
            #Set border
            worksheet["C2:D3"].BorderInside(LineStyleType.Thick)
            #Save to file
            workbook.SaveToFile("BorderInside.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def BorderInside(self ,borderLine:LineStyleType,borderColor:Color):
        """
        Sets inside border for current range.

        Args:
            borderLine: Represents border line.
            borderColor: Represents border color.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["C2"].Text = "Sample"
            worksheet["D2"].Text = "text"
            worksheet["C3"].Text = "in"
            worksheet["D3"].Text = "cell"
            #Set border
            worksheet["C2:D3"].BorderInside(LineStyleType.Thick , Color.Red)
            #Save to file
            workbook.SaveToFile("BorderInside.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def BorderInside(self ,borderLine:LineStyleType,borderColor:ExcelColors):
        """
        Sets inside border for current range.

        Args:
            borderLine: Represents border line.
            borderColor: Represents border color as ExcelColors.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["C2"].Text = "Sample"
            worksheet["D2"].Text = "text"
            worksheet["C3"].Text = "in"
            worksheet["D3"].Text = "cell"
            #Set border
            worksheet["C2:D3"].BorderInside(LineStyleType.Thick , ExcelColors.Red)
            #Save to file
            workbook.SaveToFile("BorderInside.xlsx")

        """
        pass


    @abc.abstractmethod
    def BorderNone(self):
        """
        Sets none border for current range.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Remove borders
            worksheet["C2"].BorderNone()
            #Save to file
            workbook.SaveToFile("BorderNone.xlsx")

        """
        pass



    @abc.abstractmethod
    def CollapseGroup(self ,groupBy:'GroupByType'):
        """
        Collapses current group.

        Args:
            groupBy: 
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Collapse group
            worksheet.Range["A5:A15"].CollapseGroup(GroupByType.ByRows)
            #Save to file
            workbook.SaveToFile("CollapseGroup.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def ExpandGroup(self ,groupBy:GroupByType):
        """
        Expands current group.

        Args:
            groupBy: 
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Expand group with flag set to expand parent
            worksheet.Range["A5:A15"].ExpandGroup(GroupByType.ByRows)
            #Save to file
            workbook.SaveToFile("ExpandGroup.xlsx")

        """
        pass


    @dispatch

    @abc.abstractmethod
    def ExpandGroup(self ,groupBy:GroupByType,flags:ExpandCollapseFlags):
        """
        Expands current group.

        Args:
            groupBy: 
            flags: Additional option flags.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Expand group with flag set to expand parent
            worksheet.Range["A5:A15"].ExpandGroup(GroupByType.ByRows, ExpandCollapseFlags.ExpandParent)
            #Save to file
            workbook.SaveToFile("ExpandGroup.xlsx")

        """
        pass


#
#    @abc.abstractmethod
#    def ExportDataTable(self ,options:'ExportTableOptions')->'DataTable':
#        """
#
#        """
#        pass
#


    @property

    @abc.abstractmethod
    def RangeAddress(self)->str:
        """
        Returns the range reference in the language of the macro. Read-only String.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get RangeAddress
            address = worksheet.Range[3, 4].RangeAddress

        """
        pass


    @property

    @abc.abstractmethod
    def RangeAddressLocal(self)->str:
        """
        Returns the range reference for the specified range in the language of the user. Read-only String.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get RangeAddressLocal
            address = worksheet.Range[3, 4].RangeAddressLocal

        """
        pass


    @property

    @abc.abstractmethod
    def RangeGlobalAddress(self)->str:
        """
        Returns range Address in format "'Sheet1'!$A$1".
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get RangeAddress
            address = worksheet.Range[3, 4].RangeGlobalAddress

        """
        pass


    @property

    @abc.abstractmethod
    def RangeR1C1Address(self)->str:
        """
        Returns the range reference using R1C1 notation. Read-only String.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get RangeR1C1Address
            address = worksheet.Range[3, 4].RangeR1C1Address

        """
        pass


    @property

    @abc.abstractmethod
    def RangeR1C1AddressLocal(self)->str:
        """
        Returns the range reference using R1C1 notation. Read-only String.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get RangeR1C1AddressLocal
            address = worksheet.Range[3, 4].RangeR1C1Address

        """
        pass


    @property
    @abc.abstractmethod
    def BooleanValue(self)->bool:
        """
        Gets / sets boolean value that is contained by this range.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set and get BooleanValue
            worksheet.Range[2, 4].BooleanValue = true
            boolean = worksheet.Range[2, 4].BooleanValue

        """
        pass


    @BooleanValue.setter
    @abc.abstractmethod
    def BooleanValue(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Borders(self)->'IBorders':
        """
        Returns a  Borders collection that represents the borders of a style or a range of cells (including a range defined as part of a conditional format).
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["C2"].Text = "Sample"
            #Set borders
            borders = worksheet["C2"].Borders
            #Set line style
            borders[BordersLineType.EdgeTop].LineStyle = LineStyleType.Thin
            borders[BordersLineType.EdgeBottom].LineStyle = LineStyleType.Thin
            #Set border color
            borders[BordersLineType.EdgeTop].Color = Color.Red
            borders[BordersLineType.EdgeBottom].Color = Color.Red
            #Save to file
            workbook.SaveToFile("CellFormats.xlsx")

        """
        pass


#    @property
#
#    @abc.abstractmethod
#    def Cells(self)->'ListCellRanges':
#        """
#    <summary>
#        Returns a Range object that represents the cells in the specified range.
#            Read-only.
#    </summary>
#        """
#        pass
#


#    @property
#
#    @abc.abstractmethod
#    def CellList(self)->'List1':
#        """
#    <summary>
#         Returns a Range object that represents the cells in the specified range.
#             Read-only.
#        <example>The following code illustrates how to access CellList property of the Range:
#        <code>
#        //Create worksheet
#        Workbook workbook = new Workbook();
#        Worksheet worksheet = workbook.Worksheets[0];
#        //Set text. The content contained by ![CDATA] will be expressed as plain text
#        ListCellRange cells = worksheet["A1:E8"].CellList;
#        //Do some manipulations
#        foreach (CellRange Range in cells)
#            Range.Text = Range.RangeAddressLocal;
#        //Save to file
#        workbook.SaveToFile("CellList.xlsx");
#        </code>
#        </example>
#    </summary>
#        """
#        pass
#


    @property
    @abc.abstractmethod
    def Column(self)->int:
        """
        Returns the number of the first column in the first area in the specified range. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get specific column
            firstColumn = worksheet["E1:R3"].Column

        """
        pass


    @property
    @abc.abstractmethod
    def ColumnGroupLevel(self)->int:
        """
        Column group level. Read-only. -1 - Not all columns in the range have same group level. 0 - No grouping, 1 - 7 - Group level.

        """
        pass


    @property
    @abc.abstractmethod
    def ColumnWidth(self)->float:
        """
        Returns or sets the width of all columns in the specified range. Read/write Double.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set the ColumnWidth
            worksheet["A1"].Text = "This cell contains sample text"
            worksheet["A1"].ColumnWidth = 25
            #Save to file
            workbook.SaveToFile("ColumnWidth.xlsx")

        """
        pass


    @ColumnWidth.setter
    @abc.abstractmethod
    def ColumnWidth(self, value:float):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def Count(self)->int:
        """
        Returns the number of objects in the collection. Read-only.

        """
        pass


    @property

    @abc.abstractmethod
    def DateTimeValue(self)->'DateTime':
        """
        Gets / sets DateTime contained by this cell. Read-write DateTime.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set and get the DateTimeValue of specified range
            worksheet.Range[2, 4].DateTimeValue = DateTime.Now
            dateTime = worksheet.Range[2, 4].DateTimeValue
            #Save to file
            workbook.SaveToFile("DateTimeValue.xlsx")

        """
        pass


    @DateTimeValue.setter
    @abc.abstractmethod
    def DateTimeValue(self, value:'DateTime'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def NumberText(self)->str:
        """
        Returns cell value after number format application. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Gets cell value with its number format
            CellRange range= worksheet.Range[3, 1]
            range.Value = "1/1/2015"
            range.NumberFormat = "dd-MMM-yyyy"
            numberText = range.NumberText
            #Save to file
            workbook.SaveToFile("NumberText.xlsx")

        """
        pass


    @property

    @abc.abstractmethod
    def EndCell(self)->'IXLSRange':
        """
        Returns a Range object that represents the cell at the end of the region that contains the source range.

        """
        pass


    @property

    @abc.abstractmethod
    def EntireColumn(self)->'IXLSRange':
        """
        Returns a Range object that represents the entire column (or columns) that contains the specified range. Read-only.

        """
        pass


    @property

    @abc.abstractmethod
    def EntireRow(self)->'IXLSRange':
        """
        Returns a Range object that represents the entire row (or rows) that contains the specified range. Read-only.

        """
        pass


    @property

    @abc.abstractmethod
    def ErrorValue(self)->str:
        """
        Gets / sets error value that is contained by this range.

        """
        pass


    @ErrorValue.setter
    @abc.abstractmethod
    def ErrorValue(self, value:str):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Formula(self)->str:
        """
        Returns or sets the object's formula in A1-style notation and in the language of the macro. Read/write Variant.

        """
        pass


    @Formula.setter
    @abc.abstractmethod
    def Formula(self, value:str):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def FormulaArray(self)->str:
        """
        Represents array-entered formula. Visit http://www.cpearson.com/excel/array.htm for more information.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Assign array formula
            worksheet.Range["A1:D1"].FormulaArray = "{1,2,3,4}"
            #Adding a named range for the range A1 to D1
            worksheet.Names.Add("ArrayRange", worksheet.Range["A1:D1"])
            #Assign formula array with named range
            worksheet.Range["A2:D2"].FormulaArray = "ArrayRange+100"
            #Save to file
            workbook.SaveToFile("FormulaArray.xlsx")

        """
        pass


    @FormulaArray.setter
    @abc.abstractmethod
    def FormulaArray(self, value:str):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def FormulaArrayR1C1(self)->str:
        """
        Returns or sets the formula array for the range, using R1C1-style notation.

        """
        pass


    @FormulaArrayR1C1.setter
    @abc.abstractmethod
    def FormulaArrayR1C1(self, value:str):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def IsFormulaHidden(self)->bool:
        """
        True if the formula will be hidden when the worksheet is protected. False if at least part of formula in the range is not hidden.

        """
        pass


    @IsFormulaHidden.setter
    @abc.abstractmethod
    def IsFormulaHidden(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def FormulaDateTime(self)->'DateTime':
        """
        Get / set formula DateTime value contained by this cell. DateTime.MinValue if not all cells of the range have same DateTime value.

        """
        pass


    @FormulaDateTime.setter
    @abc.abstractmethod
    def FormulaDateTime(self, value:'DateTime'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def FormulaR1C1(self)->str:
        """
        Returns or sets the formula for the range, using R1C1-style notation.

        """
        pass


    @FormulaR1C1.setter
    @abc.abstractmethod
    def FormulaR1C1(self, value:str):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def FormulaBoolValue(self)->bool:
        """
        Returns the calculated value of the formula as a boolean.

        """
        pass


    @FormulaBoolValue.setter
    @abc.abstractmethod
    def FormulaBoolValue(self, value:bool):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def FormulaErrorValue(self)->str:
        """
        Returns the calculated value of the formula as a string.

        """
        pass


    @FormulaErrorValue.setter
    @abc.abstractmethod
    def FormulaErrorValue(self, value:str):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def HasDataValidation(self)->bool:
        """
        Indicates whether specified range object has data validation. If Range is not single cell, then returns true only if all cells have data validation. Read-only.

        """
        pass


    @property
    @abc.abstractmethod
    def HasBoolean(self)->bool:
        """
        Indicates whether range contains bool value. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Assigning Value2 property of the Range
            worksheet["A3"].Value2 = false
            #Checking Range types
            isboolean = worksheet["A3"].HasBoolean
            #Save to file
            workbook.SaveToFile("HasBoolean.xlsx")

        """
        pass


    @property
    @abc.abstractmethod
    def HasDateTime(self)->bool:
        """
        Indicates whether range contains DateTime value. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Assigning Value2 property of the Range
            worksheet["A1"].Value2 = DateTime.Now
            #Checking Range types
            isDateTime =  worksheet["A1"].HasDateTime
            #Save to file
            workbook.SaveToFile("HasDateTime.xlsx")

        """
        pass


    @property
    @abc.abstractmethod
    def HasFormula(self)->bool:
        """
        True if all cells in the range contain formulas; False if at least one of the cells in the range doesn't contain a formula. Read-only Boolean.

        """
        pass


    @property
    @abc.abstractmethod
    def HasFormulaArray(self)->bool:
        """
        Indicates whether range contains array-entered formula. Read-only.

        """
        pass


    @property
    @abc.abstractmethod
    def HasFormulaDateTime(self)->bool:
        """
        Indicates if current range has formula value formatted as DateTime. Read-only.

        """
        pass


    @property
    @abc.abstractmethod
    def HasFormulaNumberValue(self)->bool:
        """
        Indicates if the current range has formula number value. Read-only.

        """
        pass


    @property
    @abc.abstractmethod
    def HasFormulaStringValue(self)->bool:
        """
        Indicates if the current range has formula string value. Read-only.

        """
        pass


    @property
    @abc.abstractmethod
    def HasNumber(self)->bool:
        """
        Indicates whether the range contains number. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Assigning Value2 property of the Range
            worksheet["A2"].Value2 = 45
            #Checking Range types
            isNumber =  worksheet["A2"].HasNumber
            #Save to file
            workbook.SaveToFile("HasNumber.xlsx")

        """
        pass


    @property
    @abc.abstractmethod
    def HasRichText(self)->bool:
        """
        Indicates whether cell contains formatted rich text string.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Create style
            style = workbook.Styles.Add("CustomStyle")
            #Set rich text
            richText = worksheet["C2"].RichText
            richText.Text = "Sample"
            font = style.Font
            font.Color = Color.Red
            richText.SetFont(0, 5, font)
            #Check HasRichText
            Console.Write(worksheet["C2"].HasRichText)
            #Save to file
            workbook.SaveToFile("HasRichText.xlsx")

        """
        pass


    @property
    @abc.abstractmethod
    def HasString(self)->bool:
        """
        Indicates whether the range contains String. Read-only.

        """
        pass


    @property
    @abc.abstractmethod
    def HasStyle(self)->bool:
        """
        Indicates whether range has default style. False means default style. Read-only.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Add style
            style = workbook.Styles.Add("CustomStyle")
            #Set color and style
            style.Color = Color.Red
            worksheet["C2"].Style = style
            #Check HasStyle
            Console.Write(worksheet["C2"].HasStyle)
            #Save to file
            workbook.SaveToFile("HasStyle.xlsx")

        """
        pass


    @property

    @abc.abstractmethod
    def HorizontalAlignment(self)->'HorizontalAlignType':
        """
        Returns or sets the horizontal alignment for the specified object. Read/write HorizontalAlignType.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["A1"].Text = "Test"
            #Set alignment
            worksheet["A1"].HorizontalAlignment = HorizontalAlignType.Right
            #Save to file
            workbook.SaveToFile("HorizontalAlignment.xlsx")

        """
        pass


    @HorizontalAlignment.setter
    @abc.abstractmethod
    def HorizontalAlignment(self, value:'HorizontalAlignType'):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def IndentLevel(self)->int:
        """
        Returns or sets the indent level for the cell or range. Can be an integer from 0 to 15. Read/write Integer.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["C2"].Text = "Sample"
            #Set indent level
            worksheet["C2"].IndentLevel = 2
            #Save to file
            workbook.SaveToFile("IndentLevel.xlsx")

        """
        pass


    @IndentLevel.setter
    @abc.abstractmethod
    def IndentLevel(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def IsBlank(self)->bool:
        """
        Indicates whether the range is blank. Read-only.

        """
        pass


    @property
    @abc.abstractmethod
    def HasError(self)->bool:
        """
        Indicates whether range contains error value.

        """
        pass


    @property
    @abc.abstractmethod
    def IsGroupedByColumn(self)->bool:
        """
        Indicates whether this range is grouped by column. Read-only.

        """
        pass


    @property
    @abc.abstractmethod
    def IsGroupedByRow(self)->bool:
        """
        Indicates whether this range is grouped by row. Read-only.

        """
        pass


    @property
    @abc.abstractmethod
    def IsInitialized(self)->bool:
        """
        Indicates whether cell is initialized. Read-only.

        """
        pass


    @property
    @abc.abstractmethod
    def LastColumn(self)->int:
        """
        Returns last column of the range. Read-only.

        """
        pass


    @LastColumn.setter
    @abc.abstractmethod
    def LastColumn(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def LastRow(self)->int:
        """
        Returns last row of the range. Read-only.

        """
        pass


    @LastRow.setter
    @abc.abstractmethod
    def LastRow(self, value:int):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def NumberValue(self)->float:
        """
        Gets / sets double value of the range.

        """
        pass


    @NumberValue.setter
    @abc.abstractmethod
    def NumberValue(self, value:float):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def NumberFormat(self)->str:
        """
        Format of current cell. Analog of Style.NumberFormat property.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set data
            worksheet["C2"].Value = "3100.23"
            #Set number format
            worksheet["C2"].NumberFormat = "#,#1.#"
            #Save to file
            workbook.SaveToFile("NumberFormat.xlsx")

        """
        pass


    @NumberFormat.setter
    @abc.abstractmethod
    def NumberFormat(self, value:str):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def Row(self)->int:
        """
        Returns the number of the first row of the first area in the range. Read-only Long.

        """
        pass


    @property
    @abc.abstractmethod
    def RowGroupLevel(self)->int:
        """
        Row group level. Read-only. -1 - Not all rows in the range have same group level. 0 - No grouping, 1 - 7 - Group level.

        """
        pass


    @property
    @abc.abstractmethod
    def RowHeight(self)->float:
        """
        Returns the height of all the rows in the range specified, measured in points. Returns Double.MinValue if the rows in the specified range aren't all the same height. Read / write Double.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["A1"].Text = "Test"
            #Set row height
            worksheet["A1"].RowHeight = 30
            #Save to file
            workbook.SaveToFile("RowHeight.xlsx")

        """
        pass


    @RowHeight.setter
    @abc.abstractmethod
    def RowHeight(self, value:float):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Rows(self)->'ListXlsRanges':
        """
        For a Range object, returns an array of Range objects that represent the rows in the specified range.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set rows
            IXLSRange[] rows = worksheet["A1:E8"].Rows
            #Do some manipulations
            foreach (IXLSRange row in rows)
            row.Text = row.RangeAddressLocal
            #Save to file
            workbook.SaveToFile("Rows.xlsx")

        """
        pass



    @property

    @abc.abstractmethod
    def Columns(self)->'ListXlsRanges':
        """
        For a Range object, returns an array of Range objects that represent the columns in the specified range.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set columns
            IXLSRange[] columns = worksheet["A1:E8"].Columns
            #Do some manipulations
            foreach (IXLSRange column in columns)
            column.Text = column.RangeAddressLocal
            #Save to file
            workbook.SaveToFile("Columns.xlsx")

        """
        pass



    @property

    @abc.abstractmethod
    def Style(self)->'IStyle':
        """
        Returns a Style object that represents the style of the specified range. Read/write IStyle.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set text
            worksheet["C2"].Text = "Sample"
            #Add and set style
            style = workbook.Styles.Add("BorderStyle")
            style.Color = Color.Red
            worksheet["C2"].Style = style
            #Save to file
            workbook.SaveToFile("Style.xlsx")

        """
        pass


    @Style.setter
    @abc.abstractmethod
    def Style(self, value:'IStyle'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def CellStyleName(self)->str:
        """
        Returns name of the Style object that represents the style of the specified range. Read/write String.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Add and set style
            style = workbook.Styles.Add("CustomStyle")
            worksheet["C2"].Style = style
            #Check Style name
            Console.Write(worksheet["C2"].CellStyleName)

        """
        pass


    @CellStyleName.setter
    @abc.abstractmethod
    def CellStyleName(self, value:str):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Text(self)->str:
        """
        Gets / sets string value of the range.

        """
        pass


    @Text.setter
    @abc.abstractmethod
    def Text(self, value:str):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def TimeSpanValue(self)->'TimeSpan':
        """
        Gets / sets time value of the range.

        """
        pass


    @TimeSpanValue.setter
    @abc.abstractmethod
    def TimeSpanValue(self, value:'TimeSpan'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Value(self)->str:
        """
        Returns or sets the value of the specified range. Read/write Variant.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set value of the range
            CellRange range= worksheet.Range[3, 1]
            range.Value = "1/1/2015"
            #Save to file
            workbook.SaveToFile("Value.xlsx")

        """
        pass


    @Value.setter
    @abc.abstractmethod
    def Value(self, value:str):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def EnvalutedValue(self)->str:
        """
        Returns the calculated value of a formula using the most current inputs.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Returns the calculated value of a formula using the most current inputs
            calculatedValue = worksheet["C1"].EnvalutedValue
            print(calculatedValue)

        """
        pass


