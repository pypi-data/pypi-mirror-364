from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class PivotTableFields (  CollectionBase[XlsPivotField], ICloneParent, IPivotFields) :
    """Represents a collection of PivotTable fields.
    
    This class provides methods to access, add, remove, and manage fields in a PivotTable.
    PivotTable fields represent the data columns that can be used as row fields, column fields,
    page fields, or data fields in a PivotTable.
    """
    @dispatch
    def get_Item(self ,name:str)->IPivotField:
        """Gets a PivotField object by name from the collection.
        
        Args:
            name (str): The name of the field to retrieve.
            
        Returns:
            IPivotField: The PivotField object with the specified name.
        """
        
        GetDllLibXls().PivotTableFields_get_Item.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().PivotTableFields_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().PivotTableFields_get_Item, self.Ptr, name)
        ret = None if intPtr==None else XlsPivotField(intPtr)
        return ret



    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """Creates a clone of this PivotTableFields collection.
        
        Args:
            parent (SpireObject): The parent object for the cloned collection.
            
        Returns:
            SpireObject: The cloned PivotTableFields collection.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().PivotTableFields_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().PivotTableFields_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().PivotTableFields_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def RemoveAt(self ,index:int):
        """Removes a PivotField from the collection at the specified index.
        
        Args:
            index (int): The zero-based index of the field to remove.
        """
        
        GetDllLibXls().PivotTableFields_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().PivotTableFields_RemoveAt, self.Ptr, index)


    def Remove(self ,item:'PivotField')->bool:
        """Removes a specific PivotField from the collection.
        
        Args:
            item (PivotField): The PivotField object to remove.
            
        Returns:
            bool: True if the field was successfully removed; otherwise, False.
        """
        intPtritem:c_void_p = item.Ptr

        GetDllLibXls().PivotTableFields_Remove.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().PivotTableFields_Remove.restype=c_bool
        ret = CallCFunction(GetDllLibXls().PivotTableFields_Remove, self.Ptr, intPtritem)
        return ret

    def Clear(self):
        """Removes all PivotFields from the collection.
        """
        GetDllLibXls().PivotTableFields_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().PivotTableFields_Clear, self.Ptr)


    def Add(self ,item:'PivotField'):
        """Adds a PivotField to the collection.
        
        Args:
            item (PivotField): The PivotField object to add.
        """
        intPtritem:c_void_p = item.Ptr

        GetDllLibXls().PivotTableFields_Add.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().PivotTableFields_Add, self.Ptr, intPtritem)

    def GetEnumerator(self)->'IEnumerator':
        """Gets an enumerator for iterating through the collection.
        
        Returns:
            IEnumerator: An enumerator for the PivotTableFields collection.
        """
        ret = super(PivotTableFields, self).GetEnumerator()
        ret._gtype = XlsPivotField
        return ret

