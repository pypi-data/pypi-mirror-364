from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from spire.xls.Format3D import *
from ctypes import *
import abc

class XlsShape (  XlsObject, IShape, ICloneParent, INamedObject) :
    """Represents a shape in an Excel worksheet.
    
    This class provides properties and methods for manipulating shapes in Excel worksheets,
    including positioning, sizing, appearance, and other shape-specific functionality.
    It serves as a base class for various shape types and implements multiple interfaces
    for shape manipulation.
    """
    #@dispatch

    #def SaveToImage(self ,fileName:str,imageFormat:ImageFormat):
    #    """
    #<summary>
    #    Save shape to image.
    #</summary>
    #<param name="fileName">Output file name.</param>
    #<param name="imageFormat">Type of the image to create.</param>
    #    """
    #    intPtrimageFormat:c_int = imageFormat.value

    #    GetDllLibXls().XlsShape_SaveToImage.argtypes=[c_void_p ,c_void_p,c_void_p]
    #    CallCFunction(GetDllLibXls().XlsShape_SaveToImage, self.Ptr, fileName,intPtrimageFormat)

    @dispatch

    def SaveToImage(self ,fileStream:Stream):
        """
        Save shape to image.

        Args:
            fileStream: Output stream. It is ignored if null.

        """
        intPtrfileStream:c_void_p = fileStream.Ptr

        GetDllLibXls().XlsShape_SaveToImageF.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsShape_SaveToImageF, self.Ptr, intPtrfileStream)

    @dispatch

    def SaveToImage(self ,fileName:str):
        """Save the shape to an image file.
        
        Args:
            fileName (str): Output file name where the image will be saved.
        """
        
        GetDllLibXls().XlsShape_SaveToImageF1.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsShape_SaveToImageF1, self.Ptr, fileName)


    def SetTextEffect(self ,effect:'PresetTextEffect',text:str):
        """Apply a text effect to the shape.
        
        Args:
            effect (PresetTextEffect): The preset text effect to apply.
            text (str): The text to which the effect will be applied.
        """
        enumeffect:c_int = effect.value

        GetDllLibXls().XlsShape_SetTextEffect.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsShape_SetTextEffect, self.Ptr, enumeffect,text)

    @dispatch

    def Clone(self ,parent:SpireObject)->SpireObject:
        """Creates a clone of the current shape.

        Args:
            parent (SpireObject): New parent for the shape object.

        Returns:
            SpireObject: A copy of the current shape.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsShape_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsShape_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShape_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


#    @dispatch
#
#    def Clone(self ,parent:SpireObject,hashNewNames:'Dictionary2',dicFontIndexes:'Dictionary2',addToCollections:bool)->IShape:
#        """
#    <summary>
#        Creates a clone of the current shape.
#    </summary>
#    <param name="parent">New parent for the shape object.</param>
#    <param name="hashNewNames">Hashtable with new worksheet names.</param>
#    <param name="dicFontIndexes">Dictionary with new font indexes.</param>
#    <returns>A copy of the current shape.</returns>
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrhashNewNames:c_void_p = hashNewNames.Ptr
#        intPtrdicFontIndexes:c_void_p = dicFontIndexes.Ptr
#
#        GetDllLibXls().XlsShape_ClonePHDA.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsShape_ClonePHDA.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsShape_ClonePHDA, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollections)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


    @property

    def Name(self)->str:
        """Gets or sets the name of the shape.
        
        Returns:
            str: The name of the shape.
        """
        GetDllLibXls().XlsShape_get_Name.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsShape_get_Name, self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        """Sets the name of the shape.
        
        Args:
            value (str): The name to set for the shape.
        """
        GetDllLibXls().XlsShape_set_Name.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsShape_set_Name, self.Ptr, value)


    def SetName(self ,name:str):
        """Sets the name of the shape.
        
        Args:
            name (str): The name to set for the shape.
        """
        
        GetDllLibXls().XlsShape_SetName.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsShape_SetName, self.Ptr, name)


    def ChangeLayer(self ,changeType:'ShapeLayerChangeType'):
        """Changes the layer of the shape.
        
        Args:
            changeType (ShapeLayerChangeType): The type of layer change to apply.
        """
        enumchangeType:c_int = changeType.value

        GetDllLibXls().XlsShape_ChangeLayer.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsShape_ChangeLayer, self.Ptr, enumchangeType)

    @property
    def Height(self)->int:
        """Gets or sets the height of the shape in pixels.
        
        Returns:
            int: The height of the shape.
        """
        GetDllLibXls().XlsShape_get_Height.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_Height.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_Height, self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:int):
        """Sets the height of the shape in pixels.
        
        Args:
            value (int): The height to set for the shape.
        """
        GetDllLibXls().XlsShape_set_Height.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShape_set_Height, self.Ptr, value)

    @property
    def ID(self)->int:
        """Gets the unique identifier of the shape.
        
        Returns:
            int: The unique identifier of the shape.
        """
        GetDllLibXls().XlsShape_get_ID.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_ID.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_ID, self.Ptr)
        return ret

    @property
    def ShapeId(self)->int:
        """Gets or sets the shape identifier.
        
        Returns:
            int: The shape identifier.
        """
        GetDllLibXls().XlsShape_get_ShapeId.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_ShapeId.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_ShapeId, self.Ptr)
        return ret

    @ShapeId.setter
    def ShapeId(self, value:int):
        """Sets the shape identifier.
        
        Args:
            value (int): The shape identifier to set.
        """
        GetDllLibXls().XlsShape_set_ShapeId.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShape_set_ShapeId, self.Ptr, value)

    @property
    def Left(self)->int:
        """Gets or sets the position of the left edge of the shape in pixels.
        
        Returns:
            int: The position of the left edge of the shape.
        """
        GetDllLibXls().XlsShape_get_Left.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_Left.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_Left, self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:int):
        """Sets the position of the left edge of the shape in pixels.
        
        Args:
            value (int): The position of the left edge of the shape to set.
        """
        GetDllLibXls().XlsShape_set_Left.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShape_set_Left, self.Ptr, value)

    @property
    def Top(self)->int:
        """Gets or sets the position of the top edge of the shape in pixels.
        
        Returns:
            int: The position of the top edge of the shape.
        """
        GetDllLibXls().XlsShape_get_Top.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_Top.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_Top, self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:int):
        """Sets the position of the top edge of the shape in pixels.
        
        Args:
            value (int): The position of the top edge of the shape to set.
        """
        GetDllLibXls().XlsShape_set_Top.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShape_set_Top, self.Ptr, value)

    @property
    def Width(self)->int:
        """Gets or sets the width of the shape in pixels.
        
        Returns:
            int: The width of the shape.
        """
        GetDllLibXls().XlsShape_get_Width.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_Width.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_Width, self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:int):
        """Sets the width of the shape in pixels.
        
        Args:
            value (int): The width to set for the shape.
        """
        GetDllLibXls().XlsShape_set_Width.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShape_set_Width, self.Ptr, value)

    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets or sets the type of the shape.
        
        Returns:
            ExcelShapeType: An enumeration value representing the shape type.
        """
        GetDllLibXls().XlsShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_ShapeType, self.Ptr)
        objwraped = ExcelShapeType(ret)
        return objwraped

    @ShapeType.setter
    def ShapeType(self, value:'ExcelShapeType'):
        """Sets the type of the shape.
        
        Args:
            value (ExcelShapeType): An enumeration value representing the shape type to set.
        """
        GetDllLibXls().XlsShape_set_ShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShape_set_ShapeType, self.Ptr, value.value)

    @property
    def VmlShape(self)->bool:
        """Gets or sets whether the shape is a VML shape.
        
        VML (Vector Markup Language) shapes are an older format used in Excel.
        
        Returns:
            bool: True if the shape is a VML shape; otherwise, False.
        """
        GetDllLibXls().XlsShape_get_VmlShape.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_VmlShape.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShape_get_VmlShape, self.Ptr)
        return ret

    @VmlShape.setter
    def VmlShape(self, value:bool):
        """Sets whether the shape is a VML shape.
        
        Args:
            value (bool): True to set as a VML shape; False otherwise.
        """
        GetDllLibXls().XlsShape_set_VmlShape.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShape_set_VmlShape, self.Ptr, value)

    @property
    def IsRelativeResize(self)->bool:
        """Gets or sets whether the shape is resized relative to the original size.
        
        When True, the shape will maintain its proportions when resized.
        
        Returns:
            bool: True if the shape is resized relative to the original size; otherwise, False.
        """
        GetDllLibXls().XlsShape_get_IsRelativeResize.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_IsRelativeResize.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShape_get_IsRelativeResize, self.Ptr)
        return ret

    @IsRelativeResize.setter
    def IsRelativeResize(self, value:bool):
        """Sets whether the shape is resized relative to the original size.
        
        Args:
            value (bool): True to enable relative resizing; False otherwise.
        """
        GetDllLibXls().XlsShape_set_IsRelativeResize.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShape_set_IsRelativeResize, self.Ptr, value)

    @property
    def IsRelative(self)->bool:
        """Gets or sets whether the shape has relative positioning.
        
        When True, the shape position is calculated relative to the worksheet cells.
        
        Returns:
            bool: True if the shape has relative positioning; otherwise, False.
        """
        GetDllLibXls().XlsShape_get_IsRelative.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_IsRelative.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShape_get_IsRelative, self.Ptr)
        return ret

    @IsRelative.setter
    def IsRelative(self, value:bool):
        """Sets whether the shape has relative positioning.
        
        Args:
            value (bool): True to enable relative positioning; False otherwise.
        """
        GetDllLibXls().XlsShape_set_IsRelative.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShape_set_IsRelative, self.Ptr, value)

    @property
    def Instance(self)->int:
        """Gets the instance number of the shape.
        
        This is a unique identifier for the shape instance.
        
        Returns:
            int: The instance number of the shape.
        """
        GetDllLibXls().XlsShape_get_Instance.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_Instance.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_Instance, self.Ptr)
        return ret

    @property
    def IsShortVersion(self)->bool:
        """Gets or sets whether the shape is using the short version format.
        
        Returns:
            bool: True if the shape is using the short version format; otherwise, False.
        """
        GetDllLibXls().XlsShape_get_IsShortVersion.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_IsShortVersion.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShape_get_IsShortVersion, self.Ptr)
        return ret

    @IsShortVersion.setter
    def IsShortVersion(self, value:bool):
        """Sets whether the shape is using the short version format.
        
        Args:
            value (bool): True to use the short version format; False otherwise.
        """
        GetDllLibXls().XlsShape_set_IsShortVersion.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShape_set_IsShortVersion, self.Ptr, value)

    @property
    def ShapeCount(self)->int:
        """Gets the number of shapes in a group shape.
        
        If this shape is a group shape, this property returns the number of shapes it contains.
        
        Returns:
            int: The number of shapes in a group shape.
        """
        GetDllLibXls().XlsShape_get_ShapeCount.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_ShapeCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_ShapeCount, self.Ptr)
        return ret

    @property
    def Visible(self)->bool:
        """Gets or sets whether the shape is visible.
        
        Returns:
            bool: True if the shape is visible; otherwise, False.
        """
        GetDllLibXls().XlsShape_get_Visible.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_Visible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShape_get_Visible, self.Ptr)
        return ret

    @Visible.setter
    def Visible(self, value:bool):
        """Sets whether the shape is visible.
        
        Args:
            value (bool): True to make the shape visible; False to hide it.
        """
        GetDllLibXls().XlsShape_set_Visible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShape_set_Visible, self.Ptr, value)

    @property

    def HtmlString(self)->str:
        """Gets or sets the HTML string representation of the shape.
        
        This property allows accessing or modifying the shape's content as HTML.
        
        Returns:
            str: The HTML string representation of the shape.
        """
        GetDllLibXls().XlsShape_get_HtmlString.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_HtmlString.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsShape_get_HtmlString, self.Ptr))
        return ret


    @HtmlString.setter
    def HtmlString(self, value:str):
        """Sets the HTML string representation of the shape.
        
        Args:
            value (str): The HTML string representation to set for the shape.
        """
        GetDllLibXls().XlsShape_set_HtmlString.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsShape_set_HtmlString, self.Ptr, value)

    @property

    def AlternativeText(self)->str:
        """Gets or sets the alternative text for the shape.
        
        Alternative text is used for accessibility purposes and appears when the shape cannot be displayed.
        
        Returns:
            str: The alternative text for the shape.
        """
        GetDllLibXls().XlsShape_get_AlternativeText.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_AlternativeText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsShape_get_AlternativeText, self.Ptr))
        return ret


    @AlternativeText.setter
    def AlternativeText(self, value:str):
        """Sets the alternative text for the shape.
        
        Args:
            value (str): The alternative text to set for the shape.
        """
        GetDllLibXls().XlsShape_set_AlternativeText.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsShape_set_AlternativeText, self.Ptr, value)

    @property

    def Fill(self)->'IShapeFill':
        """Gets the fill formatting for the shape.
        
        This property provides access to the fill formatting options such as color, 
        gradient, texture, or pattern for the shape.
        
        Returns:
            IShapeFill: An object representing the fill formatting for the shape.
        """
        GetDllLibXls().XlsShape_get_Fill.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShape_get_Fill, self.Ptr)
        ret = None if intPtr==None else XlsShapeFill(intPtr)
        return ret


    @property
    def UpdatePositions(self)->bool:
        """Gets or sets whether the shape positions should be updated.
        
        When True, the shape's position will be updated when changes occur in the worksheet.
        
        Returns:
            bool: True if shape positions should be updated; otherwise, False.
        """
        GetDllLibXls().XlsShape_get_UpdatePositions.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_UpdatePositions.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShape_get_UpdatePositions, self.Ptr)
        return ret

    @UpdatePositions.setter
    def UpdatePositions(self, value:bool):
        """Sets whether the shape positions should be updated.
        
        Args:
            value (bool): True to enable position updates; False otherwise.
        """
        GetDllLibXls().XlsShape_set_UpdatePositions.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShape_set_UpdatePositions, self.Ptr, value)

    @property
    def HasFill(self)->bool:
        """Gets or sets whether the shape has fill formatting.
        
        Returns:
            bool: True if the shape has fill formatting; otherwise, False.
        """
        GetDllLibXls().XlsShape_get_HasFill.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_HasFill.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShape_get_HasFill, self.Ptr)
        return ret

    @HasFill.setter
    def HasFill(self, value:bool):
        """Sets whether the shape has fill formatting.
        
        Args:
            value (bool): True to enable fill formatting; False to disable it.
        """
        GetDllLibXls().XlsShape_set_HasFill.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShape_set_HasFill, self.Ptr, value)

    @property
    def HasLineFormat(self)->bool:
        """Gets or sets whether the shape has line formatting.
        
        Returns:
            bool: True if the shape has line formatting; otherwise, False.
        """
        GetDllLibXls().XlsShape_get_HasLineFormat.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_HasLineFormat.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShape_get_HasLineFormat, self.Ptr)
        return ret

    @HasLineFormat.setter
    def HasLineFormat(self, value:bool):
        """Sets whether the shape has line formatting.
        
        Args:
            value (bool): True to enable line formatting; False to disable it.
        """
        GetDllLibXls().XlsShape_set_HasLineFormat.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShape_set_HasLineFormat, self.Ptr, value)

    @property
    def IsFlipH(self)->bool:
        """Gets or sets whether the shape is flipped horizontally.
        
        Returns:
            bool: True if the shape is flipped horizontally; otherwise, False.
        """
        GetDllLibXls().XlsShape_get_IsFlipH.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_IsFlipH.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShape_get_IsFlipH, self.Ptr)
        return ret

    @IsFlipH.setter
    def IsFlipH(self, value:bool):
        """Sets whether the shape is flipped horizontally.
        
        Args:
            value (bool): True to flip the shape horizontally; False otherwise.
        """
        GetDllLibXls().XlsShape_set_IsFlipH.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShape_set_IsFlipH, self.Ptr, value)

    @property
    def IsFlipV(self)->bool:
        """Gets or sets whether the shape is flipped vertically.
        
        Returns:
            bool: True if the shape is flipped vertically; otherwise, False.
        """
        GetDllLibXls().XlsShape_get_IsFlipV.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_IsFlipV.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShape_get_IsFlipV, self.Ptr)
        return ret

    @IsFlipV.setter
    def IsFlipV(self, value:bool):
        """Sets whether the shape is flipped vertically.
        
        Args:
            value (bool): True to flip the shape vertically; False otherwise.
        """
        GetDllLibXls().XlsShape_set_IsFlipV.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShape_set_IsFlipV, self.Ptr, value)

    @property
    def IsGroup(self)->bool:
        """Gets whether the shape is a group shape.
        
        A group shape contains multiple individual shapes grouped together.
        
        Returns:
            bool: True if the shape is a group shape; otherwise, False.
        """
        GetDllLibXls().XlsShape_get_IsGroup.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_IsGroup.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShape_get_IsGroup, self.Ptr)
        return ret

    @property
    def IsInGroup(self)->bool:
        """Gets whether the shape is a child shape within a group shape.
        
        Returns:
            bool: True if the shape is a child shape within a group shape; otherwise, False.
        """
        GetDllLibXls().XlsShape_get_IsInGroup.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_IsInGroup.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShape_get_IsInGroup, self.Ptr)
        return ret

    @property

    def AlternativeTextTitle(self)->str:
        """Gets or sets the descriptive (alternative) text title for the shape.
        
        This title is used when the shape is saved to a Web page for accessibility purposes.
        
        Returns:
            str: The alternative text title for the shape.
        """
        GetDllLibXls().XlsShape_get_AlternativeTextTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_AlternativeTextTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsShape_get_AlternativeTextTitle, self.Ptr))
        return ret


    @AlternativeTextTitle.setter
    def AlternativeTextTitle(self, value:str):
        GetDllLibXls().XlsShape_set_AlternativeTextTitle.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsShape_set_AlternativeTextTitle, self.Ptr, value)

    @property

    def OnAction(self)->str:
        """Gets or sets the name of the macro or action associated with the shape.
        
        This macro or action is executed when the shape is clicked.
        
        Returns:
            str: The name of the macro or action associated with the shape.
        """
        GetDllLibXls().XlsShape_get_OnAction.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_OnAction.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsShape_get_OnAction, self.Ptr))
        return ret


    @OnAction.setter
    def OnAction(self, value:str):
        GetDllLibXls().XlsShape_set_OnAction.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsShape_set_OnAction, self.Ptr, value)

    @property
    def IsLocked(self)->bool:
        """Gets or sets whether the shape is locked.
        
        When a shape is locked, it cannot be selected or modified when the worksheet is protected.
        
        Returns:
            bool: True if the shape is locked; otherwise, False.
        """
        GetDllLibXls().XlsShape_get_IsLocked.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_IsLocked.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShape_get_IsLocked, self.Ptr)
        return ret

    @IsLocked.setter
    def IsLocked(self, value:bool):
        GetDllLibXls().XlsShape_set_IsLocked.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShape_set_IsLocked, self.Ptr, value)

    @property
    def IsPrintable(self)->bool:
        """Gets or sets whether the shape is printed when the worksheet is printed.
        
        Returns:
            bool: True if the shape is printed with the worksheet; otherwise, False.
        """
        GetDllLibXls().XlsShape_get_IsPrintable.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_IsPrintable.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShape_get_IsPrintable, self.Ptr)
        return ret

    @IsPrintable.setter
    def IsPrintable(self, value:bool):
        GetDllLibXls().XlsShape_set_IsPrintable.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShape_set_IsPrintable, self.Ptr, value)

    @property

    def ResizeBehave(self)->'ResizeBehaveType':
        """Gets or sets how the shape behaves when rows and columns are resized or inserted.
        
        Specifies all possible settings for how the drawing object will be resized when
        the rows and columns between its start and ending anchor are resized or inserted.
        Note: For ComboBoxShape, CheckBoxShape, and RadioButtonShape, the MoveAndResize type value is invalid.
        
        Returns:
            ResizeBehaveType: An enumeration value representing the resize behavior.
        """
        GetDllLibXls().XlsShape_get_ResizeBehave.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_ResizeBehave.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_ResizeBehave, self.Ptr)
        objwraped = ResizeBehaveType(ret)
        return objwraped

    @ResizeBehave.setter
    def ResizeBehave(self, value:'ResizeBehaveType'):
        GetDllLibXls().XlsShape_set_ResizeBehave.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShape_set_ResizeBehave, self.Ptr, value.value)

    @property
    def IsLockAspectRatio(self)->bool:
        """

        """
        GetDllLibXls().XlsShape_get_IsLockAspectRatio.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_IsLockAspectRatio.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShape_get_IsLockAspectRatio, self.Ptr)
        return ret

    @IsLockAspectRatio.setter
    def IsLockAspectRatio(self, value:bool):
        GetDllLibXls().XlsShape_set_IsLockAspectRatio.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShape_set_IsLockAspectRatio, self.Ptr, value)

    @property
    def BottomRow(self)->int:
        """Gets or sets the bottom row index of the shape's position.
        
        This property specifies the row that contains the bottom edge of the shape.
        
        Returns:
            int: The bottom row index of the shape's position.
        """
        GetDllLibXls().XlsShape_get_BottomRow.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_BottomRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_BottomRow, self.Ptr)
        return ret

    @BottomRow.setter
    def BottomRow(self, value:int):
        GetDllLibXls().XlsShape_set_BottomRow.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShape_set_BottomRow, self.Ptr, value)

    @property
    def BottomRowOffset(self)->int:
        """Gets or sets the offset of the bottom edge of the shape from the bottom row.
        
        This property specifies the distance in pixels from the top edge of the bottom row
        to the bottom edge of the shape.
        
        Returns:
            int: The offset in pixels from the bottom row.
        """
        GetDllLibXls().XlsShape_get_BottomRowOffset.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_BottomRowOffset.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_BottomRowOffset, self.Ptr)
        return ret

    @BottomRowOffset.setter
    def BottomRowOffset(self, value:int):
        GetDllLibXls().XlsShape_set_BottomRowOffset.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShape_set_BottomRowOffset, self.Ptr, value)

    @property
    def LeftColumn(self)->int:
        """Gets or sets the left column index of the shape's position.
        
        This property specifies the column that contains the left edge of the shape.
        
        Returns:
            int: The left column index of the shape's position.
        """
        GetDllLibXls().XlsShape_get_LeftColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_LeftColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_LeftColumn, self.Ptr)
        return ret

    @LeftColumn.setter
    def LeftColumn(self, value:int):
        GetDllLibXls().XlsShape_set_LeftColumn.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShape_set_LeftColumn, self.Ptr, value)

    @property
    def LeftColumnOffset(self)->int:
        """Gets or sets the offset of the left edge of the shape from the left column.
        
        This property specifies the distance in pixels from the left edge of the left column
        to the left edge of the shape. A value of 1024 represents a whole column offset.
        
        Returns:
            int: The offset in pixels from the left column.
        """
        GetDllLibXls().XlsShape_get_LeftColumnOffset.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_LeftColumnOffset.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_LeftColumnOffset, self.Ptr)
        return ret

    @LeftColumnOffset.setter
    def LeftColumnOffset(self, value:int):
        GetDllLibXls().XlsShape_set_LeftColumnOffset.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShape_set_LeftColumnOffset, self.Ptr, value)

    @property
    def RightColumn(self)->int:
        """Gets or sets the right column index of the shape's position.
        
        This property specifies the column that contains the right edge of the shape.
        
        Returns:
            int: The right column index of the shape's position.
        """
        GetDllLibXls().XlsShape_get_RightColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_RightColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_RightColumn, self.Ptr)
        return ret

    @RightColumn.setter
    def RightColumn(self, value:int):
        GetDllLibXls().XlsShape_set_RightColumn.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShape_set_RightColumn, self.Ptr, value)

    @property
    def RightColumnOffset(self)->int:
        """Gets or sets the offset of the right edge of the shape from the right column.
        
        This property specifies the distance in pixels from the left edge of the right column
        to the right edge of the shape.
        
        Returns:
            int: The offset in pixels from the right column.
        """
        GetDllLibXls().XlsShape_get_RightColumnOffset.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_RightColumnOffset.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_RightColumnOffset, self.Ptr)
        return ret

    @RightColumnOffset.setter
    def RightColumnOffset(self, value:int):
        GetDllLibXls().XlsShape_set_RightColumnOffset.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShape_set_RightColumnOffset, self.Ptr, value)

    @property
    def TopRow(self)->int:
        """Gets or sets the top row index of the shape's position.
        
        This property specifies the row that contains the top edge of the shape.
        
        Returns:
            int: The top row index of the shape's position.
        """
        GetDllLibXls().XlsShape_get_TopRow.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_TopRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_TopRow, self.Ptr)
        return ret

    @TopRow.setter
    def TopRow(self, value:int):
        GetDllLibXls().XlsShape_set_TopRow.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShape_set_TopRow, self.Ptr, value)

    @property
    def TopRowOffset(self)->int:
        """Gets or sets the offset of the top edge of the shape from the top row.
        
        This property specifies the distance in pixels from the top edge of the top row
        to the top edge of the shape. A value of 256 represents a whole row offset.
        
        Returns:
            int: The offset in pixels from the top row.
        """
        GetDllLibXls().XlsShape_get_TopRowOffset.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_TopRowOffset.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_TopRowOffset, self.Ptr)
        return ret

    @TopRowOffset.setter
    def TopRowOffset(self, value:int):
        GetDllLibXls().XlsShape_set_TopRowOffset.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShape_set_TopRowOffset, self.Ptr, value)

    @property

    def Line(self)->'IShapeLineFormat':
        """Gets the line format of the shape.
        
        Returns:
            IShapeLineFormat: An object representing the line format settings of the shape.
        """
        GetDllLibXls().XlsShape_get_Line.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShape_get_Line, self.Ptr)
        ret = None if intPtr==None else XlsShapeLineFormat(intPtr)
        return ret


    @property
    def AutoSize(self)->bool:
        """Gets or sets whether the shape automatically sizes to fit its contents.
        
        Returns:
            bool: True if the shape automatically resizes to fit its contents; False otherwise.
        """
        GetDllLibXls().XlsShape_get_AutoSize.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_AutoSize.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShape_get_AutoSize, self.Ptr)
        return ret

    @AutoSize.setter
    def AutoSize(self, value:bool):
        GetDllLibXls().XlsShape_set_AutoSize.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShape_set_AutoSize, self.Ptr, value)

    @property
    def Rotation(self)->int:
        """
        Returns or sets the rotation of the shape, in degrees.

        """
        GetDllLibXls().XlsShape_get_Rotation.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_Rotation.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_Rotation, self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:int):
        GetDllLibXls().XlsShape_set_Rotation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShape_set_Rotation, self.Ptr, value)

    @property

    def Shadow(self)->'IShadow':
        """Gets the shadow effect settings for the shape.
        
        Returns:
            IShadow: An object representing the shadow effect settings of the shape.
        """
        GetDllLibXls().XlsShape_get_Shadow.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_Shadow.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShape_get_Shadow, self.Ptr)
        ret = None if intPtr==None else ChartShadow(intPtr)
        return ret


    @property

    def Glow(self)->'IGlow':
        """Gets the glow effect settings for the shape.
        
        Returns:
            IGlow: An object representing the glow effect settings of the shape.
        """
        GetDllLibXls().XlsShape_get_Glow.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_Glow.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShape_get_Glow, self.Ptr)
        ret = None if intPtr==None else ShapeGlow(intPtr)
        return ret


    @property

    def Reflection(self)->'IReflectionEffect':
        """Gets the reflection effect settings for the shape.
        
        Returns:
            IReflectionEffect: An object representing the reflection effect settings of the shape.
        """
        GetDllLibXls().XlsShape_get_Reflection.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_Reflection.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShape_get_Reflection, self.Ptr)
        ret = None if intPtr==None else ShapeReflection(intPtr)
        return ret


    @property

    def RichText(self)->'IRichTextString':
        """Gets the rich text formatting for the text in the shape.
        
        Returns:
            IRichTextString: An object representing the rich text formatting of the shape's text.
        """
        GetDllLibXls().XlsShape_get_RichText.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_RichText.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShape_get_RichText, self.Ptr)
        ret = None if intPtr==None else RichTextObject(intPtr)
        return ret


    @property

    def ThreeD(self)->'IFormat3D':
        """Gets the 3D format settings for the shape.
        
        Returns:
            IFormat3D: An object representing the 3D format settings of the shape.
        """
        GetDllLibXls().XlsShape_get_ThreeD.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_ThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShape_get_ThreeD, self.Ptr)
        ret = None if intPtr==None else Format3D(intPtr)
        return ret


    @property
    def IsSmartArt(self)->bool:
        """Gets whether the shape is a SmartArt object.
        
        Returns:
            bool: True if the shape is a SmartArt object; False otherwise.
        """
        GetDllLibXls().XlsShape_get_IsSmartArt.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_IsSmartArt.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShape_get_IsSmartArt, self.Ptr)
        return ret

    @property

    def TextFrame(self)->'ITextFrame':
        """Gets the text frame of the shape.
        
        Returns:
            ITextFrame: An object representing the text frame settings of the shape.
        """
        GetDllLibXls().XlsShape_get_TextFrame.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_TextFrame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShape_get_TextFrame, self.Ptr)
        ret = None if intPtr==None else ITextFrame(intPtr)
        return ret


    @property

    def TextVerticalAlignment(self)->'ExcelVerticalAlignment':
        """Gets or sets the vertical alignment of text in the shape.
        
        Returns:
            ExcelVerticalAlignment: An enumeration value representing the vertical alignment of text.
        """
        GetDllLibXls().XlsShape_get_TextVerticalAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_TextVerticalAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShape_get_TextVerticalAlignment, self.Ptr)
        objwraped = ExcelVerticalAlignment(ret)
        return objwraped

    @TextVerticalAlignment.setter
    def TextVerticalAlignment(self, value:'ExcelVerticalAlignment'):
        GetDllLibXls().XlsShape_set_TextVerticalAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShape_set_TextVerticalAlignment, self.Ptr, value.value)

    @property

    def LinkedCell(self)->'IXLSRange':
        """Gets or sets the cell linked to the shape.
        
        Returns:
            IXLSRange: A range object representing the cell linked to the shape.
        """
        GetDllLibXls().XlsShape_get_LinkedCell.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_get_LinkedCell.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShape_get_LinkedCell, self.Ptr)
        from spire.xls.XlsRange import XlsRange
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @LinkedCell.setter
    def LinkedCell(self, value:'IXLSRange'):
        GetDllLibXls().XlsShape_set_LinkedCell.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsShape_set_LinkedCell, self.Ptr, value.Ptr)

    @dispatch
    def Remove(self):
        """Removes the shape from the worksheet.
        
        This method deletes the shape from the worksheet and releases any resources associated with it.
        """
        GetDllLibXls().XlsShape_Remove.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsShape_Remove, self.Ptr)


    def Scale(self ,scaleWidth:int,scaleHeight:int):
        """Scales the shape by the specified percentages.
        
        This method resizes the shape according to the specified width and height scaling factors.
        
        Args:
            scaleWidth (int): Width scaling factor as a percentage of the original width.
            scaleHeight (int): Height scaling factor as a percentage of the original height.
        """
        
        GetDllLibXls().XlsShape_Scale.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsShape_Scale, self.Ptr, scaleWidth,scaleHeight)

    @dispatch

    def SaveToImage(self)->Stream:
        """Saves the shape as an image and returns the image data as a stream.
        
        Returns:
            Stream: A stream containing the image data of the shape.
        """
        GetDllLibXls().XlsShape_SaveToImage1.argtypes=[c_void_p]
        GetDllLibXls().XlsShape_SaveToImage1.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShape_SaveToImage1, self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    #@dispatch

    #def SaveToImage(self ,fileStream:Stream,imageFormat:ImageFormat):
    #    """
    #<summary>
    #    Save shape to image.
    #</summary>
    #<param name="fileStream">Output stream. It is ignored if null.</param>
    #<param name="imageFormat">Type of the image to create.</param>
    #    """
    #    intPtrfileStream:c_void_p = fileStream.Ptr
    #    intPtrimageFormat:c_int = imageFormat.value

    #    GetDllLibXls().XlsShape_SaveToImageFI.argtypes=[c_void_p ,c_void_p,c_void_p]
    #    CallCFunction(GetDllLibXls().XlsShape_SaveToImageFI, self.Ptr, intPtrfileStream,intPtrimageFormat)

from spire.xls.XlsShapeLineFormat import XlsShapeLineFormat
