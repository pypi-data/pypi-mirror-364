from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class PrstGeomShapeCollection (  CollectionBase[XlsPrstGeomShape], IPrstGeomShapes) :
    """

    """
    @dispatch

    def get_Item(self ,index:int)->IPrstGeomShape:
        """

        """
        
        GetDllLibXls().PrstGeomShapeCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().PrstGeomShapeCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().PrstGeomShapeCollection_get_Item, self.Ptr, index)
        ret = None if intPtr==None else XlsPrstGeomShape(intPtr)
        return ret


    @dispatch

    def get_Item(self ,name:str)->IPrstGeomShape:
        """

        """
        
        GetDllLibXls().PrstGeomShapeCollection_get_ItemN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().PrstGeomShapeCollection_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().PrstGeomShapeCollection_get_ItemN, self.Ptr, name)
        ret = None if intPtr==None else XlsPrstGeomShape(intPtr)
        return ret


    @dispatch

    def get_Item(self ,shapeType:PrstGeomShapeType)->List[IPrstGeomShape]:
        """

        """
        enumshapeType:c_int = shapeType.value

        GetDllLibXls().PrstGeomShapeCollection_get_ItemS.argtypes=[c_void_p ,c_int]
        GetDllLibXls().PrstGeomShapeCollection_get_ItemS.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().PrstGeomShapeCollection_get_ItemS, self.Ptr, enumshapeType)
        ret = GetObjVectorFromArray(intPtrArray, IPrstGeomShape)
        return ret



    def AddNotPrimitiveShape(self ,row:int,column:int,width:int,height:int)->'IGeomPathShape':
        """
        Add a NotPrimitive shape to prstgeomshape collection;

        Args:
            row: shape's first row number in worksheet
            column: shape's first column number in worksheet
            width: shape's width, in unit of pixel.
            height: shape's height, in unit of pixel.

        """
        
        GetDllLibXls().PrstGeomShapeCollection_AddNotPrimitiveShape.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        GetDllLibXls().PrstGeomShapeCollection_AddNotPrimitiveShape.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().PrstGeomShapeCollection_AddNotPrimitiveShape, self.Ptr, row,column,width,height)
        ret = None if intPtr==None else IGeomPathShape(intPtr)
        return ret



    def AddPrstGeomShape(self ,row:int,column:int,width:int,height:int,shapeType:'PrstGeomShapeType')->'IPrstGeomShape':
        """
        Add a preset shape to prstgeomshape collection;

        Args:
            row: shape's first row number in worksheet
            column: shape's first column number in worksheet
            width: shape's width, in unit of pixel.
            height: shape's height, in unit of pixel.
            shapeType: shape's type

        """
        enumshapeType:c_int = shapeType.value

        GetDllLibXls().PrstGeomShapeCollection_AddPrstGeomShape.argtypes=[c_void_p ,c_int,c_int,c_int,c_int,c_int]
        GetDllLibXls().PrstGeomShapeCollection_AddPrstGeomShape.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().PrstGeomShapeCollection_AddPrstGeomShape, self.Ptr, row,column,width,height,enumshapeType)
        ret = None if intPtr==None else XlsPrstGeomShape(intPtr)
        return ret



    def AddCopy(self ,source:'IPrstGeomShape'):
        """

        """
        intPtrsource:c_void_p = source.Ptr

        GetDllLibXls().PrstGeomShapeCollection_AddCopy.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().PrstGeomShapeCollection_AddCopy, self.Ptr, intPtrsource)


    def Remove(self ,shape:'IShape'):
        """
        Remove a shape in collection;

        Args:
            shape: the shape to remove

        """
        intPtrshape:c_void_p = shape.Ptr

        GetDllLibXls().PrstGeomShapeCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().PrstGeomShapeCollection_Remove, self.Ptr, intPtrshape)

    def Clear(self):
        """

        """
        GetDllLibXls().PrstGeomShapeCollection_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().PrstGeomShapeCollection_Clear, self.Ptr)

