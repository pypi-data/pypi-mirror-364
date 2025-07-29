from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from spire.xls.collection.XlsBordersCollection import *
from spire.xls.collection.XlsHyperLinksCollection import *
from ctypes import *
import abc
from spire.xls.Validation import Validation

class XlsRange (  XlsObject, ICombinedRange,IEnumerable[IXLSRange]) :
    """

    """

    def GetNamedRange(self)->'INamedRange':
        """
        Get the named range object of current Range.

        """
        from spire.xls.XlsName import XlsName
        GetDllLibXls().XlsRange_GetNamedRange.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_GetNamedRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_GetNamedRange,self.Ptr)
        ret = None if intPtr==None else XlsName(intPtr)
        return ret

    @dispatch

    def InsertOrUpdateCellImage(self ,stream:Stream,scale:bool):
        """
        Adds CellImage from the specified file stream. this method only support WPS

        Args:
            stream: Represents image stream to set.
            scale: scale if true scale for cell else clip the image.

        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibXls().XlsRange_InsertOrUpdateCellImage.argtypes=[c_void_p ,c_void_p,c_bool]
        CallCFunction(GetDllLibXls().XlsRange_InsertOrUpdateCellImage,self.Ptr, intPtrstream,scale)

    @dispatch

    def InsertOrUpdateCellImage(self ,fileName:str,scale:bool):
        """
        Adds CellImage from the specified file. this method only support WPS

        Args:
            fileName: Represents image path to set.
            scale: scale if true scale for cell else clip the image.

        """
        
        GetDllLibXls().XlsRange_InsertOrUpdateCellImageFS.argtypes=[c_void_p ,c_wchar_p,c_bool]
        CallCFunction(GetDllLibXls().XlsRange_InsertOrUpdateCellImageFS,self.Ptr, fileName,scale)

    def RemoveCellImage(self):
        """
        Remove CellImage.

        """
        GetDllLibXls().XlsRange_RemoveCellImage.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_RemoveCellImage,self.Ptr)

    @dispatch

    def Merge(self ,range:IXLSRange)->IXLSRange:
        """
        Creates a merged cell from the specified Range object.

        Args:
            range: The Range to merge with.

        Returns:
            Merged ranges or null if wasn't able to merge ranges.

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().XlsRange_Merge.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsRange_Merge.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_Merge, self.Ptr, intPtrrange)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret



    def Intersect(self ,range:'IXLSRange')->'IXLSRange':
        """
        Returns intersection of this range with the specified one.

        Args:
            range: The Range with which to intersect.

        Returns:
            Range intersection. If there is no intersection, NULL is returned.
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
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().XlsRange_Intersect.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsRange_Intersect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_Intersect, self.Ptr, intPtrrange)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret



    def IsIntersect(self ,range:'IXLSRange')->bool:
        """

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().XlsRange_IsIntersect.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsRange_IsIntersect.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_IsIntersect, self.Ptr, intPtrrange)
        return ret


    def MeasureString(self ,measureString:str)->'SizeF':
        """
        Measures size of the string.

        Args:
            measureString: String to measure.

        Returns:
            Size of the string.

        """
        
        GetDllLibXls().XlsRange_MeasureString.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsRange_MeasureString.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_MeasureString, self.Ptr, measureString)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @dispatch
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
        GetDllLibXls().XlsRange_Merge1.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_Merge1, self.Ptr)

    def RemoveMergeComment(self):
        """

        """
        GetDllLibXls().XlsRange_RemoveMergeComment.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_RemoveMergeComment, self.Ptr)

    @dispatch

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
        
        GetDllLibXls().XlsRange_MergeC.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibXls().XlsRange_MergeC, self.Ptr, clearCells)

    def PartialClear(self):
        """
        Partially clear range.

        """
        GetDllLibXls().XlsRange_PartialClear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_PartialClear, self.Ptr)


    def TextPartReplace(self ,oldPartValue:str,newPartValue:str):
        """
        Replaces cell's part text and reserve text's format.

        Args:
            oldPartValue: Part value of cell's text to search for.
            newPartValue: The replacement value.

        """
        
        GetDllLibXls().XlsRange_TextPartReplace.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_TextPartReplace, self.Ptr, oldPartValue,newPartValue)


    def RemoveCombinedRange(self ,cr:'XlsRange'):
        """

        """
        intPtrcr:c_void_p = cr.Ptr

        GetDllLibXls().XlsRange_RemoveCombinedRange.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_RemoveCombinedRange, self.Ptr, intPtrcr)

#    @property
#
#    def CombinedCells(self)->'List1':
#        """
#
#        """
#        GetDllLibXls().XlsRange_get_CombinedCells.argtypes=[c_void_p]
#        GetDllLibXls().XlsRange_get_CombinedCells.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_CombinedCells, self.Ptr)
#        ret = None if intPtr==None else List1(intPtr)
#        return ret
#


    @property

    def CombinedAddress(self)->str:
        """
        Returns the combined range reference in the language. Read-only String.

        """
        GetDllLibXls().XlsRange_get_CombinedAddress.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_CombinedAddress.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_CombinedAddress, self.Ptr))
        return ret


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
        GetDllLibXls().XlsRange_UnMerge.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_UnMerge, self.Ptr)

    def ReparseFormulaString(self):
        """
        Reparses formula.

        """
        GetDllLibXls().XlsRange_ReparseFormulaString.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_ReparseFormulaString, self.Ptr)


    def GetEnumerator(self)->'EnumeratorXlsRange':
        """

        """
        GetDllLibXls().XlsRange_GetEnumerator.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_GetEnumerator, self.Ptr)
        ret = None if intPtr==None else EnumeratorXlsRange(intPtr)
        return ret



    @dispatch

    def AddComment(self ,bIsParseOptions:bool)->ICommentShape:
        """

        """
        
        GetDllLibXls().XlsRange_AddComment.argtypes=[c_void_p ,c_bool]
        GetDllLibXls().XlsRange_AddComment.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_AddComment, self.Ptr, bIsParseOptions)
        ret = None if intPtr==None else XlsComment(intPtr)
        return ret


    @dispatch

    def SetAutoFormat(self ,format:AutoFormatType):
        """

        """
        enumformat:c_int = format.value

        GetDllLibXls().XlsRange_SetAutoFormat.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsRange_SetAutoFormat, self.Ptr, enumformat)

    @dispatch

    def SetAutoFormat(self ,format:AutoFormatType,options:AutoFormatOptions):
        """

        """
        enumformat:c_int = format.value
        enumoptions:c_int = options.value

        GetDllLibXls().XlsRange_SetAutoFormatFO.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsRange_SetAutoFormatFO, self.Ptr, enumformat,enumoptions)


    def SetDataValidation(self ,dv:'XlsValidation'):
        """

        """
        intPtrdv:c_void_p = dv.Ptr

        GetDllLibXls().XlsRange_SetDataValidation.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_SetDataValidation, self.Ptr, intPtrdv)

    @dispatch

    def Replace(self ,oldValue:str,newValues:List[str],isVertical:bool):
        """
        Replaces cells' values with new data.

        Args:
            oldValue: Value to search for.
            newValues: The replacement value.
            isVertical: Indicates whether to insert values vertically or horizontally.

        """
        #arraynewValues:ArrayTypenewValues = ""
        countnewValues = len(newValues)
        ArrayTypenewValues = c_wchar_p * countnewValues
        arraynewValues = ArrayTypenewValues()
        for i in range(0, countnewValues):
            arraynewValues[i] = newValues[i]


        GetDllLibXls().XlsRange_Replace.argtypes=[c_void_p ,c_void_p,ArrayTypenewValues,c_int,c_bool]
        CallCFunction(GetDllLibXls().XlsRange_Replace, self.Ptr, oldValue,arraynewValues,countnewValues,isVertical)

    @dispatch

    def Replace(self ,oldValue:str,newValue:str):
        """
        Replaces cells' values with new data.

        Args:
            oldValue: Value to search for.
            newValue: The replacement value.

        """
        
        GetDllLibXls().XlsRange_ReplaceON.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_ReplaceON, self.Ptr, oldValue,newValue)

    @dispatch

    def Replace(self ,oldValue:str,newValues:List[float],isVertical:bool):
        """
        Replaces cells' values with new data.

        Args:
            oldValue: Value to search for.
            newValues: DataColumn to replace.
            isFieldNamesShown: Indicates whether to insert values vertically or horizontally.

        """
        #arraynewValues:ArrayTypenewValues = ""
        countnewValues = len(newValues)
        ArrayTypenewValues = c_double * countnewValues
        arraynewValues = ArrayTypenewValues()
        for i in range(0, countnewValues):
            arraynewValues[i] = newValues[i]


        GetDllLibXls().XlsRange_ReplaceONI.argtypes=[c_void_p ,c_void_p,ArrayTypenewValues,c_int,c_bool]
        CallCFunction(GetDllLibXls().XlsRange_ReplaceONI, self.Ptr, oldValue,arraynewValues,countnewValues,isVertical)

    @dispatch

    def Replace(self ,oldValue:str,newValues:List[int],isVertical:bool):
        """
        Replaces cells' values with new data.

        Args:
            oldValue: Value to search for.
            newValues: The replacement value.
            isVertical: Indicates whether to insert values vertically or horizontally.

        """
        #arraynewValues:ArrayTypenewValues = ""
        countnewValues = len(newValues)
        ArrayTypenewValues = c_int * countnewValues
        arraynewValues = ArrayTypenewValues()
        for i in range(0, countnewValues):
            arraynewValues[i] = newValues[i]


        GetDllLibXls().XlsRange_ReplaceONI1.argtypes=[c_void_p ,c_void_p,ArrayTypenewValues,c_int,c_bool]
        CallCFunction(GetDllLibXls().XlsRange_ReplaceONI1, self.Ptr, oldValue,arraynewValues,countnewValues,isVertical)

