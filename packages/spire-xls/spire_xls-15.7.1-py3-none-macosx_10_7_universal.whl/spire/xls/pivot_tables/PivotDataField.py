from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class PivotDataField (  SpireObject, IPivotDataField, ICloneParent) :
    """Represents a data field in a PivotTable.
    
    This class provides functionality for managing data fields in a PivotTable.
    Data fields represent the values that are aggregated (summed, counted, etc.)
    in the PivotTable based on the row and column fields.
    """

    @property
    def CustomName(self)->str:
        """Gets the custom name of the data field.
        
        Returns:
            str: The custom name of the data field.
        """
        GetDllLibXls().PivotDataField_get_CustomName.argtypes=[c_void_p]
        GetDllLibXls().PivotDataField_get_CustomName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().PivotDataField_get_CustomName, self.Ptr))
        return ret

    @CustomName.setter
    def CustomName(self, value:str):
        """Sets the custom name of the data field.
        
        Args:
            value (str): The custom name to set for the data field.
        """
        GetDllLibXls().PivotDataField_set_CustomName.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().PivotDataField_set_CustomName, self.Ptr, value)

    @property

    def Name(self)->str:
        """Gets the name of the data field.
        
        Returns:
            str: The name of the data field.
        """
        GetDllLibXls().PivotDataField_get_Name.argtypes=[c_void_p]
        GetDllLibXls().PivotDataField_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().PivotDataField_get_Name, self.Ptr))
        return ret


    @property

    def Subtotal(self)->'SubtotalTypes':
        """Gets the subtotal calculation type for the data field.
        
        Returns:
            SubtotalTypes: An enumeration value representing the subtotal calculation type.
        """
        GetDllLibXls().PivotDataField_get_Subtotal.argtypes=[c_void_p]
        GetDllLibXls().PivotDataField_get_Subtotal.restype=c_int
        ret = CallCFunction(GetDllLibXls().PivotDataField_get_Subtotal, self.Ptr)
        objwraped = SubtotalTypes(ret)
        return objwraped

    @Subtotal.setter
    def Subtotal(self, value:'SubtotalTypes'):
        """Sets the subtotal calculation type for the data field.
        
        Args:
            value (SubtotalTypes): An enumeration value representing the subtotal calculation type to set.
        """
        GetDllLibXls().PivotDataField_set_Subtotal.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().PivotDataField_set_Subtotal, self.Ptr, value.value)

    @property
    def BaseItem(self)->int:
        """Gets the base item for calculations that compare data.
        
        Returns:
            int: The index of the base item.
        """
        GetDllLibXls().PivotDataField_get_BaseItem.argtypes=[c_void_p]
        GetDllLibXls().PivotDataField_get_BaseItem.restype=c_int
        ret = CallCFunction(GetDllLibXls().PivotDataField_get_BaseItem, self.Ptr)
        return ret

    @BaseItem.setter
    def BaseItem(self, value:int):
        """Sets the base item for calculations that compare data.
        
        Args:
            value (int): The index of the base item to set.
        """
        GetDllLibXls().PivotDataField_set_BaseItem.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().PivotDataField_set_BaseItem, self.Ptr, value)

    @property
    def BaseField(self)->int:
        """Gets the base field for calculations that compare data.
        
        Returns:
            int: The index of the base field.
        """
        GetDllLibXls().PivotDataField_get_BaseField.argtypes=[c_void_p]
        GetDllLibXls().PivotDataField_get_BaseField.restype=c_int
        ret = CallCFunction(GetDllLibXls().PivotDataField_get_BaseField, self.Ptr)
        return ret

    @BaseField.setter
    def BaseField(self, value:int):
        """Sets the base field for calculations that compare data.
        
        Args:
            value (int): The index of the base field to set.
        """
        GetDllLibXls().PivotDataField_set_BaseField.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().PivotDataField_set_BaseField, self.Ptr, value)

    @property

    def ShowDataAs(self)->'PivotFieldFormatType':
        """Gets the data display format for the data field.
        
        Returns:
            PivotFieldFormatType: An enumeration value representing the data display format.
        """
        GetDllLibXls().PivotDataField_get_ShowDataAs.argtypes=[c_void_p]
        GetDllLibXls().PivotDataField_get_ShowDataAs.restype=c_int
        ret = CallCFunction(GetDllLibXls().PivotDataField_get_ShowDataAs, self.Ptr)
        objwraped = PivotFieldFormatType(ret)
        return objwraped

    @ShowDataAs.setter
    def ShowDataAs(self, value:'PivotFieldFormatType'):
        """Sets the data display format for the data field.
        
        Args:
            value (PivotFieldFormatType): An enumeration value representing the data display format to set.
        """
        GetDllLibXls().PivotDataField_set_ShowDataAs.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().PivotDataField_set_ShowDataAs, self.Ptr, value.value)


    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """Creates a clone of this data field.
        
        Args:
            parent (SpireObject): The parent object for the cloned data field.
            
        Returns:
            SpireObject: The cloned data field object.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().PivotDataField_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().PivotDataField_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().PivotDataField_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


