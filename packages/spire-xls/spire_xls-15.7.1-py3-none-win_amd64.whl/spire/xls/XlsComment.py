from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsComment (  XlsShape, IComment, ITextBox) :
    """Represents a comment in an Excel worksheet.
    
    This class provides properties and methods for manipulating comments in Excel,
    including text formatting, alignment, visibility, and positioning. It extends XlsShape and
    implements the IComment and ITextBox interfaces.
    """
    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets the type of the shape.
        
        Returns:
            ExcelShapeType: An enumeration value representing the type of the shape.
        """
        GetDllLibXls().XlsComment_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsComment_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsComment_get_ShapeType, self.Ptr)
        objwraped = ExcelShapeType(ret)
        return objwraped

    @property

    def Author(self)->str:
        """Gets or sets the author of the comment.
        
        Returns:
            str: The name of the author who created the comment.
        """
        GetDllLibXls().XlsComment_get_Author.argtypes=[c_void_p]
        GetDllLibXls().XlsComment_get_Author.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsComment_get_Author, self.Ptr))
        return ret


    @Author.setter
    def Author(self, value:str):
        """Sets the author of the comment.
        
        Args:
            value (str): The name of the author to set for the comment.
        """
        GetDllLibXls().XlsComment_set_Author.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsComment_set_Author, self.Ptr, value)

    @property
    def AutoSize(self)->bool:
        """Gets or sets whether the comment is automatically sized.
        
        Returns:
            bool: True if the comment is automatically sized; otherwise, False.
        """
        GetDllLibXls().XlsComment_get_AutoSize.argtypes=[c_void_p]
        GetDllLibXls().XlsComment_get_AutoSize.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsComment_get_AutoSize, self.Ptr)
        return ret

    @AutoSize.setter
    def AutoSize(self, value:bool):
        """Sets whether the comment is automatically sized.
        
        Args:
            value (bool): True to automatically size the comment; otherwise, False.
        """
        GetDllLibXls().XlsComment_set_AutoSize.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsComment_set_AutoSize, self.Ptr, value)

    @property
    def Column(self)->int:
        """Gets or sets the column index of the cell containing the comment.
        
        Returns:
            int: The zero-based column index.
        """
        GetDllLibXls().XlsComment_get_Column.argtypes=[c_void_p]
        GetDllLibXls().XlsComment_get_Column.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsComment_get_Column, self.Ptr)
        return ret

    @Column.setter
    def Column(self, value:int):
        """Sets the column index of the cell containing the comment.
        
        Args:
            value (int): The zero-based column index.
        """
        GetDllLibXls().XlsComment_set_Column.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsComment_set_Column, self.Ptr, value)

    @property
    def Row(self)->int:
        """Gets or sets the row index of the cell containing the comment.
        
        Returns:
            int: The zero-based row index.
        """
        GetDllLibXls().XlsComment_get_Row.argtypes=[c_void_p]
        GetDllLibXls().XlsComment_get_Row.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsComment_get_Row, self.Ptr)
        return ret

    @Row.setter
    def Row(self, value:int):
        """Sets the row index of the cell containing the comment.
        
        Args:
            value (int): The zero-based row index.
        """
        GetDllLibXls().XlsComment_set_Row.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsComment_set_Row, self.Ptr, value)

    @property

    def Text(self)->str:
        """Gets or sets the text content of the comment.
        
        Returns:
            str: The text content of the comment.
        """
        GetDllLibXls().XlsComment_get_Text.argtypes=[c_void_p]
        GetDllLibXls().XlsComment_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsComment_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        """Sets the text content of the comment.
        
        Args:
            value (str): The text content to set for the comment.
        """
        GetDllLibXls().XlsComment_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsComment_set_Text, self.Ptr, value)

    @property
    def IsTextLocked(self)->bool:
        """Gets or sets whether the text in the comment is locked.
        
        Returns:
            bool: True if the text is locked; otherwise, False.
        """
        GetDllLibXls().XlsComment_get_IsTextLocked.argtypes=[c_void_p]
        GetDllLibXls().XlsComment_get_IsTextLocked.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsComment_get_IsTextLocked, self.Ptr)
        return ret

    @IsTextLocked.setter
    def IsTextLocked(self, value:bool):
        """Sets whether the text in the comment is locked.
        
        Args:
            value (bool): True to lock the text; otherwise, False.
        """
        GetDllLibXls().XlsComment_set_IsTextLocked.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsComment_set_IsTextLocked, self.Ptr, value)

    @property

    def TextRotation(self)->'TextRotationType':
        """Gets or sets the rotation of the text in the comment.
        
        Returns:
            TextRotationType: An enumeration value representing the text rotation type.
        """
        GetDllLibXls().XlsComment_get_TextRotation.argtypes=[c_void_p]
        GetDllLibXls().XlsComment_get_TextRotation.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsComment_get_TextRotation, self.Ptr)
        objwraped = TextRotationType(ret)
        return objwraped

    @TextRotation.setter
    def TextRotation(self, value:'TextRotationType'):
        """Sets the rotation of the text in the comment.
        
        Args:
            value (TextRotationType): An enumeration value representing the text rotation type.
        """
        GetDllLibXls().XlsComment_set_TextRotation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsComment_set_TextRotation, self.Ptr, value.value)

    @property

    def RichText(self)->'IRichTextString':
        """Gets the rich text formatting of the comment text.
        
        Returns:
            IRichTextString: An object representing the rich text formatting.
        """
        GetDllLibXls().XlsComment_get_RichText.argtypes=[c_void_p]
        GetDllLibXls().XlsComment_get_RichText.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsComment_get_RichText, self.Ptr)
        ret = None if intPtr==None else RichTextObject(intPtr)
        return ret


    @property

    def HAlignment(self)->'CommentHAlignType':
        """Gets or sets the horizontal alignment of the text in the comment.
        
        Returns:
            CommentHAlignType: An enumeration value representing the horizontal alignment.
        """
        GetDllLibXls().XlsComment_get_HAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsComment_get_HAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsComment_get_HAlignment, self.Ptr)
        objwraped = CommentHAlignType(ret)
        return objwraped

    @HAlignment.setter
    def HAlignment(self, value:'CommentHAlignType'):
        """Sets the horizontal alignment of the text in the comment.
        
        Args:
            value (CommentHAlignType): An enumeration value representing the horizontal alignment.
        """
        GetDllLibXls().XlsComment_set_HAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsComment_set_HAlignment, self.Ptr, value.value)

    def Remove(self):
        """Removes the comment from the worksheet.
        """
        GetDllLibXls().XlsComment_Remove.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsComment_Remove, self.Ptr)

    @property

    def VAlignment(self)->'CommentVAlignType':
        """Gets or sets the vertical alignment of the text in the comment.
        
        Returns:
            CommentVAlignType: An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().XlsComment_get_VAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsComment_get_VAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsComment_get_VAlignment, self.Ptr)
        objwraped = CommentVAlignType(ret)
        return objwraped

    @VAlignment.setter
    def VAlignment(self, value:'CommentVAlignType'):
        """Sets the vertical alignment of the text in the comment.
        
        Args:
            value (CommentVAlignType): An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().XlsComment_set_VAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsComment_set_VAlignment, self.Ptr, value.value)

    @property
    def IsVisible(self)->bool:
        """Gets or sets whether the comment is visible.
        
        Returns:
            bool: True if the comment is visible; otherwise, False.
        """
        GetDllLibXls().XlsComment_get_IsVisible.argtypes=[c_void_p]
        GetDllLibXls().XlsComment_get_IsVisible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsComment_get_IsVisible, self.Ptr)
        return ret

    @IsVisible.setter
    def IsVisible(self, value:bool):
        """Sets whether the comment is visible.
        
        Args:
            value (bool): True to make the comment visible; otherwise, False.
        """
        GetDllLibXls().XlsComment_set_IsVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsComment_set_IsVisible, self.Ptr, value)

    @property

    def Fill(self)->'IShapeFill':
        """Gets the fill formatting of the comment.
        
        Returns:
            IShapeFill: An object representing the fill formatting.
        """
        GetDllLibXls().XlsComment_get_Fill.argtypes=[c_void_p]
        GetDllLibXls().XlsComment_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsComment_get_Fill, self.Ptr)
        ret = None if intPtr==None else XlsShapeFill(intPtr)
        return ret


#
#    def Clone(self ,parent:'SpireObject',hashNewNames:'Dictionary2',dicFontIndexes:'Dictionary2',addToCollections:bool)->'IShape':
#        """
#
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrhashNewNames:c_void_p = hashNewNames.Ptr
#        intPtrdicFontIndexes:c_void_p = dicFontIndexes.Ptr
#
#        GetDllLibXls().XlsComment_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsComment_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsComment_Clone, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollections)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