#    @dispatch
#
#    def Replace(self ,oldValue:str,newValues:'DataTable',isFieldNamesShown:bool):
#        """
#    <summary>
#        Replaces cells' values with new data.
#    </summary>
#    <param name="oldValue">Value to search for.</param>
#    <param name="newValues">The replacement value.</param>
#    <param name="isVertical">Indicates whether to insert values vertically or horizontally.</param>
#        """
#        intPtrnewValues:c_void_p = newValues.Ptr
#
#        GetDllLibXls().XlsRange_ReplaceONI11.argtypes=[c_void_p ,c_void_p,c_void_p,c_bool]
#        CallCFunction(GetDllLibXls().XlsRange_ReplaceONI11, self.Ptr, oldValue,intPtrnewValues,isFieldNamesShown)


    @dispatch

    def Replace(self ,oldValue:str,newValue:DateTime):
        """
        Replaces cells' values with new data.

        Args:
            oldValue: Value to search for.
            newValue: The replacement value.

        """
        intPtrnewValue:c_void_p = newValue.Ptr

        GetDllLibXls().XlsRange_ReplaceON1.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_ReplaceON1, self.Ptr, oldValue,intPtrnewValue)

    @dispatch

    def Replace(self ,oldValue:str,newValue:float):
        """
        Replaces cells' values with new data.

        Args:
            oldValue: Value to search for.
            newValue: The replacement value.

        """
        
        GetDllLibXls().XlsRange_ReplaceON11.argtypes=[c_void_p ,c_void_p,c_double]
        CallCFunction(GetDllLibXls().XlsRange_ReplaceON11, self.Ptr, oldValue,newValue)


    def Union(self ,range:'XlsRange')->'RangesCollection':
        """

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().XlsRange_Union.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsRange_Union.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_Union, self.Ptr, intPtrrange)
        ret = None if intPtr==None else RangesCollection(intPtr)
        return ret


#    @dispatch
#
#    def Replace(self ,oldValue:str,newValues:'DataColumn',isFieldNamesShown:bool):
#        """
#    <summary>
#        Replaces cells' values with new data.
#    </summary>
#    <param name="oldValue">Value to search for.</param>
#    <param name="newValues">DataColumn to replace.</param>
#    <param name="isFieldNamesShown">Indicates whether to insert values vertically or horizontally.</param>
#        """
#        intPtrnewValues:c_void_p = newValues.Ptr
#
#        GetDllLibXls().XlsRange_ReplaceONI111.argtypes=[c_void_p ,c_void_p,c_void_p,c_bool]
#        CallCFunction(GetDllLibXls().XlsRange_ReplaceONI111, self.Ptr, oldValue,intPtrnewValues,isFieldNamesShown)


