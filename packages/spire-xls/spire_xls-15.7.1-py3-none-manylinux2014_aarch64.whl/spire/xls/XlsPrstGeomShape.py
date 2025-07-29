from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsPrstGeomShape (  XlsShape, IPrstGeomShape) :
    """Represents a preset geometry shape in an Excel worksheet.
    
    This class provides properties and methods for manipulating preset geometry shapes in Excel,
    such as rectangles, ovals, arrows, and other standard shapes. It extends XlsShape and
    implements the IPrstGeomShape interface.
    """
    @property

    def PrstShapeType(self)->'PrstGeomShapeType':
        """Gets the preset geometry shape type.
        
        Returns:
            PrstGeomShapeType: An enumeration value representing the preset geometry shape type.
        """
        GetDllLibXls().XlsPrstGeomShape_get_PrstShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsPrstGeomShape_get_PrstShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPrstGeomShape_get_PrstShapeType, self.Ptr)
        objwraped = PrstGeomShapeType(ret)
        return objwraped

    @property

    def Text(self)->str:
        """Gets or sets the text displayed in the preset geometry shape.
        
        Returns:
            str: The text displayed in the shape.
        """
        GetDllLibXls().XlsPrstGeomShape_get_Text.argtypes=[c_void_p]
        GetDllLibXls().XlsPrstGeomShape_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPrstGeomShape_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        """Sets the text displayed in the preset geometry shape.
        
        Args:
            value (str): The text to display in the shape.
        """
        GetDllLibXls().XlsPrstGeomShape_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPrstGeomShape_set_Text, self.Ptr, value)

    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets the shape type of the preset geometry shape.
        
        Returns:
            ExcelShapeType: An enumeration value representing the shape type.
        """
        GetDllLibXls().XlsPrstGeomShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsPrstGeomShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPrstGeomShape_get_ShapeType, self.Ptr)
        objwraped = ExcelShapeType(ret)
        return objwraped

#    @property
#
#    def GeomPaths(self)->'CollectionExtended1':
#        """
#
#        """
#        GetDllLibXls().XlsPrstGeomShape_get_GeomPaths.argtypes=[c_void_p]
#        GetDllLibXls().XlsPrstGeomShape_get_GeomPaths.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsPrstGeomShape_get_GeomPaths, self.Ptr)
#        ret = None if intPtr==None else CollectionExtended1(intPtr)
#        return ret
#


#
#    def Clone(self ,parent:'SpireObject',hashNewNames:'Dictionary2',dicFontIndexes:'Dictionary2',addToCollections:bool)->'IShape':
#        """
#
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrhashNewNames:c_void_p = hashNewNames.Ptr
#        intPtrdicFontIndexes:c_void_p = dicFontIndexes.Ptr
#
#        GetDllLibXls().XlsPrstGeomShape_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsPrstGeomShape_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsPrstGeomShape_Clone, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollections)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


    @property

    def ShapeAdjustValues(self)->'GeomertyAdjustValuesCollection':
        """Gets the collection of adjustment values for the preset geometry shape.
        
        Adjustment values allow customization of the shape's appearance, such as
        the roundness of corners or the length of arrows.
        
        Returns:
            GeomertyAdjustValuesCollection: A collection of adjustment values for the shape.
        """
        GetDllLibXls().XlsPrstGeomShape_get_ShapeAdjustValues.argtypes=[c_void_p]
        GetDllLibXls().XlsPrstGeomShape_get_ShapeAdjustValues.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPrstGeomShape_get_ShapeAdjustValues, self.Ptr)
        ret = None if intPtr==None else GeomertyAdjustValuesCollection(intPtr)
        return ret


