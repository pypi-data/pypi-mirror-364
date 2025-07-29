from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsLabelShape (  XlsShape, ILabelShape) :
    """Represents a label shape in an Excel worksheet.
    
    This class provides properties and methods for manipulating label shapes in Excel,
    including text content and locking settings. It extends XlsShape and implements
    the ILabelShape interface.
    """
    @property

    def Text(self)->str:
        """Gets or sets the text displayed in the label shape.
        
        Returns:
            str: The text displayed in the label shape.
        """
        GetDllLibXls().XlsLabelShape_get_Text.argtypes=[c_void_p]
        GetDllLibXls().XlsLabelShape_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsLabelShape_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        """Sets the text displayed in the label shape.
        
        Args:
            value (str): The text to display in the label shape.
        """
        GetDllLibXls().XlsLabelShape_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsLabelShape_set_Text, self.Ptr, value)

    @property
    def IsTextLocked(self)->bool:
        """Gets or sets whether the text in the label shape is locked.
        
        Returns:
            bool: True if the text is locked; otherwise, False.
        """
        GetDllLibXls().XlsLabelShape_get_IsTextLocked.argtypes=[c_void_p]
        GetDllLibXls().XlsLabelShape_get_IsTextLocked.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsLabelShape_get_IsTextLocked, self.Ptr)
        return ret

    @IsTextLocked.setter
    def IsTextLocked(self, value:bool):
        """Sets whether the text in the label shape is locked.
        
        Args:
            value (bool): True to lock the text; otherwise, False.
        """
        GetDllLibXls().XlsLabelShape_set_IsTextLocked.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsLabelShape_set_IsTextLocked, self.Ptr, value)

    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets the type of the shape.
        
        Returns:
            ExcelShapeType: An enumeration value representing the type of the shape.
        """
        GetDllLibXls().XlsLabelShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsLabelShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsLabelShape_get_ShapeType, self.Ptr)
        objwraped = ExcelShapeType(ret)
        return objwraped

#
#    def Clone(self ,parent:'SpireObject',hashNewNames:'Dictionary2',dicFontIndexes:'Dictionary2',addToCollections:bool)->'IShape':
#        """
#
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrhashNewNames:c_void_p = hashNewNames.Ptr
#        intPtrdicFontIndexes:c_void_p = dicFontIndexes.Ptr
#
#        GetDllLibXls().XlsLabelShape_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsLabelShape_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsLabelShape_Clone, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollections)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


