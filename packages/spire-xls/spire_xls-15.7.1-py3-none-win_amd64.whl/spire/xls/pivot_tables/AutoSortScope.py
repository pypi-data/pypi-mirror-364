from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class AutoSortScope (SpireObject) :
    """Represents the scope for auto-sorting in a PivotField.
    
    This class defines the scope for automatic sorting operations in a PivotField,
    allowing for control over which items are included in the sort operation.
    """
    @property

    def Parent(self)->'PivotField':
        """Gets the parent PivotField of this AutoSortScope.
        
        Returns:
            PivotField: The parent PivotField object that contains this AutoSortScope.
        """
        GetDllLibXls().AutoSortScope_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().AutoSortScope_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().AutoSortScope_get_Parent, self.Ptr)
        ret = None if intPtr==None else PivotField(intPtr)
        return ret


