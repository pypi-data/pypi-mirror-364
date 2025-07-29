from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsName (  XlsObject, INamedRange, IXLSRange) :
    """Represents a named range or defined name in an Excel workbook.
    
    This class extends XlsObject and implements INamedRange and IXLSRange interfaces
    to provide functionality for working with named ranges, including accessing
    and manipulating range properties, formatting, and cell values.
    """
    @property

    def Comment(self)->'ICommentShape':
        """Gets the comment associated with the named range.
        
        Returns:
            ICommentShape: The comment object.
        """
        GetDllLibXls().XlsName_get_Comment.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Comment.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_Comment, self.Ptr)
        ret = None if intPtr==None else XlsComment(intPtr)
        return ret


    @property

    def RichText(self)->'IRichTextString':
        """Gets the rich text formatting for the named range.
        
        Returns:
            IRichTextString: The rich text formatting object.
        """
        GetDllLibXls().XlsName_get_RichText.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_RichText.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_RichText, self.Ptr)
        ret = None if intPtr==None else RichTextObject(intPtr)
        return ret


    @property

    def HtmlString(self)->str:
        """Gets and sets the HTML string which contains data and some formattings in this cell.
        
        Returns:
            str: The HTML string representation of the cell content.
        """
        GetDllLibXls().XlsName_get_HtmlString.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HtmlString.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_HtmlString, self.Ptr))
        return ret


    @HtmlString.setter
    def HtmlString(self, value:str):
        GetDllLibXls().XlsName_set_HtmlString.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsName_set_HtmlString, self.Ptr, value)

    @property
    def HasMerged(self)->bool:
        """Gets whether the named range contains merged cells.
        
        Returns:
            bool: True if the range contains merged cells; otherwise, False.
        """
        GetDllLibXls().XlsName_get_HasMerged.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HasMerged.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_HasMerged, self.Ptr)
        return ret

    @property

    def MergeArea(self)->'IXLSRange':
        """Gets the range that represents the merged area containing the named range.
        
        Returns:
            IXLSRange: The merged range.
        """
        GetDllLibXls().XlsName_get_MergeArea.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_MergeArea.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_MergeArea, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @property
    def IsWrapText(self)->bool:
        """Gets or sets whether text is wrapped within the cells in the named range.
        
        Returns:
            bool: True if text wrapping is enabled; otherwise, False.
        """
        GetDllLibXls().XlsName_get_IsWrapText.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_IsWrapText.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_IsWrapText, self.Ptr)
        return ret

    @IsWrapText.setter
    def IsWrapText(self, value:bool):
        GetDllLibXls().XlsName_set_IsWrapText.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsName_set_IsWrapText, self.Ptr, value)

    @property
    def HasExternalFormula(self)->bool:
        """Indicates if the current range has an external formula.
        
        Returns:
            bool: True if the range has an external formula; otherwise, False.
        """
        GetDllLibXls().XlsName_get_HasExternalFormula.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HasExternalFormula.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_HasExternalFormula, self.Ptr)
        return ret

    @property

    def IgnoreErrorOptions(self)->'IgnoreErrorType':
        """Gets or sets the error options to ignore for the named range.
        
        If the range is not a single cell, returns concatenated flags.
        
        Returns:
            IgnoreErrorType: The error options to ignore.
        """
        GetDllLibXls().XlsName_get_IgnoreErrorOptions.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_IgnoreErrorOptions.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsName_get_IgnoreErrorOptions, self.Ptr)
        objwraped = IgnoreErrorType(ret)
        return objwraped

    @IgnoreErrorOptions.setter
    def IgnoreErrorOptions(self, value:'IgnoreErrorType'):
        GetDllLibXls().XlsName_set_IgnoreErrorOptions.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsName_set_IgnoreErrorOptions, self.Ptr, value.value)

    @property

    def IsStringsPreserved(self)->bool:
        """Indicates whether all values in the range are preserved as strings.
        
        Returns:
            bool: True if values are preserved as strings; otherwise, False.
        """
        GetDllLibXls().XlsName_get_IsStringsPreserved.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_IsStringsPreserved.restype=c_bool
        return CallCFunction(GetDllLibXls().XlsName_get_IsStringsPreserved, self.Ptr)



    @IsStringsPreserved.setter
    def IsStringsPreserved(self, value:bool):
        GetDllLibXls().XlsName_set_IsStringsPreserved.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsName_set_IsStringsPreserved, self.Ptr, value)


    @property

    def BuiltInStyle(self)->BuiltInStyles:
        """Gets or sets the built-in style for the named range.
        
        Returns:
            BuiltInStyles: The built-in style.
        """
        GetDllLibXls().XlsName_get_BuiltInStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_BuiltInStyle.restype=c_int
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_BuiltInStyle, self.Ptr)
        ret = None if intPtr==None else BuiltInStyles(intPtr)
        return ret



    @BuiltInStyle.setter
    def BuiltInStyle(self, value:BuiltInStyles):
        GetDllLibXls().XlsName_set_BuiltInStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsName_set_BuiltInStyle, self.Ptr, value.value)


    @property

    def Hyperlinks(self)->'IHyperLinks':
        """Gets the hyperlinks collection for the named range.
        
        Returns:
            IHyperLinks: The collection of hyperlinks.
        """
        GetDllLibXls().XlsName_get_Hyperlinks.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Hyperlinks.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_Hyperlinks, self.Ptr)
        ret = None if intPtr==None else IHyperLinks(intPtr)
        return ret


    @dispatch

    def Activate(self ,scroll:bool)->IXLSRange:
        """Activates the named range and optionally scrolls to it.
        
        Args:
            scroll (bool): True to scroll the worksheet to display the range; otherwise, False.
            
        Returns:
            IXLSRange: The activated range.
        """
        
        GetDllLibXls().XlsName_Activate.argtypes=[c_void_p ,c_bool]
        GetDllLibXls().XlsName_Activate.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_Activate, self.Ptr, scroll)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch
    def Merge(self):
        """Merges all cells in the named range into a single cell.
        """
        GetDllLibXls().XlsName_Merge.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsName_Merge, self.Ptr)

    @dispatch

    def Merge(self ,clearCells:bool):
        """Merges all cells in the named range into a single cell with an option to clear contents.
        
        Args:
            clearCells (bool): True to clear the contents of the merged cells; otherwise, False.
        """
        
        GetDllLibXls().XlsName_MergeC.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibXls().XlsName_MergeC, self.Ptr, clearCells)

    def UnMerge(self):
        """Unmerges previously merged cells in the named range.
        
        This method separates a merged cell into individual cells.
        """
        GetDllLibXls().XlsName_UnMerge.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsName_UnMerge, self.Ptr)

    def FreezePanes(self):
        """Freezes panes at the position of the named range.
        
        This method locks rows and columns to keep them visible while scrolling.
        """
        GetDllLibXls().XlsName_FreezePanes.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsName_FreezePanes, self.Ptr)

    def ClearContents(self):
        """Clears the contents of the cells in the named range.
        
        This method removes values but leaves formatting intact.
        """
        GetDllLibXls().XlsName_ClearContents.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsName_ClearContents, self.Ptr)

    @dispatch

    def Clear(self ,option:ExcelClearOptions):
        """Clears specified aspects of the cells in the named range.
        
        Args:
            option (ExcelClearOptions): The options specifying what to clear.
        """
        enumoption:c_int = option.value

        GetDllLibXls().XlsName_Clear.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsName_Clear, self.Ptr, enumoption)

    @dispatch

    def Clear(self ,isClearFormat:bool):
        """Clears the cells in the named range with an option to clear formatting.
        
        Args:
            isClearFormat (bool): True to clear formatting; otherwise, False.
        """
        
        GetDllLibXls().XlsName_ClearI.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibXls().XlsName_ClearI, self.Ptr, isClearFormat)


    def Intersect(self ,range:'IXLSRange')->'IXLSRange':
        """Gets the range that represents the intersection of the named range and another range.
        
        Args:
            range (IXLSRange): The range to intersect with.
            
        Returns:
            IXLSRange: The range representing the intersection.
        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().XlsName_Intersect.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsName_Intersect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_Intersect, self.Ptr, intPtrrange)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def Merge(self ,range:IXLSRange)->IXLSRange:
        """Merges the named range with another range.
        
        Args:
            range (IXLSRange): The range to merge with.
            
        Returns:
            IXLSRange: The merged range.
        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().XlsName_MergeR.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsName_MergeR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_MergeR, self.Ptr, intPtrrange)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    def AutoFitRows(self):
        """Automatically adjusts the height of rows in the named range to fit their contents.
        """
        GetDllLibXls().XlsName_AutoFitRows.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsName_AutoFitRows, self.Ptr)

    def AutoFitColumns(self):
        """Automatically adjusts the width of columns in the named range to fit their contents.
        """
        GetDllLibXls().XlsName_AutoFitColumns.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsName_AutoFitColumns, self.Ptr)


    def AddComment(self)->'ICommentShape':
        """Adds a comment to the named range.
        
        Returns:
            ICommentShape: The newly added comment.
        """
        GetDllLibXls().XlsName_AddComment.argtypes=[c_void_p]
        GetDllLibXls().XlsName_AddComment.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_AddComment, self.Ptr)
        ret = None if intPtr==None else XlsComment(intPtr)
        return ret


    @dispatch
    def BorderAround(self):
        """Adds a border around the named range using default line style and color.
        
        This method applies a standard border around the outer edges of the named range.
        """
        GetDllLibXls().XlsName_BorderAround.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsName_BorderAround, self.Ptr)

    @dispatch

    def BorderAround(self ,borderLine:LineStyleType):
        """Adds a border around the named range with the specified line style.
        
        Args:
            borderLine (LineStyleType): The style of the border line.
        """
        enumborderLine:c_int = borderLine.value

        GetDllLibXls().XlsName_BorderAroundB.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsName_BorderAroundB, self.Ptr, enumborderLine)

    @dispatch

    def BorderAround(self ,borderLine:LineStyleType,borderColor:Color):
        """Adds a border around the named range with the specified line style and color.
        
        Args:
            borderLine (LineStyleType): The style of the border line.
            borderColor (Color): The color of the border.
        """
        enumborderLine:c_int = borderLine.value
        intPtrborderColor:c_void_p = borderColor.Ptr

        GetDllLibXls().XlsName_BorderAroundBB.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsName_BorderAroundBB, self.Ptr, enumborderLine,intPtrborderColor)

    @dispatch

    def BorderAround(self ,borderLine:LineStyleType,borderColor:ExcelColors):
        """Adds a border around the named range with the specified line style and Excel color.
        
        Args:
            borderLine (LineStyleType): The style of the border line.
            borderColor (ExcelColors): The Excel color of the border.
        """
        enumborderLine:c_int = borderLine.value
        enumborderColor:c_int = borderColor.value

        GetDllLibXls().XlsName_BorderAroundBB1.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsName_BorderAroundBB1, self.Ptr, enumborderLine,enumborderColor)

    @dispatch
    def BorderInside(self):
        """Adds inside borders to the named range using default line style and color.
        
        This method applies borders to the inner cell boundaries of the named range.
        """
        GetDllLibXls().XlsName_BorderInside.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsName_BorderInside, self.Ptr)

    @dispatch

    def BorderInside(self ,borderLine:LineStyleType):
        """Adds inside borders to the named range with the specified line style.
        
        Args:
            borderLine (LineStyleType): The style of the inside border lines.
        """
        enumborderLine:c_int = borderLine.value

        GetDllLibXls().XlsName_BorderInsideB.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsName_BorderInsideB, self.Ptr, enumborderLine)

    @dispatch

    def BorderInside(self ,borderLine:LineStyleType,borderColor:Color):
        """Adds inside borders to the named range with the specified line style and color.
        
        Args:
            borderLine (LineStyleType): The style of the inside border lines.
            borderColor (Color): The color of the inside borders.
        """
        enumborderLine:c_int = borderLine.value
        intPtrborderColor:c_void_p = borderColor.Ptr

        GetDllLibXls().XlsName_BorderInsideBB.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsName_BorderInsideBB, self.Ptr, enumborderLine,intPtrborderColor)

    @dispatch

    def BorderInside(self ,borderLine:LineStyleType,borderColor:ExcelColors):
        """Adds inside borders to the named range with the specified line style and Excel color.
        
        Args:
            borderLine (LineStyleType): The style of the inside border lines.
            borderColor (ExcelColors): The Excel color of the inside borders.
        """
        enumborderLine:c_int = borderLine.value
        enumborderColor:c_int = borderColor.value

        GetDllLibXls().XlsName_BorderInsideBB1.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsName_BorderInsideBB1, self.Ptr, enumborderLine,enumborderColor)

    def BorderNone(self):
        """Removes all borders from the named range.
        
        This method clears both outside and inside borders from the range.
        """
        GetDllLibXls().XlsName_BorderNone.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsName_BorderNone, self.Ptr)


    def CollapseGroup(self ,groupBy:'GroupByType'):
        """Collapses a group of rows or columns in the named range.
        
        Args:
            groupBy (GroupByType): Specifies whether to collapse by rows or columns.
        """
        enumgroupBy:c_int = groupBy.value

        GetDllLibXls().XlsName_CollapseGroup.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsName_CollapseGroup, self.Ptr, enumgroupBy)

    @dispatch

    def ExpandGroup(self ,groupBy:GroupByType):
        """Expands a collapsed group of rows or columns in the named range.
        
        Args:
            groupBy (GroupByType): Specifies whether to expand by rows or columns.
        """
        enumgroupBy:c_int = groupBy.value

        GetDllLibXls().XlsName_ExpandGroup.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsName_ExpandGroup, self.Ptr, enumgroupBy)

    @dispatch

    def ExpandGroup(self ,groupBy:GroupByType,flags:ExpandCollapseFlags):
        """Expands a collapsed group of rows or columns with additional options.
        
        Args:
            groupBy (GroupByType): Specifies whether to expand by rows or columns.
            flags (ExpandCollapseFlags): Additional flags to control the expand behavior.
        """
        enumgroupBy:c_int = groupBy.value
        enumflags:c_int = flags.value

        GetDllLibXls().XlsName_ExpandGroupGF.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsName_ExpandGroupGF, self.Ptr, enumgroupBy,enumflags)


    def GetEnumerator(self)->'IEnumerator':
        """Gets an enumerator that can be used to iterate through the cells in the named range.
        
        Returns:
            IEnumerator: An enumerator for iterating through the cells.
        """
        GetDllLibXls().XlsName_GetEnumerator.argtypes=[c_void_p]
        GetDllLibXls().XlsName_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_GetEnumerator, self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    @dispatch

    def Activate(self)->IXLSRange:
        """Activates the named range in the worksheet.
        
        This overload activates the range without scrolling the worksheet.
        
        Returns:
            IXLSRange: The activated range.
        """
        GetDllLibXls().XlsName_Activate1.argtypes=[c_void_p]
        GetDllLibXls().XlsName_Activate1.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_Activate1, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def Clone(self ,parent:SpireObject)->SpireObject:
        """Creates a copy of this named range with the specified parent object.
        
        Args:
            parent (SpireObject): The parent object for the cloned range.
            
        Returns:
            SpireObject: The cloned named range.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsName_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsName_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


#    @dispatch
#
#    def Clone(self ,parent:SpireObject,hashNewNames:'Dictionary2',book:XlsWorkbook)->IXLSRange:
#        """
#
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrhashNewNames:c_void_p = hashNewNames.Ptr
#        intPtrbook:c_void_p = book.Ptr
#
#        GetDllLibXls().XlsName_ClonePHB.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p]
#        GetDllLibXls().XlsName_ClonePHB.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsName_ClonePHB, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrbook)
#        ret = None if intPtr==None else XlsRange(intPtr)
#        return ret
#



    def ConvertFullRowColumnName(self ,version:'ExcelVersion'):
        """Converts the named range to a full row or column reference based on Excel version.
        
        This method adjusts the named range reference to cover entire rows or columns
        according to the specified Excel version's format.
        
        Args:
            version (ExcelVersion): The Excel version to use for the conversion.
        """
        enumversion:c_int = version.value

        GetDllLibXls().XlsName_ConvertFullRowColumnName.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsName_ConvertFullRowColumnName, self.Ptr, enumversion)


    def CopyTo(self ,destination:'IXLSRange')->'IXLSRange':
        """Copies the content and formatting of the named range to a destination range.
        
        Args:
            destination (IXLSRange): The destination range to copy to.
            
        Returns:
            IXLSRange: The destination range after the copy operation.
        """
        intPtrdestination:c_void_p = destination.Ptr

        GetDllLibXls().XlsName_CopyTo.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsName_CopyTo.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_CopyTo, self.Ptr, intPtrdestination)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


