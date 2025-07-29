from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class AutoFiltersCollection (  XlsAutoFiltersCollection) :
    """
    Represents a collection of auto filters in a worksheet, providing methods to filter, add, and remove filters.
    """
    @property
    def Worksheet(self)->'Worksheet':
        """
        Returns the parent worksheet. Read-only.

        Returns:
            Worksheet: The parent worksheet.
        """
        GetDllLibXls().AutoFiltersCollection_get_Worksheet.argtypes=[c_void_p]
        GetDllLibXls().AutoFiltersCollection_get_Worksheet.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().AutoFiltersCollection_get_Worksheet, self.Ptr)
        ret = None if intPtr==None else Worksheet(intPtr)
        return ret



    #def get_Item(self ,columnIndex:int)->'IAutoFilter':
    #    """
    #<summary>
    #    Get auto filter item..
    #</summary>
    #    """
        
    #    GetDllLibXls().AutoFiltersCollection_get_Item.argtypes=[c_void_p ,c_int]
    #    GetDllLibXls().AutoFiltersCollection_get_Item.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibXls().AutoFiltersCollection_get_Item, self.Ptr, columnIndex)
    #    ret = None if intPtr==None else IAutoFilter(intPtr)
    #    return ret


    @property
    def Range(self)->'CellRange':
        """
        Gets or sets the range to be filtered.

        Returns:
            CellRange: The range to be filtered.
        """
        GetDllLibXls().AutoFiltersCollection_get_Range.argtypes=[c_void_p]
        GetDllLibXls().AutoFiltersCollection_get_Range.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().AutoFiltersCollection_get_Range, self.Ptr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @Range.setter
    def Range(self, value:'CellRange'):
        """
        Sets the range to be filtered.

        Args:
            value (CellRange): The range to be filtered.
        """
        GetDllLibXls().AutoFiltersCollection_set_Range.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_set_Range, self.Ptr, value.Ptr)

    @dispatch
    def Filter(self):
        """
        Filters the data in the range.
        """
        GetDllLibXls().AutoFiltersCollection_Filter.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_Filter, self.Ptr)

    @dispatch

    def Filter(self ,hideRows:bool)->List[int]:
        """
        Gets all hidden rows' indexes after filtering.

        Args:
            hideRows (bool): If true, hide the filtered rows.

        Returns:
            List[int]: All hidden rows indexes.

        """
        
        GetDllLibXls().AutoFiltersCollection_FilterH.argtypes=[c_void_p ,c_bool]
        GetDllLibXls().AutoFiltersCollection_FilterH.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().AutoFiltersCollection_FilterH, self.Ptr, hideRows)
        ret = GetVectorFromArray(intPtrArray, c_int)
        return ret

    @dispatch

    def AddFilter(self ,columnIndex:int,criteria:str):
        """
        Adds a filter for a filter column.

        Args:
            columnIndex (int): The column field on which you want to base the filter.
            criteria (str): The specified criteria (a string; for example, "hello").

        """
        
        GetDllLibXls().AutoFiltersCollection_AddFilter.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_AddFilter, self.Ptr, columnIndex,criteria)

    @dispatch

    def AddFilter(self ,column:IAutoFilter,criteria:str):
        """
        Adds a filter for a filter column by IAutoFilter object.

        Args:
            column (IAutoFilter): The filter column object.
            criteria (str): The specified criteria.

        """
        intPtrcolumn:c_void_p = column.Ptr

        GetDllLibXls().AutoFiltersCollection_AddFilterCC.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_AddFilterCC, self.Ptr, intPtrcolumn,criteria)

    @dispatch

    def AddDateFilter(self ,columnIndex:int,dateTimeGroupingType:DateTimeGroupingType,year:int,month:int,day:int,hour:int,minute:int,second:int):
        """
        Adds a date filter for a filter column.

        Args:
            columnIndex (int): The column field on which you want to base the filter.
            dateTimeGroupingType (DateTimeGroupingType): The grouping type.
            year (int): The year.
            month (int): The month.
            day (int): The day.
            hour (int): The hour.
            minute (int): The minute.
            second (int): The second.

        """
        enumdateTimeGroupingType:c_int = dateTimeGroupingType.value

        GetDllLibXls().AutoFiltersCollection_AddDateFilter.argtypes=[c_void_p ,c_int,c_int,c_int,c_int,c_int,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_AddDateFilter, self.Ptr, columnIndex,enumdateTimeGroupingType,year,month,day,hour,minute,second)


    def RemoveDateFilter(self ,columnIndex:int,dateTimeGroupingType:'DateTimeGroupingType',year:int,month:int,day:int,hour:int,minute:int,second:int):
        """
        Removes a date filter.

        Args:
            columnIndex (int): The column field on which you want to base the filter.
            dateTimeGroupingType (DateTimeGroupingType): The grouping type.
            year (int): The year.
            month (int): The month.
            day (int): The day.
            hour (int): The hour.
            minute (int): The minute.
            second (int): The second.

        """
        enumdateTimeGroupingType:c_int = dateTimeGroupingType.value

        GetDllLibXls().AutoFiltersCollection_RemoveDateFilter.argtypes=[c_void_p ,c_int,c_int,c_int,c_int,c_int,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_RemoveDateFilter, self.Ptr, columnIndex,enumdateTimeGroupingType,year,month,day,hour,minute,second)


    def RemoveFilter(self ,columnIndex:int,criteria:str):
        """
        Removes a filter for a filter column.

        Args:
            columnIndex (int): The column field on which you want to base the filter.
            criteria (str): The specified criteria.

        """
        
        GetDllLibXls().AutoFiltersCollection_RemoveFilter.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_RemoveFilter, self.Ptr, columnIndex,criteria)

    @dispatch

    def QuickFilter(self ,columnIndex:int,criteria:str):
        """
        Filters a list with specified criteria.

        Args:
            columnIndex (int): The column field on which you want to base the filter.
            criteria (str): The specified criteria.

        """
        
        GetDllLibXls().AutoFiltersCollection_QuickFilter.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_QuickFilter, self.Ptr, columnIndex,criteria)

    @dispatch

    def QuickFilter(self ,column:IAutoFilter,criteria:str):
        """
        Filters a list with specified criteria by IAutoFilter object.

        Args:
            column (IAutoFilter): The filter column object.
            criteria (str): The specified criteria.

        """
        intPtrcolumn:c_void_p = column.Ptr

        GetDllLibXls().AutoFiltersCollection_QuickFilterCC.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_QuickFilterCC, self.Ptr, intPtrcolumn,criteria)

    @dispatch

    def DynamicFilter(self ,columnIndex:int,dynamicFilterType:DynamicFilterType):
        """
        Adds a dynamic filter.

        Args:
            columnIndex (int): The column field on which you want to base the filter.
            dynamicFilterType (DynamicFilterType): Dynamic filter type.

        """
        enumdynamicFilterType:c_int = dynamicFilterType.value

        GetDllLibXls().AutoFiltersCollection_DynamicFilter.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_DynamicFilter, self.Ptr, columnIndex,enumdynamicFilterType)

    @dispatch

    def AddFontColorFilter(self ,columnIndex:int,color:Color):
        """
        Adds a font color filter.

        Args:
            columnIndex (int): The column field on which you want to base the filter.
            color (Color): Font Color.

        """
        intPtrcolor:c_void_p = color.Ptr

        GetDllLibXls().AutoFiltersCollection_AddFontColorFilter.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_AddFontColorFilter, self.Ptr, columnIndex,intPtrcolor)

    @dispatch

    def AddFillColorFilter(self ,columnIndex:int,pattern:ExcelPatternType,foreColor:Color,backColor:Color):
        """
        Adds a fill color filter.

        Args:
            columnIndex (int): The column field on which you want to base the filter.
            pattern (ExcelPatternType): The background pattern type.
            foreColor (Color): The foreground color.
            backColor (Color): The background color.

        """
        enumpattern:c_int = pattern.value
        intPtrforeColor:c_void_p = foreColor.Ptr
        intPtrbackColor:c_void_p = backColor.Ptr

        GetDllLibXls().AutoFiltersCollection_AddFillColorFilter.argtypes=[c_void_p ,c_int,c_int,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_AddFillColorFilter, self.Ptr, columnIndex,enumpattern,intPtrforeColor,intPtrbackColor)

    @dispatch

    def AddFillColorFilter(self ,filterColumnIndex:int,color:Color):
        """
        Adds a fill color filter.

        Args:
            filterColumnIndex (int): The column field index on which you want to base the filter (from the left of the list; the leftmost field is field 0).
            color (Color): Fill Color.

        """
        intPtrcolor:c_void_p = color.Ptr

        GetDllLibXls().AutoFiltersCollection_AddFillColorFilterFC.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_AddFillColorFilterFC, self.Ptr, filterColumnIndex,intPtrcolor)

    @dispatch

    def AddFillColorFilter(self ,column:IAutoFilter,color:Color):
        """

        """
        intPtrcolumn:c_void_p = column.Ptr
        intPtrcolor:c_void_p = color.Ptr

        GetDllLibXls().AutoFiltersCollection_AddFillColorFilterCC.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_AddFillColorFilterCC, self.Ptr, intPtrcolumn,intPtrcolor)

    @dispatch

    def AddFontColorFilter(self ,column:IAutoFilter,color:Color):
        """

        """
        intPtrcolumn:c_void_p = column.Ptr
        intPtrcolor:c_void_p = color.Ptr

        GetDllLibXls().AutoFiltersCollection_AddFontColorFilterCC.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_AddFontColorFilterCC, self.Ptr, intPtrcolumn,intPtrcolor)


    def AddIconFilter(self ,columnIndex:int,iconSetType:'IconSetType',iconId:int):
        """

        """
        enumiconSetType:c_int = iconSetType.value

        GetDllLibXls().AutoFiltersCollection_AddIconFilter.argtypes=[c_void_p ,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_AddIconFilter, self.Ptr, columnIndex,enumiconSetType,iconId)

    @dispatch

    def MatchBlanks(self ,columnIndex:int):
        """
        Match all blank cell in the list.

        Args:
            columnIndex (int): The column field on which you want to base the filter.

        """
        
        GetDllLibXls().AutoFiltersCollection_MatchBlanks.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_MatchBlanks, self.Ptr, columnIndex)

    @dispatch

    def MatchBlanks(self ,column:IAutoFilter):
        """
        Match all blank cell in the list.

        Args:
            column (IAutoFilter): The column field on which you want to base the filter.

        """
        intPtrcolumn:c_void_p = column.Ptr

        GetDllLibXls().AutoFiltersCollection_MatchBlanksC.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_MatchBlanksC, self.Ptr, intPtrcolumn)

    @dispatch

    def CustomFilter(self ,columnIndex:int,operatorType:FilterOperatorType,criteria:SpireObject):
        """
        Filters a list with a custom criteria.

        Args:
            columnIndex (int): The column field on which you want to base the filter.
            operatorType (FilterOperatorType): The filter operator type
            criteria (SpireObject): The custom criteria

        """
        enumoperatorType:c_int = operatorType.value
        intPtrcriteria:c_void_p = criteria.Ptr

        GetDllLibXls().AutoFiltersCollection_CustomFilter.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_CustomFilter, self.Ptr, columnIndex,enumoperatorType,intPtrcriteria)

    @dispatch

    def CustomFilter(self ,columnIndex:int,operatorType1:FilterOperatorType,criteria1:SpireObject,isAnd:bool,operatorType2:FilterOperatorType,criteria2:SpireObject):
        """
        Filters a list with custom criterias.

        Args:
            columnIndex (int): The column field on which you want to base the filter.
            operatorType1 (FilterOperatorType): The first filter operator type
            criteria1 (SpireObject): The first custom criteria
            isAnd (bool): 
            operatorType2 (FilterOperatorType): The second filter operator type
            criteria2 (SpireObject): The second custom criteria

        """
        enumoperatorType1:c_int = operatorType1.value
        intPtrcriteria1:c_void_p = criteria1.Ptr
        enumoperatorType2:c_int = operatorType2.value
        intPtrcriteria2:c_void_p = criteria2.Ptr

        GetDllLibXls().AutoFiltersCollection_CustomFilterCOCIOC.argtypes=[c_void_p ,c_int,c_int,c_void_p,c_bool,c_int,c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_CustomFilterCOCIOC, self.Ptr, columnIndex,enumoperatorType1,intPtrcriteria1,isAnd,enumoperatorType2,intPtrcriteria2)

    @dispatch

    def CustomFilter(self ,column:FilterColumn,operatorType:FilterOperatorType,criteria:SpireObject):
        """

        """
        intPtrcolumn:c_void_p = column.Ptr
        enumoperatorType:c_int = operatorType.value
        intPtrcriteria:c_void_p = criteria.Ptr

        GetDllLibXls().AutoFiltersCollection_CustomFilterCOC.argtypes=[c_void_p ,c_void_p,c_int,c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_CustomFilterCOC, self.Ptr, intPtrcolumn,enumoperatorType,intPtrcriteria)

    @dispatch

    def CustomFilter(self ,column:FilterColumn,operatorType1:FilterOperatorType,criteria1:SpireObject,isAnd:bool,operatorType2:FilterOperatorType,criteria2:SpireObject):
        """

        """
        intPtrcolumn:c_void_p = column.Ptr
        enumoperatorType1:c_int = operatorType1.value
        intPtrcriteria1:c_void_p = criteria1.Ptr
        enumoperatorType2:c_int = operatorType2.value
        intPtrcriteria2:c_void_p = criteria2.Ptr

        GetDllLibXls().AutoFiltersCollection_CustomFilterCOCIOC1.argtypes=[c_void_p ,c_void_p,c_int,c_void_p,c_bool,c_int,c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_CustomFilterCOCIOC1, self.Ptr, intPtrcolumn,enumoperatorType1,intPtrcriteria1,isAnd,enumoperatorType2,intPtrcriteria2)

    @dispatch

    def DynamicFilter(self ,column:IAutoFilter,dynamicFilterType:DynamicFilterType):
        """

        """
        intPtrcolumn:c_void_p = column.Ptr
        enumdynamicFilterType:c_int = dynamicFilterType.value

        GetDllLibXls().AutoFiltersCollection_DynamicFilterCD.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_DynamicFilterCD, self.Ptr, intPtrcolumn,enumdynamicFilterType)

    @dispatch

    def ClearFilter(self ,columnName:str):
        """
        Delete the column filter by column name

        Args:
            columName (str): column name

        """
        
        GetDllLibXls().AutoFiltersCollection_ClearFilter.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_ClearFilter, self.Ptr, columnName)

    @dispatch

    def ClearFilter(self ,filterColumnIndex:int):
        """
        Delete the column filter by column index(filters column index not sheet column index)

        Args:
            columName (int): column index

        """
        
        GetDllLibXls().AutoFiltersCollection_ClearFilterF.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_ClearFilterF, self.Ptr, filterColumnIndex)

    @dispatch

    def AddDateFilter(self ,column:IAutoFilter,dateTimeGroupingType:DateTimeGroupingType,year:int,month:int,day:int,hour:int,minute:int,second:int):
        """

        """
        intPtrcolumn:c_void_p = column.Ptr
        enumdateTimeGroupingType:c_int = dateTimeGroupingType.value

        GetDllLibXls().AutoFiltersCollection_AddDateFilterCDYMDHMS.argtypes=[c_void_p ,c_void_p,c_int,c_int,c_int,c_int,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_AddDateFilterCDYMDHMS, self.Ptr, intPtrcolumn,enumdateTimeGroupingType,year,month,day,hour,minute,second)

    @dispatch

    def FilterTop10(self ,filterColumnIndex:int,isTop:bool,isPercent:bool,itemCount:int):
        """
        Filter the top 10 item in the list

        Args:
            filterColumnIndex (int): The column field index on which you want to base the filter (from the left of the list; the leftmost field is field 0).
            isTop (bool): Indicates whether filter from top or bottom
            isPercent (bool): Indicates whether the items is percent or count
            itemCount (int): The item count

        """
        
        GetDllLibXls().AutoFiltersCollection_FilterTop10.argtypes=[c_void_p ,c_int,c_bool,c_bool,c_int]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_FilterTop10, self.Ptr, filterColumnIndex,isTop,isPercent,itemCount)

    @dispatch

    def FilterTop10(self ,column:IAutoFilter,isTop:bool,isPercent:bool,itemCount:int):
        """
        Filter the top 10 item in the list

        Args:
            column (IAutoFilter): The column field on which you want to base the filter.
            isTop (bool): Indicates whether filter from top or bottom
            isPercent (bool): Indicates whether the items is percent or count
            itemCount (int): The item count

        """
        intPtrcolumn:c_void_p = column.Ptr

        GetDllLibXls().AutoFiltersCollection_FilterTop10CIII.argtypes=[c_void_p ,c_void_p,c_bool,c_bool,c_int]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_FilterTop10CIII, self.Ptr, intPtrcolumn,isTop,isPercent,itemCount)

    @dispatch

    def MatchNonBlanks(self ,filterColumnIndex:int):
        """
        Match all not blank cell in the list.

        Args:
            filterColumnIndex (int): The column field index on which you want to base the filter (from the left of the list; the leftmost field is field 0).

        """
        
        GetDllLibXls().AutoFiltersCollection_MatchNonBlanks.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_MatchNonBlanks, self.Ptr, filterColumnIndex)

    @dispatch

    def MatchNonBlanks(self ,column:FilterColumn):
        """
        Match all not blank cell in the list.

        Args:
            column (FilterColumn): The column field on which you want to base the filter.

        """
        intPtrcolumn:c_void_p = column.Ptr

        GetDllLibXls().AutoFiltersCollection_MatchNonBlanksC.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_MatchNonBlanksC, self.Ptr, intPtrcolumn)

    def Clear(self):
        """

        """
        GetDllLibXls().AutoFiltersCollection_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().AutoFiltersCollection_Clear, self.Ptr)

