from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsConditionalFormats (  SpireObject, ICloneParent, IConditionalFormats) :
    """
    Represents a collection of conditional formats in Excel.
    """

    def AddCondition(self)->'IConditionalFormat':
        """
        Adds a new conditional format to the collection.

        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        GetDllLibXls().XlsConditionalFormats_AddCondition.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormats_AddCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_AddCondition, self.Ptr)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret


    @dispatch

    def AddCellValueCondition(self ,operatorType:ComparisonOperatorType,value1:str,value2:str)->IConditionalFormat:
        """
        Adds a new cell value condition to the collection.

        Args:
            operatorType (ComparisonOperatorType): The comparison operator for conditional formatting.
            value1 (str): The first value.
            value2 (str): The second value.
        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        enumoperatorType:c_int = operatorType.value

        GetDllLibXls().XlsConditionalFormats_AddCellValueCondition.argtypes=[c_void_p ,c_int,c_void_p,c_void_p]
        GetDllLibXls().XlsConditionalFormats_AddCellValueCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_AddCellValueCondition, self.Ptr, enumoperatorType,value1,value2)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret


    @dispatch

    def AddCellValueCondition(self ,operatorType:ComparisonOperatorType,value1:float,value2:float)->IConditionalFormat:
        """
        Adds a new cell value condition to the collection with float values.

        Args:
            operatorType (ComparisonOperatorType): The comparison operator for conditional formatting.
            value1 (float): The first value.
            value2 (float): The second value.
        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        enumoperatorType:c_int = operatorType.value

        GetDllLibXls().XlsConditionalFormats_AddCellValueConditionOVV.argtypes=[c_void_p ,c_int,c_double,c_double]
        GetDllLibXls().XlsConditionalFormats_AddCellValueConditionOVV.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_AddCellValueConditionOVV, self.Ptr, enumoperatorType,value1,value2)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def AddBeginsWithCondition(self ,text:str)->'IConditionalFormat':
        """
        Adds a new 'begins with' text condition to the collection.

        Args:
            text (str): The text to match at the beginning.
        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        
        GetDllLibXls().XlsConditionalFormats_AddBeginsWithCondition.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsConditionalFormats_AddBeginsWithCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_AddBeginsWithCondition, self.Ptr, text)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def AddContainsTextCondition(self ,text:str)->'IConditionalFormat':
        """
        Adds a new 'contains text' condition to the collection.

        Args:
            text (str): The text to search for.
        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        
        GetDllLibXls().XlsConditionalFormats_AddContainsTextCondition.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsConditionalFormats_AddContainsTextCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_AddContainsTextCondition, self.Ptr, text)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def AddEndsWithCondition(self ,text:str)->'IConditionalFormat':
        """
        Adds a new 'ends with' text condition to the collection.

        Args:
            text (str): The text to match at the end.
        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        
        GetDllLibXls().XlsConditionalFormats_AddEndsWithCondition.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsConditionalFormats_AddEndsWithCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_AddEndsWithCondition, self.Ptr, text)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def AddNotContainsTextCondition(self ,text:str)->'IConditionalFormat':
        """
        Adds a new 'not contains text' condition to the collection.

        Args:
            text (str): The text that should not be present.
        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        
        GetDllLibXls().XlsConditionalFormats_AddNotContainsTextCondition.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsConditionalFormats_AddNotContainsTextCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_AddNotContainsTextCondition, self.Ptr, text)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def AddContainsBlanksCondition(self)->'IConditionalFormat':
        """
        Adds a new 'contains blanks' condition to the collection.

        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        GetDllLibXls().XlsConditionalFormats_AddContainsBlanksCondition.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormats_AddContainsBlanksCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_AddContainsBlanksCondition, self.Ptr)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def AddContainsErrorsCondition(self)->'IConditionalFormat':
        """
        Adds a new 'contains errors' condition to the collection.

        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        GetDllLibXls().XlsConditionalFormats_AddContainsErrorsCondition.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormats_AddContainsErrorsCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_AddContainsErrorsCondition, self.Ptr)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def AddDuplicateValuesCondition(self)->'IConditionalFormat':
        """
        Adds a new 'duplicate values' condition to the collection.

        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        GetDllLibXls().XlsConditionalFormats_AddDuplicateValuesCondition.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormats_AddDuplicateValuesCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_AddDuplicateValuesCondition, self.Ptr)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def AddNotContainsBlanksCondition(self)->'IConditionalFormat':
        """
        Adds a new 'not contains blanks' condition to the collection.

        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        GetDllLibXls().XlsConditionalFormats_AddNotContainsBlanksCondition.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormats_AddNotContainsBlanksCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_AddNotContainsBlanksCondition, self.Ptr)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def AddNotContainsErrorsCondition(self)->'IConditionalFormat':
        """
        Adds a new 'not contains errors' condition to the collection.

        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        GetDllLibXls().XlsConditionalFormats_AddNotContainsErrorsCondition.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormats_AddNotContainsErrorsCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_AddNotContainsErrorsCondition, self.Ptr)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def AddUniqueValuesCondition(self)->'IConditionalFormat':
        """
        Adds a new 'unique values' condition to the collection.

        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        GetDllLibXls().XlsConditionalFormats_AddUniqueValuesCondition.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormats_AddUniqueValuesCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_AddUniqueValuesCondition, self.Ptr)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def AddTimePeriodCondition(self ,timePeriodType:'TimePeriodType')->'IConditionalFormat':
        """
        Adds a new time period condition to the collection.

        Args:
            timePeriodType (TimePeriodType): The type of the time period.
        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        enumtimePeriodType:c_int = timePeriodType.value

        GetDllLibXls().XlsConditionalFormats_AddTimePeriodCondition.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsConditionalFormats_AddTimePeriodCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_AddTimePeriodCondition, self.Ptr, enumtimePeriodType)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def AddAverageCondition(self ,averageType:'AverageType')->'IConditionalFormat':
        """
        Adds a new above or below average condition to the collection.

        Args:
            averageType (AverageType): The type of the average.
        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        enumaverageType:c_int = averageType.value

        GetDllLibXls().XlsConditionalFormats_AddAverageCondition.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsConditionalFormats_AddAverageCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_AddAverageCondition, self.Ptr, enumaverageType)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def AddTopBottomCondition(self ,topBottomType:'TopBottomType',rank:int)->'IConditionalFormat':
        """
        Adds a new TopN or BottomN condition to the collection.

        Args:
            topBottomType (TopBottomType): The type of the Top or Bottom.
            rank (int): The rank of the Top or Bottom.
        Returns:
            IConditionalFormat: The newly added conditional format.
        """
        enumtopBottomType:c_int = topBottomType.value

        GetDllLibXls().XlsConditionalFormats_AddTopBottomCondition.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsConditionalFormats_AddTopBottomCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_AddTopBottomCondition, self.Ptr, enumtopBottomType,rank)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret


    @dispatch

    def Remove(self ,startRow:int,startColumn:int,totalRows:int,totalColumns:int):
        """
        Removes conditional formats from the specified range.

        Args:
            startRow (int): The starting row.
            startColumn (int): The starting column.
            totalRows (int): The total number of rows.
            totalColumns (int): The total number of columns.
        """
        
        GetDllLibXls().XlsConditionalFormats_Remove.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormats_Remove, self.Ptr, startRow,startColumn,totalRows,totalColumns)


    def RemoveAt(self ,index:int):
        """
        Removes the conditional format at the specified index.

        Args:
            index (int): The index of the conditional format to remove.
        """
        
        GetDllLibXls().XlsConditionalFormats_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormats_RemoveAt, self.Ptr, index)


    def CompareTo(self ,formats:'XlsConditionalFormats')->bool:
        """
        Compares this collection to another XlsConditionalFormats collection.

        Args:
            formats (XlsConditionalFormats): The collection to compare to.
        Returns:
            bool: True if equal; otherwise, False.
        """
        intPtrformats:c_void_p = formats.Ptr

        GetDllLibXls().XlsConditionalFormats_CompareTo.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsConditionalFormats_CompareTo.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormats_CompareTo, self.Ptr, intPtrformats)
        return ret


    def CompareFormats(self ,firstFormat:'IConditionalFormat',secondFormat:'IConditionalFormat')->bool:
        """
        Compares two conditional formats for equality.

        Args:
            firstFormat (IConditionalFormat): The first conditional format.
            secondFormat (IConditionalFormat): The second conditional format.
        Returns:
            bool: True if equal; otherwise, False.
        """
        intPtrfirstFormat:c_void_p = firstFormat.Ptr
        intPtrsecondFormat:c_void_p = secondFormat.Ptr

        GetDllLibXls().XlsConditionalFormats_CompareFormats.argtypes=[c_void_p ,c_void_p,c_void_p]
        GetDllLibXls().XlsConditionalFormats_CompareFormats.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormats_CompareFormats, self.Ptr, intPtrfirstFormat,intPtrsecondFormat)
        return ret

    @dispatch

    def AddCells(self ,formats:'XlsConditionalFormats'):
        """
        Adds all conditional formats from another collection.

        Args:
            formats (XlsConditionalFormats): The collection to add from.
        """
        intPtrformats:c_void_p = formats.Ptr

        GetDllLibXls().XlsConditionalFormats_AddCells.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormats_AddCells, self.Ptr, intPtrformats)

#
#    def Contains(self ,arrRanges:'Rectangle[]')->bool:
#        """
#
#        """
#        #arrayarrRanges:ArrayTypearrRanges = ""
#        countarrRanges = len(arrRanges)
#        ArrayTypearrRanges = c_void_p * countarrRanges
#        arrayarrRanges = ArrayTypearrRanges()
#        for i in range(0, countarrRanges):
#            arrayarrRanges[i] = arrRanges[i].Ptr
#
#
#        GetDllLibXls().XlsConditionalFormats_Contains.argtypes=[c_void_p ,ArrayTypearrRanges]
#        GetDllLibXls().XlsConditionalFormats_Contains.restype=c_bool
#        ret = CallCFunction(GetDllLibXls().XlsConditionalFormats_Contains, self.Ptr, arrayarrRanges)
#        return ret



    def ContainsCount(self ,range:'Rectangle')->int:
        """

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().XlsConditionalFormats_ContainsCount.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsConditionalFormats_ContainsCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormats_ContainsCount, self.Ptr, intPtrrange)
        return ret

    @dispatch

    def AddCells(self ,arrCells:IList):
        """
        Adds conditional formats to the specified cells.

        Args:
            arrCells (IList): The list of cells to add formats to.
        """
        intPtrarrCells:c_void_p = arrCells.Ptr

        GetDllLibXls().XlsConditionalFormats_AddCellsA.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormats_AddCellsA, self.Ptr, intPtrarrCells)


    def AddRange(self ,range:'IXLSRange'):
        """
        Adds a range to the collection for conditional formatting.

        Args:
            range (IXLSRange): The range to add.
        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().XlsConditionalFormats_AddRange.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormats_AddRange, self.Ptr, intPtrrange)

