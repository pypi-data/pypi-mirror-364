from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsCheckBoxShape (  XlsShape, ICheckBox) :
    """Represents a checkbox shape in an Excel worksheet.
    
    This class provides properties and methods for manipulating checkbox shapes in Excel,
    including check state, text formatting, alignment, and rotation. It extends XlsShape and
    implements the ICheckBox interface.
    """
    @property

    def CheckState(self)->'CheckState':
        """Gets or sets the check state of the checkbox.
        
        Returns:
            CheckState: An enumeration value representing the check state (checked, unchecked, or mixed).
        """
        GetDllLibXls().XlsCheckBoxShape_get_CheckState.argtypes=[c_void_p]
        GetDllLibXls().XlsCheckBoxShape_get_CheckState.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsCheckBoxShape_get_CheckState, self.Ptr)
        objwraped = CheckState(ret)
        return objwraped

    @CheckState.setter
    def CheckState(self, value:'CheckState'):
        """Sets the check state of the checkbox.
        
        Args:
            value (CheckState): An enumeration value representing the check state (checked, unchecked, or mixed).
        """
        GetDllLibXls().XlsCheckBoxShape_set_CheckState.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsCheckBoxShape_set_CheckState, self.Ptr, value.value)

    @property

    def Text(self)->str:
        """Gets or sets the text displayed next to the checkbox.
        
        Returns:
            str: The text displayed next to the checkbox.
        """
        GetDllLibXls().XlsCheckBoxShape_get_Text.argtypes=[c_void_p]
        GetDllLibXls().XlsCheckBoxShape_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsCheckBoxShape_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        """Sets the text displayed next to the checkbox.
        
        Args:
            value (str): The text to display next to the checkbox.
        """
        GetDllLibXls().XlsCheckBoxShape_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsCheckBoxShape_set_Text, self.Ptr, value)

    @property
    def IsTextLocked(self)->bool:
        """Gets or sets whether the text next to the checkbox is locked.
        
        Returns:
            bool: True if the text is locked; otherwise, False.
        """
        GetDllLibXls().XlsCheckBoxShape_get_IsTextLocked.argtypes=[c_void_p]
        GetDllLibXls().XlsCheckBoxShape_get_IsTextLocked.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsCheckBoxShape_get_IsTextLocked, self.Ptr)
        return ret

    @IsTextLocked.setter
    def IsTextLocked(self, value:bool):
        """Sets whether the text next to the checkbox is locked.
        
        Args:
            value (bool): True to lock the text; otherwise, False.
        """
        GetDllLibXls().XlsCheckBoxShape_set_IsTextLocked.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsCheckBoxShape_set_IsTextLocked, self.Ptr, value)

    @property
    def Display3DShading(self)->bool:
        """Gets or sets whether the checkbox displays 3D shading.
        
        Returns:
            bool: True if 3D shading is displayed; otherwise, False.
        """
        GetDllLibXls().XlsCheckBoxShape_get_Display3DShading.argtypes=[c_void_p]
        GetDllLibXls().XlsCheckBoxShape_get_Display3DShading.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsCheckBoxShape_get_Display3DShading, self.Ptr)
        return ret

    @Display3DShading.setter
    def Display3DShading(self, value:bool):
        """Sets whether the checkbox displays 3D shading.
        
        Args:
            value (bool): True to display 3D shading; otherwise, False.
        """
        GetDllLibXls().XlsCheckBoxShape_set_Display3DShading.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsCheckBoxShape_set_Display3DShading, self.Ptr, value)

    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets the type of the shape.
        
        Returns:
            ExcelShapeType: An enumeration value representing the type of the shape.
        """
        GetDllLibXls().XlsCheckBoxShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsCheckBoxShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsCheckBoxShape_get_ShapeType, self.Ptr)
        objwraped = ExcelShapeType(ret)
        return objwraped

    @property

    def HAlignment(self)->'CommentHAlignType':
        """Gets or sets the horizontal alignment of the text next to the checkbox.
        
        Returns:
            CommentHAlignType: An enumeration value representing the horizontal alignment.
        """
        GetDllLibXls().XlsCheckBoxShape_get_HAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsCheckBoxShape_get_HAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsCheckBoxShape_get_HAlignment, self.Ptr)
        objwraped = CommentHAlignType(ret)
        return objwraped

    @HAlignment.setter
    def HAlignment(self, value:'CommentHAlignType'):
        """Sets the horizontal alignment of the text next to the checkbox.
        
        Args:
            value (CommentHAlignType): An enumeration value representing the horizontal alignment.
        """
        GetDllLibXls().XlsCheckBoxShape_set_HAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsCheckBoxShape_set_HAlignment, self.Ptr, value.value)

    @property

    def VAlignment(self)->'CommentVAlignType':
        """Gets or sets the vertical alignment of the text next to the checkbox.
        
        Returns:
            CommentVAlignType: An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().XlsCheckBoxShape_get_VAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsCheckBoxShape_get_VAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsCheckBoxShape_get_VAlignment, self.Ptr)
        objwraped = CommentVAlignType(ret)
        return objwraped

    @VAlignment.setter
    def VAlignment(self, value:'CommentVAlignType'):
        """Sets the vertical alignment of the text next to the checkbox.
        
        Args:
            value (CommentVAlignType): An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().XlsCheckBoxShape_set_VAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsCheckBoxShape_set_VAlignment, self.Ptr, value.value)

    @property

    def TextRotation(self)->'TextRotationType':
        """Gets or sets the rotation of the text next to the checkbox.
        
        Returns:
            TextRotationType: An enumeration value representing the text rotation type.
        """
        GetDllLibXls().XlsCheckBoxShape_get_TextRotation.argtypes=[c_void_p]
        GetDllLibXls().XlsCheckBoxShape_get_TextRotation.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsCheckBoxShape_get_TextRotation, self.Ptr)
        objwraped = TextRotationType(ret)
        return objwraped

    @TextRotation.setter
    def TextRotation(self, value:'TextRotationType'):
        """Sets the rotation of the text next to the checkbox.
        
        Args:
            value (TextRotationType): An enumeration value representing the text rotation type.
        """
        GetDllLibXls().XlsCheckBoxShape_set_TextRotation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsCheckBoxShape_set_TextRotation, self.Ptr, value.value)

#
#    def Clone(self ,parent:'SpireObject',hashNewNames:'Dictionary2',dicFontIndexes:'Dictionary2',addToCollections:bool)->'IShape':
#        """
#
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrhashNewNames:c_void_p = hashNewNames.Ptr
#        intPtrdicFontIndexes:c_void_p = dicFontIndexes.Ptr
#
#        GetDllLibXls().XlsCheckBoxShape_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsCheckBoxShape_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsCheckBoxShape_Clone, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollections)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


