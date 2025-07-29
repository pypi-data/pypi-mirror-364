from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ComboBoxCollection (  CollectionBase[XlsComboBoxShape],IComboBoxes) :
    """
    Represents a collection of ComboBox shapes in an Excel worksheet.
    """
    @dispatch
    def get_Item(self ,index:int)->IComboBoxShape:
        """
        Gets a ComboBox shape by its index.

        Args:
            index (int): The index of the ComboBox shape.
        Returns:
            IComboBoxShape: The ComboBox shape at the specified index.
        """
        
        GetDllLibXls().ComboBoxCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().ComboBoxCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ComboBoxCollection_get_Item, self.Ptr, index)
        ret = None if intPtr==None else XlsComboBoxShape(intPtr)
        return ret


    @dispatch
    def get_Item(self ,name:str)->IComboBoxShape:
        """
        Gets a ComboBox shape by its name.

        Args:
            name (str): The name of the ComboBox shape.
        Returns:
            IComboBoxShape: The ComboBox shape with the specified name.
        """
        
        GetDllLibXls().ComboBoxCollection_get_ItemN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().ComboBoxCollection_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ComboBoxCollection_get_ItemN, self.Ptr, name)
        ret = None if intPtr==None else XlsComboBoxShape(intPtr)
        return ret



    def AddCopy(self ,comboboxsource:'IComboBoxShape'):
        """
        Adds a copy of the specified ComboBox shape to the collection.

        Args:
            comboboxsource (IComboBoxShape): The ComboBox shape to copy.
        """
        intPtrcomboboxsource:c_void_p = comboboxsource.Ptr

        GetDllLibXls().ComboBoxCollection_AddCopy.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().ComboBoxCollection_AddCopy, self.Ptr, intPtrcomboboxsource)


    def AddComboBox(self ,row:int,column:int,height:int,width:int)->'IComboBoxShape':
        """
        Adds a new ComboBox shape to the worksheet at the specified position and size.

        Args:
            row (int): The row index.
            column (int): The column index.
            height (int): The height of the ComboBox.
            width (int): The width of the ComboBox.
        Returns:
            IComboBoxShape: The newly added ComboBox shape.
        """
        
        GetDllLibXls().ComboBoxCollection_AddComboBox.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        GetDllLibXls().ComboBoxCollection_AddComboBox.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ComboBoxCollection_AddComboBox, self.Ptr, row,column,height,width)
        ret = None if intPtr==None else XlsComboBoxShape(intPtr)
        return ret


    def Clear(self):
        """
        Removes all ComboBox shapes from the collection.
        """
        GetDllLibXls().ComboBoxCollection_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().ComboBoxCollection_Clear, self.Ptr)

