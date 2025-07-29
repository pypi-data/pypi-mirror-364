from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsTextBoxShape (  XlsShape, ITextBoxLinkShape, TextBoxShapeBase) :
    """Represents a text box shape in an Excel worksheet.
    
    This class provides properties and methods for manipulating text box shapes,
    including text content, formatting, alignment, and margins.
    """
    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets the shape type of the text box.
        
        Returns:
            ExcelShapeType: An enumeration value representing the shape type of the text box.
        """
        GetDllLibXls().XlsTextBoxShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_ShapeType, self.Ptr)
        objwraped = ExcelShapeType(ret)
        return objwraped

    @property

    def Text(self)->str:
        """Gets or sets the text displayed in the text box.
        
        Returns:
            str: The text content of the text box.
        """
        GetDllLibXls().XlsTextBoxShape_get_Text.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsTextBoxShape_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        """Sets the text displayed in the text box.
        
        Args:
            value (str): The text to display in the text box.
        """
        GetDllLibXls().XlsTextBoxShape_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_Text, self.Ptr, value)

    @property
    def IsTextLocked(self)->bool:
        """Gets or sets whether the text in the text box is locked.
        
        Returns:
            bool: True if the text is locked; otherwise, False.
        """
        GetDllLibXls().XlsTextBoxShape_get_IsTextLocked.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_IsTextLocked.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_IsTextLocked, self.Ptr)
        return ret

    @IsTextLocked.setter
    def IsTextLocked(self, value:bool):
        """Sets whether the text in the text box is locked.
        
        Args:
            value (bool): True to lock the text; False to unlock it.
        """
        GetDllLibXls().XlsTextBoxShape_set_IsTextLocked.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_IsTextLocked, self.Ptr, value)

    @property
    def IsWrapText(self)->bool:
        """Gets or sets whether text wrapping is enabled in the text box.
        
        Returns:
            bool: True if text wrapping is enabled; otherwise, False.
        """
        GetDllLibXls().XlsTextBoxShape_get_IsWrapText.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_IsWrapText.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_IsWrapText, self.Ptr)
        return ret

    @IsWrapText.setter
    def IsWrapText(self, value:bool):
        """Sets whether text wrapping is enabled in the text box.
        
        Args:
            value (bool): True to enable text wrapping; False to disable it.
        """
        GetDllLibXls().XlsTextBoxShape_set_IsWrapText.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_IsWrapText, self.Ptr, value)

    @property

    def TextRotation(self)->'TextRotationType':
        """Gets or sets the text rotation in the text box.
        
        Returns:
            TextRotationType: An enumeration value representing the text rotation.
        """
        GetDllLibXls().XlsTextBoxShape_get_TextRotation.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_TextRotation.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_TextRotation, self.Ptr)
        objwraped = TextRotationType(ret)
        return objwraped

    @TextRotation.setter
    def TextRotation(self, value:'TextRotationType'):
        """Sets the text rotation in the text box.
        
        Args:
            value (TextRotationType): An enumeration value representing the text rotation.
        """
        GetDllLibXls().XlsTextBoxShape_set_TextRotation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_TextRotation, self.Ptr, value.value)

    @property

    def RichText(self)->'IRichTextString':
        """Gets the rich text formatting for the text in the text box.
        
        Returns:
            IRichTextString: An object that represents the rich text formatting.
        """
        GetDllLibXls().XlsTextBoxShape_get_RichText.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_RichText.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_RichText, self.Ptr)
        ret = None if intPtr==None else RichTextShape(intPtr)
        return ret


    @property

    def HAlignment(self)->'CommentHAlignType':
        """Gets or sets the horizontal alignment of text in the text box.
        
        Returns:
            CommentHAlignType: An enumeration value representing the horizontal alignment.
        """
        GetDllLibXls().XlsTextBoxShape_get_HAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_HAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_HAlignment, self.Ptr)
        objwraped = CommentHAlignType(ret)
        return objwraped

    @HAlignment.setter
    def HAlignment(self, value:'CommentHAlignType'):
        """Sets the horizontal alignment of text in the text box.
        
        Args:
            value (CommentHAlignType): An enumeration value representing the horizontal alignment.
        """
        GetDllLibXls().XlsTextBoxShape_set_HAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_HAlignment, self.Ptr, value.value)

    @property

    def VAlignment(self)->'CommentVAlignType':
        """Gets or sets the vertical alignment of text in the text box.
        
        Returns:
            CommentVAlignType: An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().XlsTextBoxShape_get_VAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_VAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_VAlignment, self.Ptr)
        objwraped = CommentVAlignType(ret)
        return objwraped

    @VAlignment.setter
    def VAlignment(self, value:'CommentVAlignType'):
        """Sets the vertical alignment of text in the text box.
        
        Args:
            value (CommentVAlignType): An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().XlsTextBoxShape_set_VAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_VAlignment, self.Ptr, value.value)

    @property

    def Coordinates2007(self)->'Rectangle':
        """Gets or sets the coordinates of the text box in Excel 2007 format.
        
        Returns:
            Rectangle: A Rectangle object representing the position and size of the text box.
        """
        GetDllLibXls().XlsTextBoxShape_get_Coordinates2007.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_Coordinates2007.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_Coordinates2007, self.Ptr)
        ret = None if intPtr==None else Rectangle(intPtr)
        return ret


    @Coordinates2007.setter
    def Coordinates2007(self, value:'Rectangle'):
        """Sets the coordinates of the text box in Excel 2007 format.
        
        Args:
            value (Rectangle): A Rectangle object representing the position and size of the text box.
        """
        GetDllLibXls().XlsTextBoxShape_set_Coordinates2007.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_Coordinates2007, self.Ptr, value.Ptr)

    @property
    def HasStyleProperties(self)->bool:
        """Gets whether the text box has style properties.
        
        Returns:
            bool: True if the text box has style properties; otherwise, False.
        """
        GetDllLibXls().XlsTextBoxShape_get_HasStyleProperties.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_HasStyleProperties.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_HasStyleProperties, self.Ptr)
        return ret

    @property

    def TextFieldId(self)->str:
        """Gets or sets the text field ID for the text box.
        
        This property is used for identifying the text box in field operations.
        
        Returns:
            str: The text field ID.
        """
        GetDllLibXls().XlsTextBoxShape_get_TextFieldId.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_TextFieldId.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsTextBoxShape_get_TextFieldId, self.Ptr))
        return ret


    @TextFieldId.setter
    def TextFieldId(self, value:str):
        """Sets the text field ID for the text box.
        
        Args:
            value (str): The text field ID to set.
        """
        GetDllLibXls().XlsTextBoxShape_set_TextFieldId.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_TextFieldId, self.Ptr, value)

    @property

    def TextFieldType(self)->str:
        """Gets or sets the text field type for the text box.
        
        This property defines the type of field that the text box represents.
        
        Returns:
            str: The text field type.
        """
        GetDllLibXls().XlsTextBoxShape_get_TextFieldType.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_TextFieldType.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsTextBoxShape_get_TextFieldType, self.Ptr))
        return ret


    @TextFieldType.setter
    def TextFieldType(self, value:str):
        """Sets the text field type for the text box.
        
        Args:
            value (str): The text field type to set.
        """
        GetDllLibXls().XlsTextBoxShape_set_TextFieldType.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_TextFieldType, self.Ptr, value)

    @property

    def FillColor(self)->'Color':
        """Gets or sets the fill color of the text box.
        
        Returns:
            Color: A Color object representing the fill color of the text box.
        """
        GetDllLibXls().XlsTextBoxShape_get_FillColor.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_FillColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_FillColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @FillColor.setter
    def FillColor(self, value:'Color'):
        """Sets the fill color of the text box.
        
        Args:
            value (Color): A Color object representing the fill color to set.
        """
        GetDllLibXls().XlsTextBoxShape_set_FillColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_FillColor, self.Ptr, value.Ptr)

    @property

    def InsetMode(self)->str:
        """Gets or sets the inset mode for the text box.
        
        The inset mode determines how the text is positioned within the text box.
        
        Returns:
            str: A string representing the inset mode.
        """
        GetDllLibXls().XlsTextBoxShape_get_InsetMode.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_InsetMode.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsTextBoxShape_get_InsetMode, self.Ptr))
        return ret


    @InsetMode.setter
    def InsetMode(self, value:str):
        """Sets the inset mode for the text box.
        
        Args:
            value (str): A string representing the inset mode to set.
        """
        GetDllLibXls().XlsTextBoxShape_set_InsetMode.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_InsetMode, self.Ptr, value)

    @property
    def LeftMarginEMU(self)->int:
        """Gets or sets the left margin of the text box in EMU (English Metric Units).
        
        Returns:
            int: The left margin value in EMU.
        """
        GetDllLibXls().XlsTextBoxShape_get_LeftMarginEMU.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_LeftMarginEMU.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_LeftMarginEMU, self.Ptr)
        return ret

    @LeftMarginEMU.setter
    def LeftMarginEMU(self, value:int):
        """Sets the left margin of the text box in EMU (English Metric Units).
        
        Args:
            value (int): The left margin value in EMU to set.
        """
        GetDllLibXls().XlsTextBoxShape_set_LeftMarginEMU.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_LeftMarginEMU, self.Ptr, value)

    @property
    def TopMarginEMU(self)->int:
        """Gets or sets the top margin of the text box in EMU (English Metric Units).
        
        Returns:
            int: The top margin value in EMU.
        """
        GetDllLibXls().XlsTextBoxShape_get_TopMarginEMU.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_TopMarginEMU.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_TopMarginEMU, self.Ptr)
        return ret

    @TopMarginEMU.setter
    def TopMarginEMU(self, value:int):
        """Sets the top margin of the text box in EMU (English Metric Units).
        
        Args:
            value (int): The top margin value in EMU to set.
        """
        GetDllLibXls().XlsTextBoxShape_set_TopMarginEMU.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_TopMarginEMU, self.Ptr, value)

    @property
    def RightMarginEMU(self)->int:
        """Gets or sets the right margin of the text box in EMU (English Metric Units).
        
        Returns:
            int: The right margin value in EMU.
        """
        GetDllLibXls().XlsTextBoxShape_get_RightMarginEMU.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_RightMarginEMU.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_RightMarginEMU, self.Ptr)
        return ret

    @RightMarginEMU.setter
    def RightMarginEMU(self, value:int):
        """Sets the right margin of the text box in EMU (English Metric Units).
        
        Args:
            value (int): The right margin value in EMU to set.
        """
        GetDllLibXls().XlsTextBoxShape_set_RightMarginEMU.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_RightMarginEMU, self.Ptr, value)

    @property
    def BottomMarginEMU(self)->int:
        """Gets or sets the bottom margin of the text box in EMU (English Metric Units).
        
        Returns:
            int: The bottom margin value in EMU.
        """
        GetDllLibXls().XlsTextBoxShape_get_BottomMarginEMU.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_BottomMarginEMU.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_BottomMarginEMU, self.Ptr)
        return ret

    @BottomMarginEMU.setter
    def BottomMarginEMU(self, value:int):
        """Sets the bottom margin of the text box in EMU (English Metric Units).
        
        Args:
            value (int): The bottom margin value in EMU to set.
        """
        GetDllLibXls().XlsTextBoxShape_set_BottomMarginEMU.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_BottomMarginEMU, self.Ptr, value)

    @property
    def InnerBottomMargin(self)->float:
        """Gets or sets the inner bottom margin of the text box in points.
        
        Returns:
            float: The inner bottom margin value in points.
        """
        GetDllLibXls().XlsTextBoxShape_get_InnerBottomMargin.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_InnerBottomMargin.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_InnerBottomMargin, self.Ptr)
        return ret

    @InnerBottomMargin.setter
    def InnerBottomMargin(self, value:float):
        """Sets the inner bottom margin of the text box in points.
        
        Args:
            value (float): The inner bottom margin value in points to set.
        """
        GetDllLibXls().XlsTextBoxShape_set_InnerBottomMargin.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_InnerBottomMargin, self.Ptr, value)

    @property
    def InnerLeftMargin(self)->float:
        """Gets or sets the inner left margin of the text box in points.
        
        Returns:
            float: The inner left margin value in points.
        """
        GetDllLibXls().XlsTextBoxShape_get_InnerLeftMargin.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_InnerLeftMargin.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_InnerLeftMargin, self.Ptr)
        return ret

    @InnerLeftMargin.setter
    def InnerLeftMargin(self, value:float):
        """Sets the inner left margin of the text box in points.
        
        Args:
            value (float): The inner left margin value in points to set.
        """
        GetDllLibXls().XlsTextBoxShape_set_InnerLeftMargin.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_InnerLeftMargin, self.Ptr, value)

    @property
    def InnerRightMargin(self)->float:
        """Gets or sets the inner right margin of the text box in points.
        
        Returns:
            float: The inner right margin value in points.
        """
        GetDllLibXls().XlsTextBoxShape_get_InnerRightMargin.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_InnerRightMargin.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_InnerRightMargin, self.Ptr)
        return ret

    @InnerRightMargin.setter
    def InnerRightMargin(self, value:float):
        """Sets the inner right margin of the text box in points.
        
        Args:
            value (float): The inner right margin value in points to set.
        """
        GetDllLibXls().XlsTextBoxShape_set_InnerRightMargin.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_InnerRightMargin, self.Ptr, value)

    @property
    def InnerTopMargin(self)->float:
        """Gets or sets the inner top margin of the text box in points.
        
        Returns:
            float: The inner top margin value in points.
        """
        GetDllLibXls().XlsTextBoxShape_get_InnerTopMargin.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_InnerTopMargin.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_InnerTopMargin, self.Ptr)
        return ret

    @InnerTopMargin.setter
    def InnerTopMargin(self, value:float):
        """Sets the inner top margin of the text box in points.
        
        Args:
            value (float): The inner top margin value in points to set.
        """
        GetDllLibXls().XlsTextBoxShape_set_InnerTopMargin.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_InnerTopMargin, self.Ptr, value)

    @property

    def VertOverflow(self)->str:
        """Gets or sets the vertical overflow behavior for text in the text box.
        
        This property determines how text is handled when it exceeds the vertical bounds of the text box.
        
        Returns:
            str: A string representing the vertical overflow behavior.
        """
        GetDllLibXls().XlsTextBoxShape_get_VertOverflow.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_VertOverflow.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsTextBoxShape_get_VertOverflow, self.Ptr))
        return ret


    @VertOverflow.setter
    def VertOverflow(self, value:str):
        """Sets the vertical overflow behavior for text in the text box.
        
        Args:
            value (str): A string representing the vertical overflow behavior to set.
        """
        GetDllLibXls().XlsTextBoxShape_set_VertOverflow.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_VertOverflow, self.Ptr, value)

    @property

    def HorzOverflow(self)->str:
        """Gets or sets the horizontal overflow behavior for text in the text box.
        
        This property determines how text is handled when it exceeds the horizontal bounds of the text box.
        
        Returns:
            str: A string representing the horizontal overflow behavior.
        """
        GetDllLibXls().XlsTextBoxShape_get_HorzOverflow.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_HorzOverflow.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsTextBoxShape_get_HorzOverflow, self.Ptr))
        return ret


    @HorzOverflow.setter
    def HorzOverflow(self, value:str):
        """Sets the horizontal overflow behavior for text in the text box.
        
        Args:
            value (str): A string representing the horizontal overflow behavior to set.
        """
        GetDllLibXls().XlsTextBoxShape_set_HorzOverflow.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_HorzOverflow, self.Ptr, value)

    @property

    def Anchor(self)->str:
        """Gets or sets the anchor type for the text box.
        
        The anchor type determines how the text box is positioned relative to cells in the worksheet.
        
        Returns:
            str: A string representing the anchor type.
        """
        GetDllLibXls().XlsTextBoxShape_get_Anchor.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_Anchor.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsTextBoxShape_get_Anchor, self.Ptr))
        return ret


    @Anchor.setter
    def Anchor(self, value:str):
        """Sets the anchor type for the text box.
        
        Args:
            value (str): A string representing the anchor type to set.
        """
        GetDllLibXls().XlsTextBoxShape_set_Anchor.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_Anchor, self.Ptr, value)

    @property

    def Vert(self)->str:
        """Gets or sets the vertical text direction for the text box.
        
        This property determines the direction in which text flows vertically within the text box.
        
        Returns:
            str: A string representing the vertical text direction.
        """
        GetDllLibXls().XlsTextBoxShape_get_Vert.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_Vert.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsTextBoxShape_get_Vert, self.Ptr))
        return ret


    @Vert.setter
    def Vert(self, value:str):
        """Sets the vertical text direction for the text box.
        
        Args:
            value (str): A string representing the vertical text direction to set.
        """
        GetDllLibXls().XlsTextBoxShape_set_Vert.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_Vert, self.Ptr, value)

    @property
    def IsTextWrapped(self)->bool:
        """Gets or sets whether text is wrapped within the text box.
        
        When text wrapping is enabled, text that exceeds the width of the text box will wrap to the next line.
        
        Returns:
            bool: True if text wrapping is enabled; otherwise, False.
        """
        GetDllLibXls().XlsTextBoxShape_get_IsTextWrapped.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_IsTextWrapped.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_IsTextWrapped, self.Ptr)
        return ret

    @IsTextWrapped.setter
    def IsTextWrapped(self, value:bool):
        """Sets whether text is wrapped within the text box.
        
        Args:
            value (bool): True to enable text wrapping; False to disable it.
        """
        GetDllLibXls().XlsTextBoxShape_set_IsTextWrapped.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_IsTextWrapped, self.Ptr, value)

    @property
    def UpRight(self)->int:
        """Gets or sets whether text is displayed upright in the text box.
        
        This property controls the orientation of text characters within the text box.
        
        Returns:
            int: A value indicating the upright text setting.
        """
        GetDllLibXls().XlsTextBoxShape_get_UpRight.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_UpRight.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_UpRight, self.Ptr)
        return ret

    @UpRight.setter
    def UpRight(self, value:int):
        """Sets whether text is displayed upright in the text box.
        
        Args:
            value (int): A value indicating the upright text setting to apply.
        """
        GetDllLibXls().XlsTextBoxShape_set_UpRight.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsTextBoxShape_set_UpRight, self.Ptr, value)

    @property

    def HyLink(self)->'IHyperLink':
        """Gets the hyperlink associated with the text box.
        
        Returns:
            IHyperLink: An object representing the hyperlink associated with the text box.
        """
        GetDllLibXls().XlsTextBoxShape_get_HyLink.argtypes=[c_void_p]
        GetDllLibXls().XlsTextBoxShape_get_HyLink.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsTextBoxShape_get_HyLink, self.Ptr)
        ret = None if intPtr==None else HyperLink(intPtr)
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
#        GetDllLibXls().XlsTextBoxShape_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsTextBoxShape_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsTextBoxShape_Clone, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollections)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


