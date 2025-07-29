from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class PivotConditionalFormat (SpireObject) :
    """Represents conditional formatting in a PivotTable.
    
    This class provides functionality for managing conditional formatting rules
    that apply to cells in a PivotTable, allowing for visual highlighting of data
    based on specified conditions.
    """
    @property

    def scope(self)->'ConditionalFormatScope':
        """Gets the scope of the conditional formatting.
        
        Returns:
            ConditionalFormatScope: An enumeration value representing the scope of the conditional formatting.
        """
        GetDllLibXls().PivotConditionalFormat_get_scope.argtypes=[c_void_p]
        GetDllLibXls().PivotConditionalFormat_get_scope.restype=c_int
        ret = CallCFunction(GetDllLibXls().PivotConditionalFormat_get_scope, self.Ptr)
        objwraped = ConditionalFormatScope(ret)
        return objwraped

    @scope.setter
    def scope(self, value:'ConditionalFormatScope'):
        """Sets the scope of the conditional formatting.
        
        Args:
            value (ConditionalFormatScope): An enumeration value representing the scope to set.
        """
        GetDllLibXls().PivotConditionalFormat_set_scope.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().PivotConditionalFormat_set_scope, self.Ptr, value.value)


    def get_Item(self ,index:int)->'IConditionalFormat':
        """Gets the conditional format at the specified index.
        
        Args:
            index (int): The zero-based index of the conditional format to retrieve.
            
        Returns:
            IConditionalFormat: The conditional format at the specified index.
        """
        
        GetDllLibXls().PivotConditionalFormat_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().PivotConditionalFormat_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().PivotConditionalFormat_get_Item, self.Ptr, index)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret



    def AddCondition(self)->'IConditionalFormat':
        """Adds a new conditional format to the collection.
        
        Returns:
            IConditionalFormat: The newly created conditional format.
        """
        GetDllLibXls().PivotConditionalFormat_AddCondition.argtypes=[c_void_p]
        GetDllLibXls().PivotConditionalFormat_AddCondition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().PivotConditionalFormat_AddCondition, self.Ptr)
        ret = None if intPtr==None else XlsConditionalFormat(intPtr)
        return ret


