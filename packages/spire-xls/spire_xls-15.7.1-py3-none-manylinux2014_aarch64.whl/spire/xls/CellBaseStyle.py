from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class CellBaseStyle (  AddtionalFormatWrapper, IInternalAddtionalFormat) :
    """Represents the base class for cell styles in an Excel worksheet.
    
    This class extends AddtionalFormatWrapper and implements IInternalAddtionalFormat,
    providing basic functionality for cell formatting and styling. It serves as a base
    for more specific cell style classes and includes methods for managing style updates.
    """
    def BeginUpdate(self):
        """Begins a batch update operation on the cell style.
        
        This method marks the beginning of a series of changes to the style properties.
        Changes made between BeginUpdate and EndUpdate are applied together for better performance.
        """
        GetDllLibXls().CellBaseStyle_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().CellBaseStyle_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """Ends a batch update operation on the cell style.
        
        This method completes the batch update started with BeginUpdate and
        applies all pending changes to the style properties.
        """
        GetDllLibXls().CellBaseStyle_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().CellBaseStyle_EndUpdate, self.Ptr)

