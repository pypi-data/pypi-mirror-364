from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *

class IPivotTableOptions (SpireObject) :
    """
    Represents the options and settings for a PivotTable.
    """
    def RepeatAllItemLabels(self, value:bool):
        """Sets whether to repeat all item labels in the PivotTable.
        
        Args:
            value (bool): True to repeat all item labels; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_set_RepeatAllItemLabels.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_RepeatAllItemLabels, self.Ptr, value)

    @property
    def ShowAsteriskTotals(self)->bool:
        """
        Indicates whether asterisks are shown for totals in the PivotTable.

        Returns:
            bool: True if asterisks are shown; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_get_ShowAsteriskTotals.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_ShowAsteriskTotals.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_ShowAsteriskTotals, self.Ptr)
        return ret

    @ShowAsteriskTotals.setter
    def ShowAsteriskTotals(self, value:bool):
        """Sets whether to show asterisks for totals in the PivotTable.
        
        Args:
            value (bool): True to show asterisks for totals; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_set_ShowAsteriskTotals.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_ShowAsteriskTotals, self.Ptr, value)

    @property
    def ColumnHeaderCaption(self)->str:
        """
        Gets or sets the caption for the column header in the PivotTable.

        Returns:
            str: The column header caption.
        """
        GetDllLibXls().IPivotTableOptions_get_ColumnHeaderCaption.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_ColumnHeaderCaption.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().IPivotTableOptions_get_ColumnHeaderCaption, self.Ptr))
        return ret

    @ColumnHeaderCaption.setter
    def ColumnHeaderCaption(self, value:str):
        """Sets the caption for the column header in the PivotTable.
        
        Args:
            value (str): The caption to set for the column header.
        """
        GetDllLibXls().IPivotTableOptions_set_ColumnHeaderCaption.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_ColumnHeaderCaption, self.Ptr, value)

    @property
    def RowHeaderCaption(self)->str:
        """
        Gets or sets the caption for the row header in the PivotTable.

        Returns:
            str: The row header caption.
        """
        GetDllLibXls().IPivotTableOptions_get_RowHeaderCaption.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_RowHeaderCaption.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().IPivotTableOptions_get_RowHeaderCaption, self.Ptr))
        return ret

    @RowHeaderCaption.setter
    def RowHeaderCaption(self, value:str):
        """Sets the caption for the row header in the PivotTable.
        
        Args:
            value (str): The caption to set for the row header.
        """
        GetDllLibXls().IPivotTableOptions_set_RowHeaderCaption.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_RowHeaderCaption, self.Ptr, value)

    @property
    def ShowCustomSortList(self)->bool:
        """
        Indicates whether the custom sort list is shown in the PivotTable.

        Returns:
            bool: True if the custom sort list is shown; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_get_ShowCustomSortList.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_ShowCustomSortList.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_ShowCustomSortList, self.Ptr)
        return ret

    @ShowCustomSortList.setter
    def ShowCustomSortList(self, value:bool):
        """Sets whether to show the custom sort list in the PivotTable.
        
        Args:
            value (bool): True to show the custom sort list; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_set_ShowCustomSortList.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_ShowCustomSortList, self.Ptr, value)

    @property
    def ShowFieldList(self)->bool:
        """
        Indicates whether the field list is shown in the PivotTable.

        Returns:
            bool: True if the field list is shown; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_get_ShowFieldList.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_ShowFieldList.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_ShowFieldList, self.Ptr)
        return ret

    @ShowFieldList.setter
    def ShowFieldList(self, value:bool):
        """Sets whether to show the field list in the PivotTable.
        
        Args:
            value (bool): True to show the field list; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_set_ShowFieldList.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_ShowFieldList, self.Ptr, value)

    @property
    def ShowGridDropZone(self)->bool:
        """
        Indicates whether the grid drop zone is shown in the PivotTable.

        Returns:
            bool: True if the grid drop zone is shown; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_get_ShowGridDropZone.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_ShowGridDropZone.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_ShowGridDropZone, self.Ptr)
        return ret

    @ShowGridDropZone.setter
    def ShowGridDropZone(self, value:bool):
        GetDllLibXls().IPivotTableOptions_set_ShowGridDropZone.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_ShowGridDropZone, self.Ptr, value)

    @property
    def IsDataEditable(self)->bool:
        """
        Indicates whether the data in the PivotTable is editable.

        Returns:
            bool: True if the data is editable; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_get_IsDataEditable.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_IsDataEditable.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_IsDataEditable, self.Ptr)
        return ret

    @IsDataEditable.setter
    def IsDataEditable(self, value:bool):
        GetDllLibXls().IPivotTableOptions_set_IsDataEditable.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_IsDataEditable, self.Ptr, value)

    @property
    def EnableFieldProperties(self)->bool:
        """
        Indicates whether field properties are enabled in the PivotTable.

        Returns:
            bool: True if field properties are enabled; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_get_EnableFieldProperties.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_EnableFieldProperties.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_EnableFieldProperties, self.Ptr)
        return ret

    @EnableFieldProperties.setter
    def EnableFieldProperties(self, value:bool):
        GetDllLibXls().IPivotTableOptions_set_EnableFieldProperties.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_EnableFieldProperties, self.Ptr, value)

    @property
    def Indent(self)->'UInt32':
        """
        Gets or sets the indent value for the PivotTable.

        Returns:
            UInt32: The indent value.
        """
        GetDllLibXls().IPivotTableOptions_get_Indent.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_Indent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IPivotTableOptions_get_Indent, self.Ptr)
        ret = None if intPtr==None else UInt32(intPtr)
        return ret

    @Indent.setter
    def Indent(self, value:'UInt32'):
        GetDllLibXls().IPivotTableOptions_set_Indent.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_Indent, self.Ptr, value.Ptr)

    @property
    def ErrorString(self)->str:
        """
        Gets or sets the error string displayed in the PivotTable.

        Returns:
            str: The error string.
        """
        GetDllLibXls().IPivotTableOptions_get_ErrorString.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_ErrorString.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().IPivotTableOptions_get_ErrorString, self.Ptr))
        return ret

    @ErrorString.setter
    def ErrorString(self, value:str):
        GetDllLibXls().IPivotTableOptions_set_ErrorString.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_ErrorString, self.Ptr, value)

    @property
    def DisplayErrorString(self)->bool:
        """
        Indicates whether the error string is displayed in the PivotTable.

        Returns:
            bool: True if the error string is displayed; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_get_DisplayErrorString.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_DisplayErrorString.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_DisplayErrorString, self.Ptr)
        return ret

    @DisplayErrorString.setter
    def DisplayErrorString(self, value:bool):
        GetDllLibXls().IPivotTableOptions_set_DisplayErrorString.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_DisplayErrorString, self.Ptr, value)

    @property
    def MergeLabels(self)->bool:
        """
        Indicates whether labels are merged in the PivotTable.

        Returns:
            bool: True if labels are merged; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_get_MergeLabels.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_MergeLabels.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_MergeLabels, self.Ptr)
        return ret

    @MergeLabels.setter
    def MergeLabels(self, value:bool):
        GetDllLibXls().IPivotTableOptions_set_MergeLabels.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_MergeLabels, self.Ptr, value)

    @property
    def PageFieldWrapCount(self)->int:
        """
        Gets or sets the number of page fields to wrap in the PivotTable.

        Returns:
            int: The number of page fields to wrap.
        """
        GetDllLibXls().IPivotTableOptions_get_PageFieldWrapCount.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_PageFieldWrapCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_PageFieldWrapCount, self.Ptr)
        return ret

    @PageFieldWrapCount.setter
    def PageFieldWrapCount(self, value:int):
        GetDllLibXls().IPivotTableOptions_set_PageFieldWrapCount.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_PageFieldWrapCount, self.Ptr, value)

    @property
    def PageFieldsOrder(self)->'PivotPageAreaFieldsOrderType':
        """
        Gets or sets the order of page fields in the PivotTable.

        Returns:
            PivotPageAreaFieldsOrderType: The order of page fields.
        """
        GetDllLibXls().IPivotTableOptions_get_PageFieldsOrder.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_PageFieldsOrder.restype=c_int
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_PageFieldsOrder, self.Ptr)
        objwraped = PivotPageAreaFieldsOrderType(ret)
        return objwraped

    @PageFieldsOrder.setter
    def PageFieldsOrder(self, value:'PivotPageAreaFieldsOrderType'):
        GetDllLibXls().IPivotTableOptions_set_PageFieldsOrder.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_PageFieldsOrder, self.Ptr, value.value)

    @property
    def DisplayNullString(self)->bool:
        """
        Indicates whether the null string is displayed in the PivotTable.

        Returns:
            bool: True if the null string is displayed; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_get_DisplayNullString.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_DisplayNullString.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_DisplayNullString, self.Ptr)
        return ret

    @DisplayNullString.setter
    def DisplayNullString(self, value:bool):
        GetDllLibXls().IPivotTableOptions_set_DisplayNullString.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_DisplayNullString, self.Ptr, value)

    @property
    def NullString(self)->str:
        """
        Gets or sets the string displayed for null values in the PivotTable.

        Returns:
            str: The null value string.
        """
        GetDllLibXls().IPivotTableOptions_get_NullString.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_NullString.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().IPivotTableOptions_get_NullString, self.Ptr))
        return ret

    @NullString.setter
    def NullString(self, value:str):
        GetDllLibXls().IPivotTableOptions_set_NullString.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_NullString, self.Ptr, value)

    @property
    def PreserveFormatting(self)->bool:
        """
        Indicates whether formatting is preserved in the PivotTable.

        Returns:
            bool: True if formatting is preserved; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_get_PreserveFormatting.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_PreserveFormatting.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_PreserveFormatting, self.Ptr)
        return ret

    @PreserveFormatting.setter
    def PreserveFormatting(self, value:bool):
        GetDllLibXls().IPivotTableOptions_set_PreserveFormatting.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_PreserveFormatting, self.Ptr, value)

    @property
    def IsAutoFormat(self)->bool:
        """
        Indicates whether the PivotTable has an autoformat applied. Checkbox "autofit column width on update"which in pivot table Options :Layout Format for Excel 2007

        """
        GetDllLibXls().IPivotTableOptions_get_IsAutoFormat.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_IsAutoFormat.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_IsAutoFormat, self.Ptr)
        return ret

    @IsAutoFormat.setter
    def IsAutoFormat(self, value:bool):
        GetDllLibXls().IPivotTableOptions_set_IsAutoFormat.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_IsAutoFormat, self.Ptr, value)

    @property
    def ShowTooltips(self)->bool:
        """
        Indicates whether tooltips are shown in the PivotTable.

        Returns:
            bool: True if tooltips are shown; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_get_ShowTooltips.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_ShowTooltips.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_ShowTooltips, self.Ptr)
        return ret

    @ShowTooltips.setter
    def ShowTooltips(self, value:bool):
        GetDllLibXls().IPivotTableOptions_set_ShowTooltips.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_ShowTooltips, self.Ptr, value)

    @property
    def DisplayFieldCaptions(self)->bool:
        """
        Indicates whether field captions are displayed in the PivotTable.

        Returns:
            bool: True if field captions are displayed; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_get_DisplayFieldCaptions.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_DisplayFieldCaptions.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_DisplayFieldCaptions, self.Ptr)
        return ret

    @DisplayFieldCaptions.setter
    def DisplayFieldCaptions(self, value:bool):
        GetDllLibXls().IPivotTableOptions_set_DisplayFieldCaptions.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_DisplayFieldCaptions, self.Ptr, value)

    @property
    def PrintTitles(self)->bool:
        """
        Indicates whether titles are printed in the PivotTable.

        Returns:
            bool: True if titles are printed; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_get_PrintTitles.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_PrintTitles.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_PrintTitles, self.Ptr)
        return ret

    @PrintTitles.setter
    def PrintTitles(self, value:bool):
        GetDllLibXls().IPivotTableOptions_set_PrintTitles.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_PrintTitles, self.Ptr, value)

    @property
    def IsSaveData(self)->bool:
        """
        Indicates whether data is saved with the PivotTable.

        Returns:
            bool: True if data is saved; otherwise, False.
        """
        GetDllLibXls().IPivotTableOptions_get_IsSaveData.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_IsSaveData.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_IsSaveData, self.Ptr)
        return ret

    @IsSaveData.setter
    def IsSaveData(self, value:bool):
        GetDllLibXls().IPivotTableOptions_set_IsSaveData.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_IsSaveData, self.Ptr, value)

    @property
    def ReportLayout(self)->'PivotTableLayoutType':
        """
        Gets or sets the report layout type for the PivotTable.

        Returns:
            PivotTableLayoutType: The report layout type.
        """
        GetDllLibXls().IPivotTableOptions_get_ReportLayout.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_ReportLayout.restype=c_int
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_ReportLayout, self.Ptr)
        objwraped = PivotTableLayoutType(ret)
        return objwraped

    @ReportLayout.setter
    def ReportLayout(self, value:'PivotTableLayoutType'):
        GetDllLibXls().IPivotTableOptions_set_ReportLayout.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_ReportLayout, self.Ptr, value.value)

    @property
    def RowLayout(self)->'PivotTableLayoutType':
        """

        """
        GetDllLibXls().IPivotTableOptions_get_RowLayout.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_RowLayout.restype=c_int
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_RowLayout, self.Ptr)
        objwraped = PivotTableLayoutType(ret)
        return objwraped

    @RowLayout.setter
    def RowLayout(self, value:'PivotTableLayoutType'):
        GetDllLibXls().IPivotTableOptions_set_RowLayout.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_RowLayout, self.Ptr, value.value)

    @property
    def ShowDrillIndicators(self)->bool:
        """

        """
        GetDllLibXls().IPivotTableOptions_get_ShowDrillIndicators.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_ShowDrillIndicators.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IPivotTableOptions_get_ShowDrillIndicators, self.Ptr)
        return ret

    @ShowDrillIndicators.setter
    def ShowDrillIndicators(self, value:bool):
        GetDllLibXls().IPivotTableOptions_set_ShowDrillIndicators.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_ShowDrillIndicators, self.Ptr, value)

    @property
    def DataPosition(self)->'Int16':
        """

        """
        GetDllLibXls().IPivotTableOptions_get_DataPosition.argtypes=[c_void_p]
        GetDllLibXls().IPivotTableOptions_get_DataPosition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IPivotTableOptions_get_DataPosition, self.Ptr)
        ret = None if intPtr==None else Int16(intPtr)
        return ret

    @DataPosition.setter
    def DataPosition(self, value:'Int16'):
        GetDllLibXls().IPivotTableOptions_set_DataPosition.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().IPivotTableOptions_set_DataPosition, self.Ptr, value.Ptr)

