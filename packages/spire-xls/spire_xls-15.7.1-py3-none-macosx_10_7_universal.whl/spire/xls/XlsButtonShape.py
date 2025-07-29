from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsButtonShape (  XlsShape, IShape, ITextBox) :
    """Represents a button shape in an Excel worksheet.
    
    This class provides properties and methods for manipulating button shapes in Excel,
    including text formatting, alignment, and rotation. It extends XlsShape and
    implements the IShape and ITextBox interfaces.
    """
    @property

    def Text(self)->str:
        """Gets or sets the text displayed on the button.
        
        Returns:
            str: The text displayed on the button.
        """
        GetDllLibXls().XlsButtonShape_get_Text.argtypes=[c_void_p]
        GetDllLibXls().XlsButtonShape_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsButtonShape_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        """Sets the text displayed on the button.
        
        Args:
            value (str): The text to display on the button.
        """
        GetDllLibXls().XlsButtonShape_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsButtonShape_set_Text, self.Ptr, value)

    @property
    def IsTextLocked(self)->bool:
        """Gets or sets whether the text on the button is locked.
        
        Returns:
            bool: True if the text is locked; otherwise, False.
        """
        GetDllLibXls().XlsButtonShape_get_IsTextLocked.argtypes=[c_void_p]
        GetDllLibXls().XlsButtonShape_get_IsTextLocked.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsButtonShape_get_IsTextLocked, self.Ptr)
        return ret

    @IsTextLocked.setter
    def IsTextLocked(self, value:bool):
        """Sets whether the text on the button is locked.
        
        Args:
            value (bool): True to lock the text; otherwise, False.
        """
        GetDllLibXls().XlsButtonShape_set_IsTextLocked.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsButtonShape_set_IsTextLocked, self.Ptr, value)

    @property

    def TextRotation(self)->'TextRotationType':
        """Gets or sets the rotation of the text on the button.
        
        Returns:
            TextRotationType: An enumeration value representing the text rotation type.
        """
        GetDllLibXls().XlsButtonShape_get_TextRotation.argtypes=[c_void_p]
        GetDllLibXls().XlsButtonShape_get_TextRotation.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsButtonShape_get_TextRotation, self.Ptr)
        objwraped = TextRotationType(ret)
        return objwraped

    @TextRotation.setter
    def TextRotation(self, value:'TextRotationType'):
        """Sets the rotation of the text on the button.
        
        Args:
            value (TextRotationType): An enumeration value representing the text rotation type.
        """
        GetDllLibXls().XlsButtonShape_set_TextRotation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsButtonShape_set_TextRotation, self.Ptr, value.value)

    @property

    def RichText(self)->'IRichTextString':
        """Gets the rich text formatting of the button text.
        
        Returns:
            IRichTextString: An object representing the rich text formatting.
        """
        GetDllLibXls().XlsButtonShape_get_RichText.argtypes=[c_void_p]
        GetDllLibXls().XlsButtonShape_get_RichText.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsButtonShape_get_RichText, self.Ptr)
        ret = None if intPtr==None else RichTextObject(intPtr)
        return ret


    @property

    def HAlignment(self)->'CommentHAlignType':
        """Gets or sets the horizontal alignment of the text on the button.
        
        Returns:
            CommentHAlignType: An enumeration value representing the horizontal alignment.
        """
        GetDllLibXls().XlsButtonShape_get_HAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsButtonShape_get_HAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsButtonShape_get_HAlignment, self.Ptr)
        objwraped = CommentHAlignType(ret)
        return objwraped

    @HAlignment.setter
    def HAlignment(self, value:'CommentHAlignType'):
        """Sets the horizontal alignment of the text on the button.
        
        Args:
            value (CommentHAlignType): An enumeration value representing the horizontal alignment.
        """
        GetDllLibXls().XlsButtonShape_set_HAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsButtonShape_set_HAlignment, self.Ptr, value.value)

    @property

    def VAlignment(self)->'CommentVAlignType':
        """Gets or sets the vertical alignment of the text on the button.
        
        Returns:
            CommentVAlignType: An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().XlsButtonShape_get_VAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsButtonShape_get_VAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsButtonShape_get_VAlignment, self.Ptr)
        objwraped = CommentVAlignType(ret)
        return objwraped

    @VAlignment.setter
    def VAlignment(self, value:'CommentVAlignType'):
        """Sets the vertical alignment of the text on the button.
        
        Args:
            value (CommentVAlignType): An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().XlsButtonShape_set_VAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsButtonShape_set_VAlignment, self.Ptr, value.value)

    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets the type of the shape.
        
        Returns:
            ExcelShapeType: An enumeration value representing the type of the shape.
        """
        GetDllLibXls().XlsButtonShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsButtonShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsButtonShape_get_ShapeType, self.Ptr)
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
#        GetDllLibXls().XlsButtonShape_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsButtonShape_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsButtonShape_Clone, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollections)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