#    @dispatch
#
#    def FindAll(self ,findValue:TimeSpan)->ListCellRanges:
#        """
#
#        """
#        intPtrfindValue:c_void_p = findValue.Ptr
#
#        GetDllLibXls().XlsName_FindAll.argtypes=[c_void_p ,c_void_p]
#        GetDllLibXls().XlsName_FindAll.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsName_FindAll, self.Ptr, intPtrfindValue)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret


#    @dispatch
#
#    def FindAll(self ,findValue:DateTime)->ListCellRanges:
#        """
#
#        """
#        intPtrfindValue:c_void_p = findValue.Ptr
#
#        GetDllLibXls().XlsName_FindAllF.argtypes=[c_void_p ,c_void_p]
#        GetDllLibXls().XlsName_FindAllF.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsName_FindAllF, self.Ptr, intPtrfindValue)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret


#    @dispatch
#
#    def FindAll(self ,findValue:bool)->ListCellRanges:
#        """
#
#        """
#        
#        GetDllLibXls().XlsName_FindAllF1.argtypes=[c_void_p ,c_bool]
#        GetDllLibXls().XlsName_FindAllF1.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsName_FindAllF1, self.Ptr, findValue)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret


#    @dispatch
#
#    def FindAll(self ,findValue:float,flags:FindType)->ListCellRanges:
#        """
#
#        """
#        enumflags:c_int = flags.value
#
#        GetDllLibXls().XlsName_FindAllFF.argtypes=[c_void_p ,c_double,c_int]
#        GetDllLibXls().XlsName_FindAllFF.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsName_FindAllFF, self.Ptr, findValue,enumflags)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret


