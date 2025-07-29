from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ArcShapeCollection (  IArcShapes) :
    """
    Represents a collection of arc shapes in a worksheet.
    """
    @dispatch

    def get_Item(self ,index:int)->IArcShape:
        """
        Gets the arc shape at the specified index.

        Args:
            index (int): The index of the arc shape.

        Returns:
            IArcShape: The arc shape at the specified index.
        """
        
        GetDllLibXls().ArcShapeCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().ArcShapeCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ArcShapeCollection_get_Item, self.Ptr, index)
        ret = None if intPtr==None else XlsArcShape(intPtr)
        return ret


    @dispatch

    def get_Item(self ,name:str)->IArcShape:
        """
        Gets the arc shape by its name.

        Args:
            name (str): The name of the arc shape.

        Returns:
            IArcShape: The arc shape with the specified name.
        """
        
        GetDllLibXls().ArcShapeCollection_get_ItemN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().ArcShapeCollection_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ArcShapeCollection_get_ItemN, self.Ptr, name)
        ret = None if intPtr==None else XlsArcShape(intPtr)
        return ret



    def AddArc(self ,row:int,column:int,height:int,width:int)->'IArcShape':
        """
        Adds a new arc shape to the collection.

        Args:
            row (int): The row index.
            column (int): The column index.
            height (int): The height of the arc.
            width (int): The width of the arc.

        Returns:
            IArcShape: The added arc shape.
        """
        
        GetDllLibXls().ArcShapeCollection_AddArc.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        GetDllLibXls().ArcShapeCollection_AddArc.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ArcShapeCollection_AddArc, self.Ptr, row,column,height,width)
        ret = None if intPtr==None else XlsArcShape(intPtr)
        return ret



    def AddCopy(self ,source:'IArcShape'):
        """
        Adds a copy of the specified arc shape to the collection.

        Args:
            source (IArcShape): The arc shape to copy.
        """
        intPtrsource:c_void_p = source.Ptr

        GetDllLibXls().ArcShapeCollection_AddCopy.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().ArcShapeCollection_AddCopy, self.Ptr, intPtrsource)

    def Clear(self):
        """
        Removes all arc shapes from the collection.
        """
        GetDllLibXls().ArcShapeCollection_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().ArcShapeCollection_Clear, self.Ptr)

