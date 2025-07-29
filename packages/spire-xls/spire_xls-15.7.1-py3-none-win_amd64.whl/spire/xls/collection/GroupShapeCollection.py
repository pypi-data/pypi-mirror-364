from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class GroupShapeCollection (CollectionBase[GroupShape]) :
    """

    """

    def Group(self ,shapes:'List[IShape]')->'GroupShape':
        """
        Group shapes.

        Args:
            shapes: 

        """
        #arrayshapes:ArrayTypeshapes = ""
        countshapes = len(shapes)
        ArrayTypeshapes = c_void_p * countshapes
        arrayshapes = ArrayTypeshapes()
        for i in range(0, countshapes):
            arrayshapes[i] = shapes[i].Ptr


        GetDllLibXls().GroupShapeCollection_Group.argtypes=[c_void_p ,ArrayTypeshapes,c_int]
        GetDllLibXls().GroupShapeCollection_Group.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().GroupShapeCollection_Group, self.Ptr, arrayshapes,countshapes)
        ret = None if intPtr==None else GroupShape(intPtr)
        return ret



    def UnGroupAll(self):
        """
        UnGroup all group shape.

        """
        GetDllLibXls().GroupShapeCollection_UnGroupAll.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().GroupShapeCollection_UnGroupAll, self.Ptr)

