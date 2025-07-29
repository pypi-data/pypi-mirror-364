from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsRectangleShape (  XlsPrstGeomShape, IRectangleShape) :
    """Represents a rectangle shape in an Excel worksheet.
    
    This class provides properties and methods for manipulating rectangle shapes,
    including text, alignment, and hyperlinks.
    """
    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets the shape type of the rectangle.
        
        Returns:
            ExcelShapeType: An enumeration value representing the shape type of the rectangle.
        """
        GetDllLibXls().XlsRectangleShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsRectangleShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRectangleShape_get_ShapeType, self.Ptr)
        objwraped = ExcelShapeType(ret)
        return objwraped

    @property

    def RectShapeType(self)->'RectangleShapeType':
        """Gets the specific rectangle shape type.
        
        Returns:
            RectangleShapeType: An enumeration value representing the specific type of rectangle shape.
        """
        GetDllLibXls().XlsRectangleShape_get_RectShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsRectangleShape_get_RectShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRectangleShape_get_RectShapeType, self.Ptr)
        objwraped = RectangleShapeType(ret)
        return objwraped

    @property

    def Text(self)->str:
        """Gets or sets the text displayed in the rectangle shape.
        
        Returns:
            str: The text content of the rectangle shape.
        """
        GetDllLibXls().XlsRectangleShape_get_Text.argtypes=[c_void_p]
        GetDllLibXls().XlsRectangleShape_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRectangleShape_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        """Sets the text displayed in the rectangle shape.
        
        Args:
            value (str): The text to display in the rectangle shape.
        """
        GetDllLibXls().XlsRectangleShape_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsRectangleShape_set_Text, self.Ptr, value)

    @property
    def IsTextLocked(self)->bool:
        """Gets or sets whether the text in the rectangle shape is locked.
        
        Returns:
            bool: True if the text is locked; otherwise, False.
        """
        GetDllLibXls().XlsRectangleShape_get_IsTextLocked.argtypes=[c_void_p]
        GetDllLibXls().XlsRectangleShape_get_IsTextLocked.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRectangleShape_get_IsTextLocked, self.Ptr)
        return ret

    @IsTextLocked.setter
    def IsTextLocked(self, value:bool):
        """Sets whether the text in the rectangle shape is locked.
        
        Args:
            value (bool): True to lock the text; False to unlock it.
        """
        GetDllLibXls().XlsRectangleShape_set_IsTextLocked.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsRectangleShape_set_IsTextLocked, self.Ptr, value)

    @property

    def TextRotation(self)->'TextRotationType':
        """Gets or sets the text rotation in the rectangle shape.
        
        Returns:
            TextRotationType: An enumeration value representing the text rotation.
        """
        GetDllLibXls().XlsRectangleShape_get_TextRotation.argtypes=[c_void_p]
        GetDllLibXls().XlsRectangleShape_get_TextRotation.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRectangleShape_get_TextRotation, self.Ptr)
        objwraped = TextRotationType(ret)
        return objwraped

    @TextRotation.setter
    def TextRotation(self, value:'TextRotationType'):
        """Sets the text rotation in the rectangle shape.
        
        Args:
            value (TextRotationType): An enumeration value representing the text rotation.
        """
        GetDllLibXls().XlsRectangleShape_set_TextRotation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsRectangleShape_set_TextRotation, self.Ptr, value.value)

    @property

    def RichText(self)->'IRichTextString':
        """Gets the rich text formatting for the text in the rectangle shape.
        
        Returns:
            IRichTextString: An object that represents the rich text formatting.
        """
        GetDllLibXls().XlsRectangleShape_get_RichText.argtypes=[c_void_p]
        GetDllLibXls().XlsRectangleShape_get_RichText.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRectangleShape_get_RichText, self.Ptr)
        ret = None if intPtr==None else RichTextObject(intPtr)
        return ret


    @property

    def HAlignment(self)->'CommentHAlignType':
        """Gets or sets the horizontal alignment of text in the rectangle shape.
        
        Returns:
            CommentHAlignType: An enumeration value representing the horizontal alignment.
        """
        GetDllLibXls().XlsRectangleShape_get_HAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsRectangleShape_get_HAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRectangleShape_get_HAlignment, self.Ptr)
        objwraped = CommentHAlignType(ret)
        return objwraped

    @HAlignment.setter
    def HAlignment(self, value:'CommentHAlignType'):
        """Sets the horizontal alignment of text in the rectangle shape.
        
        Args:
            value (CommentHAlignType): An enumeration value representing the horizontal alignment.
        """
        GetDllLibXls().XlsRectangleShape_set_HAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsRectangleShape_set_HAlignment, self.Ptr, value.value)

    @property

    def VAlignment(self)->'CommentVAlignType':
        """Gets or sets the vertical alignment of text in the rectangle shape.
        
        Returns:
            CommentVAlignType: An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().XlsRectangleShape_get_VAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsRectangleShape_get_VAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRectangleShape_get_VAlignment, self.Ptr)
        objwraped = CommentVAlignType(ret)
        return objwraped

    @VAlignment.setter
    def VAlignment(self, value:'CommentVAlignType'):
        """Sets the vertical alignment of text in the rectangle shape.
        
        Args:
            value (CommentVAlignType): An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().XlsRectangleShape_set_VAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsRectangleShape_set_VAlignment, self.Ptr, value.value)

    @property

    def HyLink(self)->'IHyperLink':
        """Gets the hyperlink associated with the rectangle shape.
        
        Returns:
            IHyperLink: An object representing the hyperlink associated with the shape.
        """
        GetDllLibXls().XlsRectangleShape_get_HyLink.argtypes=[c_void_p]
        GetDllLibXls().XlsRectangleShape_get_HyLink.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRectangleShape_get_HyLink, self.Ptr)
        ret = None if intPtr==None else HyperLink(intPtr)
        return ret


    @property

    def PrstShapeType(self)->'PrstGeomShapeType':
        """Gets the preset geometry shape type of the rectangle.
        
        Returns:
            PrstGeomShapeType: An enumeration value representing the preset geometry shape type.
        """
        GetDllLibXls().XlsRectangleShape_get_PrstShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsRectangleShape_get_PrstShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRectangleShape_get_PrstShapeType, self.Ptr)
        objwraped = PrstGeomShapeType(ret)
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
#        GetDllLibXls().XlsRectangleShape_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsRectangleShape_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsRectangleShape_Clone, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollections)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


