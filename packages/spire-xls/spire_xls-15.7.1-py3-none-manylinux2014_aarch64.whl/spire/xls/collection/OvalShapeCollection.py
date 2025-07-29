from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class OvalShapeCollection (  CollectionBase[XlsOvalShape], IOvalShapes) :
    """
    Represents a collection of oval shapes in an Excel worksheet.
    """
    @dispatch
    def get_Item(self ,index:int)->IOvalShape:
        """
        Gets an oval shape by its index.

        Args:
            index (int): The index of the oval shape.
        Returns:
            IOvalShape: The oval shape at the specified index.
        """
        
        GetDllLibXls().OvalShapeCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().OvalShapeCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().OvalShapeCollection_get_Item, self.Ptr, index)
        ret = None if intPtr==None else XlsOvalShape(intPtr)
        return ret


    @dispatch
    def get_Item(self ,name:str)->IOvalShape:
        """
        Gets an oval shape by its name.

        Args:
            name (str): The name of the oval shape.
        Returns:
            IOvalShape: The oval shape with the specified name.
        """
        
        GetDllLibXls().OvalShapeCollection_get_ItemN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().OvalShapeCollection_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().OvalShapeCollection_get_ItemN, self.Ptr, name)
        ret = None if intPtr==None else XlsOvalShape(intPtr)
        return ret



    def AddOval(self ,row:int,column:int,height:int,width:int)->'IOvalShape':
        """
        Adds a new oval shape to the worksheet at the specified position and size.

        Args:
            row (int): The row index.
            column (int): The column index.
            height (int): The height of the oval shape.
            width (int): The width of the oval shape.
        Returns:
            IOvalShape: The newly added oval shape.
        """
        
        GetDllLibXls().OvalShapeCollection_AddOval.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        GetDllLibXls().OvalShapeCollection_AddOval.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().OvalShapeCollection_AddOval, self.Ptr, row,column,height,width)
        ret = None if intPtr==None else XlsOvalShape(intPtr)
        return ret



    def AddCopy(self ,source:'IOvalShape'):
        """
        Adds a copy of the specified oval shape to the collection.

        Args:
            source (IOvalShape): The oval shape to copy.
        """
        intPtrsource:c_void_p = source.Ptr

        GetDllLibXls().OvalShapeCollection_AddCopy.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().OvalShapeCollection_AddCopy, self.Ptr, intPtrsource)

    def Clear(self):
        """
        Removes all oval shapes from the collection.
        """
        GetDllLibXls().OvalShapeCollection_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().OvalShapeCollection_Clear, self.Ptr)