#    @dispatch
#
#    def FindAll(self ,findValue:str,flags:FindType)->List1:
#        """
#
#        """
#        enumflags:c_int = flags.value
#
#        GetDllLibXls().XlsName_FindAllFF1.argtypes=[c_void_p ,c_void_p,c_int]
#        GetDllLibXls().XlsName_FindAllFF1.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsName_FindAllFF1, self.Ptr, findValue,enumflags)
#        ret = None if intPtr==None else List1(intPtr)
#        return ret
#


    @dispatch

    def FindFirst(self ,findValue:TimeSpan)->IXLSRange:
        """Finds the first cell in the named range containing the specified TimeSpan value.
        
        Args:
            findValue (TimeSpan): The TimeSpan value to search for.
            
        Returns:
            IXLSRange: The first cell containing the specified value, or None if not found.
        """
        intPtrfindValue:c_void_p = findValue.Ptr

        GetDllLibXls().XlsName_FindFirst.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsName_FindFirst.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_FindFirst, self.Ptr, intPtrfindValue)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def FindFirst(self ,findValue:DateTime)->IXLSRange:
        """Finds the first cell in the named range containing the specified DateTime value.
        
        Args:
            findValue (DateTime): The DateTime value to search for.
            
        Returns:
            IXLSRange: The first cell containing the specified value, or None if not found.
        """
        intPtrfindValue:c_void_p = findValue.Ptr

        GetDllLibXls().XlsName_FindFirstF.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsName_FindFirstF.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_FindFirstF, self.Ptr, intPtrfindValue)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def FindFirst(self ,findValue:bool)->IXLSRange:
        """Finds the first cell in the named range containing the specified boolean value.
        
        Args:
            findValue (bool): The boolean value to search for.
            
        Returns:
            IXLSRange: The first cell containing the specified value, or None if not found.
        """
        
        GetDllLibXls().XlsName_FindFirstF1.argtypes=[c_void_p ,c_bool]
        GetDllLibXls().XlsName_FindFirstF1.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_FindFirstF1, self.Ptr, findValue)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def FindFirst(self ,findValue:float,flags:FindType)->IXLSRange:
        """Finds the first cell in the named range containing the specified numeric value.
        
        Args:
            findValue (float): The numeric value to search for.
            flags (FindType): Search options to control how the value is matched.
            
        Returns:
            IXLSRange: The first cell containing the specified value, or None if not found.
        """
        enumflags:c_int = flags.value

        GetDllLibXls().XlsName_FindFirstFF.argtypes=[c_void_p ,c_double,c_int]
        GetDllLibXls().XlsName_FindFirstFF.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_FindFirstFF, self.Ptr, findValue,enumflags)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def FindFirst(self ,findValue:str,flags:FindType)->IXLSRange:
        """Finds the first cell in the named range containing the specified string value.
        
        Args:
            findValue (str): The string value to search for.
            flags (FindType): Search options to control how the string is matched.
            
        Returns:
            IXLSRange: The first cell containing the specified value, or None if not found.
        """
        enumflags:c_int = flags.value

        GetDllLibXls().XlsName_FindFirstFF1.argtypes=[c_void_p ,c_void_p,c_int]
        GetDllLibXls().XlsName_FindFirstFF1.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_FindFirstFF1, self.Ptr, findValue,enumflags)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def SetIndex(self ,index:int):
        """Sets the index of the named range in the collection.
        
        This method changes the position of the named range in the collection.
        
        Args:
            index (int): The new index position for the named range.
        """
        
        GetDllLibXls().XlsName_SetIndex.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsName_SetIndex, self.Ptr, index)

    @dispatch

    def SetIndex(self ,index:int,bRaiseEvent:bool):
        """Sets the index of the named range with an option to raise an event.
        
        This method changes the position of the named range in the collection
        and optionally raises a notification event.
        
        Args:
            index (int): The new index position for the named range.
            bRaiseEvent (bool): True to raise an event after setting the index; False otherwise.
        """
        
        GetDllLibXls().XlsName_SetIndexIB.argtypes=[c_void_p ,c_int,c_bool]
        CallCFunction(GetDllLibXls().XlsName_SetIndexIB, self.Ptr, index,bRaiseEvent)

