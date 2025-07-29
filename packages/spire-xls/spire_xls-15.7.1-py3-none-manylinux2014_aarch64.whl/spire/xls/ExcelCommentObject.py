from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ExcelCommentObject (  SpireObject, IComment) :
    """Represents a comment object in an Excel worksheet.
    
    This class encapsulates the functionality of a comment attached to a cell in an Excel worksheet.
    It provides properties and methods to manage comment visibility, text content, formatting,
    and positioning. The class implements the IComment interface to support standard comment operations.
    """

    def SetCommentLocation(self ,isMoveWithCell:bool,isSizeWithCell:bool):
        """Sets the location behavior of the comment when cells are moved or resized.
        
        Args:
            isMoveWithCell (bool): True to move the comment when the cell is moved; otherwise, False.
            isSizeWithCell (bool): True to resize the comment when the cell is resized; otherwise, False.
        """
        
        GetDllLibXls().ExcelCommentObject_SetCommentLocation.argtypes=[c_void_p ,c_bool,c_bool]
        CallCFunction(GetDllLibXls().ExcelCommentObject_SetCommentLocation, self.Ptr, isMoveWithCell,isSizeWithCell)

    @property

    def Author(self)->str:
        """Gets or sets the author of the comment.
        
        Returns:
            str: The name of the author who created the comment.
        """
        GetDllLibXls().ExcelCommentObject_get_Author.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_Author.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ExcelCommentObject_get_Author, self.Ptr))
        return ret


    @Author.setter
    def Author(self, value:str):
        GetDllLibXls().ExcelCommentObject_set_Author.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_Author, self.Ptr, value)

    @property
    def IsVisible(self)->bool:
        """Gets or sets whether the comment is visible.
        
        Returns:
            bool: True if the comment is visible; otherwise, False.
        """
        GetDllLibXls().ExcelCommentObject_get_IsVisible.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_IsVisible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_IsVisible, self.Ptr)
        return ret

    @IsVisible.setter
    def IsVisible(self, value:bool):
        GetDllLibXls().ExcelCommentObject_set_IsVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_IsVisible, self.Ptr, value)

    @property

    def HtmlString(self)->str:
        """Gets or sets the HTML string which contains data and some formatting in this comment.
        
        Returns:
            str: The HTML representation of the comment content with formatting.
        """
        GetDllLibXls().ExcelCommentObject_get_HtmlString.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_HtmlString.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ExcelCommentObject_get_HtmlString, self.Ptr))
        return ret


    @HtmlString.setter
    def HtmlString(self, value:str):
        GetDllLibXls().ExcelCommentObject_set_HtmlString.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_HtmlString, self.Ptr, value)

    @property
    def Row(self)->int:
        """Gets the row index of the cell that contains the comment.
        
        Returns:
            int: The zero-based row index.
        """
        GetDllLibXls().ExcelCommentObject_get_Row.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_Row.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_Row, self.Ptr)
        return ret

    @property
    def Column(self)->int:
        """Gets the column index of the cell that contains the comment.
        
        Returns:
            int: The zero-based column index.
        """
        GetDllLibXls().ExcelCommentObject_get_Column.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_Column.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_Column, self.Ptr)
        return ret

    @property

    def RichText(self)->'IRichTextString':
        """Gets the rich text formatting of the comment.
        
        Returns:
            IRichTextString: An object representing the rich text formatting applied to the comment text.
        """
        GetDllLibXls().ExcelCommentObject_get_RichText.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_RichText.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelCommentObject_get_RichText, self.Ptr)
        ret = None if intPtr==None else RichTextObject(intPtr)
        return ret


    @property

    def Line(self)->'IShapeLineFormat':
        """Gets the line formatting for the comment shape border.
        
        The line formatting includes properties such as line color, style, and weight.
        
        Returns:
            IShapeLineFormat: The line formatting object for the comment shape border.
        """
        GetDllLibXls().ExcelCommentObject_get_Line.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelCommentObject_get_Line, self.Ptr)
        ret = None if intPtr==None else XlsShapeLineFormat(intPtr)
        return ret


    @property

    def Fill(self)->'IShapeFill':
        """Gets the fill formatting for the comment shape.
        
        The fill formatting includes properties such as fill color, pattern, and gradient.
        
        Returns:
            IShapeFill: The fill formatting object for the comment shape.
        """
        GetDllLibXls().ExcelCommentObject_get_Fill.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelCommentObject_get_Fill, self.Ptr)
        ret = None if intPtr==None else XlsShapeFill(intPtr)
        return ret


    @property

    def Text(self)->str:
        """Gets or sets the text content of the comment.
        
        Returns:
            str: The text content of the comment.
        """
        GetDllLibXls().ExcelCommentObject_get_Text.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ExcelCommentObject_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        GetDllLibXls().ExcelCommentObject_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_Text, self.Ptr, value)

    @property
    def AutoSize(self)->bool:
        """Gets or sets whether the comment is automatically sized to fit its content.
        
        When set to True, the comment will automatically resize to fit the text within its boundaries.
        
        Returns:
            bool: True if the comment is automatically sized; otherwise, False.
        """
        GetDllLibXls().ExcelCommentObject_get_AutoSize.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_AutoSize.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_AutoSize, self.Ptr)
        return ret

    @AutoSize.setter
    def AutoSize(self, value:bool):
        GetDllLibXls().ExcelCommentObject_set_AutoSize.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_AutoSize, self.Ptr, value)

    @property

    def TextFrame(self)->'ITextFrame':
        """Gets the text frame object for the comment shape.
        
        The text frame contains properties related to the text display within the comment.
        
        Returns:
            ITextFrame: The text frame object for the comment shape.
        """
        GetDllLibXls().ExcelCommentObject_get_TextFrame.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_TextFrame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelCommentObject_get_TextFrame, self.Ptr)
        ret = None if intPtr==None else ITextFrame(intPtr)
        return ret


    @property

    def ResizeBehave(self)->'ResizeBehaveType':
        """Gets or sets how the comment shape resizes when rows and columns are resized.
        
        This property specifies how the drawing object shall be resized when the rows and columns 
        between its start and ending anchor are resized or inserted.
        
        Returns:
            ResizeBehaveType: An enumeration value representing the resize behavior type.
        """
        GetDllLibXls().ExcelCommentObject_get_ResizeBehave.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_ResizeBehave.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_ResizeBehave, self.Ptr)
        objwraped = ResizeBehaveType(ret)
        return objwraped

    @ResizeBehave.setter
    def ResizeBehave(self, value:'ResizeBehaveType'):
        GetDllLibXls().ExcelCommentObject_set_ResizeBehave.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_ResizeBehave, self.Ptr, value.value)

    @property
    def Visible(self)->bool:
        """Gets or sets whether the comment shape is visible in the worksheet.
        
        Returns:
            bool: True if the comment shape is visible; otherwise, False.
        """
        GetDllLibXls().ExcelCommentObject_get_Visible.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_Visible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_Visible, self.Ptr)
        return ret

    @Visible.setter
    def Visible(self, value:bool):
        GetDllLibXls().ExcelCommentObject_set_Visible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_Visible, self.Ptr, value)

    @property
    def Height(self)->int:
        """Gets or sets the height of the comment shape in points.
        
        Returns:
            int: The height of the comment shape in points.
        """
        GetDllLibXls().ExcelCommentObject_get_Height.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_Height.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_Height, self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:int):
        GetDllLibXls().ExcelCommentObject_set_Height.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_Height, self.Ptr, value)

    @property

    def HAlignment(self)->'CommentHAlignType':
        """Gets or sets the horizontal alignment of text in the comment.
        
        Returns:
            CommentHAlignType: An enumeration value representing the horizontal alignment type.
        """
        GetDllLibXls().ExcelCommentObject_get_HAlignment.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_HAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_HAlignment, self.Ptr)
        objwraped = CommentHAlignType(ret)
        return objwraped

    @HAlignment.setter
    def HAlignment(self, value:'CommentHAlignType'):
        GetDllLibXls().ExcelCommentObject_set_HAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_HAlignment, self.Ptr, value.value)

    @property

    def VAlignment(self)->'CommentVAlignType':
        """Gets or sets the vertical alignment of text in the comment.
        
        Returns:
            CommentVAlignType: An enumeration value representing the vertical alignment type.
        """
        GetDllLibXls().ExcelCommentObject_get_VAlignment.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_VAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_VAlignment, self.Ptr)
        objwraped = CommentVAlignType(ret)
        return objwraped

    @VAlignment.setter
    def VAlignment(self, value:'CommentVAlignType'):
        GetDllLibXls().ExcelCommentObject_set_VAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_VAlignment, self.Ptr, value.value)

    @property

    def TextRotation(self)->'TextRotationType':
        """Gets or sets the rotation type of the text in the comment.
        
        Returns:
            TextRotationType: An enumeration value representing the text rotation type.
        """
        GetDllLibXls().ExcelCommentObject_get_TextRotation.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_TextRotation.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_TextRotation, self.Ptr)
        objwraped = TextRotationType(ret)
        return objwraped

    @TextRotation.setter
    def TextRotation(self, value:'TextRotationType'):
        GetDllLibXls().ExcelCommentObject_set_TextRotation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_TextRotation, self.Ptr, value.value)

    @property
    def ID(self)->int:
        """Gets the unique identifier for the comment shape.
        
        Returns:
            int: The unique identifier for the comment shape.
        """
        GetDllLibXls().ExcelCommentObject_get_ID.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_ID.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_ID, self.Ptr)
        return ret

    @property
    def Left(self)->int:
        """Gets or sets the horizontal position of the comment shape in points.
        
        Returns:
            int: The horizontal position of the comment shape in points, measured from the left edge.
        """
        GetDllLibXls().ExcelCommentObject_get_Left.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_Left.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_Left, self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:int):
        GetDllLibXls().ExcelCommentObject_set_Left.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_Left, self.Ptr, value)

    @property

    def Name(self)->str:
        """Gets or sets the name of the comment shape.
        
        Returns:
            str: The name of the comment shape.
        """
        GetDllLibXls().ExcelCommentObject_get_Name.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ExcelCommentObject_get_Name, self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        GetDllLibXls().ExcelCommentObject_set_Name.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_Name, self.Ptr, value)

    @property
    def Top(self)->int:
        """Gets or sets the vertical position of the comment shape in points.
        
        Returns:
            int: The vertical position of the comment shape in points, measured from the top edge.
        """
        GetDllLibXls().ExcelCommentObject_get_Top.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_Top.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_Top, self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:int):
        GetDllLibXls().ExcelCommentObject_set_Top.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_Top, self.Ptr, value)

    @property
    def Width(self)->int:
        """Gets or sets the width of the comment shape in points.
        
        Returns:
            int: The width of the comment shape in points.
        """
        GetDllLibXls().ExcelCommentObject_get_Width.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_Width.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_Width, self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:int):
        GetDllLibXls().ExcelCommentObject_set_Width.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_Width, self.Ptr, value)

    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets or sets the shape type of the comment.
        
        Returns:
            ExcelShapeType: An enumeration value representing the shape type of the comment.
        """
        GetDllLibXls().ExcelCommentObject_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_ShapeType, self.Ptr)
        objwraped = ExcelShapeType(ret)
        return objwraped

    @ShapeType.setter
    def ShapeType(self, value:'ExcelShapeType'):
        GetDllLibXls().ExcelCommentObject_set_ShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_ShapeType, self.Ptr, value.value)

    @property
    def IsLocked(self)->bool:
        """Gets or sets whether the comment shape is locked.
        
        When a comment shape is locked, it cannot be modified when the worksheet is protected.
        
        Returns:
            bool: True if the comment shape is locked; otherwise, False.
        """
        GetDllLibXls().ExcelCommentObject_get_IsLocked.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_IsLocked.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_IsLocked, self.Ptr)
        return ret

    @IsLocked.setter
    def IsLocked(self, value:bool):
        GetDllLibXls().ExcelCommentObject_set_IsLocked.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_IsLocked, self.Ptr, value)

    @property
    def IsPrintable(self)->bool:
        """Gets or sets whether the comment shape is printed when the worksheet is printed.
        
        Returns:
            bool: True if the comment shape is printed; otherwise, False.
        """
        GetDllLibXls().ExcelCommentObject_get_IsPrintable.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_IsPrintable.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_IsPrintable, self.Ptr)
        return ret

    @IsPrintable.setter
    def IsPrintable(self, value:bool):
        GetDllLibXls().ExcelCommentObject_set_IsPrintable.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_IsPrintable, self.Ptr, value)

    @property

    def AlternativeText(self)->str:
        """Gets or sets the alternative text description for the comment shape.
        
        Alternative text is used for accessibility purposes and appears when the comment
        is hovered over or when the comment cannot be displayed.
        
        Returns:
            str: The alternative text for the comment shape.
        """
        GetDllLibXls().ExcelCommentObject_get_AlternativeText.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_AlternativeText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ExcelCommentObject_get_AlternativeText, self.Ptr))
        return ret


    @AlternativeText.setter
    def AlternativeText(self, value:str):
        GetDllLibXls().ExcelCommentObject_set_AlternativeText.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_AlternativeText, self.Ptr, value)

    @property

    def Parent(self)->'SpireObject':
        """Gets the parent object of the comment.
        
        Returns:
            SpireObject: The parent object that contains this comment.
        """
        GetDllLibXls().ExcelCommentObject_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelCommentObject_get_Parent, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @property
    def IsTextLocked(self)->bool:
        """Gets or sets whether the text in the comment is locked.
        
        When the text is locked, it cannot be edited when the worksheet is protected.
        
        Returns:
            bool: True if the text in the comment is locked; otherwise, False.
        """
        GetDllLibXls().ExcelCommentObject_get_IsTextLocked.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_IsTextLocked.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_IsTextLocked, self.Ptr)
        return ret

    @IsTextLocked.setter
    def IsTextLocked(self, value:bool):
        GetDllLibXls().ExcelCommentObject_set_IsTextLocked.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_IsTextLocked, self.Ptr, value)

    @property
    def IsSmartArt(self)->bool:
        """Gets whether the comment is part of a SmartArt object.
        
        Returns:
            bool: True if the comment is part of a SmartArt object; otherwise, False.
        """
        GetDllLibXls().ExcelCommentObject_get_IsSmartArt.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_IsSmartArt.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_IsSmartArt, self.Ptr)
        return ret

    @property

    def OnAction(self)->str:
        """Gets or sets the name of the macro to run when the comment is clicked.
        
        Returns:
            str: The name of the macro to run when the comment is clicked.
        """
        GetDllLibXls().ExcelCommentObject_get_OnAction.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_OnAction.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ExcelCommentObject_get_OnAction, self.Ptr))
        return ret


    @OnAction.setter
    def OnAction(self, value:str):
        GetDllLibXls().ExcelCommentObject_set_OnAction.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_OnAction, self.Ptr, value)

    @property
    def IsLockAspectRatio(self)->bool:
        """Gets or sets whether the aspect ratio of the comment shape is locked.
        
        When the aspect ratio is locked, the width and height of the comment shape
        maintain their proportions when the shape is resized.
        
        Returns:
            bool: True if the aspect ratio is locked; otherwise, False.
        """
        GetDllLibXls().ExcelCommentObject_get_IsLockAspectRatio.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_IsLockAspectRatio.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_IsLockAspectRatio, self.Ptr)
        return ret

    @IsLockAspectRatio.setter
    def IsLockAspectRatio(self, value:bool):
        GetDllLibXls().ExcelCommentObject_set_IsLockAspectRatio.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_IsLockAspectRatio, self.Ptr, value)

    @property

    def Shadow(self)->'IShadow':
        """Gets the shadow effect formatting for the comment shape.
        
        The shadow effect adds a shadow behind the comment.
        
        Returns:
            IShadow: The shadow effect formatting object for the comment shape.
        """
        GetDllLibXls().ExcelCommentObject_get_Shadow.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_Shadow.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelCommentObject_get_Shadow, self.Ptr)
        ret = None if intPtr==None else ChartShadow(intPtr)
        return ret


    @property

    def Glow(self)->'IGlow':
        """Gets the glow effect formatting for the comment shape.
        
        The glow effect adds a colored, blurred outline around the comment.
        
        Returns:
            IGlow: The glow effect formatting object for the comment shape.
        """
        GetDllLibXls().ExcelCommentObject_get_Glow.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_Glow.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelCommentObject_get_Glow, self.Ptr)
        ret = None if intPtr==None else ShapeGlow(intPtr)
        return ret


    @property

    def Reflection(self)->'IReflectionEffect':
        """Gets the reflection effect formatting for the comment shape.
        
        The reflection effect adds a reflection of the comment below it.
        
        Returns:
            IReflectionEffect: The reflection effect formatting object for the comment shape.
        """
        GetDllLibXls().ExcelCommentObject_get_Reflection.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_Reflection.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelCommentObject_get_Reflection, self.Ptr)
        ret = None if intPtr==None else ShapeReflection(intPtr)
        return ret


    @property

    def ThreeD(self)->'IFormat3D':
        """Gets the 3D formatting for the comment shape.
        
        The 3D formatting includes properties such as depth, contour, and surface.
        
        Returns:
            IFormat3D: The 3D formatting object for the comment shape.
        """
        GetDllLibXls().ExcelCommentObject_get_ThreeD.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_ThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelCommentObject_get_ThreeD, self.Ptr)
        ret = None if intPtr==None else Format3D(intPtr)
        return ret


    @property
    def Rotation(self)->int:
        """Gets or sets the rotation of the comment shape, in degrees.
        
        This property controls the angle of rotation for the comment shape.
        Positive values rotate the shape clockwise, while negative values
        rotate it counterclockwise.
        
        Returns:
            int: The rotation angle in degrees.
        """
        GetDllLibXls().ExcelCommentObject_get_Rotation.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_Rotation.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExcelCommentObject_get_Rotation, self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:int):
        GetDllLibXls().ExcelCommentObject_set_Rotation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_Rotation, self.Ptr, value)

    @property

    def LinkedCell(self)->'IXLSRange':
        """Gets or sets the cell range that is linked to the comment.
        
        When a cell range is linked to a comment, changes to the linked cell
        can affect the comment's behavior or appearance.
        
        Returns:
            IXLSRange: The cell range that is linked to the comment.
        """
        GetDllLibXls().ExcelCommentObject_get_LinkedCell.argtypes=[c_void_p]
        GetDllLibXls().ExcelCommentObject_get_LinkedCell.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ExcelCommentObject_get_LinkedCell, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @LinkedCell.setter
    def LinkedCell(self, value:'IXLSRange'):
        GetDllLibXls().ExcelCommentObject_set_LinkedCell.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ExcelCommentObject_set_LinkedCell, self.Ptr, value.Ptr)

    def Remove(self):
        """Removes the comment from the worksheet.
        
        This method permanently deletes the comment from the worksheet.
        After calling this method, the comment object is no longer valid.
        """
        GetDllLibXls().ExcelCommentObject_Remove.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().ExcelCommentObject_Remove, self.Ptr)


    def Scale(self ,scaleWidth:int,scaleHeight:int):
        """Scales the comment shape by the specified percentages.
        
        This method resizes the comment shape according to the specified width and height
        scaling percentages.
        
        Args:
            scaleWidth (int): The percentage to scale the width (100 = original size).
            scaleHeight (int): The percentage to scale the height (100 = original size).
        """
        
        GetDllLibXls().ExcelCommentObject_Scale.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().ExcelCommentObject_Scale, self.Ptr, scaleWidth,scaleHeight)

