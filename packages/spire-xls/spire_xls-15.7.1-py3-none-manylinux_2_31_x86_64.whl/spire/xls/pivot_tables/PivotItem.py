from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class PivotItem (SpireObject) :
    """Represents an item in a PivotField.
    
    This class provides functionality for managing individual items within a PivotField,
    including properties for controlling visibility, expansion state, and item type.
    """
    @property
    def HasChildItems(self)->bool:
        """Gets whether the item has child items.
        
        Returns:
            bool: True if the item has child items; otherwise, False.
        """
        GetDllLibXls().PivotItem_get_HasChildItems.argtypes=[c_void_p]
        GetDllLibXls().PivotItem_get_HasChildItems.restype=c_bool
        ret = CallCFunction(GetDllLibXls().PivotItem_get_HasChildItems, self.Ptr)
        return ret

    @HasChildItems.setter
    def HasChildItems(self, value:bool):
        """Sets whether the item has child items.
        
        Args:
            value (bool): True to indicate the item has child items; otherwise, False.
        """
        GetDllLibXls().PivotItem_set_HasChildItems.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().PivotItem_set_HasChildItems, self.Ptr, value)

    @property
    def IsExpaned(self)->bool:
        """Gets whether the item is expanded to show its child items.
        
        Returns:
            bool: True if the item is expanded; otherwise, False.
        """
        GetDllLibXls().PivotItem_get_IsExpaned.argtypes=[c_void_p]
        GetDllLibXls().PivotItem_get_IsExpaned.restype=c_bool
        ret = CallCFunction(GetDllLibXls().PivotItem_get_IsExpaned, self.Ptr)
        return ret

    @IsExpaned.setter
    def IsExpaned(self, value:bool):
        """Sets whether the item is expanded to show its child items.
        
        Args:
            value (bool): True to expand the item; otherwise, False.
        """
        GetDllLibXls().PivotItem_set_IsExpaned.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().PivotItem_set_IsExpaned, self.Ptr, value)

    @property
    def DrillAcross(self)->bool:
        """Gets whether the item allows drill across functionality.
        
        Returns:
            bool: True if drill across is enabled; otherwise, False.
        """
        GetDllLibXls().PivotItem_get_DrillAcross.argtypes=[c_void_p]
        GetDllLibXls().PivotItem_get_DrillAcross.restype=c_bool
        ret = CallCFunction(GetDllLibXls().PivotItem_get_DrillAcross, self.Ptr)
        return ret

    @DrillAcross.setter
    def DrillAcross(self, value:bool):
        """Sets whether the item allows drill across functionality.
        
        Args:
            value (bool): True to enable drill across; otherwise, False.
        """
        GetDllLibXls().PivotItem_set_DrillAcross.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().PivotItem_set_DrillAcross, self.Ptr, value)

    @property
    def IsCalculatedItem(self)->bool:
        """Gets whether the item is a calculated item.
        
        Returns:
            bool: True if the item is calculated; otherwise, False.
        """
        GetDllLibXls().PivotItem_get_IsCalculatedItem.argtypes=[c_void_p]
        GetDllLibXls().PivotItem_get_IsCalculatedItem.restype=c_bool
        ret = CallCFunction(GetDllLibXls().PivotItem_get_IsCalculatedItem, self.Ptr)
        return ret

    @IsCalculatedItem.setter
    def IsCalculatedItem(self, value:bool):
        """Sets whether the item is a calculated item.
        
        Args:
            value (bool): True to mark as a calculated item; otherwise, False.
        """
        GetDllLibXls().PivotItem_set_IsCalculatedItem.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().PivotItem_set_IsCalculatedItem, self.Ptr, value)

    @property
    def IsHidden(self)->bool:
        """Gets whether the item is hidden in the PivotTable.
        
        Returns:
            bool: True if the item is hidden; otherwise, False.
        """
        GetDllLibXls().PivotItem_get_IsHidden.argtypes=[c_void_p]
        GetDllLibXls().PivotItem_get_IsHidden.restype=c_bool
        ret = CallCFunction(GetDllLibXls().PivotItem_get_IsHidden, self.Ptr)
        return ret

    @IsHidden.setter
    def IsHidden(self, value:bool):
        """Sets whether the item is hidden in the PivotTable.
        
        Args:
            value (bool): True to hide the item; otherwise, False.
        """
        GetDllLibXls().PivotItem_set_IsHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().PivotItem_set_IsHidden, self.Ptr, value)

    @property
    def IsMissing(self)->bool:
        """Gets whether the item represents missing data.
        
        Returns:
            bool: True if the item represents missing data; otherwise, False.
        """
        GetDllLibXls().PivotItem_get_IsMissing.argtypes=[c_void_p]
        GetDllLibXls().PivotItem_get_IsMissing.restype=c_bool
        ret = CallCFunction(GetDllLibXls().PivotItem_get_IsMissing, self.Ptr)
        return ret

    @IsMissing.setter
    def IsMissing(self, value:bool):
        """Sets whether the item represents missing data.
        
        Args:
            value (bool): True to mark as missing data; otherwise, False.
        """
        GetDllLibXls().PivotItem_set_IsMissing.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().PivotItem_set_IsMissing, self.Ptr, value)

    @property

    def UserCaption(self)->str:
        """Gets the user-defined caption for the item.
        
        Returns:
            str: The user-defined caption.
        """
        GetDllLibXls().PivotItem_get_UserCaption.argtypes=[c_void_p]
        GetDllLibXls().PivotItem_get_UserCaption.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().PivotItem_get_UserCaption, self.Ptr))
        return ret


    @property
    def IsChar(self)->bool:
        """Gets whether the item represents character data.
        
        Returns:
            bool: True if the item represents character data; otherwise, False.
        """
        GetDllLibXls().PivotItem_get_IsChar.argtypes=[c_void_p]
        GetDllLibXls().PivotItem_get_IsChar.restype=c_bool
        ret = CallCFunction(GetDllLibXls().PivotItem_get_IsChar, self.Ptr)
        return ret

    @IsChar.setter
    def IsChar(self, value:bool):
        """Sets whether the item represents character data.
        
        Args:
            value (bool): True to mark as character data; otherwise, False.
        """
        GetDllLibXls().PivotItem_set_IsChar.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().PivotItem_set_IsChar, self.Ptr, value)

    @property
    def IsHiddenDetails(self)->bool:
        """Gets whether the details of the item are hidden.
        
        Returns:
            bool: True if the details are hidden; otherwise, False.
        """
        GetDllLibXls().PivotItem_get_IsHiddenDetails.argtypes=[c_void_p]
        GetDllLibXls().PivotItem_get_IsHiddenDetails.restype=c_bool
        ret = CallCFunction(GetDllLibXls().PivotItem_get_IsHiddenDetails, self.Ptr)
        return ret

    @IsHiddenDetails.setter
    def IsHiddenDetails(self, value:bool):
        """Sets whether the details of the item are hidden.
        
        Args:
            value (bool): True to hide details; otherwise, False.
        """
        GetDllLibXls().PivotItem_set_IsHiddenDetails.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().PivotItem_set_IsHiddenDetails, self.Ptr, value)

    @property

    def ItemType(self)->'PivotItemType':
        """Gets the type of the pivot item.
        
        Returns:
            PivotItemType: An enumeration value representing the item type.
        """
        GetDllLibXls().PivotItem_get_ItemType.argtypes=[c_void_p]
        GetDllLibXls().PivotItem_get_ItemType.restype=c_int
        ret = CallCFunction(GetDllLibXls().PivotItem_get_ItemType, self.Ptr)
        objwraped = PivotItemType(ret)
        return objwraped

    @ItemType.setter
    def ItemType(self, value:'PivotItemType'):
        """Sets the type of the pivot item.
        
        Args:
            value (PivotItemType): An enumeration value representing the item type to set.
        """
        GetDllLibXls().PivotItem_set_ItemType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().PivotItem_set_ItemType, self.Ptr, value.value)

