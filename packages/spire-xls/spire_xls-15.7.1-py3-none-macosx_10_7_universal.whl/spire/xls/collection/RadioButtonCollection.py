from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class RadioButtonCollection (  CollectionBase[XlsRadioButtonShape], IRadioButtons) :
    """

    """
    @dispatch

    def get_Item(self ,index:int)->IRadioButton:
        """
        Returns single item from the collection.

        """
        
        GetDllLibXls().RadioButtonCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().RadioButtonCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RadioButtonCollection_get_Item, self.Ptr, index)
        ret = None if intPtr==None else XlsRadioButtonShape(intPtr)
        return ret


    @dispatch

    def get_Item(self ,name:str)->IRadioButton:
        """
        Gets single item from the collection.

        """
        
        GetDllLibXls().RadioButtonCollection_get_ItemN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().RadioButtonCollection_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RadioButtonCollection_get_ItemN, self.Ptr, name)
        ret = None if intPtr==None else XlsRadioButtonShape(intPtr)
        return ret


    @dispatch

    def Add(self)->IRadioButton:
        """
        Adds Option button default Dimension

        Returns:
            returns option button shape

        """
        GetDllLibXls().RadioButtonCollection_Add.argtypes=[c_void_p]
        GetDllLibXls().RadioButtonCollection_Add.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RadioButtonCollection_Add, self.Ptr)
        ret = None if intPtr==None else XlsRadioButtonShape(intPtr)
        return ret


    @dispatch

    def Add(self ,row:int,column:int)->IRadioButton:
        """
        Adds the Shape with default size

        Args:
            row: Top row for the new shape.
            column: Left column for the new shape

        """
        
        GetDllLibXls().RadioButtonCollection_AddRC.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().RadioButtonCollection_AddRC.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RadioButtonCollection_AddRC, self.Ptr, row,column)
        ret = None if intPtr==None else XlsRadioButtonShape(intPtr)
        return ret


    @dispatch

    def Add(self ,row:int,column:int,height:int,width:int)->IRadioButton:
        """
        Adds new RadioButton to the collection.

        Args:
            row: Top row for the new shape.
            column: Left column for the new shape.
            height: Height in pixels of the new shape.
            width: Width in pixels of the new shape.

        Returns:
            Newly created TextBox object.

        """
        
        GetDllLibXls().RadioButtonCollection_AddRCHW.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        GetDllLibXls().RadioButtonCollection_AddRCHW.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RadioButtonCollection_AddRCHW, self.Ptr, row,column,height,width)
        ret = None if intPtr==None else XlsRadioButtonShape(intPtr)
        return ret



    def AddCopy(self ,source:'IRadioButton'):
        """

        """
        intPtrsource:c_void_p = source.Ptr

        GetDllLibXls().RadioButtonCollection_AddCopy.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RadioButtonCollection_AddCopy, self.Ptr, intPtrsource)

    def Clear(self):
        """

        """
        GetDllLibXls().RadioButtonCollection_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RadioButtonCollection_Clear, self.Ptr)

    @staticmethod
    def AverageWidth()->int:
        """

        """
        #GetDllLibXls().RadioButtonCollection_AverageWidth.argtypes=[]
        GetDllLibXls().RadioButtonCollection_AverageWidth.restype=c_int
        ret = CallCFunction(GetDllLibXls().RadioButtonCollection_AverageWidth)
        return ret

    @staticmethod
    def AverageHeight()->int:
        """

        """
        #GetDllLibXls().RadioButtonCollection_AverageHeight.argtypes=[]
        GetDllLibXls().RadioButtonCollection_AverageHeight.restype=c_int
        ret = CallCFunction(GetDllLibXls().RadioButtonCollection_AverageHeight)
        return ret

