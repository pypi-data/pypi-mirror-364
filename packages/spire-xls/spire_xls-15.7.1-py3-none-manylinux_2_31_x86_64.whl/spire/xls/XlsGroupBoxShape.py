from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsGroupBoxShape (  XlsShape, IGroupBox) :
    """Represents a group box shape in an Excel worksheet.
    
    This class provides properties and methods for manipulating group box shapes in Excel,
    including text display, 3D shading effects, and other formatting options. It extends
    XlsShape and implements the IGroupBox interface.
    """
    @property
    def Display3DShading(self)->bool:
        """Gets or sets whether the group box displays with 3D shading.
        
        Returns:
            bool: True if the group box displays with 3D shading; otherwise, False.
        """
        GetDllLibXls().XlsGroupBoxShape_get_Display3DShading.argtypes=[c_void_p]
        GetDllLibXls().XlsGroupBoxShape_get_Display3DShading.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsGroupBoxShape_get_Display3DShading, self.Ptr)
        return ret

    @Display3DShading.setter
    def Display3DShading(self, value:bool):
        """Sets whether the group box displays with 3D shading.
        
        Args:
            value (bool): True to display the group box with 3D shading; otherwise, False.
        """
        GetDllLibXls().XlsGroupBoxShape_set_Display3DShading.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsGroupBoxShape_set_Display3DShading, self.Ptr, value)

    @property

    def Text(self)->str:
        """Gets or sets the text displayed in the group box.
        
        Returns:
            str: The text displayed in the group box.
        """
        GetDllLibXls().XlsGroupBoxShape_get_Text.argtypes=[c_void_p]
        GetDllLibXls().XlsGroupBoxShape_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsGroupBoxShape_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        """Sets the text displayed in the group box.
        
        Args:
            value (str): The text to display in the group box.
        """
        GetDllLibXls().XlsGroupBoxShape_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsGroupBoxShape_set_Text, self.Ptr, value)

    @property
    def IsTextLocked(self)->bool:
        """Gets or sets whether the text in the group box is locked.
        
        Returns:
            bool: True if the text is locked; otherwise, False.
        """
        GetDllLibXls().XlsGroupBoxShape_get_IsTextLocked.argtypes=[c_void_p]
        GetDllLibXls().XlsGroupBoxShape_get_IsTextLocked.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsGroupBoxShape_get_IsTextLocked, self.Ptr)
        return ret

    @IsTextLocked.setter
    def IsTextLocked(self, value:bool):
        """Sets whether the text in the group box is locked.
        
        Args:
            value (bool): True to lock the text; otherwise, False.
        """
        GetDllLibXls().XlsGroupBoxShape_set_IsTextLocked.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsGroupBoxShape_set_IsTextLocked, self.Ptr, value)

    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets the type of the shape.
        
        Returns:
            ExcelShapeType: An enumeration value representing the type of the shape.
        """
        GetDllLibXls().XlsGroupBoxShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsGroupBoxShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsGroupBoxShape_get_ShapeType, self.Ptr)
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
#        GetDllLibXls().XlsGroupBoxShape_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsGroupBoxShape_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsGroupBoxShape_Clone, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollections)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