#
#    def ExportDataTable(self ,options:'ExportTableOptions')->'DataTable':
#        """
#
#        """
#        intPtroptions:c_void_p = options.Ptr
#
#        GetDllLibXls().XlsName_ExportDataTable.argtypes=[c_void_p ,c_void_p]
#        GetDllLibXls().XlsName_ExportDataTable.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsName_ExportDataTable, self.Ptr, intPtroptions)
#        ret = None if intPtr==None else DataTable(intPtr)
#        return ret
#


    @property
    def Index(self)->int:
        """Gets the index of the named range in the collection.
        
        Returns:
            int: The zero-based index of the named range.
        """
        GetDllLibXls().XlsName_get_Index.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Index.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsName_get_Index, self.Ptr)
        return ret

    @property

    def Name(self)->str:
        """Gets or sets the name of the named range.
        
        Returns:
            str: The name of the named range.
        """
        GetDllLibXls().XlsName_get_Name.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_Name, self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        """Sets the name of the named range.
        
        Args:
            value (str): The new name to assign to the named range.
        """
        GetDllLibXls().XlsName_set_Name.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsName_set_Name, self.Ptr, value)

    @property

    def NameLocal(self)->str:
        """Gets or sets the localized name of the named range.
        
        Returns:
            str: The localized name of the named range.
        """
        GetDllLibXls().XlsName_get_NameLocal.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_NameLocal.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_NameLocal, self.Ptr))
        return ret


    @NameLocal.setter
    def NameLocal(self, value:str):
        """Sets the localized name of the named range.
        
        Args:
            value (str): The new localized name to assign to the named range.
        """
        GetDllLibXls().XlsName_set_NameLocal.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsName_set_NameLocal, self.Ptr, value)

    @property

    def RefersToRange(self)->'IXLSRange':
        """Gets or sets the cell range that this named range refers to.
        
        Returns:
            IXLSRange: The cell range that this named range refers to.
        """
        GetDllLibXls().XlsName_get_RefersToRange.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_RefersToRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_RefersToRange, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @RefersToRange.setter
    def RefersToRange(self, value:'IXLSRange'):
        """Sets the cell range that this named range refers to.
        
        Args:
            value (IXLSRange): The cell range to associate with this named range.
        """
        GetDllLibXls().XlsName_set_RefersToRange.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsName_set_RefersToRange, self.Ptr, value.Ptr)

    @property

    def Value(self)->str:
        """Gets or sets the value of the named range as a string.
        
        Returns:
            str: The value of the named range.
        """
        GetDllLibXls().XlsName_get_Value.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Value.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_Value, self.Ptr))
        return ret


    @Value.setter
    def Value(self, value:str):
        """Sets the value of the named range.
        
        Args:
            value (str): The value to set for the named range.
        """
        GetDllLibXls().XlsName_set_Value.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsName_set_Value, self.Ptr, value)

    @property
    def Visible(self)->bool:
        """Gets or sets whether the named range is visible in the workbook.
        
        Returns:
            bool: True if the named range is visible; otherwise, False.
        """
        GetDllLibXls().XlsName_get_Visible.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Visible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_Visible, self.Ptr)
        return ret

    @Visible.setter
    def Visible(self, value:bool):
        """Sets whether the named range is visible in the workbook.
        
        Args:
            value (bool): True to make the named range visible; False to hide it.
        """
        GetDllLibXls().XlsName_set_Visible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsName_set_Visible, self.Ptr, value)

    @property
    def IsLocal(self)->bool:
        """Gets whether the named range is local to a specific worksheet.
        
        Returns:
            bool: True if the named range is local to a worksheet; False if it's workbook-level.
        """
        GetDllLibXls().XlsName_get_IsLocal.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_IsLocal.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_IsLocal, self.Ptr)
        return ret

    @property

    def ValueR1C1(self)->str:
        """Gets the formula of the named range in R1C1 notation.
        
        Returns:
            str: The formula in R1C1 notation.
        """
        GetDllLibXls().XlsName_get_ValueR1C1.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_ValueR1C1.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_ValueR1C1, self.Ptr))
        return ret


    @property

    def Worksheet(self)->'IWorksheet':
        """Gets the worksheet containing the named range.
        
        Returns:
            IWorksheet: The worksheet that contains the named range.
        """
        GetDllLibXls().XlsName_get_Worksheet.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Worksheet.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_Worksheet, self.Ptr)
        ret = None if intPtr==None else XlsWorksheet(intPtr)
        return ret


    @property

    def Scope(self)->str:
        """Gets the scope of the named range (workbook or worksheet level).
        
        Returns:
            str: The scope of the named range.
        """
        GetDllLibXls().XlsName_get_Scope.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Scope.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_Scope, self.Ptr))
        return ret


    def Delete(self):
        """Deletes the named range from the workbook.
        
        This method removes the named range definition but does not affect the cells it refers to.
        """
        GetDllLibXls().XlsName_Delete.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsName_Delete, self.Ptr)

    @property

    def RangeAddress(self)->str:
        """Gets the address of the named range in A1 notation.
        
        Returns:
            str: The address of the named range in A1 notation.
        """
        GetDllLibXls().XlsName_get_RangeAddress.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_RangeAddress.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_RangeAddress, self.Ptr))
        return ret


    @property

    def RangeAddressLocal(self)->str:
        """Gets the localized address of the named range in A1 notation.
        
        Returns:
            str: The localized address of the named range in A1 notation.
        """
        GetDllLibXls().XlsName_get_RangeAddressLocal.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_RangeAddressLocal.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_RangeAddressLocal, self.Ptr))
        return ret


    @property

    def RangeGlobalAddress(self)->str:
        """Gets the global address of the named range.
        
        Returns:
            str: The global address of the named range, including the worksheet name.
        """
        GetDllLibXls().XlsName_get_RangeGlobalAddress.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_RangeGlobalAddress.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_RangeGlobalAddress, self.Ptr))
        return ret


    @property

    def RangeGlobalAddress2007(self)->str:
        """Gets the global address of the named range in Excel 2007 format.
        
        Returns:
            str: The global address of the named range in Excel 2007 format.
        """
        GetDllLibXls().XlsName_get_RangeGlobalAddress2007.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_RangeGlobalAddress2007.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_RangeGlobalAddress2007, self.Ptr))
        return ret


    @property

    def RangeR1C1Address(self)->str:
        """Gets the address of the named range in R1C1 notation.
        
        Returns:
            str: The address of the named range in R1C1 notation.
        """
        GetDllLibXls().XlsName_get_RangeR1C1Address.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_RangeR1C1Address.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_RangeR1C1Address, self.Ptr))
        return ret


    @property

    def RangeR1C1AddressLocal(self)->str:
        """Gets the localized address of the named range in R1C1 notation.
        
        Returns:
            str: The localized address of the named range in R1C1 notation.
        """
        GetDllLibXls().XlsName_get_RangeR1C1AddressLocal.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_RangeR1C1AddressLocal.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_RangeR1C1AddressLocal, self.Ptr))
        return ret


    @property
    def BooleanValue(self)->bool:
        """Gets or sets the boolean value of the named range.
        
        Returns:
            bool: The boolean value.
        """
        GetDllLibXls().XlsName_get_BooleanValue.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_BooleanValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_BooleanValue, self.Ptr)
        return ret

    @BooleanValue.setter
    def BooleanValue(self, value:bool):
        """Sets the boolean value of the named range.
        
        Args:
            value (bool): The boolean value to set.
        """
        GetDllLibXls().XlsName_set_BooleanValue.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsName_set_BooleanValue, self.Ptr, value)

    @property

    def Borders(self)->'IBorders':
        """Gets the borders collection for the named range.
        
        Returns:
            IBorders: The collection of borders.
        """
        GetDllLibXls().XlsName_get_Borders.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Borders.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_Borders, self.Ptr)
        ret = None if intPtr==None else XlsBordersCollection(intPtr)
        return ret


#    @property
#
#    def Cells(self)->'ListCellRanges':
#        """
#
#        """
#        GetDllLibXls().XlsName_get_Cells.argtypes=[c_void_p]
#        GetDllLibXls().XlsName_get_Cells.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsName_get_Cells, self.Ptr)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret
#