#
#    def ExportDataTable(self ,options:'ExportTableOptions')->'DataTable':
#        """
#
#        """
#        intPtroptions:c_void_p = options.Ptr
#
#        GetDllLibXls().XlsRange_ExportDataTable.argtypes=[c_void_p ,c_void_p]
#        GetDllLibXls().XlsRange_ExportDataTable.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsRange_ExportDataTable, self.Ptr, intPtroptions)
#        ret = None if intPtr==None else DataTable(intPtr)
#        return ret
#



    def AddCombinedRange(self ,cr:'XlsRange')->'XlsRange':
        """

        """
        intPtrcr:c_void_p = cr.Ptr

        GetDllLibXls().XlsRange_AddCombinedRange.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsRange_AddCombinedRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_AddCombinedRange, self.Ptr, intPtrcr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret



    def UpdateRange(self ,startRow:int,startColumn:int,endRow:int,endColumn:int):
        """
        Update region of range

        Args:
            startRow: first Row
            startColumn: first Column
            endRow: last Row
            endColumn: last Column

        """
        
        GetDllLibXls().XlsRange_UpdateRange.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsRange_UpdateRange, self.Ptr, startRow,startColumn,endRow,endColumn)

    def ConvertToNumber(self):
        """
        Convert number that stored as text to number

        """
        GetDllLibXls().XlsRange_ConvertToNumber.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_ConvertToNumber, self.Ptr)


    def SetSharedFormula(self ,sharedFormula:str,rowNumber:int,columnNumber:int):
        """

        """
        
        GetDllLibXls().XlsRange_SetSharedFormula.argtypes=[c_void_p ,c_void_p,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsRange_SetSharedFormula, self.Ptr, sharedFormula,rowNumber,columnNumber)


    def GetConditionFormatsStyle(self)->'CellStyle':
        """
        Get the calculated condition format style of current Range. If style of every cell is not same, return null. If current range without condition format, return null.

        """
        GetDllLibXls().XlsRange_GetConditionFormatsStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_GetConditionFormatsStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_GetConditionFormatsStyle, self.Ptr)
        ret = None if intPtr==None else CellStyle(intPtr)
        return ret


    @property

    def RangeR1C1Address(self)->str:
        """
        Returns the range reference using R1C1 notation.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get RangeR1C1Address
            address = worksheet.Range[3, 4].RangeR1C1Address

        """
        GetDllLibXls().XlsRange_get_RangeR1C1Address.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_RangeR1C1Address.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_RangeR1C1Address, self.Ptr))
        return ret


    @property

    def RangeR1C1AddressLocal(self)->str:
        """
        Returns the range reference using R1C1 notation.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get RangeR1C1AddressLocal
            address = worksheet.Range[3, 4].RangeR1C1Address

        """
        GetDllLibXls().XlsRange_get_RangeR1C1AddressLocal.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_RangeR1C1AddressLocal.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_RangeR1C1AddressLocal, self.Ptr))
        return ret


    @property

    def RichText(self)->'IRichTextString':
        """

        """
        from spire.xls.RichTextString import RichTextString
        GetDllLibXls().XlsRange_get_RichText.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_RichText.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_RichText, self.Ptr)
        ret = None if intPtr==None else RichTextString(intPtr)
        return ret


    @property

    def HtmlString(self)->str:
        """
        Gets and sets the html string which contains data and some formattings in this cell.

        """
        GetDllLibXls().XlsRange_get_HtmlString.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HtmlString.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_HtmlString, self.Ptr))
        return ret


    @HtmlString.setter
    def HtmlString(self, value:str):
        GetDllLibXls().XlsRange_set_HtmlString.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsRange_set_HtmlString, self.Ptr, value)

    @property
    def Row(self)->int:
        """
        Returns the number of the first row of the first area in the range.

        """
        GetDllLibXls().XlsRange_get_Row.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_Row.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRange_get_Row, self.Ptr)
        return ret

    @property
    def RowGroupLevel(self)->int:
        """
        Row group level.

        """
        GetDllLibXls().XlsRange_get_RowGroupLevel.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_RowGroupLevel.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRange_get_RowGroupLevel, self.Ptr)
        return ret

    @property
    def RowHeight(self)->float:
        """
        Returns the height of all the rows in the range specified, measured in points.
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
        GetDllLibXls().XlsRange_get_RowHeight.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_RowHeight.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsRange_get_RowHeight, self.Ptr)
        return ret

    @RowHeight.setter
    def RowHeight(self, value:float):
        GetDllLibXls().XlsRange_set_RowHeight.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsRange_set_RowHeight, self.Ptr, value)

    @property

    def Rows(self)->'ListXlsRanges':
        """

        """
        GetDllLibXls().XlsRange_get_Rows.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_Rows.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_Rows, self.Ptr)
        ret = None if intPtr==None else ListXlsRanges(intPtr)
        return ret


    @property

    def ExtendedFormatIndex(self)->'UInt16':
        """

        """
        GetDllLibXls().XlsRange_get_ExtendedFormatIndex.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_ExtendedFormatIndex.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_ExtendedFormatIndex, self.Ptr)
        ret = None if intPtr==None else UInt16(intPtr)
        return ret


    @ExtendedFormatIndex.setter
    def ExtendedFormatIndex(self, value:'UInt16'):
        GetDllLibXls().XlsRange_set_ExtendedFormatIndex.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_set_ExtendedFormatIndex, self.Ptr, value.Ptr)


    def SetExtendedFormatIndex(self ,index:int):
        """

        """
        
        GetDllLibXls().XlsRange_SetExtendedFormatIndex.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsRange_SetExtendedFormatIndex, self.Ptr, index)


    def SetRowHeight(self ,rowHeight:float,bIsBadFontHeight:bool):
        """

        """
        
        GetDllLibXls().XlsRange_SetRowHeight.argtypes=[c_void_p ,c_double,c_bool]
        CallCFunction(GetDllLibXls().XlsRange_SetRowHeight, self.Ptr, rowHeight,bIsBadFontHeight)


    def ApplyStyle(self ,style:'IStyle',flag:'CellStyleFlag'):
        """

        """
        intPtrstyle:c_void_p = style.Ptr
        intPtrflag:c_void_p = flag.Ptr

        GetDllLibXls().XlsRange_ApplyStyle.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_ApplyStyle, self.Ptr, intPtrstyle,intPtrflag)

    @property

    def Style(self)->'IStyle':
        """

        """
        GetDllLibXls().XlsRange_get_Style.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_Style.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_Style, self.Ptr)
        ret = None if intPtr==None else CellStyle(intPtr)
        return ret


    @Style.setter
    def Style(self, value:'IStyle'):
        GetDllLibXls().XlsRange_set_Style.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_set_Style, self.Ptr, value.Ptr)

    @property

    def Text(self)->str:
        """
        Gets / sets text of range.

        """
        GetDllLibXls().XlsRange_get_Text.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        GetDllLibXls().XlsRange_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsRange_set_Text, self.Ptr, value)

    @dispatch

    def get_Item(self ,row:int,column:int,lastRow:int,lastColumn:int)->IXLSRange:
        """

        """
        
        GetDllLibXls().XlsRange_get_Item.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        GetDllLibXls().XlsRange_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_Item, self.Ptr, row,column,lastRow,lastColumn)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def get_Item(self ,row:int,column:int)->IXLSRange:
        """

        """
        
        GetDllLibXls().XlsRange_get_ItemRC.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsRange_get_ItemRC.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_ItemRC, self.Ptr, row,column)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret



    def set_Item(self ,row:int,column:int,value:'IXLSRange'):
        """

        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibXls().XlsRange_set_Item.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_set_Item, self.Ptr, row,column,intPtrvalue)

    @dispatch

    def get_Item(self ,name:str,IsR1C1Notation:bool)->IXLSRange:
        """

        """
        
        GetDllLibXls().XlsRange_get_ItemNI.argtypes=[c_void_p ,c_void_p,c_bool]
        GetDllLibXls().XlsRange_get_ItemNI.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_ItemNI, self.Ptr, name,IsR1C1Notation)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def get_Item(self ,name:str)->IXLSRange:
        """

        """
        
        GetDllLibXls().XlsRange_get_ItemN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsRange_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_ItemN, self.Ptr, name)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @property

    def TimeSpanValue(self)->'TimeSpan':
        """
        Gets or sets timespan value of cell.

        """
        GetDllLibXls().XlsRange_get_TimeSpanValue.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_TimeSpanValue.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_TimeSpanValue, self.Ptr)
        ret = None if intPtr==None else TimeSpan(intPtr)
        return ret


    @TimeSpanValue.setter
    def TimeSpanValue(self, value:'TimeSpan'):
        GetDllLibXls().XlsRange_set_TimeSpanValue.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_set_TimeSpanValue, self.Ptr, value.Ptr)

    @property

    def Value(self)->str:
        """
        Returns or sets the value of the specified range.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set value of the range
            XlsRange range= worksheet.Range[3, 1]
            range.Value = "1/1/2015"
            #Save to file
            workbook.SaveToFile("Value.xlsx")

        """
        GetDllLibXls().XlsRange_get_Value.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_Value.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_Value, self.Ptr))
        return ret


    @Value.setter
    def Value(self, value:str):
        GetDllLibXls().XlsRange_set_Value.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsRange_set_Value, self.Ptr, value)

    @property
    def Value2(self)->'SpireObject':
        """
        Returns or sets the cell value. It's not use for current and datetime types.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Assigning Value2 property of the Range
            worksheet["A1"].Value2 = DateTime.Now
            worksheet["A3"].Value2 = false
            #Checking Range types
            print(worksheet["A1"].HasDateTime)
            print(worksheet["A3"].HasBoolean)

        """
        GetDllLibXls().XlsRange_get_Value2.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_Value2.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_Value2, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @Value2.setter
    def Value2(self, value:'SpireObject'):
        GetDllLibXls().XlsRange_set_Value2.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_set_Value2, self.Ptr, value.Ptr)

    @property

    def VerticalAlignment(self)->'VerticalAlignType':
        """
        Returns or sets the vertical alignment of the specified object.
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
        GetDllLibXls().XlsRange_get_VerticalAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_VerticalAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRange_get_VerticalAlignment, self.Ptr)
        objwraped = VerticalAlignType(ret)
        return objwraped

    @VerticalAlignment.setter
    def VerticalAlignment(self, value:'VerticalAlignType'):
        GetDllLibXls().XlsRange_set_VerticalAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsRange_set_VerticalAlignment, self.Ptr, value.value)

    @property

    def Worksheet(self)->'IWorksheet':
        """
        Returns a worksheet object that represents the worksheet containing the specified range.

        """
        GetDllLibXls().XlsRange_get_Worksheet.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_Worksheet.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_Worksheet, self.Ptr)
        ret = None if intPtr==None else XlsWorksheet(intPtr)
        return ret


#
#    def GetNewRangeLocation(self ,names:'Dictionary2',sheetName:'String&')->str:
#        """
#
#        """
#        intPtrnames:c_void_p = names.Ptr
#        intPtrsheetName:c_void_p = sheetName.Ptr
#
#        GetDllLibXls().XlsRange_GetNewRangeLocation.argtypes=[c_void_p ,c_void_p,c_void_p]
#        GetDllLibXls().XlsRange_GetNewRangeLocation.restype=c_wchar_p
#        ret = CallCFunction(GetDllLibXls().XlsRange_GetNewRangeLocation, self.Ptr, intPtrnames,intPtrsheetName)
#        return ret
#


