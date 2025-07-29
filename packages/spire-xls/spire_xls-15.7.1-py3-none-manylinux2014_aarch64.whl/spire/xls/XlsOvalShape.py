from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsOvalShape (  XlsShape, IOvalShape) :
    """Represents an oval shape in an Excel worksheet.
    
    This class provides properties and methods for manipulating oval shapes in Excel,
    including text settings, alignment, hyperlinks, and other oval-specific functionality.
    It extends XlsShape and implements the IOvalShape interface.
    """
    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets the shape type of the oval shape.
        
        Returns:
            ExcelShapeType: An enumeration value representing the shape type of the oval.
        """
        GetDllLibXls().XlsOvalShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsOvalShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsOvalShape_get_ShapeType, self.Ptr)
        objwraped = ExcelShapeType(ret)
        return objwraped

    @property

    def Text(self)->str:
        """Gets or sets the text displayed in the oval shape.
        
        Returns:
            str: The text displayed in the oval shape.
        """
        GetDllLibXls().XlsOvalShape_get_Text.argtypes=[c_void_p]
        GetDllLibXls().XlsOvalShape_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsOvalShape_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        """Sets the text displayed in the oval shape.
        
        Args:
            value (str): The text to display in the oval shape.
        """
        GetDllLibXls().XlsOvalShape_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsOvalShape_set_Text, self.Ptr, value)

    @property
    def IsTextLocked(self)->bool:
        """Gets or sets whether the text in the oval shape is locked.
        
        Returns:
            bool: True if the text is locked, False otherwise.
        """
        GetDllLibXls().XlsOvalShape_get_IsTextLocked.argtypes=[c_void_p]
        GetDllLibXls().XlsOvalShape_get_IsTextLocked.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsOvalShape_get_IsTextLocked, self.Ptr)
        return ret

    @IsTextLocked.setter
    def IsTextLocked(self, value:bool):
        """Sets whether the text in the oval shape is locked.
        
        Args:
            value (bool): True to lock the text, False otherwise.
        """
        GetDllLibXls().XlsOvalShape_set_IsTextLocked.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsOvalShape_set_IsTextLocked, self.Ptr, value)

    @property

    def TextRotation(self)->'TextRotationType':
        """Gets or sets the text rotation in the oval shape.
        
        Returns:
            TextRotationType: An enumeration value representing the text rotation.
        """
        GetDllLibXls().XlsOvalShape_get_TextRotation.argtypes=[c_void_p]
        GetDllLibXls().XlsOvalShape_get_TextRotation.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsOvalShape_get_TextRotation, self.Ptr)
        objwraped = TextRotationType(ret)
        return objwraped

    @TextRotation.setter
    def TextRotation(self, value:'TextRotationType'):
        """Sets the text rotation in the oval shape.
        
        Args:
            value (TextRotationType): An enumeration value representing the text rotation.
        """
        GetDllLibXls().XlsOvalShape_set_TextRotation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsOvalShape_set_TextRotation, self.Ptr, value.value)

    @property

    def RichText(self)->'IRichTextString':
        """Gets the rich text formatting for the text in the oval shape.
        
        Returns:
            IRichTextString: An object representing the rich text formatting.
        """
        GetDllLibXls().XlsOvalShape_get_RichText.argtypes=[c_void_p]
        GetDllLibXls().XlsOvalShape_get_RichText.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsOvalShape_get_RichText, self.Ptr)
        ret = None if intPtr==None else RichTextObject(intPtr)
        return ret


    @property

    def HAlignment(self)->'CommentHAlignType':
        """Gets or sets the horizontal alignment of text in the oval shape.
        
        Returns:
            CommentHAlignType: An enumeration value representing the horizontal alignment.
        """
        GetDllLibXls().XlsOvalShape_get_HAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsOvalShape_get_HAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsOvalShape_get_HAlignment, self.Ptr)
        objwraped = CommentHAlignType(ret)
        return objwraped

    @HAlignment.setter
    def HAlignment(self, value:'CommentHAlignType'):
        """Sets the horizontal alignment of text in the oval shape.
        
        Args:
            value (CommentHAlignType): An enumeration value representing the horizontal alignment.
        """
        GetDllLibXls().XlsOvalShape_set_HAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsOvalShape_set_HAlignment, self.Ptr, value.value)

    @property

    def VAlignment(self)->'CommentVAlignType':
        """Gets or sets the vertical alignment of text in the oval shape.
        
        Returns:
            CommentVAlignType: An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().XlsOvalShape_get_VAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsOvalShape_get_VAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsOvalShape_get_VAlignment, self.Ptr)
        objwraped = CommentVAlignType(ret)
        return objwraped

    @VAlignment.setter
    def VAlignment(self, value:'CommentVAlignType'):
        """Sets the vertical alignment of text in the oval shape.
        
        Args:
            value (CommentVAlignType): An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().XlsOvalShape_set_VAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsOvalShape_set_VAlignment, self.Ptr, value.value)

    @property

    def HyLink(self)->'IHyperLink':
        """Gets the hyperlink associated with the oval shape.
        
        Returns:
            IHyperLink: An object representing the hyperlink associated with the oval shape.
        """
        GetDllLibXls().XlsOvalShape_get_HyLink.argtypes=[c_void_p]
        GetDllLibXls().XlsOvalShape_get_HyLink.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsOvalShape_get_HyLink, self.Ptr)
        ret = None if intPtr==None else HyperLink(intPtr)
        return ret


    @property

    def PrstShapeType(self)->'PrstGeomShapeType':
        """Gets the preset geometry shape type of the oval shape.
        
        Returns:
            PrstGeomShapeType: An enumeration value representing the preset geometry shape type.
        """
        GetDllLibXls().XlsOvalShape_get_PrstShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsOvalShape_get_PrstShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsOvalShape_get_PrstShapeType, self.Ptr)
        objwraped = PrstGeomShapeType(ret)
        return objwraped

#    @property
#
#    def GeomPaths(self)->'CollectionExtended1':
#        """
#        Gets the collection of geometric paths that define the oval shape.
#
#        Returns:
#            CollectionExtended1: A collection of geometric paths.
#        """
#        GetDllLibXls().XlsOvalShape_get_GeomPaths.argtypes=[c_void_p]
#        GetDllLibXls().XlsOvalShape_get_GeomPaths.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsOvalShape_get_GeomPaths, self.Ptr)
#        ret = None if intPtr==None else CollectionExtended1(intPtr)
#        return ret
#


#
#    def Clone(self ,parent:'SpireObject',hashNewNames:'Dictionary2',dicFontIndexes:'Dictionary2',addToCollections:bool)->'IShape':
#        """
#        Creates a clone of this oval shape.
#
#        Args:
#            parent (SpireObject): The parent object for the cloned shape.
#            hashNewNames (Dictionary2): A dictionary of new names.
#            dicFontIndexes (Dictionary2): A dictionary of font indexes.
#            addToCollections (bool): Whether to add the cloned shape to collections.
#
#        Returns:
#            IShape: A clone of this oval shape.
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrhashNewNames:c_void_p = hashNewNames.Ptr
#        intPtrdicFontIndexes:c_void_p = dicFontIndexes.Ptr
#
#        GetDllLibXls().XlsOvalShape_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsOvalShape_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsOvalShape_Clone, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollections)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


