from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsPivotField (  SpireObject, IPivotField, ICloneParent) :
    """Implementation of the PivotField interface.
    
    This class provides functionality for managing fields in a PivotTable,
    including field properties, filtering, grouping, and sorting options.
    """

    def AddLabelFilter(self ,type:'PivotLabelFilterType',value1:'SpireObject',value2:'SpireObject'):
        """Adds a label filter to the pivot field.
        
        This method adds a label filter for row and column fields only.
        
        Args:
            type: Filter type.
            value1: First filter value.
            value2: Second filter value, only for Between and NotBetween type.
        """
        enumtype:c_int = type.value
        intPtrvalue1:c_void_p = value1.Ptr
        intPtrvalue2:c_void_p = None if value2==None else value2.Ptr

        GetDllLibXls().XlsPivotField_AddLabelFilter.argtypes=[c_void_p ,c_int,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsPivotField_AddLabelFilter,self.Ptr, enumtype,intPtrvalue1,intPtrvalue2)


    def AddValueFilter(self ,type:'PivotValueFilterType',dataField:'IPivotDataField',value1:'SpireObject',value2:'SpireObject'):
        """Adds a value filter to the pivot field.
        
        This method adds a value filter for row and column fields only.
        
        Args:
            type: Filter type.
            dataField: Filter data field.
            value1: First filter value.
            value2: Second filter value, only for Between and NotBetween type.
        """
        enumtype:c_int = type.value
        intPtrdataField:c_void_p = dataField.Ptr
        intPtrvalue1:c_void_p = value1.Ptr
        intPtrvalue2:c_void_p = None if value2==None else value2.Ptr

        GetDllLibXls().XlsPivotField_AddValueFilter.argtypes=[c_void_p ,c_int,c_void_p,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsPivotField_AddValueFilter,self.Ptr, enumtype,intPtrdataField,intPtrvalue1,intPtrvalue2)



    @dispatch

    def CreateGroup(self ,start:DateTime,end:DateTime,groupByArray:List[PivotGroupByTypes]):
        """Creates a date-based group for the field.
        
        Args:
            start: The start date time.
            end: The end date time.
            groupByArray: The array of group by types.
        """
        intPtrstart:c_void_p = start.Ptr
        intPtrend:c_void_p = end.Ptr
        #arraygroupByArray:ArrayTypegroupByArray = ""
        countgroupByArray = len(groupByArray)
        ArrayTypegroupByArray = c_int * countgroupByArray
        arraygroupByArray = ArrayTypegroupByArray()
        for i in range(0, countgroupByArray):
            arraygroupByArray[i] = groupByArray[i].value


        GetDllLibXls().XlsPivotField_CreateGroup.argtypes=[c_void_p ,c_void_p,c_void_p,ArrayTypegroupByArray,c_int]
        CallCFunction(GetDllLibXls().XlsPivotField_CreateGroup,self.Ptr, intPtrstart,intPtrend,arraygroupByArray,countgroupByArray)


    @dispatch

    def CreateGroup(self ,start:DateTime,end:DateTime,groupByArray:List[PivotGroupByTypes],days:int):
        """Creates a date-based group for the field with specified days.
        
        Args:
            start: The start date time.
            end: The end date time.
            groupByArray: The array of group by types.
            days: The number of days for grouping.
        """
        intPtrstart:c_void_p = start.Ptr
        intPtrend:c_void_p = end.Ptr
        #arraygroupByArray:ArrayTypegroupByArray = ""
        countgroupByArray = len(groupByArray)
        ArrayTypegroupByArray = c_int * countgroupByArray
        arraygroupByArray = ArrayTypegroupByArray()
        for i in range(0, countgroupByArray):
            arraygroupByArray[i] = groupByArray[i].value


        GetDllLibXls().XlsPivotField_CreateGroupSEGD.argtypes=[c_void_p ,c_void_p,c_void_p,ArrayTypegroupByArray,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsPivotField_CreateGroupSEGD,self.Ptr, intPtrstart,intPtrend,arraygroupByArray,countgroupByArray,days)

    @dispatch

    def CreateGroup(self ,startValue:float,endValue:float,intervalValue:float):
        """Creates a number-based group for the field.
        
        Args:
            startValue: The start number value.
            endValue: The end number value.
            intervalValue: The interval number value.
        """
        
        GetDllLibXls().XlsPivotField_CreateGroupSEI.argtypes=[c_void_p ,c_double,c_double,c_double]
        CallCFunction(GetDllLibXls().XlsPivotField_CreateGroupSEI,self.Ptr, startValue,endValue,intervalValue)

    @property
    def CustomName(self)->str:
        """Gets the custom name of the field.
        
        Returns:
            str: The custom name of the field.
        """
        GetDllLibXls().XlsPivotField_get_CustomName.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_CustomName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPivotField_get_CustomName, self.Ptr))
        return ret

    @CustomName.setter
    def CustomName(self, value:str):
        """Sets the custom name of the field.
        
        Args:
            value (str): The custom name to set for the field.
        """
        GetDllLibXls().XlsPivotField_set_CustomName.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsPivotField_set_CustomName, self.Ptr, value)
    
    @property

    def Parent(self)->'PivotTableFields':
        """Gets the parent collection of the pivot field.
        
        Returns:
            PivotTableFields: The parent collection object.
        """
        GetDllLibXls().XlsPivotField_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotField_get_Parent, self.Ptr)
        ret = None if intPtr==None else PivotTableFields(intPtr)
        return ret


    @property

    def Name(self)->str:
        """Gets the name of the field.
        
        Returns:
            str: The name of the field.
        """
        GetDllLibXls().XlsPivotField_get_Name.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPivotField_get_Name, self.Ptr))
        return ret


    @property

    def Axis(self)->'AxisTypes':
        """Gets the axis type of the field.
        
        Returns:
            AxisTypes: An enumeration value representing the axis type.
        """
        GetDllLibXls().XlsPivotField_get_Axis.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_Axis.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_Axis, self.Ptr)
        objwraped = AxisTypes(ret)
        return objwraped

    @Axis.setter
    def Axis(self, value:'AxisTypes'):
        """Sets the axis type of the field.
        
        Args:
            value (AxisTypes): An enumeration value representing the axis type to set.
        """
        GetDllLibXls().XlsPivotField_set_Axis.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotField_set_Axis, self.Ptr, value.value)

    @property

    def NumberFormat(self)->str:
        """Gets the number format string for the field.
        
        Returns:
            str: The number format string.
        """
        GetDllLibXls().XlsPivotField_get_NumberFormat.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_NumberFormat.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPivotField_get_NumberFormat, self.Ptr))
        return ret


    @NumberFormat.setter
    def NumberFormat(self, value:str):
        """Sets the number format string for the field.
        
        Args:
            value (str): The number format string to set.
        """
        GetDllLibXls().XlsPivotField_set_NumberFormat.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPivotField_set_NumberFormat, self.Ptr, value)

    @property

    def Subtotals(self)->'SubtotalTypes':
        """Gets the subtotal calculation type for the field.
        
        Returns:
            SubtotalTypes: An enumeration value representing the subtotal calculation type.
        """
        GetDllLibXls().XlsPivotField_get_Subtotals.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_Subtotals.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_Subtotals, self.Ptr)
        objwraped = SubtotalTypes(ret)
        return objwraped

    @Subtotals.setter
    def Subtotals(self, value:'SubtotalTypes'):
        GetDllLibXls().XlsPivotField_set_Subtotals.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotField_set_Subtotals, self.Ptr, value.value)

    @property
    def CanDragToRow(self)->bool:
        """Gets whether the field can be dragged to the row area.
        
        Returns:
            bool: True if the field can be dragged to the row area; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_get_CanDragToRow.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_CanDragToRow.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_CanDragToRow, self.Ptr)
        return ret

    @CanDragToRow.setter
    def CanDragToRow(self, value:bool):
        """Sets whether the field can be dragged to the row area.
        
        Args:
            value (bool): True to allow the field to be dragged to the row area; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_set_CanDragToRow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_CanDragToRow, self.Ptr, value)

    @property
    def CanDragToColumn(self)->bool:
        """Gets whether the field can be dragged to the column area.
        
        Returns:
            bool: True if the field can be dragged to the column area; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_get_CanDragToColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_CanDragToColumn.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_CanDragToColumn, self.Ptr)
        return ret

    @CanDragToColumn.setter
    def CanDragToColumn(self, value:bool):
        """Sets whether the field can be dragged to the column area.
        
        Args:
            value (bool): True to allow the field to be dragged to the column area; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_set_CanDragToColumn.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_CanDragToColumn, self.Ptr, value)

    @property
    def CanDragToPage(self)->bool:
        """Gets whether the field can be dragged to the page area.
        
        Returns:
            bool: True if the field can be dragged to the page area; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_get_CanDragToPage.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_CanDragToPage.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_CanDragToPage, self.Ptr)
        return ret

    @CanDragToPage.setter
    def CanDragToPage(self, value:bool):
        """Sets whether the field can be dragged to the page area.
        
        Args:
            value (bool): True to allow the field to be dragged to the page area; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_set_CanDragToPage.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_CanDragToPage, self.Ptr, value)

    @property
    def CanDragOff(self)->bool:
        """Gets whether the field can be removed from the PivotTable.
        
        Returns:
            bool: True if the field can be removed from the PivotTable; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_get_CanDragOff.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_CanDragOff.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_CanDragOff, self.Ptr)
        return ret

    @CanDragOff.setter
    def CanDragOff(self, value:bool):
        """Sets whether the field can be removed from the PivotTable.
        
        Args:
            value (bool): True to allow the field to be removed from the PivotTable; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_set_CanDragOff.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_CanDragOff, self.Ptr, value)

    @property
    def CanDragToData(self)->bool:
        """Gets whether the field can be dragged to the data area.
        
        Returns:
            bool: True if the field can be dragged to the data area; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_get_CanDragToData.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_CanDragToData.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_CanDragToData, self.Ptr)
        return ret

    @CanDragToData.setter
    def CanDragToData(self, value:bool):
        """Sets whether the field can be dragged to the data area.
        
        Args:
            value (bool): True to allow the field to be dragged to the data area; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_set_CanDragToData.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_CanDragToData, self.Ptr, value)

    @property
    def DataField(self)->bool:
        """Gets whether the field is in the data area of the PivotTable.
        
        Returns:
            bool: True if the field is in the data area; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_get_DataField.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_DataField.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_DataField, self.Ptr)
        return ret

    @DataField.setter
    def DataField(self, value:bool):
        """Sets whether the field is in the data area of the PivotTable.
        
        Args:
            value (bool): True to place the field in the data area; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_set_DataField.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_DataField, self.Ptr, value)

    @property
    def IsDataField(self)->bool:
        """Gets whether the field is a data field.
        
        Returns:
            bool: True if the field is a data field; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_get_IsDataField.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_IsDataField.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_IsDataField, self.Ptr)
        return ret

    @property
    def NumberFormatIndex(self)->int:
        """Gets the index of the number format applied to the field.
        
        Returns:
            int: The index of the number format.
        """
        GetDllLibXls().XlsPivotField_get_NumberFormatIndex.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_NumberFormatIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_NumberFormatIndex, self.Ptr)
        return ret

    @NumberFormatIndex.setter
    def NumberFormatIndex(self, value:int):
        """Sets the index of the number format applied to the field.
        
        Args:
            value (int): The index of the number format to apply.
        """
        GetDllLibXls().XlsPivotField_set_NumberFormatIndex.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotField_set_NumberFormatIndex, self.Ptr, value)

    @property

    def SubtotalCaption(self)->str:
        """Gets the custom text that is displayed for the subtotals caption.
        
        Returns:
            str: The custom text for the subtotals caption.
        """
        GetDllLibXls().XlsPivotField_get_SubtotalCaption.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_SubtotalCaption.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPivotField_get_SubtotalCaption, self.Ptr))
        return ret


    @SubtotalCaption.setter
    def SubtotalCaption(self, value:str):
        """Sets the custom text that is displayed for the subtotals caption.
        
        Args:
            value (str): The custom text for the subtotals caption.
        """
        GetDllLibXls().XlsPivotField_set_SubtotalCaption.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPivotField_set_SubtotalCaption, self.Ptr, value)

    @property
    def SubtotalTop(self)->bool:
        """Gets whether subtotals are displayed at the top of each group.
        
        Returns:
            bool: True if subtotals are displayed at the top; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_get_SubtotalTop.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_SubtotalTop.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_SubtotalTop, self.Ptr)
        return ret

    @SubtotalTop.setter
    def SubtotalTop(self, value:bool):
        """Sets whether subtotals are displayed at the top of each group.
        
        Args:
            value (bool): True to display subtotals at the top; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_set_SubtotalTop.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_SubtotalTop, self.Ptr, value)

    @property
    def IsAutoShow(self)->bool:
        """Gets whether AutoShow is enabled for the field.
        
        Returns:
            bool: True if AutoShow is enabled; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_get_IsAutoShow.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_IsAutoShow.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_IsAutoShow, self.Ptr)
        return ret

    @IsAutoShow.setter
    def IsAutoShow(self, value:bool):
        """Sets whether AutoShow is enabled for the field.
        
        Args:
            value (bool): True to enable AutoShow; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_set_IsAutoShow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_IsAutoShow, self.Ptr, value)

    @property
    def IsDragToHide(self)->bool:
        """Gets whether the user can remove the field from view.
        
        Returns:
            bool: True if the user can remove the field from view; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_get_IsDragToHide.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_IsDragToHide.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_IsDragToHide, self.Ptr)
        return ret

    @IsDragToHide.setter
    def IsDragToHide(self, value:bool):
        """Sets whether the user can remove the field from view.
        
        Args:
            value (bool): True to allow the user to remove the field from view; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_set_IsDragToHide.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_IsDragToHide, self.Ptr, value)

    @property
    def ShowNewItemsInFilter(self)->bool:
        """Gets whether manual filter is in inclusive mode.
        
        Returns:
            bool: True if manual filter is in inclusive mode; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_get_ShowNewItemsInFilter.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_ShowNewItemsInFilter.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_ShowNewItemsInFilter, self.Ptr)
        return ret

    @ShowNewItemsInFilter.setter
    def ShowNewItemsInFilter(self, value:bool):
        """Sets whether manual filter is in inclusive mode.
        
        Args:
            value (bool): True to set manual filter to inclusive mode; otherwise, False.
        """
        GetDllLibXls().XlsPivotField_set_ShowNewItemsInFilter.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_ShowNewItemsInFilter, self.Ptr, value)

    @property
    def ShowNewItemsOnRefresh(self)->bool:
        """
        Specifies a boolean value that indicates whether new items that appear after a refresh should be hidden by default.

        """
        GetDllLibXls().XlsPivotField_get_ShowNewItemsOnRefresh.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_ShowNewItemsOnRefresh.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_ShowNewItemsOnRefresh, self.Ptr)
        return ret

    @ShowNewItemsOnRefresh.setter
    def ShowNewItemsOnRefresh(self, value:bool):
        GetDllLibXls().XlsPivotField_set_ShowNewItemsOnRefresh.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_ShowNewItemsOnRefresh, self.Ptr, value)

    @property
    def ShowBlankRow(self)->bool:
        """
        True if a blank row is inserted after the specified row field in a PivotTable report.

        """
        GetDllLibXls().XlsPivotField_get_ShowBlankRow.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_ShowBlankRow.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_ShowBlankRow, self.Ptr)
        return ret

    @ShowBlankRow.setter
    def ShowBlankRow(self, value:bool):
        GetDllLibXls().XlsPivotField_set_ShowBlankRow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_ShowBlankRow, self.Ptr, value)

    @property
    def ShowPageBreak(self)->bool:
        """
        True if a page break is inserted after each field.

        """
        GetDllLibXls().XlsPivotField_get_ShowPageBreak.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_ShowPageBreak.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_ShowPageBreak, self.Ptr)
        return ret

    @ShowPageBreak.setter
    def ShowPageBreak(self, value:bool):
        GetDllLibXls().XlsPivotField_set_ShowPageBreak.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_ShowPageBreak, self.Ptr, value)

    @property
    def ItemsPerPage(self)->int:
        """
        Specifies the number of items showed per page in the PivotTable.

        """
        GetDllLibXls().XlsPivotField_get_ItemsPerPage.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_ItemsPerPage.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_ItemsPerPage, self.Ptr)
        return ret

    @ItemsPerPage.setter
    def ItemsPerPage(self, value:int):
        GetDllLibXls().XlsPivotField_set_ItemsPerPage.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotField_set_ItemsPerPage, self.Ptr, value)

    @property
    def IsMultiSelected(self)->bool:
        """
        Specifies a boolean value that indicates whether the field can have multiple items selected in the page field.

        """
        GetDllLibXls().XlsPivotField_get_IsMultiSelected.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_IsMultiSelected.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_IsMultiSelected, self.Ptr)
        return ret

    @IsMultiSelected.setter
    def IsMultiSelected(self, value:bool):
        GetDllLibXls().XlsPivotField_set_IsMultiSelected.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_IsMultiSelected, self.Ptr, value)

    @property
    def IsShowAllItems(self)->bool:
        """
        Show all items for this field.

        """
        GetDllLibXls().XlsPivotField_get_IsShowAllItems.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_IsShowAllItems.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_IsShowAllItems, self.Ptr)
        return ret

    @IsShowAllItems.setter
    def IsShowAllItems(self, value:bool):
        GetDllLibXls().XlsPivotField_set_IsShowAllItems.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_IsShowAllItems, self.Ptr, value)

    @property
    def ShowOutline(self)->bool:
        """
        Specifies a boolean value that indicates whether the items in this field should be shown in Outline form. If the parameter is true, the field layout is "Show item labels in outline form". If the parameter is false, the field layout is "Show item labels in tabular form".

        """
        GetDllLibXls().XlsPivotField_get_ShowOutline.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_ShowOutline.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_ShowOutline, self.Ptr)
        return ret

    @ShowOutline.setter
    def ShowOutline(self, value:bool):
        GetDllLibXls().XlsPivotField_set_ShowOutline.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_ShowOutline, self.Ptr, value)

    @property
    def ShowDropDown(self)->bool:
        """
        True if the flag for the specified PivotTable field or PivotTable item is set to "drilled" (expanded, or visible).

        """
        GetDllLibXls().XlsPivotField_get_ShowDropDown.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_ShowDropDown.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_ShowDropDown, self.Ptr)
        return ret

    @ShowDropDown.setter
    def ShowDropDown(self, value:bool):
        GetDllLibXls().XlsPivotField_set_ShowDropDown.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_ShowDropDown, self.Ptr, value)

    @property
    def ShowPropAsCaption(self)->bool:
        """
        Specifies a boolean value that indicates whether to show the property as a member caption.

        """
        GetDllLibXls().XlsPivotField_get_ShowPropAsCaption.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_ShowPropAsCaption.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_ShowPropAsCaption, self.Ptr)
        return ret

    @ShowPropAsCaption.setter
    def ShowPropAsCaption(self, value:bool):
        GetDllLibXls().XlsPivotField_set_ShowPropAsCaption.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_ShowPropAsCaption, self.Ptr, value)

    @property
    def ShowToolTip(self)->bool:
        """
        Specifies a boolean value that indicates whether to show the member property value in a tooltip on the appropriate PivotTable cells.

        """
        GetDllLibXls().XlsPivotField_get_ShowToolTip.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_ShowToolTip.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_ShowToolTip, self.Ptr)
        return ret

    @ShowToolTip.setter
    def ShowToolTip(self, value:bool):
        GetDllLibXls().XlsPivotField_set_ShowToolTip.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_ShowToolTip, self.Ptr, value)

    @property

    def SortType(self)->PivotFieldSortType:
        """
        Specifies the type of sort that is applied to this field.

        """
        GetDllLibXls().XlsPivotField_get_SortType.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_SortType.restype=c_int
        intPtr = CallCFunction(GetDllLibXls().XlsPivotField_get_SortType, self.Ptr)
        ret = None if intPtr==None else PivotFieldSortType(intPtr)
        return ret



    @SortType.setter
    def SortType(self, value:PivotFieldSortType):
        GetDllLibXls().XlsPivotField_set_SortType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotField_set_SortType, self.Ptr, value.value)


    @property

    def Caption(self)->str:
        """
        Specifies the unique name of the member property to be used as a caption for the field and field items.

        """
        GetDllLibXls().XlsPivotField_get_Caption.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_Caption.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPivotField_get_Caption, self.Ptr))
        return ret


    @Caption.setter
    def Caption(self, value:str):
        GetDllLibXls().XlsPivotField_set_Caption.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPivotField_set_Caption, self.Ptr, value)

    @property
    def Compact(self)->bool:
        """
        Specifies a boolean value that indicates whether the application will display fields compactly in the sheet on which this PivotTable resides

        """
        GetDllLibXls().XlsPivotField_get_Compact.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_Compact.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_Compact, self.Ptr)
        return ret

    @Compact.setter
    def Compact(self, value:bool):
        GetDllLibXls().XlsPivotField_set_Compact.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_Compact, self.Ptr, value)

    @property

    def Formula(self)->str:
        """
        Specifies the formula for the calculated field

        """
        GetDllLibXls().XlsPivotField_get_Formula.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_Formula.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPivotField_get_Formula, self.Ptr))
        return ret


    @Formula.setter
    def Formula(self, value:str):
        GetDllLibXls().XlsPivotField_set_Formula.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPivotField_set_Formula, self.Ptr, value)

    @property
    def IsFormulaField(self)->bool:
        """
        Indicates whether this field is formula field

        """
        GetDllLibXls().XlsPivotField_get_IsFormulaField.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_IsFormulaField.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_IsFormulaField, self.Ptr)
        return ret

    @property
    def RepeatItemLabels(self)->bool:
        """
        True if the field repeat item labels.

        """
        GetDllLibXls().XlsPivotField_get_RepeatItemLabels.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_RepeatItemLabels.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_RepeatItemLabels, self.Ptr)
        return ret

    @RepeatItemLabels.setter
    def RepeatItemLabels(self, value:bool):
        GetDllLibXls().XlsPivotField_set_RepeatItemLabels.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_set_RepeatItemLabels, self.Ptr, value)

    @property

    def AutoSort(self)->'AutoSortScope':
        """
        Preserves the sorting elements of the field

        """
        GetDllLibXls().XlsPivotField_get_AutoSort.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_AutoSort.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotField_get_AutoSort, self.Ptr)
        ret = None if intPtr==None else AutoSortScope(intPtr)
        return ret


    @AutoSort.setter
    def AutoSort(self, value:'AutoSortScope'):
        GetDllLibXls().XlsPivotField_set_AutoSort.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsPivotField_set_AutoSort, self.Ptr, value.Ptr)

    @property

    def ShowDataAs(self)->'PivotFieldFormatType':
        """

        """
        GetDllLibXls().XlsPivotField_get_ShowDataAs.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotField_get_ShowDataAs.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotField_get_ShowDataAs, self.Ptr)
        objwraped = PivotFieldFormatType(ret)
        return objwraped

    @ShowDataAs.setter
    def ShowDataAs(self, value:'PivotFieldFormatType'):
        GetDllLibXls().XlsPivotField_set_ShowDataAs.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotField_set_ShowDataAs, self.Ptr, value.value)


    def AddItemOption(self ,index:int):
        """Adds an item option at the specified index.
        
        This method represents the index of item and item options key pairs.
        
        Args:
            index (int): The index at which to add the item option.
        """
        
        GetDllLibXls().XlsPivotField_AddItemOption.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsPivotField_AddItemOption, self.Ptr, index)


    def IsHiddenItemDetail(self ,index:int)->bool:
        """
        Indicates whether the specific PivotItem is hidden detail. Must call after pivottable CalculateData function.

        Args:
            index: the index of the pivotItem in the pivotField.

        Returns:
            whether the specific PivotItem is hidden detail

        """
        
        GetDllLibXls().XlsPivotField_IsHiddenItemDetail.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsPivotField_IsHiddenItemDetail.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_IsHiddenItemDetail, self.Ptr, index)
        return ret

    @dispatch

    def HideItemDetail(self ,index:int,isHiddenDetail:bool):
        """
        Sets whether the specific PivotItem in a pivot field is hidden detail. Must call after pivottable CalculateData function.

        Args:
            index: the index of the pivotItem in the pivotField.
            isHiddenDetail: whether the specific PivotItem is hidden

        """
        
        GetDllLibXls().XlsPivotField_HideItemDetail.argtypes=[c_void_p ,c_int,c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_HideItemDetail, self.Ptr, index,isHiddenDetail)

    @dispatch

    def HideItemDetail(self ,itemValue:str,isHiddenDetail:bool):
        """
        Sets whether the PivotItems in a pivot field is hidden detail.That is collapse/expand this field. Must call after pivottable CalculateData function.

        Args:
            itemValue: the value of the pivotItem in the pivotField.
            isHiddenDetail: whether the specific PivotItem is hidden

        """
        
        GetDllLibXls().XlsPivotField_HideItemDetailII.argtypes=[c_void_p ,c_void_p,c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_HideItemDetailII, self.Ptr, itemValue,isHiddenDetail)


    def HideDetail(self ,isHiddenDetail:bool):
        """
        Sets whether the PivotItems in a pivot field is hidden detail.That is collapse/expand this field. Must call after pivottable CalculateData function.

        Args:
            isHiddenDetail: whether DetailItems is hidden

        """
        
        GetDllLibXls().XlsPivotField_HideDetail.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_HideDetail, self.Ptr, isHiddenDetail)


    def IsHiddenItem(self ,index:int)->bool:
        """
        Indicates whether the specific PivotItem is hidden. Must call after pivottable CalculateData function.

        Args:
            index: the index of the pivotItem in the pivotField.

        Returns:
            whether the specific PivotItem is hidden

        """
        
        GetDllLibXls().XlsPivotField_IsHiddenItem.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsPivotField_IsHiddenItem.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotField_IsHiddenItem, self.Ptr, index)
        return ret

    @dispatch

    def HideItem(self ,index:int,isHidden:bool):
        """
        Sets whether the specific PivotItem in a data field is hidden. Must call after pivottable CalculateData function.

        Args:
            index: the index of the pivotItem in the pivotField.
            isHidden: whether the specific PivotItem is hidden

        """
        
        GetDllLibXls().XlsPivotField_HideItem.argtypes=[c_void_p ,c_int,c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_HideItem, self.Ptr, index,isHidden)


    def HideAllItem(self ,isHidden:bool):
        """
        Sets whether the all PivotItem in a data field is hidden. Must call after pivottable CalculateData function.

        Args:
            isHidden: whether the specific PivotItem is hidden

        """
        
        GetDllLibXls().XlsPivotField_HideAllItem.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_HideAllItem, self.Ptr, isHidden)

    @dispatch

    def HideItem(self ,itemValue:str,isHidden:bool):
        """
        Sets whether the specific PivotItem in a data field is hidden. Must call after pivottable CalculateData function.

        Args:
            itemValue: the value of the pivotItem in the pivotField.
            isHidden: whether the specific PivotItem is hidden

        """
        
        GetDllLibXls().XlsPivotField_HideItemII.argtypes=[c_void_p ,c_void_p,c_bool]
        CallCFunction(GetDllLibXls().XlsPivotField_HideItemII, self.Ptr, itemValue,isHidden)


    def Sort(self ,isAscendSort:bool,sortByField:'PivotDataField'):
        """Sorts row fields or column fields by data field.
        
        Args:
            isAscendSort (bool): True for ascending sort; False for descending sort.
            sortByField (PivotDataField): The data field to sort by.
        """
        intPtrsortByField:c_void_p = sortByField.Ptr

        GetDllLibXls().XlsPivotField_Sort.argtypes=[c_void_p ,c_bool,c_void_p]
        CallCFunction(GetDllLibXls().XlsPivotField_Sort, self.Ptr, isAscendSort,intPtrsortByField)


    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """Creates a clone of this pivot field.
        
        Args:
            parent (SpireObject): The parent object for the cloned field.
            
        Returns:
            SpireObject: The cloned pivot field.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsPivotField_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsPivotField_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotField_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


