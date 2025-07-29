from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsRadioButtonShape (  XlsShape, IRadioButton) :
    """Represents a radio button control in an Excel worksheet.
    
    This class provides properties and methods for manipulating radio button controls,
    including text, state, and alignment.
    """
    @property

    def Text(self)->str:
        """Gets or sets the text displayed next to the radio button.
        
        Returns:
            str: The text label of the radio button.
        """
        GetDllLibXls().XlsRadioButtonShape_get_Text.argtypes=[c_void_p]
        GetDllLibXls().XlsRadioButtonShape_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsRadioButtonShape_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        """Sets the text displayed next to the radio button.
        
        Args:
            value (str): The text label to display next to the radio button.
        """
        GetDllLibXls().XlsRadioButtonShape_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsRadioButtonShape_set_Text, self.Ptr, value)

    @property
    def IsTextLocked(self)->bool:
        """Gets or sets whether the text in the radio button is locked.
        
        Returns:
            bool: True if the text is locked; otherwise, False.
        """
        GetDllLibXls().XlsRadioButtonShape_get_IsTextLocked.argtypes=[c_void_p]
        GetDllLibXls().XlsRadioButtonShape_get_IsTextLocked.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRadioButtonShape_get_IsTextLocked, self.Ptr)
        return ret

    @IsTextLocked.setter
    def IsTextLocked(self, value:bool):
        """Sets whether the text in the radio button is locked.
        
        Args:
            value (bool): True to lock the text; False to unlock it.
        """
        GetDllLibXls().XlsRadioButtonShape_set_IsTextLocked.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsRadioButtonShape_set_IsTextLocked, self.Ptr, value)

    @property

    def LinkedCell(self)->'IXLSRange':
        """Gets or sets the cell linked to the radio button state.
        
        The linked cell will contain the value of the radio button's state.
        
        Returns:
            IXLSRange: A cell range object representing the linked cell.
        """
        GetDllLibXls().XlsRadioButtonShape_get_LinkedCell.argtypes=[c_void_p]
        GetDllLibXls().XlsRadioButtonShape_get_LinkedCell.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsRadioButtonShape_get_LinkedCell, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @LinkedCell.setter
    def LinkedCell(self, value:'IXLSRange'):
        """Sets the cell linked to the radio button state.
        
        Args:
            value (IXLSRange): A cell range object representing the cell to link to the radio button.
        """
        GetDllLibXls().XlsRadioButtonShape_set_LinkedCell.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsRadioButtonShape_set_LinkedCell, self.Ptr, value.Ptr)

    @property
    def Display3DShading(self)->bool:
        """Gets or sets whether the radio button displays with 3D shading.
        
        Returns:
            bool: True if the radio button has 3D shading; otherwise, False.
        """
        GetDllLibXls().XlsRadioButtonShape_get_Display3DShading.argtypes=[c_void_p]
        GetDllLibXls().XlsRadioButtonShape_get_Display3DShading.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRadioButtonShape_get_Display3DShading, self.Ptr)
        return ret

    @Display3DShading.setter
    def Display3DShading(self, value:bool):
        """Sets whether the radio button displays with 3D shading.
        
        Args:
            value (bool): True to display with 3D shading; False for flat appearance.
        """
        GetDllLibXls().XlsRadioButtonShape_set_Display3DShading.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsRadioButtonShape_set_Display3DShading, self.Ptr, value)

    @property
    def IsFirstButton(self)->bool:
        """Gets whether this radio button is the first in its group.
        
        Radio buttons in the same group are mutually exclusive. The first button
        in a group defines the start of a new group.
        
        Returns:
            bool: True if this is the first button in its group; otherwise, False.
        """
        GetDllLibXls().XlsRadioButtonShape_get_IsFirstButton.argtypes=[c_void_p]
        GetDllLibXls().XlsRadioButtonShape_get_IsFirstButton.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsRadioButtonShape_get_IsFirstButton, self.Ptr)
        return ret

    @property

    def CheckState(self)->'CheckState':
        """Gets or sets the check state of the radio button.
        
        Returns:
            CheckState: An enumeration value representing the check state.
        """
        GetDllLibXls().XlsRadioButtonShape_get_CheckState.argtypes=[c_void_p]
        GetDllLibXls().XlsRadioButtonShape_get_CheckState.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRadioButtonShape_get_CheckState, self.Ptr)
        objwraped = CheckState(ret)
        return objwraped

    @CheckState.setter
    def CheckState(self, value:'CheckState'):
        """Sets the check state of the radio button.
        
        Args:
            value (CheckState): An enumeration value representing the check state.
        """
        GetDllLibXls().XlsRadioButtonShape_set_CheckState.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsRadioButtonShape_set_CheckState, self.Ptr, value.value)

    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets the shape type of the radio button.
        
        Returns:
            ExcelShapeType: An enumeration value representing the shape type.
        """
        GetDllLibXls().XlsRadioButtonShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsRadioButtonShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRadioButtonShape_get_ShapeType, self.Ptr)
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
#        GetDllLibXls().XlsRadioButtonShape_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsRadioButtonShape_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsRadioButtonShape_Clone, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollections)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


    @property

    def HAlignment(self)->'CommentHAlignType':
        """Gets or sets the horizontal alignment of text in the radio button.
        
        Returns:
            CommentHAlignType: An enumeration value representing the horizontal alignment.
        """
        GetDllLibXls().XlsRadioButtonShape_get_HAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsRadioButtonShape_get_HAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRadioButtonShape_get_HAlignment, self.Ptr)
        objwraped = CommentHAlignType(ret)
        return objwraped

    @HAlignment.setter
    def HAlignment(self, value:'CommentHAlignType'):
        """Sets the horizontal alignment of text in the radio button.
        
        Args:
            value (CommentHAlignType): An enumeration value representing the horizontal alignment.
        """
        GetDllLibXls().XlsRadioButtonShape_set_HAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsRadioButtonShape_set_HAlignment, self.Ptr, value.value)

    @property

    def VAlignment(self)->'CommentVAlignType':
        """Gets or sets the vertical alignment of text in the radio button.
        
        Returns:
            CommentVAlignType: An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().XlsRadioButtonShape_get_VAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsRadioButtonShape_get_VAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRadioButtonShape_get_VAlignment, self.Ptr)
        objwraped = CommentVAlignType(ret)
        return objwraped

    @VAlignment.setter
    def VAlignment(self, value:'CommentVAlignType'):
        """Sets the vertical alignment of text in the radio button.
        
        Args:
            value (CommentVAlignType): An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().XlsRadioButtonShape_set_VAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsRadioButtonShape_set_VAlignment, self.Ptr, value.value)

    @property

    def TextRotation(self)->'TextRotationType':
        """Gets or sets the text rotation in the radio button.
        
        Returns:
            TextRotationType: An enumeration value representing the text rotation.
        """
        GetDllLibXls().XlsRadioButtonShape_get_TextRotation.argtypes=[c_void_p]
        GetDllLibXls().XlsRadioButtonShape_get_TextRotation.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsRadioButtonShape_get_TextRotation, self.Ptr)
        objwraped = TextRotationType(ret)
        return objwraped

    @TextRotation.setter
    def TextRotation(self, value:'TextRotationType'):
        """Sets the text rotation in the radio button.
        
        Args:
            value (TextRotationType): An enumeration value representing the text rotation.
        """
        GetDllLibXls().XlsRadioButtonShape_set_TextRotation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsRadioButtonShape_set_TextRotation, self.Ptr, value.value)

    def SetRichText(self, value:RichTextString):
        """Sets rich text formatting for the radio button text.
        
        Args:
            value (RichTextString): A rich text string object containing the formatted text.
        """
        GetDllLibXls().XlsRadioButtonShape_set_RichText.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsRadioButtonShape_set_RichText, self.Ptr, value.Ptr)