#    @property
#
#    def CellList(self)->'List1':
#        """
#
#        """
#        GetDllLibXls().XlsName_get_CellList.argtypes=[c_void_p]
#        GetDllLibXls().XlsName_get_CellList.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsName_get_CellList, self.Ptr)
#        ret = None if intPtr==None else List1(intPtr)
#        return ret
#


    @property
    def Column(self)->int:
        """Gets the column index of the first cell in the named range.
        
        Returns:
            int: The zero-based column index.
        """
        GetDllLibXls().XlsName_get_Column.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Column.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsName_get_Column, self.Ptr)
        return ret

    @property
    def ColumnGroupLevel(self)->int:
        """Gets the outline level for columns in the named range.
        
        Returns:
            int: The column group level.
        """
        GetDllLibXls().XlsName_get_ColumnGroupLevel.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_ColumnGroupLevel.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsName_get_ColumnGroupLevel, self.Ptr)
        return ret

    @property
    def ColumnWidth(self)->float:
        """Gets or sets the width of columns in the named range.
        
        Returns:
            float: The column width in characters.
        """
        GetDllLibXls().XlsName_get_ColumnWidth.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_ColumnWidth.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsName_get_ColumnWidth, self.Ptr)
        return ret

    @ColumnWidth.setter
    def ColumnWidth(self, value:float):
        """Sets the width of columns in the named range.
        
        Args:
            value (float): The column width in characters.
        """
        GetDllLibXls().XlsName_set_ColumnWidth.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsName_set_ColumnWidth, self.Ptr, value)

    @property
    def Count(self)->int:
        """Gets the number of cells in the named range.
        
        Returns:
            int: The count of cells.
        """
        GetDllLibXls().XlsName_get_Count.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsName_get_Count, self.Ptr)
        return ret

    @property

    def DateTimeValue(self)->'DateTime':
        """Gets or sets the date/time value of the named range.
        
        Returns:
            DateTime: The date/time value.
        """
        GetDllLibXls().XlsName_get_DateTimeValue.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_DateTimeValue.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_DateTimeValue, self.Ptr)
        ret = None if intPtr==None else DateTime(intPtr)
        return ret


    @DateTimeValue.setter
    def DateTimeValue(self, value:'DateTime'):
        """Sets the date/time value of the named range.
        
        Args:
            value (DateTime): The date/time value to set.
        """
        GetDllLibXls().XlsName_set_DateTimeValue.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsName_set_DateTimeValue, self.Ptr, value.Ptr)

    @property

    def NumberText(self)->str:
        """Gets the text representation of the numeric value in the named range.
        
        Returns:
            str: The text representation of the numeric value.
        """
        GetDllLibXls().XlsName_get_NumberText.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_NumberText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_NumberText, self.Ptr))
        return ret


    @property

    def EndCell(self)->'IXLSRange':
        """Gets the cell at the bottom-right corner of the named range.
        
        Returns:
            IXLSRange: The end cell of the named range.
        """
        GetDllLibXls().XlsName_get_EndCell.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_EndCell.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_EndCell, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @property

    def EntireColumn(self)->'IXLSRange':
        """Gets a range representing all cells in the columns of the named range.
        
        Returns:
            IXLSRange: The range representing the entire columns.
        """
        GetDllLibXls().XlsName_get_EntireColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_EntireColumn.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_EntireColumn, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @property

    def EntireRow(self)->'IXLSRange':
        """Gets a range representing all cells in the rows of the named range.
        
        Returns:
            IXLSRange: The range representing the entire rows.
        """
        GetDllLibXls().XlsName_get_EntireRow.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_EntireRow.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_EntireRow, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @property

    def ErrorValue(self)->str:
        """Gets or sets the error value of the named range.
        
        Returns:
            str: The error value as a string.
        """
        GetDllLibXls().XlsName_get_ErrorValue.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_ErrorValue.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_ErrorValue, self.Ptr))
        return ret


    @ErrorValue.setter
    def ErrorValue(self, value:str):
        """Sets the error value of the named range.
        
        Args:
            value (str): The error value to set.
        """
        GetDllLibXls().XlsName_set_ErrorValue.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsName_set_ErrorValue, self.Ptr, value)

    @property

    def Formula(self)->str:
        """Gets or sets the formula of the named range in A1 notation.
        
        Returns:
            str: The formula string in A1 notation.
        """
        GetDllLibXls().XlsName_get_Formula.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Formula.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_Formula, self.Ptr))
        return ret


    @Formula.setter
    def Formula(self, value:str):
        """Sets the formula of the named range in A1 notation.
        
        Args:
            value (str): The formula string in A1 notation.
        """
        GetDllLibXls().XlsName_set_Formula.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsName_set_Formula, self.Ptr, value)

    @property

    def FormulaArray(self)->str:
        """Gets or sets the array formula of the named range.
        
        Returns:
            str: The array formula string.
        """
        GetDllLibXls().XlsName_get_FormulaArray.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_FormulaArray.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_FormulaArray, self.Ptr))
        return ret


    @FormulaArray.setter
    def FormulaArray(self, value:str):
        """Sets the array formula of the named range.
        
        Args:
            value (str): The array formula string to set.
        """
        GetDllLibXls().XlsName_set_FormulaArray.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsName_set_FormulaArray, self.Ptr, value)

    @property

    def FormulaArrayR1C1(self)->str:
        """Gets or sets the array formula of the named range in R1C1 notation.
        
        Returns:
            str: The array formula string in R1C1 notation.
        """
        GetDllLibXls().XlsName_get_FormulaArrayR1C1.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_FormulaArrayR1C1.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_FormulaArrayR1C1, self.Ptr))
        return ret


    @FormulaArrayR1C1.setter
    def FormulaArrayR1C1(self, value:str):
        """Sets the array formula of the named range in R1C1 notation.
        
        Args:
            value (str): The array formula string in R1C1 notation to set.
        """
        GetDllLibXls().XlsName_set_FormulaArrayR1C1.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsName_set_FormulaArrayR1C1, self.Ptr, value)

    @property
    def IsFormulaHidden(self)->bool:
        """Gets or sets whether the formula in the named range is hidden.
        
        Returns:
            bool: True if the formula is hidden; otherwise, False.
        """
        GetDllLibXls().XlsName_get_IsFormulaHidden.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_IsFormulaHidden.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_IsFormulaHidden, self.Ptr)
        return ret

    @IsFormulaHidden.setter
    def IsFormulaHidden(self, value:bool):
        """Sets whether the formula in the named range is hidden.
        
        Args:
            value (bool): True to hide the formula; False to show it.
        """
        GetDllLibXls().XlsName_set_IsFormulaHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsName_set_IsFormulaHidden, self.Ptr, value)

    @property

    def FormulaDateTime(self)->'DateTime':
        """Gets or sets the DateTime value of a formula in the named range.
        
        Returns:
            DateTime: The DateTime value of the formula.
        """
        GetDllLibXls().XlsName_get_FormulaDateTime.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_FormulaDateTime.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_FormulaDateTime, self.Ptr)
        ret = None if intPtr==None else DateTime(intPtr)
        return ret


    @FormulaDateTime.setter
    def FormulaDateTime(self, value:'DateTime'):
        """Sets the DateTime value of a formula in the named range.
        
        Args:
            value (DateTime): The DateTime value to set for the formula.
        """
        GetDllLibXls().XlsName_set_FormulaDateTime.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsName_set_FormulaDateTime, self.Ptr, value.Ptr)

    @property

    def FormulaR1C1(self)->str:
        """Gets or sets the formula of the named range in R1C1 notation.
        
        Returns:
            str: The formula string in R1C1 notation.
        """
        GetDllLibXls().XlsName_get_FormulaR1C1.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_FormulaR1C1.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_FormulaR1C1, self.Ptr))
        return ret


    @FormulaR1C1.setter
    def FormulaR1C1(self, value:str):
        """Sets the formula of the named range in R1C1 notation.
        
        Args:
            value (str): The formula string in R1C1 notation to set.
        """
        GetDllLibXls().XlsName_set_FormulaR1C1.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsName_set_FormulaR1C1, self.Ptr, value)

    @property
    def FormulaBoolValue(self)->bool:
        """Gets or sets the boolean value of a formula in the named range.
        
        Returns:
            bool: The boolean value of the formula.
        """
        GetDllLibXls().XlsName_get_FormulaBoolValue.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_FormulaBoolValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_FormulaBoolValue, self.Ptr)
        return ret

    @FormulaBoolValue.setter
    def FormulaBoolValue(self, value:bool):
        """Sets the boolean value of a formula in the named range.
        
        Args:
            value (bool): The boolean value to set for the formula.
        """
        GetDllLibXls().XlsName_set_FormulaBoolValue.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsName_set_FormulaBoolValue, self.Ptr, value)

    @property

    def FormulaErrorValue(self)->str:
        """Gets or sets the error value of a formula in the named range.
        
        Returns:
            str: The error value of the formula as a string.
        """
        GetDllLibXls().XlsName_get_FormulaErrorValue.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_FormulaErrorValue.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_FormulaErrorValue, self.Ptr))
        return ret


    @FormulaErrorValue.setter
    def FormulaErrorValue(self, value:str):
        """Sets the error value of a formula in the named range.
        
        Args:
            value (str): The error value to set for the formula.
        """
        GetDllLibXls().XlsName_set_FormulaErrorValue.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsName_set_FormulaErrorValue, self.Ptr, value)

    @property
    def HasDataValidation(self)->bool:
        """Gets whether the named range has data validation rules applied.
        
        Returns:
            bool: True if the named range has data validation; otherwise, False.
        """
        GetDllLibXls().XlsName_get_HasDataValidation.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HasDataValidation.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_HasDataValidation, self.Ptr)
        return ret

    @property
    def HasBoolean(self)->bool:
        """Gets whether the named range contains a boolean value.
        
        Returns:
            bool: True if the named range contains a boolean value; otherwise, False.
        """
        GetDllLibXls().XlsName_get_HasBoolean.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HasBoolean.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_HasBoolean, self.Ptr)
        return ret

    @property
    def HasDateTime(self)->bool:
        """Gets whether the named range contains a DateTime value.
        
        Returns:
            bool: True if the named range contains a DateTime value; otherwise, False.
        """
        GetDllLibXls().XlsName_get_HasDateTime.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HasDateTime.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_HasDateTime, self.Ptr)
        return ret

    @property
    def HasFormula(self)->bool:
        """Gets whether the named range contains a formula.
        
        Returns:
            bool: True if the named range contains a formula; otherwise, False.
        """
        GetDllLibXls().XlsName_get_HasFormula.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HasFormula.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_HasFormula, self.Ptr)
        return ret

    @property
    def HasFormulaArray(self)->bool:
        """Gets whether the named range has an array formula.
        
        Returns:
            bool: True if the named range has an array formula; otherwise, False.
        """
        GetDllLibXls().XlsName_get_HasFormulaArray.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HasFormulaArray.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_HasFormulaArray, self.Ptr)
        return ret

    @property
    def HasFormulaDateTime(self)->bool:
        """Gets whether the named range has a date/time formula value.
        
        Returns:
            bool: True if the named range has a date/time formula value; otherwise, False.
        """
        GetDllLibXls().XlsName_get_HasFormulaDateTime.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HasFormulaDateTime.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_HasFormulaDateTime, self.Ptr)
        return ret

    @property
    def HasFormulaNumberValue(self)->bool:
        """Gets whether the named range has a numeric formula value.
        
        Returns:
            bool: True if the named range has a numeric formula value; otherwise, False.
        """
        GetDllLibXls().XlsName_get_HasFormulaNumberValue.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HasFormulaNumberValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_HasFormulaNumberValue, self.Ptr)
        return ret

    @property
    def HasFormulaStringValue(self)->bool:
        """Gets whether the named range has a string formula value.
        
        Returns:
            bool: True if the named range has a string formula value; otherwise, False.
        """
        GetDllLibXls().XlsName_get_HasFormulaStringValue.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HasFormulaStringValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_HasFormulaStringValue, self.Ptr)
        return ret

    @property
    def HasNumber(self)->bool:
        """Gets whether the named range has a numeric value.
        
        Returns:
            bool: True if the named range has a numeric value; otherwise, False.
        """
        GetDllLibXls().XlsName_get_HasNumber.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HasNumber.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_HasNumber, self.Ptr)
        return ret

    @property
    def HasRichText(self)->bool:
        """Gets whether the named range has rich text content.
        
        Returns:
            bool: True if the named range has rich text content; otherwise, False.
        """
        GetDllLibXls().XlsName_get_HasRichText.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HasRichText.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_HasRichText, self.Ptr)
        return ret

    @property
    def HasString(self)->bool:
        """Gets whether the named range has a string value.
        
        Returns:
            bool: True if the named range has a string value; otherwise, False.
        """
        GetDllLibXls().XlsName_get_HasString.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HasString.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_HasString, self.Ptr)
        return ret

    @property
    def HasStyle(self)->bool:
        """Gets whether the named range has a style applied.
        
        Returns:
            bool: True if the named range has a style applied; otherwise, False.
        """
        GetDllLibXls().XlsName_get_HasStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HasStyle.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_HasStyle, self.Ptr)
        return ret

    @property

    def HorizontalAlignment(self)->'HorizontalAlignType':
        """Gets or sets the horizontal alignment of the named range.
        
        Returns:
            HorizontalAlignType: The horizontal alignment setting.
        """
        GetDllLibXls().XlsName_get_HorizontalAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HorizontalAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsName_get_HorizontalAlignment, self.Ptr)
        objwraped = HorizontalAlignType(ret)
        return objwraped

    @HorizontalAlignment.setter
    def HorizontalAlignment(self, value:'HorizontalAlignType'):
        """Sets the horizontal alignment of the named range.
        
        Args:
            value (HorizontalAlignType): The horizontal alignment setting to apply.
        """
        GetDllLibXls().XlsName_set_HorizontalAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsName_set_HorizontalAlignment, self.Ptr, value.value)

    @property
    def IndentLevel(self)->int:
        """Gets or sets the indent level for the named range.
        
        Returns:
            int: The indent level value.
        """
        GetDllLibXls().XlsName_get_IndentLevel.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_IndentLevel.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsName_get_IndentLevel, self.Ptr)
        return ret

    @IndentLevel.setter
    def IndentLevel(self, value:int):
        """Sets the indent level for the named range.
        
        Args:
            value (int): The indent level to set.
        """
        GetDllLibXls().XlsName_set_IndentLevel.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsName_set_IndentLevel, self.Ptr, value)

    @property
    def IsBlank(self)->bool:
        """Gets whether the named range contains blank cells.
        
        Returns:
            bool: True if the named range contains blank cells; otherwise, False.
        """
        GetDllLibXls().XlsName_get_IsBlank.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_IsBlank.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_IsBlank, self.Ptr)
        return ret

    @property
    def IsBuiltIn(self)->bool:
        """Gets whether the named range is a built-in name.
        
        Returns:
            bool: True if the named range is a built-in name; otherwise, False.
        """
        GetDllLibXls().XlsName_get_IsBuiltIn.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_IsBuiltIn.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_IsBuiltIn, self.Ptr)
        return ret

    @IsBuiltIn.setter
    def IsBuiltIn(self, value:bool):
        """Sets whether the named range is a built-in name.
        
        Args:
            value (bool): True to mark the named range as built-in; False otherwise.
        """
        GetDllLibXls().XlsName_set_IsBuiltIn.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsName_set_IsBuiltIn, self.Ptr, value)

    @property
    def IsExternName(self)->bool:
        """Gets whether the named range is an external name.
        
        Returns:
            bool: True if the named range is an external name; otherwise, False.
        """
        GetDllLibXls().XlsName_get_IsExternName.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_IsExternName.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_IsExternName, self.Ptr)
        return ret

    @property
    def IsFunction(self)->bool:
        """Gets whether the named range is a function.
        
        Returns:
            bool: True if the named range is a function; otherwise, False.
        """
        GetDllLibXls().XlsName_get_IsFunction.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_IsFunction.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_IsFunction, self.Ptr)
        return ret

    @IsFunction.setter
    def IsFunction(self, value:bool):
        """Sets whether the named range is a function.
        
        Args:
            value (bool): True to make the named range a function; False otherwise.
        """
        GetDllLibXls().XlsName_set_IsFunction.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsName_set_IsFunction, self.Ptr, value)

    @property
    def HasError(self)->bool:
        """Gets whether the named range has an error.
        
        Returns:
            bool: True if the named range has an error; otherwise, False.
        """
        GetDllLibXls().XlsName_get_HasError.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HasError.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_HasError, self.Ptr)
        return ret

    @property
    def IsGroupedByColumn(self)->bool:
        """Gets whether the named range is grouped by columns.
        
        Returns:
            bool: True if the named range is grouped by columns; otherwise, False.
        """
        GetDllLibXls().XlsName_get_IsGroupedByColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_IsGroupedByColumn.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_IsGroupedByColumn, self.Ptr)
        return ret

    @property
    def IsGroupedByRow(self)->bool:
        """Gets whether the named range is grouped by rows.
        
        Returns:
            bool: True if the named range is grouped by rows; otherwise, False.
        """
        GetDllLibXls().XlsName_get_IsGroupedByRow.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_IsGroupedByRow.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_IsGroupedByRow, self.Ptr)
        return ret

    @property
    def IsInitialized(self)->bool:
        """Gets whether the named range is initialized.
        
        Returns:
            bool: True if the named range is initialized; otherwise, False.
        """
        GetDllLibXls().XlsName_get_IsInitialized.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_IsInitialized.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_IsInitialized, self.Ptr)
        return ret

    @property
    def LastColumn(self)->int:
        """Gets the index of the last column of the named range.
        
        Returns:
            int: The index of the last column of the named range.
        """
        GetDllLibXls().XlsName_get_LastColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_LastColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsName_get_LastColumn, self.Ptr)
        return ret

    @LastColumn.setter
    def LastColumn(self, value:int):
        """Sets the index of the last column of the named range.
        
        Args:
            value (int): The index of the last column of the named range.
        """
        GetDllLibXls().XlsName_set_LastColumn.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsName_set_LastColumn, self.Ptr, value)

    @property
    def LastRow(self)->int:
        """Gets the index of the last row of the named range.
        
        Returns:
            int: The index of the last row of the named range.
        """
        GetDllLibXls().XlsName_get_LastRow.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_LastRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsName_get_LastRow, self.Ptr)
        return ret

    @LastRow.setter
    def LastRow(self, value:int):
        """Sets the index of the last row of the named range.
        
        Args:
            value (int): The index of the last row of the named range.
        """
        GetDllLibXls().XlsName_set_LastRow.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsName_set_LastRow, self.Ptr, value)

    @property
    def NumberValue(self)->float:
        """Gets the numeric value of the named range.
        
        Returns:
            float: The numeric value of the named range.
        """
        GetDllLibXls().XlsName_get_NumberValue.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_NumberValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsName_get_NumberValue, self.Ptr)
        return ret

    @NumberValue.setter
    def NumberValue(self, value:float):
        """Sets the numeric value of the named range.
        
        Args:
            value (float): The numeric value to set.
        """
        GetDllLibXls().XlsName_set_NumberValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsName_set_NumberValue, self.Ptr, value)

    @property
    def NumberFormat(self)->str:
        """Gets the number format string of the named range.
        
        Returns:
            str: The number format string of the named range.
        """
        GetDllLibXls().XlsName_get_NumberFormat.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_NumberFormat.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_NumberFormat, self.Ptr))
        return ret

    @NumberFormat.setter
    def NumberFormat(self, value:str):
        """Sets the number format string of the named range.
        
        Args:
            value (str): The number format string to set.
        """
        GetDllLibXls().XlsName_set_NumberFormat.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsName_set_NumberFormat, self.Ptr, value)

    @property
    def Row(self)->int:
        """Gets the index of the first row of the named range.
        
        Returns:
            int: The index of the first row of the named range.
        """
        GetDllLibXls().XlsName_get_Row.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Row.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsName_get_Row, self.Ptr)
        return ret

    @property
    def RowGroupLevel(self)->int:
        """Gets the outline level of the row in the named range.
        
        Returns:
            int: The outline level of the row in the named range.
        """
        GetDllLibXls().XlsName_get_RowGroupLevel.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_RowGroupLevel.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsName_get_RowGroupLevel, self.Ptr)
        return ret

    @property
    def RowHeight(self)->float:
        """Gets the height of the row in the named range.
        
        Returns:
            float: The height of the row in the named range.
        """
        GetDllLibXls().XlsName_get_RowHeight.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_RowHeight.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsName_get_RowHeight, self.Ptr)
        return ret

    @RowHeight.setter
    def RowHeight(self, value:float):
        """Sets the height of the row in the named range.
        
        Args:
            value (float): The height to set.
        """
        GetDllLibXls().XlsName_set_RowHeight.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsName_set_RowHeight, self.Ptr, value)

    @property
    def Rows(self)->ListXlsRanges:
        """Gets the collection of rows in the named range.
        
        Returns:
            ListXlsRanges: The collection of rows in the named range.
        """
        GetDllLibXls().XlsName_get_Rows.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Rows.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_Rows, self.Ptr)
        ret = None if intPtr==None else ListXlsRanges(intPtr)
        return ret

    @property
    def Columns(self)->ListXlsRanges:
        """Gets the collection of columns in the named range.
        
        Returns:
            ListXlsRanges: The collection of columns in the named range.
        """
        GetDllLibXls().XlsName_get_Columns.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Columns.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_Columns, self.Ptr)
        ret = None if intPtr==None else ListXlsRanges(intPtr)
        return ret

    @property
    def Style(self)->'IStyle':
        """Gets the style applied to the named range.
        
        Returns:
            IStyle: The style applied to the named range.
        """
        GetDllLibXls().XlsName_get_Style.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Style.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_Style, self.Ptr)
        ret = None if intPtr==None else CellStyle(intPtr)
        return ret

    @Style.setter
    def Style(self, value:'IStyle'):
        """Sets the style applied to the named range.
        
        Args:
            value (IStyle): The style to apply.
        """
        GetDllLibXls().XlsName_set_Style.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsName_set_Style, self.Ptr, value.Ptr)

    @property
    def CellStyleName(self)->str:
        """Gets the name of the cell style applied to the named range.
        
        Returns:
            str: The name of the cell style applied to the named range.
        """
        GetDllLibXls().XlsName_get_CellStyleName.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_CellStyleName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_CellStyleName, self.Ptr))
        return ret

    @CellStyleName.setter
    def CellStyleName(self, value:str):
        """Sets the name of the cell style applied to the named range.
        
        Args:
            value (str): The name of the cell style to apply.
        """
        GetDllLibXls().XlsName_set_CellStyleName.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsName_set_CellStyleName, self.Ptr, value)

    @property
    def Text(self)->str:
        """Gets the text value of the named range.
        
        Returns:
            str: The text value of the named range.
        """
        GetDllLibXls().XlsName_get_Text.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_Text, self.Ptr))
        return ret

    @Text.setter
    def Text(self, value:str):
        """Sets the text value of the named range.
        
        Args:
            value (str): The text value to set.
        """
        GetDllLibXls().XlsName_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsName_set_Text, self.Ptr, value)

    @property
    def TimeSpanValue(self)->'TimeSpan':
        """Gets the TimeSpan value of the named range.
        
        Returns:
            TimeSpan: The TimeSpan value of the named range.
        """
        GetDllLibXls().XlsName_get_TimeSpanValue.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_TimeSpanValue.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_TimeSpanValue, self.Ptr)
        ret = None if intPtr==None else TimeSpan(intPtr)
        return ret

    @TimeSpanValue.setter
    def TimeSpanValue(self, value:'TimeSpan'):
        """Sets the TimeSpan value of the named range.
        
        Args:
            value (TimeSpan): The TimeSpan value to set.
        """
        GetDllLibXls().XlsName_set_TimeSpanValue.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsName_set_TimeSpanValue, self.Ptr, value.Ptr)

    @property
    def EnvalutedValue(self)->str:
        """Gets the calculated value of a formula in the named range.
        
        Returns:
            str: The calculated value of the formula.
        """
        GetDllLibXls().XlsName_get_EnvalutedValue.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_EnvalutedValue.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_EnvalutedValue, self.Ptr))
        return ret

    @property
    def VerticalAlignment(self)->'VerticalAlignType':
        """Gets the vertical alignment of the named range.
        
        Returns:
            VerticalAlignType: The vertical alignment of the named range.
        """
        GetDllLibXls().XlsName_get_VerticalAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_VerticalAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsName_get_VerticalAlignment, self.Ptr)
        objwraped = VerticalAlignType(ret)
        return objwraped

    @VerticalAlignment.setter
    def VerticalAlignment(self, value:'VerticalAlignType'):
        """Sets the vertical alignment of the named range.
        
        Args:
            value (VerticalAlignType): The vertical alignment setting to apply.
        """
        GetDllLibXls().XlsName_set_VerticalAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsName_set_VerticalAlignment, self.Ptr, value.value)

    @property
    def Value2(self)->'SpireObject':
        """Gets the value of the named range as a SpireObject.
        
        This property can return different types based on the cell content.
        
        Returns:
            SpireObject: The value of the named range as an object.
        """
        GetDllLibXls().XlsName_get_Value2.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_Value2.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_Value2, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret

    @Value2.setter
    def Value2(self, value:'SpireObject'):
        """Sets the value of the named range as a SpireObject.
        
        Args:
            value (SpireObject): The object value to set.
        """
        GetDllLibXls().XlsName_set_Value2.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsName_set_Value2, self.Ptr, value.Ptr)

    @dispatch
    def get_Item(self ,row:int,column:int)->IXLSRange:
        """Gets the cell at the specified row and column in the named range.
        
        Args:
            row (int): The row index.
            column (int): The column index.
        
        Returns:
            IXLSRange: The cell at the specified row and column.
        """
        
        GetDllLibXls().XlsName_get_Item.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsName_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_Item, self.Ptr, row,column)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret

    def set_Item(self ,row:int,column:int,value:'IXLSRange'):
        """Sets the cell at the specified row and column in the named range.
        
        Args:
            row (int): The row index.
            column (int): The column index.
            value (IXLSRange): The cell to set.
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibXls().XlsName_set_Item.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsName_set_Item, self.Ptr, row,column,intPtrvalue)

    @dispatch
    def get_Item(self ,row:int,column:int,lastRow:int,lastColumn:int)->IXLSRange:
        """Gets a range of cells specified by the start and end row and column indices.
        
        Args:
            row (int): The start row index.
            column (int): The start column index.
            lastRow (int): The end row index.
            lastColumn (int): The end column index.
        
        Returns:
            IXLSRange: The range of cells.
        """
        
        GetDllLibXls().XlsName_get_ItemRCLL.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        GetDllLibXls().XlsName_get_ItemRCLL.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_ItemRCLL, self.Ptr, row,column,lastRow,lastColumn)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret

    @dispatch
    def get_Item(self ,name:str)->IXLSRange:
        """Gets a named range by its name.
        
        Args:
            name (str): The name of the named range.
        
        Returns:
            IXLSRange: The named range.
        """
        
        GetDllLibXls().XlsName_get_ItemN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsName_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_ItemN, self.Ptr, name)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret

    @dispatch
    def get_Item(self ,name:str,IsR1C1Notation:bool)->IXLSRange:
        """Gets a named range by its name and whether to use R1C1 notation.
        
        Args:
            name (str): The name of the named range.
            IsR1C1Notation (bool): True to use R1C1 notation; False to use A1 notation.
        
        Returns:
            IXLSRange: The named range.
        """
        
        GetDllLibXls().XlsName_get_ItemNI.argtypes=[c_void_p ,c_void_p,c_bool]
        GetDllLibXls().XlsName_get_ItemNI.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_ItemNI, self.Ptr, name,IsR1C1Notation)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret

    @property
    def ConditionalFormats(self)->'ConditionalFormats':
        """Gets the collection of conditional formats applied to the named range.
        
        Returns:
            ConditionalFormats: The collection of conditional formats.
        """
        GetDllLibXls().XlsName_get_ConditionalFormats.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_ConditionalFormats.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_ConditionalFormats, self.Ptr)
        ret = None if intPtr==None else ConditionalFormats(intPtr)
        return ret

    @property
    def DataValidation(self)->'Validation':
        """Gets the data validation rules applied to the named range.
        
        Returns:
            Validation: The data validation rules.
        """
        GetDllLibXls().XlsName_get_DataValidation.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_DataValidation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsName_get_DataValidation, self.Ptr)
        ret = None if intPtr==None else Validation(intPtr)
        return ret

    @property
    def FormulaStringValue(self)->str:
        """Gets the formula string value of the named range.
        
        Returns:
            str: The formula string value.
        """
        GetDllLibXls().XlsName_get_FormulaStringValue.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_FormulaStringValue.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsName_get_FormulaStringValue, self.Ptr))
        return ret

    @FormulaStringValue.setter
    def FormulaStringValue(self, value:str):
        """Sets the formula string value of the named range.
        
        Args:
            value (str): The formula string value to set.
        """
        GetDllLibXls().XlsName_set_FormulaStringValue.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsName_set_FormulaStringValue, self.Ptr, value)

    @property
    def FormulaNumberValue(self)->float:
        """Gets the formula numeric value of the named range.
        
        Returns:
            float: The formula numeric value.
        """
        GetDllLibXls().XlsName_get_FormulaNumberValue.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_FormulaNumberValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsName_get_FormulaNumberValue, self.Ptr)
        return ret

    @FormulaNumberValue.setter
    def FormulaNumberValue(self, value:float):
        """Sets the formula numeric value of the named range.
        
        Args:
            value (float): The formula numeric value to set.
        """
        GetDllLibXls().XlsName_set_FormulaNumberValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsName_set_FormulaNumberValue, self.Ptr, value)

    @property
    def HasFormulaBoolValue(self)->bool:
        """Checks if the named range has a boolean formula value.
        
        Returns:
            bool: True if the named range has a boolean formula value; otherwise, False.
        """
        GetDllLibXls().XlsName_get_HasFormulaBoolValue.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HasFormulaBoolValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_HasFormulaBoolValue, self.Ptr)
        return ret

    @property
    def HasFormulaErrorValue(self)->bool:
        """Checks if the named range has an error formula value.
        
        Returns:
            bool: True if the named range has an error formula value; otherwise, False.
        """
        GetDllLibXls().XlsName_get_HasFormulaErrorValue.argtypes=[c_void_p]
        GetDllLibXls().XlsName_get_HasFormulaErrorValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsName_get_HasFormulaErrorValue, self.Ptr)
        return ret