#
#    def Clone(self ,parent:'SpireObject',rangeNames:'Dictionary2',book:'XlsWorkbook')->'IXLSRange':
#        """
#
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrrangeNames:c_void_p = rangeNames.Ptr
#        intPtrbook:c_void_p = book.Ptr
#
#        GetDllLibXls().XlsRange_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p]
#        GetDllLibXls().XlsRange_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsRange_Clone, self.Ptr, intPtrparent,intPtrrangeNames,intPtrbook)
#        ret = None if intPtr==None else XlsRange(intPtr)
#        return ret
#


    def ClearConditionalFormats(self):
        """
        Clears conditional formats.

        """
        GetDllLibXls().XlsRange_ClearConditionalFormats.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_ClearConditionalFormats, self.Ptr)


    def GetRectangles(self)->List['Rectangle']:
        """
        Gets rectangle information of current range.

        Returns:
            Rectangles information

        """
        GetDllLibXls().XlsRange_GetRectangles.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_GetRectangles.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().XlsRange_GetRectangles, self.Ptr)
        ret = GetVectorFromArray(intPtrArray, Rectangle)
        return ret


    def GetRectanglesCount(self)->int:
        """
        Returns number of rectangles..

        Returns:
            Number of rectangles.

        """
        GetDllLibXls().XlsRange_GetRectanglesCount.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_GetRectanglesCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRange_GetRectanglesCount, self.Ptr)
        return ret

    @property

    def WorksheetName(self)->str:
        """
        Returns name of the parent worksheet.

        """
        GetDllLibXls().XlsRange_get_WorksheetName.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_WorksheetName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_WorksheetName, self.Ptr))
        return ret


    @property
    def CellsCount(self)->int:
        """
        Gets number of cells.

        """
        GetDllLibXls().XlsRange_get_CellsCount.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_CellsCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRange_get_CellsCount, self.Ptr)
        return ret

    @property

    def RangeGlobalAddress2007(self)->str:
        """
        Gets address global in the format required by Excel 2007.

        """
        GetDllLibXls().XlsRange_get_RangeGlobalAddress2007.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_RangeGlobalAddress2007.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_RangeGlobalAddress2007, self.Ptr))
        return ret


    def CalculateAllValue(self):
        """
        Caculate all formula for the specified range

        """
        GetDllLibXls().XlsRange_CalculateAllValue.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_CalculateAllValue, self.Ptr)

    @dispatch

    def Activate(self ,scroll:bool)->IXLSRange:
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
        
        GetDllLibXls().XlsRange_Activate.argtypes=[c_void_p ,c_bool]
        GetDllLibXls().XlsRange_Activate.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_Activate, self.Ptr, scroll)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def Activate(self)->IXLSRange:
        """
        Active single cell in the worksheet

        Returns:
            Returns the active cell.

        """
        GetDllLibXls().XlsRange_Activate1.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_Activate1.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_Activate1, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def AddComment(self)->ICommentShape:
        """
        Adds a comment to the range.

        Returns:
            Created comment or exists one.

        """
        GetDllLibXls().XlsRange_AddComment1.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_AddComment1.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_AddComment1, self.Ptr)
        ret = None if intPtr==None else XlsComment(intPtr)
        return ret


    def AutoFitColumns(self):
        """
        Changes the width of the columns in the range in the range to achieve the best fit.
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
        GetDllLibXls().XlsRange_AutoFitColumns.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_AutoFitColumns, self.Ptr)

    def AutoFitRows(self):
        """
        Changes the width of the height of the rows in the range to achieve the best fit.
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
        GetDllLibXls().XlsRange_AutoFitRows.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_AutoFitRows, self.Ptr)

    @dispatch
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
        GetDllLibXls().XlsRange_BorderAround.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_BorderAround, self.Ptr)

    @dispatch

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
        enumborderLine:c_int = borderLine.value

        GetDllLibXls().XlsRange_BorderAroundB.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsRange_BorderAroundB, self.Ptr, enumborderLine)

    @dispatch

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
        enumborderLine:c_int = borderLine.value
        intPtrborderColor:c_void_p = borderColor.Ptr

        GetDllLibXls().XlsRange_BorderAroundBB.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_BorderAroundBB, self.Ptr, enumborderLine,intPtrborderColor)

    @dispatch

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
        enumborderLine:c_int = borderLine.value
        enumborderColor:c_int = borderColor.value

        GetDllLibXls().XlsRange_BorderAroundBB1.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsRange_BorderAroundBB1, self.Ptr, enumborderLine,enumborderColor)

    @dispatch
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
        GetDllLibXls().XlsRange_BorderInside.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_BorderInside, self.Ptr)

    @dispatch

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
        enumborderLine:c_int = borderLine.value

        GetDllLibXls().XlsRange_BorderInsideB.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsRange_BorderInsideB, self.Ptr, enumborderLine)

    @dispatch

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
        enumborderLine:c_int = borderLine.value
        intPtrborderColor:c_void_p = borderColor.Ptr

        GetDllLibXls().XlsRange_BorderInsideBB.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_BorderInsideBB, self.Ptr, enumborderLine,intPtrborderColor)

    @dispatch

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
        enumborderLine:c_int = borderLine.value
        enumborderColor:c_int = borderColor.value

        GetDllLibXls().XlsRange_BorderInsideBB1.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsRange_BorderInsideBB1, self.Ptr, enumborderLine,enumborderColor)

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
        GetDllLibXls().XlsRange_BorderNone.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_BorderNone, self.Ptr)


    def Clear(self ,option:'ExcelClearOptions'):
        """
        Clears the cell based on clear options.

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
        enumoption:c_int = option.value

        GetDllLibXls().XlsRange_Clear.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsRange_Clear, self.Ptr, enumoption)

    def ClearAll(self):
        """
        Clears the entire object.

        """
        GetDllLibXls().XlsRange_ClearAll.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_ClearAll, self.Ptr)

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
        GetDllLibXls().XlsRange_ClearContents.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_ClearContents, self.Ptr)


    def GroupByColumns(self ,isCollapsed:bool)->'XlsRange':
        """
        Groups columns.

        Args:
            isCollapsed: Indicates whether group should be collapsed.

        """
        
        GetDllLibXls().XlsRange_GroupByColumns.argtypes=[c_void_p ,c_bool]
        GetDllLibXls().XlsRange_GroupByColumns.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_GroupByColumns, self.Ptr, isCollapsed)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret



    def GroupByRows(self ,isCollapsed:bool)->'XlsRange':
        """
        Groups row.

        Args:
            isCollapsed: Indicates whether group should be collapsed.

        """
        
        GetDllLibXls().XlsRange_GroupByRows.argtypes=[c_void_p ,c_bool]
        GetDllLibXls().XlsRange_GroupByRows.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_GroupByRows, self.Ptr, isCollapsed)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret



    def UngroupByColumns(self)->'XlsRange':
        """
        Ungroups column.

        """
        GetDllLibXls().XlsRange_UngroupByColumns.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_UngroupByColumns.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_UngroupByColumns, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret



    def UngroupByRows(self)->'XlsRange':
        """
        Ungroups row.

        """
        GetDllLibXls().XlsRange_UngroupByRows.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_UngroupByRows.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_UngroupByRows, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret



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
        enumgroupBy:c_int = groupBy.value

        GetDllLibXls().XlsRange_CollapseGroup.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsRange_CollapseGroup, self.Ptr, enumgroupBy)

    def CopyToClipboard(self):
        """

        """
        GetDllLibXls().XlsRange_CopyToClipboard.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_CopyToClipboard, self.Ptr)

    def Dispose(self):
        """

        """
        GetDllLibXls().XlsRange_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_Dispose, self.Ptr)

    @dispatch

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
        enumgroupBy:c_int = groupBy.value

        GetDllLibXls().XlsRange_ExpandGroup.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsRange_ExpandGroup, self.Ptr, enumgroupBy)

    @dispatch

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
        enumgroupBy:c_int = groupBy.value
        enumflags:c_int = flags.value

        GetDllLibXls().XlsRange_ExpandGroupGF.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsRange_ExpandGroupGF, self.Ptr, enumgroupBy,enumflags)

    def FreezePanes(self):
        """
        Freezes panes at the current range in the worksheet. current range should be single cell range.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Applying Freeze Pane to the sheet by specifying a cell
            worksheet.Range["B2"].FreezePanes()
            #Save to file
            workbook.SaveToFile("FreezePanes.xlsx")

        """
        GetDllLibXls().XlsRange_FreezePanes.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_FreezePanes, self.Ptr)

    @property
    def BooleanValue(self)->bool:
        """
        Returns or sets the bool value of the specified range.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set and get BooleanValue
            worksheet.Range[2, 4].BooleanValue = true
            boolean = worksheet.Range[2, 4].BooleanValue

        """
        GetDllLibXls().XlsRange_get_BooleanValue.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_BooleanValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_BooleanValue, self.Ptr)
        return ret

    @BooleanValue.setter
    def BooleanValue(self, value:bool):
        GetDllLibXls().XlsRange_set_BooleanValue.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsRange_set_BooleanValue, self.Ptr, value)

    @property

    def Borders(self)->'IBorders':
        """

        """
        from spire.xls.collection.XlsBordersCollection import XlsBordersCollection
        GetDllLibXls().XlsRange_get_Borders.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_Borders.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_Borders, self.Ptr)
        ret = None if intPtr==None else XlsBordersCollection(intPtr)
        return ret


    @property

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
        GetDllLibXls().XlsRange_get_BuiltInStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_BuiltInStyle.restype=c_int
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_BuiltInStyle, self.Ptr)
        ret = None if intPtr==None else BuiltInStyles(intPtr)
        return ret



    @BuiltInStyle.setter
    def BuiltInStyle(self, value:BuiltInStyles):
        GetDllLibXls().XlsRange_set_BuiltInStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsRange_set_BuiltInStyle, self.Ptr, value.value)


    @property

    def Cells(self)->'ListXlsRanges':
        """

        """
        GetDllLibXls().XlsRange_get_Cells.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_Cells.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_Cells, self.Ptr)
        ret = None if intPtr==None else ListXlsRanges(intPtr)
        return ret


#    @property
#
#    def CellList(self)->'List1':
#        """
#
#        """
#        GetDllLibXls().XlsRange_get_CellList.argtypes=[c_void_p]
#        GetDllLibXls().XlsRange_get_CellList.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_CellList, self.Ptr)
#        ret = None if intPtr==None else List1(intPtr)
#        return ret
#


    @property

    def CellStyleName(self)->str:
        """
        Gets/sets name of the style for the current range.
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
        GetDllLibXls().XlsRange_get_CellStyleName.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_CellStyleName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_CellStyleName, self.Ptr))
        return ret


    @CellStyleName.setter
    def CellStyleName(self, value:str):
        GetDllLibXls().XlsRange_set_CellStyleName.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsRange_set_CellStyleName, self.Ptr, value)

    @property
    def Column(self)->int:
        """
        Returns the number of the first column in the first area in the specified range.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get specified column
            firstColumn = worksheet["E1:R3"].Column

        """
        GetDllLibXls().XlsRange_get_Column.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_Column.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRange_get_Column, self.Ptr)
        return ret

    @property
    def ColumnGroupLevel(self)->int:
        """
        Column group level.

        """
        GetDllLibXls().XlsRange_get_ColumnGroupLevel.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_ColumnGroupLevel.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRange_get_ColumnGroupLevel, self.Ptr)
        return ret

    @property

    def Columns(self)->'ListXlsRanges':
        """

        """
        GetDllLibXls().XlsRange_get_Columns.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_Columns.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_Columns, self.Ptr)
        ret = None if intPtr==None else ListXlsRanges(intPtr)
        return ret


    @property
    def ColumnWidth(self)->float:
        """
        Returns or sets the width of all columns in the specified range.
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
        GetDllLibXls().XlsRange_get_ColumnWidth.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_ColumnWidth.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsRange_get_ColumnWidth, self.Ptr)
        return ret

    @ColumnWidth.setter
    def ColumnWidth(self, value:float):
        GetDllLibXls().XlsRange_set_ColumnWidth.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsRange_set_ColumnWidth, self.Ptr, value)

    @property

    def Comment(self)->'ICommentShape':
        """
        Returns a Comment object that represents the comment associated with the cell in the upper-left corner of the range.

        """
        GetDllLibXls().XlsRange_get_Comment.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_Comment.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_Comment, self.Ptr)
        ret = None if intPtr==None else XlsComment(intPtr)
        return ret


    @property

    def ConditionalFormats(self)->'ConditionalFormats':
        """

        """
        GetDllLibXls().XlsRange_get_ConditionalFormats.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_ConditionalFormats.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_ConditionalFormats, self.Ptr)
        ret = None if intPtr==None else ConditionalFormats(intPtr)
        return ret


    @property
    def Count(self)->int:
        """
        Returns the number of objects in the collection.

        """
        GetDllLibXls().XlsRange_get_Count.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRange_get_Count, self.Ptr)
        return ret

    @property

    def CurrentRegion(self)->'IXLSRange':
        """
        Get the range associated with a range.

        """
        GetDllLibXls().XlsRange_get_CurrentRegion.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_CurrentRegion.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_CurrentRegion, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @property

    def DataValidation(self)->'Validation':
        """
        Get dataValidation of the sheet. Read Only.
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
        GetDllLibXls().XlsRange_get_DataValidation.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_DataValidation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_DataValidation, self.Ptr)
        ret = None if intPtr==None else Validation(intPtr)
        return ret


    @property

    def DateTimeValue(self)->'DateTime':
        """
        Gets/sets DateTime value of the range.
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
        GetDllLibXls().XlsRange_get_DateTimeValue.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_DateTimeValue.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_DateTimeValue, self.Ptr)
        ret = None if intPtr==None else DateTime(intPtr)
        return ret


    @DateTimeValue.setter
    def DateTimeValue(self, value:'DateTime'):
        GetDllLibXls().XlsRange_set_DateTimeValue.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_set_DateTimeValue, self.Ptr, value.Ptr)

    @property

    def EndCell(self)->'IXLSRange':
        """

        """
        GetDllLibXls().XlsRange_get_EndCell.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_EndCell.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_EndCell, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @property

    def EntireColumn(self)->'IXLSRange':
        """

        """
        GetDllLibXls().XlsRange_get_EntireColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_EntireColumn.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_EntireColumn, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @property

    def EntireRow(self)->'IXLSRange':
        """
        Returns a Range object that represents the entire row (or rows) that contains the specified range. Read-only.

        """
        GetDllLibXls().XlsRange_get_EntireRow.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_EntireRow.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_EntireRow, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @property

    def EnvalutedValue(self)->str:
        """
        Returns the calculated value of a formula.
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Returns the calculated value of a formula using the most current inputs
            calculatedValue = worksheet["C1"].EnvalutedValue
            print(calculatedValue)

        """
        GetDllLibXls().XlsRange_get_EnvalutedValue.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_EnvalutedValue.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_EnvalutedValue, self.Ptr))
        return ret


    @property

    def ErrorValue(self)->str:
        """
        Gets or sets error value of this range.

        """
        GetDllLibXls().XlsRange_get_ErrorValue.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_ErrorValue.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_ErrorValue, self.Ptr))
        return ret


    @ErrorValue.setter
    def ErrorValue(self, value:str):
        GetDllLibXls().XlsRange_set_ErrorValue.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsRange_set_ErrorValue, self.Ptr, value)

    @property

    def Formula(self)->str:
        """
        Returns or sets the object's formula in A1-style notation and in the language of the macro.

        """
        GetDllLibXls().XlsRange_get_Formula.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_Formula.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_Formula, self.Ptr))
        return ret


    @Formula.setter
    def Formula(self, value:str):
        GetDllLibXls().XlsRange_set_Formula.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsRange_set_Formula, self.Ptr, value)

    @property

    def FormulaArray(self)->str:
        """
        Returns or sets the array formula of a range.
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
        GetDllLibXls().XlsRange_get_FormulaArray.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_FormulaArray.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_FormulaArray, self.Ptr))
        return ret


    @FormulaArray.setter
    def FormulaArray(self, value:str):
        GetDllLibXls().XlsRange_set_FormulaArray.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsRange_set_FormulaArray, self.Ptr, value)

    @property

    def FormulaArrayR1C1(self)->str:
        """
        Returns or sets the formula for the object, using R1C1-style notation in the language of the macro

        """
        GetDllLibXls().XlsRange_get_FormulaArrayR1C1.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_FormulaArrayR1C1.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_FormulaArrayR1C1, self.Ptr))
        return ret


    @FormulaArrayR1C1.setter
    def FormulaArrayR1C1(self, value:str):
        GetDllLibXls().XlsRange_set_FormulaArrayR1C1.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsRange_set_FormulaArrayR1C1, self.Ptr, value)

    @property
    def FormulaBoolValue(self)->bool:
        """

        """
        GetDllLibXls().XlsRange_get_FormulaBoolValue.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_FormulaBoolValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_FormulaBoolValue, self.Ptr)
        return ret

    @FormulaBoolValue.setter
    def FormulaBoolValue(self, value:bool):
        GetDllLibXls().XlsRange_set_FormulaBoolValue.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsRange_set_FormulaBoolValue, self.Ptr, value)

    @property

    def FormulaDateTime(self)->'DateTime':
        """
        Gets or sets bool value of the formula.

        """
        GetDllLibXls().XlsRange_get_FormulaDateTime.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_FormulaDateTime.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_FormulaDateTime, self.Ptr)
        ret = None if intPtr==None else DateTime(intPtr)
        return ret


    @FormulaDateTime.setter
    def FormulaDateTime(self, value:'DateTime'):
        GetDllLibXls().XlsRange_set_FormulaDateTime.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsRange_set_FormulaDateTime, self.Ptr, value.Ptr)

    @property

    def FormulaErrorValue(self)->str:
        """
        Gets or sets error value of the formula.

        """
        GetDllLibXls().XlsRange_get_FormulaErrorValue.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_FormulaErrorValue.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_FormulaErrorValue, self.Ptr))
        return ret


    @FormulaErrorValue.setter
    def FormulaErrorValue(self, value:str):
        GetDllLibXls().XlsRange_set_FormulaErrorValue.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsRange_set_FormulaErrorValue, self.Ptr, value)

    @property
    def FormulaNumberValue(self)->float:
        """
        Gets or sets double value of the formula.

        """
        GetDllLibXls().XlsRange_get_FormulaNumberValue.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_FormulaNumberValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsRange_get_FormulaNumberValue, self.Ptr)
        return ret

    @FormulaNumberValue.setter
    def FormulaNumberValue(self, value:float):
        GetDllLibXls().XlsRange_set_FormulaNumberValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsRange_set_FormulaNumberValue, self.Ptr, value)

    @property

    def FormulaR1C1(self)->str:
        """
        Returns or sets the formula for the object, using R1C1-style notation in the language of the macro

        """
        GetDllLibXls().XlsRange_get_FormulaR1C1.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_FormulaR1C1.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_FormulaR1C1, self.Ptr))
        return ret


    @FormulaR1C1.setter
    def FormulaR1C1(self, value:str):
        GetDllLibXls().XlsRange_set_FormulaR1C1.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsRange_set_FormulaR1C1, self.Ptr, value)

    @property

    def FormulaStringValue(self)->str:
        """
        Gets or sets string value of the range.

        """
        GetDllLibXls().XlsRange_get_FormulaStringValue.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_FormulaStringValue.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_FormulaStringValue, self.Ptr))
        return ret


    @FormulaStringValue.setter
    def FormulaStringValue(self, value:str):
        GetDllLibXls().XlsRange_set_FormulaStringValue.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsRange_set_FormulaStringValue, self.Ptr, value)

    @property

    def FormulaValue(self)->'str':
        """
        Gets formula value.

        """
        GetDllLibXls().XlsRange_get_FormulaValue.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_FormulaValue.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_FormulaValue, self.Ptr)
        ret = None if intPtr==None else PtrToStr(intPtr)
        return ret


    @property
    def HasBoolean(self)->bool:
        """
        Indicates whether range contains bool value.
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
        GetDllLibXls().XlsRange_get_HasBoolean.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasBoolean.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasBoolean, self.Ptr)
        return ret

    @property
    def HasComment(self)->bool:
        """

        """
        GetDllLibXls().XlsRange_get_HasComment.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasComment.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasComment, self.Ptr)
        return ret

    @property
    def ColumnCount(self)->int:
        """
        Gets number of columns.

        """
        GetDllLibXls().XlsRange_get_ColumnCount.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_ColumnCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRange_get_ColumnCount, self.Ptr)
        return ret

    @property
    def RowCount(self)->int:
        """
        Gets number of rows.

        """
        GetDllLibXls().XlsRange_get_RowCount.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_RowCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRange_get_RowCount, self.Ptr)
        return ret

    @property
    def HasDataValidation(self)->bool:
        """
        Indicates whether specified range object has data validation. If Range is not single cell, then returns true only if all cells have data validation. Read-only.

        """
        GetDllLibXls().XlsRange_get_HasDataValidation.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasDataValidation.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasDataValidation, self.Ptr)
        return ret

    @property
    def HasDateTime(self)->bool:
        """
        Determines if all cells in the range contain datetime.
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
        GetDllLibXls().XlsRange_get_HasDateTime.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasDateTime.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasDateTime, self.Ptr)
        return ret

    @property
    def HasError(self)->bool:
        """
        Indicates whether range contains error value.

        """
        GetDllLibXls().XlsRange_get_HasError.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasError.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasError, self.Ptr)
        return ret

    @property
    def HasExternalFormula(self)->bool:
        """
        Check if the formula in the range has external links. Read-only.

        """
        GetDllLibXls().XlsRange_get_HasExternalFormula.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasExternalFormula.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasExternalFormula, self.Ptr)
        return ret

    @property
    def HasFormula(self)->bool:
        """
        True if all cells in the range contain formulas;

        """
        GetDllLibXls().XlsRange_get_HasFormula.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasFormula.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasFormula, self.Ptr)
        return ret

    @property
    def HasFormulaArray(self)->bool:
        """
        Determines if all cells in the range contain array-entered formula.

        """
        GetDllLibXls().XlsRange_get_HasFormulaArray.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasFormulaArray.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasFormulaArray, self.Ptr)
        return ret

    @property
    def HasFormulaBoolValue(self)->bool:
        """
        Determines if all cells in the range contain formula bool value..

        """
        GetDllLibXls().XlsRange_get_HasFormulaBoolValue.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasFormulaBoolValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasFormulaBoolValue, self.Ptr)
        return ret

    @property
    def HasFormulaDateTime(self)->bool:
        """
        Indicates if current range has formula value formatted as DateTime. Read-only.

        """
        GetDllLibXls().XlsRange_get_HasFormulaDateTime.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasFormulaDateTime.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasFormulaDateTime, self.Ptr)
        return ret

    @property
    def HasFormulaErrorValue(self)->bool:
        """
        Determines if all cells in the range contain error value.

        """
        GetDllLibXls().XlsRange_get_HasFormulaErrorValue.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasFormulaErrorValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasFormulaErrorValue, self.Ptr)
        return ret

    @property
    def HasFormulaNumberValue(self)->bool:
        """
        Indicates whether current range has formula number value.

        """
        GetDllLibXls().XlsRange_get_HasFormulaNumberValue.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasFormulaNumberValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasFormulaNumberValue, self.Ptr)
        return ret

    @property
    def HasFormulaStringValue(self)->bool:
        """

        """
        GetDllLibXls().XlsRange_get_HasFormulaStringValue.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasFormulaStringValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasFormulaStringValue, self.Ptr)
        return ret

    @property
    def HasMerged(self)->bool:
        """
        Indicates whether this range is part of merged range.
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
        GetDllLibXls().XlsRange_get_HasMerged.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasMerged.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasMerged, self.Ptr)
        return ret

    @property
    def HasNumber(self)->bool:
        """
        Determines if any one cell in the range contain number.
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
        GetDllLibXls().XlsRange_get_HasNumber.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasNumber.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasNumber, self.Ptr)
        return ret

    @property
    def HasPictures(self)->bool:
        """
        Indicates whether the range is blank.

        """
        GetDllLibXls().XlsRange_get_HasPictures.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasPictures.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasPictures, self.Ptr)
        return ret

    @property
    def HasRichText(self)->bool:
        """
        Determines if all cells in the range contain rich text string.
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
        GetDllLibXls().XlsRange_get_HasRichText.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasRichText.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasRichText, self.Ptr)
        return ret

    @property
    def HasString(self)->bool:
        """
        Determines if all cells in the range contain string.

        """
        GetDllLibXls().XlsRange_get_HasString.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasString.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasString, self.Ptr)
        return ret

    @property
    def HasStyle(self)->bool:
        """
        Determines if all cells in the range contain  differs from default style.
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
        GetDllLibXls().XlsRange_get_HasStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasStyle.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasStyle, self.Ptr)
        return ret

    @property

    def HorizontalAlignment(self)->'HorizontalAlignType':
        """
        Returns or sets the horizontal alignment for the specified object.
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
        GetDllLibXls().XlsRange_get_HorizontalAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HorizontalAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HorizontalAlignment, self.Ptr)
        objwraped = HorizontalAlignType(ret)
        return objwraped

    @HorizontalAlignment.setter
    def HorizontalAlignment(self, value:'HorizontalAlignType'):
        GetDllLibXls().XlsRange_set_HorizontalAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsRange_set_HorizontalAlignment, self.Ptr, value.value)

    @property

    def Hyperlinks(self)->'IHyperLinks':
        """
        Returns hyperlinks for this range.

        """
        GetDllLibXls().XlsRange_get_Hyperlinks.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_Hyperlinks.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_Hyperlinks, self.Ptr)
        ret = None if intPtr==None else XlsHyperLinksCollection(intPtr)
        return ret


    @property

    def IgnoreErrorOptions(self)->'IgnoreErrorType':
        """
        Represents ignore error options. If not single cell returs concatenateed flags.

        """
        GetDllLibXls().XlsRange_get_IgnoreErrorOptions.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_IgnoreErrorOptions.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRange_get_IgnoreErrorOptions, self.Ptr)
        objwraped = IgnoreErrorType(ret)
        return objwraped

    @IgnoreErrorOptions.setter
    def IgnoreErrorOptions(self, value:'IgnoreErrorType'):
        GetDllLibXls().XlsRange_set_IgnoreErrorOptions.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsRange_set_IgnoreErrorOptions, self.Ptr, value.value)

    @property
    def IndentLevel(self)->int:
        """
        Returns or sets the indent level for the cell or range. value should be 0 between 15.
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
        GetDllLibXls().XlsRange_get_IndentLevel.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_IndentLevel.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRange_get_IndentLevel, self.Ptr)
        return ret

    @IndentLevel.setter
    def IndentLevel(self, value:int):
        GetDllLibXls().XlsRange_set_IndentLevel.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsRange_set_IndentLevel, self.Ptr, value)

    @property
    def IsAllNumber(self)->bool:
        """
        Determines if all cells in the range contain number.

        """
        GetDllLibXls().XlsRange_get_IsAllNumber.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_IsAllNumber.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_IsAllNumber, self.Ptr)
        return ret

    @property
    def IsBlank(self)->bool:
        """
        Indicates whether the range is blank.

        """
        GetDllLibXls().XlsRange_get_IsBlank.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_IsBlank.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_IsBlank, self.Ptr)
        return ret

    @property
    def IsFormulaHidden(self)->bool:
        """
        Determines if the formula will be hidden when the worksheet is protected.

        """
        GetDllLibXls().XlsRange_get_IsFormulaHidden.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_IsFormulaHidden.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_IsFormulaHidden, self.Ptr)
        return ret

    @IsFormulaHidden.setter
    def IsFormulaHidden(self, value:bool):
        GetDllLibXls().XlsRange_set_IsFormulaHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsRange_set_IsFormulaHidden, self.Ptr, value)

    @property
    def IsGroupedByColumn(self)->bool:
        """
        Indicates whether this range is grouped by column.

        """
        GetDllLibXls().XlsRange_get_IsGroupedByColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_IsGroupedByColumn.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_IsGroupedByColumn, self.Ptr)
        return ret

    @property
    def IsGroupedByRow(self)->bool:
        """
        Indicates whether this range is grouped by row.

        """
        GetDllLibXls().XlsRange_get_IsGroupedByRow.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_IsGroupedByRow.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_IsGroupedByRow, self.Ptr)
        return ret

    @property
    def IsInitialized(self)->bool:
        """
        Indicates whether range has been initialized.

        """
        GetDllLibXls().XlsRange_get_IsInitialized.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_IsInitialized.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_IsInitialized, self.Ptr)
        return ret

    @property

    def IsStringsPreserved(self)->bool:
        """
        Indicates whether all values in the range are preserved as strings.

        """
        GetDllLibXls().XlsRange_get_IsStringsPreserved.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_IsStringsPreserved.restype=c_bool
        return CallCFunction(GetDllLibXls().XlsRange_get_IsStringsPreserved, self.Ptr)



    @IsStringsPreserved.setter
    def IsStringsPreserved(self, value:bool):
        GetDllLibXls().XlsRange_set_IsStringsPreserved.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsRange_set_IsStringsPreserved, self.Ptr, value)


    @property
    def IsWrapText(self)->bool:
        """
        Determines if Microsoft Excel wraps the text in the object.
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
        GetDllLibXls().XlsRange_get_IsWrapText.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_IsWrapText.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_IsWrapText, self.Ptr)
        return ret

    @IsWrapText.setter
    def IsWrapText(self, value:bool):
        GetDllLibXls().XlsRange_set_IsWrapText.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsRange_set_IsWrapText, self.Ptr, value)

    @property
    def LastColumn(self)->int:
        """
        Gets or sets last column of the range.

        """
        GetDllLibXls().XlsRange_get_LastColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_LastColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRange_get_LastColumn, self.Ptr)
        return ret

    @LastColumn.setter
    def LastColumn(self, value:int):
        GetDllLibXls().XlsRange_set_LastColumn.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsRange_set_LastColumn, self.Ptr, value)

    @property
    def LastRow(self)->int:
        """
        Gets or sets last row of the range.

        """
        GetDllLibXls().XlsRange_get_LastRow.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_LastRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRange_get_LastRow, self.Ptr)
        return ret

    @LastRow.setter
    def LastRow(self, value:int):
        GetDllLibXls().XlsRange_set_LastRow.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsRange_set_LastRow, self.Ptr, value)

    @property

    def MergeArea(self)->'IXLSRange':
        """

        """
        GetDllLibXls().XlsRange_get_MergeArea.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_MergeArea.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_MergeArea, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @property

    def DisplayedText(self)->str:
        """
        Gets cell displayed text.

        """
        GetDllLibXls().XlsRange_get_DisplayedText.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_DisplayedText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_DisplayedText, self.Ptr))
        return ret


    @property
    def HasConditionFormats(self)->bool:
        """
        Indicates whether each cell of the range has some conditional formatting.

        """
        GetDllLibXls().XlsRange_get_HasConditionFormats.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_HasConditionFormats.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRange_get_HasConditionFormats, self.Ptr)
        return ret

    @property

    def NumberFormat(self)->str:
        """
        Returns or sets the format code for the object.
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
        GetDllLibXls().XlsRange_get_NumberFormat.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_NumberFormat.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_NumberFormat, self.Ptr))
        return ret


    @NumberFormat.setter
    def NumberFormat(self, value:str):
        GetDllLibXls().XlsRange_set_NumberFormat.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsRange_set_NumberFormat, self.Ptr, value)

    @property

    def NumberText(self)->str:
        """
        Returns cell text for number format.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Gets cell value with its number format
            XlsRange range= worksheet.Range[3, 1]
            range.Value = "1/1/2015"
            range.NumberFormat = "dd-MMM-yyyy"
            numberText = range.NumberText
            #Save to file
            workbook.SaveToFile("NumberText.xlsx")

        """
        GetDllLibXls().XlsRange_get_NumberText.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_NumberText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_NumberText, self.Ptr))
        return ret


    @property
    def NumberValue(self)->float:
        """
        Gets or sets number value of the range.

        """
        GetDllLibXls().XlsRange_get_NumberValue.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_NumberValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsRange_get_NumberValue, self.Ptr)
        return ret

    @NumberValue.setter
    def NumberValue(self, value:float):
        GetDllLibXls().XlsRange_set_NumberValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsRange_set_NumberValue, self.Ptr, value)

    @property

    def Parent(self)->'SpireObject':
        """

        """
        GetDllLibXls().XlsRange_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRange_get_Parent, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @property

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
        GetDllLibXls().XlsRange_get_RangeAddress.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_RangeAddress.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_RangeAddress, self.Ptr))
        return ret


    @property

    def RangeAddressLocal(self)->str:
        """
        Returns the range reference for the specified range in the language of the user.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get RangeAddressLocal
            address = worksheet.Range[3, 4].RangeAddressLocal

        """
        GetDllLibXls().XlsRange_get_RangeAddressLocal.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_RangeAddressLocal.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_RangeAddressLocal, self.Ptr))
        return ret


    @property

    def RangeGlobalAddressWithoutSheetName(self)->str:
        """
        Return global address without worksheet name.

        """
        GetDllLibXls().XlsRange_get_RangeGlobalAddressWithoutSheetName.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_RangeGlobalAddressWithoutSheetName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_RangeGlobalAddressWithoutSheetName, self.Ptr))
        return ret


    @property

    def RangeGlobalAddress(self)->str:
        """
        Returns the range reference in the language of the macro.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Get RangeAddress
            address = worksheet.Range[3, 4].RangeGlobalAddress

        """
        GetDllLibXls().XlsRange_get_RangeGlobalAddress.argtypes=[c_void_p]
        GetDllLibXls().XlsRange_get_RangeGlobalAddress.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRange_get_RangeGlobalAddress, self.Ptr))
        return ret


    @staticmethod
    def DEF_MAX_HEIGHT()->float:
        """

        """
        #GetDllLibXls().XlsRange_DEF_MAX_HEIGHT.argtypes=[]
        GetDllLibXls().XlsRange_DEF_MAX_HEIGHT.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsRange_DEF_MAX_HEIGHT)
        return ret

class EnumeratorXlsRange(IEnumerator[XlsRange]):
    pass
class ListXlsRanges (IList[IXLSRange]):
    def __init__(self, ptr):
        super(ListXlsRanges, self).__init__(ptr)
        self._gtype = XlsRange

    def GetEnumerator(self)->'IEnumerator':
        """

        """
        ret = super(ListXlsRanges, self).GetEnumerator()
        ret._gtype = XlsRange
        return ret