#    @dispatch
#
#    def Remove(self ,arrRanges:'Rectangle[]'):
#        """
#
#        """
#        #arrayarrRanges:ArrayTypearrRanges = ""
#        countarrRanges = len(arrRanges)
#        ArrayTypearrRanges = c_void_p * countarrRanges
#        arrayarrRanges = ArrayTypearrRanges()
#        for i in range(0, countarrRanges):
#            arrayarrRanges[i] = arrRanges[i].Ptr
#
#
#        GetDllLibXls().XlsConditionalFormats_RemoveA.argtypes=[c_void_p ,ArrayTypearrRanges]
#        CallCFunction(GetDllLibXls().XlsConditionalFormats_RemoveA, self.Ptr, arrayarrRanges)


    def ClearCells(self):
        """
        Clears all conditional formats from the cells in the collection.
        """
        GetDllLibXls().XlsConditionalFormats_ClearCells.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormats_ClearCells, self.Ptr)

    def BeginUpdate(self):
        """
        Begins batch update of the collection.
        """
        GetDllLibXls().XlsConditionalFormats_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormats_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """
        Ends batch update of the collection.
        """
        GetDllLibXls().XlsConditionalFormats_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormats_EndUpdate, self.Ptr)

    def GetHashCode(self)->int:
        """
        Returns the hash code for this collection.

        Returns:
            int: The hash code.
        """
        GetDllLibXls().XlsConditionalFormats_GetHashCode.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormats_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormats_GetHashCode, self.Ptr)
        return ret


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified object is equal to this collection.

        Args:
            obj (SpireObject): The object to compare.
        Returns:
            bool: True if equal; otherwise, False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibXls().XlsConditionalFormats_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsConditionalFormats_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormats_Equals, self.Ptr, intPtrobj)
        return ret


    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """
        Creates a new object that is a copy of this collection.

        Args:
            parent (SpireObject): The parent object for the new collection.
        Returns:
            SpireObject: A new object that is a copy of this collection.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsConditionalFormats_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsConditionalFormats_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @property
    def IsEmpty(self)->bool:
        """
        Gets a value indicating whether the collection is empty.

        Returns:
            bool: True if empty; otherwise, False.
        """
        GetDllLibXls().XlsConditionalFormats_get_IsEmpty.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormats_get_IsEmpty.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormats_get_IsEmpty, self.Ptr)
        return ret

    @property

    def Address(self)->str:
        """
        Gets the address of the range to which the conditional formats apply.

        Returns:
            str: The address string.
        """
        GetDllLibXls().XlsConditionalFormats_get_Address.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormats_get_Address.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsConditionalFormats_get_Address, self.Ptr))
        return ret


    @property

    def AddressR1C1(self)->str:
        """
        Gets the address of the range in R1C1 notation.

        Returns:
            str: The address string in R1C1 notation.
        """
        GetDllLibXls().XlsConditionalFormats_get_AddressR1C1.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormats_get_AddressR1C1.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsConditionalFormats_get_AddressR1C1, self.Ptr))
        return ret


#    @property
#
#    def CellRectangles(self)->'List1':
#        """
#
#        """
#        GetDllLibXls().XlsConditionalFormats_get_CellRectangles.argtypes=[c_void_p]
#        GetDllLibXls().XlsConditionalFormats_get_CellRectangles.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_get_CellRectangles, self.Ptr)
#        ret = None if intPtr==None else List1(intPtr)
#        return ret
#



    def GetByIndex(self ,index:int)->'IConditionalFormat':
        """
        Gets the conditional format at the specified index.

        Args:
            index (int): The index of the conditional format.
        Returns:
            IConditionalFormat: The conditional format at the specified index.
        """
        
        GetDllLibXls().XlsConditionalFormats_GetByIndex.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsConditionalFormats_GetByIndex.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_GetByIndex, self.Ptr, index)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def get_Item(self ,fieldIndex:int)->'IConditionalFormat':
        """
        Gets the conditional format at the specified field index.

        Args:
            fieldIndex (int): The field index.
        Returns:
            IConditionalFormat: The conditional format at the specified field index.
        """
        
        GetDllLibXls().XlsConditionalFormats_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsConditionalFormats_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_get_Item, self.Ptr, fieldIndex)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
        Returns an enumerator that iterates through the collection.

        Returns:
            IEnumerator: An enumerator for the collection.
        """
        GetDllLibXls().XlsConditionalFormats_GetEnumerator.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormats_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormats_GetEnumerator, self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    def Clear(self):
        """
        Removes all conditional formats from the collection.
        """
        GetDllLibXls().XlsConditionalFormats_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormats_Clear, self.Ptr)

    @property
    def Capacity(self)->int:
        """
        Gets or sets the capacity of the collection.

        Returns:
            int: The capacity value.
        """
        GetDllLibXls().XlsConditionalFormats_get_Capacity.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormats_get_Capacity.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormats_get_Capacity, self.Ptr)
        return ret

    @Capacity.setter
    def Capacity(self, value:int):
        """
        Sets the capacity of the collection.

        Args:
            value (int): The capacity value.
        """
        GetDllLibXls().XlsConditionalFormats_set_Capacity.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormats_set_Capacity, self.Ptr, value)

    @property
    def Count(self)->int:
        """
        Gets the number of conditional formats in the collection.

        Returns:
            int: The number of conditional formats.
        """
        GetDllLibXls().XlsConditionalFormats_get_Count.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormats_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormats_get_Count, self.Ptr)
        return ret

    @staticmethod
    def MAXIMUM_CF_NUMBER()->int:
        """
        Gets the maximum number of conditional formats allowed.

        Returns:
            int: The maximum number of conditional formats.
        """
        #GetDllLibXls().XlsConditionalFormats_MAXIMUM_CF_NUMBER.argtypes=[]
        GetDllLibXls().XlsConditionalFormats_MAXIMUM_CF_NUMBER.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormats_MAXIMUM_CF_NUMBER)
        return ret

