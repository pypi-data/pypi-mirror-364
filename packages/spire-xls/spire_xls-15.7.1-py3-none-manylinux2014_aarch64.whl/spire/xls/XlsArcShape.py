from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsArcShape (  XlsPrstGeomShape, IArcShape) :
    """Represents an arc shape in an Excel worksheet.
    
    This class provides properties and methods for manipulating arc shapes in Excel,
    including appearance settings such as line style, color, arrow styles, and text
    formatting. It extends XlsPrstGeomShape and implements the IArcShape interface.
    """
    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets the type of the shape.
        
        Returns:
            ExcelShapeType: An enumeration value representing the type of the shape.
        """
        GetDllLibXls().XlsArcShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsArcShape_get_ShapeType, self.Ptr)
        objwraped = ExcelShapeType(ret)
        return objwraped

    @property

    def Text(self)->str:
        """Gets the text content of the arc shape.
        
        Returns:
            str: The text content of the arc shape.
        """
        GetDllLibXls().XlsArcShape_get_Text.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsArcShape_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        """Sets the text content of the arc shape.
        
        Args:
            value (str): The text content to set for the arc shape.
        """
        GetDllLibXls().XlsArcShape_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsArcShape_set_Text, self.Ptr, value)

    @property
    def IsTextLocked(self)->bool:
        """Gets a value indicating whether the text in the arc shape is locked.
        
        Returns:
            bool: True if the text is locked; otherwise, False.
        """
        GetDllLibXls().XlsArcShape_get_IsTextLocked.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_IsTextLocked.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsArcShape_get_IsTextLocked, self.Ptr)
        return ret

    @IsTextLocked.setter
    def IsTextLocked(self, value:bool):
        """Sets a value indicating whether the text in the arc shape is locked.
        
        Args:
            value (bool): True to lock the text; otherwise, False.
        """
        GetDllLibXls().XlsArcShape_set_IsTextLocked.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsArcShape_set_IsTextLocked, self.Ptr, value)

    @property

    def TextRotation(self)->'TextRotationType':
        """Gets the rotation type of the text in the arc shape.
        
        Returns:
            TextRotationType: An enumeration value representing the text rotation type.
        """
        GetDllLibXls().XlsArcShape_get_TextRotation.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_TextRotation.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsArcShape_get_TextRotation, self.Ptr)
        objwraped = TextRotationType(ret)
        return objwraped

    @TextRotation.setter
    def TextRotation(self, value:'TextRotationType'):
        """Sets the rotation type of the text in the arc shape.
        
        Args:
            value (TextRotationType): An enumeration value representing the text rotation type.
        """
        GetDllLibXls().XlsArcShape_set_TextRotation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsArcShape_set_TextRotation, self.Ptr, value.value)

    @property

    def RichText(self)->'IRichTextString':
        """Gets the rich text formatting of the text in the arc shape.
        
        Returns:
            IRichTextString: An object representing the rich text formatting.
        """
        GetDllLibXls().XlsArcShape_get_RichText.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_RichText.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsArcShape_get_RichText, self.Ptr)
        ret = None if intPtr==None else RichTextObject(intPtr)
        return ret


    @property

    def HAlignment(self)->'CommentHAlignType':
        """Gets the horizontal alignment of the text in the arc shape.
        
        Returns:
            CommentHAlignType: An enumeration value representing the horizontal alignment.
        """
        GetDllLibXls().XlsArcShape_get_HAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_HAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsArcShape_get_HAlignment, self.Ptr)
        objwraped = CommentHAlignType(ret)
        return objwraped

    @HAlignment.setter
    def HAlignment(self, value:'CommentHAlignType'):
        """Sets the horizontal alignment of the text in the arc shape.
        
        Args:
            value (CommentHAlignType): An enumeration value representing the horizontal alignment.
        """
        GetDllLibXls().XlsArcShape_set_HAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsArcShape_set_HAlignment, self.Ptr, value.value)

    @property

    def VAlignment(self)->'CommentVAlignType':
        """Gets the vertical alignment of the text in the arc shape.
        
        Returns:
            CommentVAlignType: An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().XlsArcShape_get_VAlignment.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_VAlignment.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsArcShape_get_VAlignment, self.Ptr)
        objwraped = CommentVAlignType(ret)
        return objwraped

    @VAlignment.setter
    def VAlignment(self, value:'CommentVAlignType'):
        """Sets the vertical alignment of the text in the arc shape.
        
        Args:
            value (CommentVAlignType): An enumeration value representing the vertical alignment.
        """
        GetDllLibXls().XlsArcShape_set_VAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsArcShape_set_VAlignment, self.Ptr, value.value)

    @property
    def Weight(self)->float:
        """Gets the weight (thickness) of the arc line in points.
        
        Returns:
            float: The weight of the arc line in points.
        """
        GetDllLibXls().XlsArcShape_get_Weight.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_Weight.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsArcShape_get_Weight, self.Ptr)
        return ret

    @Weight.setter
    def Weight(self, value:float):
        """Sets the weight (thickness) of the arc line in points.
        
        Args:
            value (float): The weight of the arc line in points.
        """
        GetDllLibXls().XlsArcShape_set_Weight.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsArcShape_set_Weight, self.Ptr, value)

    @property

    def Color(self)->'Color':
        """Gets the color of the arc line.
        
        Returns:
            Color: A Color object representing the color of the arc line.
        """
        GetDllLibXls().XlsArcShape_get_Color.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsArcShape_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        """Sets the color of the arc line.
        
        Args:
            value (Color): A Color object representing the color of the arc line.
        """
        GetDllLibXls().XlsArcShape_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsArcShape_set_Color, self.Ptr, value.Ptr)

    @property

    def Style(self)->'ShapeLineStyleType':
        """Gets the line style of the arc.
        
        Returns:
            ShapeLineStyleType: An enumeration value representing the line style.
        """
        GetDllLibXls().XlsArcShape_get_Style.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_Style.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsArcShape_get_Style, self.Ptr)
        objwraped = ShapeLineStyleType(ret)
        return objwraped

    @Style.setter
    def Style(self, value:'ShapeLineStyleType'):
        """Sets the line style of the arc.
        
        Args:
            value (ShapeLineStyleType): An enumeration value representing the line style.
        """
        GetDllLibXls().XlsArcShape_set_Style.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsArcShape_set_Style, self.Ptr, value.value)

    @property

    def DashStyle(self)->'ShapeDashLineStyleType':
        """Gets the dash style of the arc line.
        
        Returns:
            ShapeDashLineStyleType: An enumeration value representing the dash style.
        """
        GetDllLibXls().XlsArcShape_get_DashStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_DashStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsArcShape_get_DashStyle, self.Ptr)
        objwraped = ShapeDashLineStyleType(ret)
        return objwraped

    @DashStyle.setter
    def DashStyle(self, value:'ShapeDashLineStyleType'):
        """Sets the dash style of the arc line.
        
        Args:
            value (ShapeDashLineStyleType): An enumeration value representing the dash style.
        """
        GetDllLibXls().XlsArcShape_set_DashStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsArcShape_set_DashStyle, self.Ptr, value.value)

    @property

    def BeginArrowheadWidth(self)->'ShapeArrowWidthType':
        """Gets the width of the arrowhead at the beginning of the arc.
        
        Returns:
            ShapeArrowWidthType: An enumeration value representing the arrowhead width.
        """
        GetDllLibXls().XlsArcShape_get_BeginArrowheadWidth.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_BeginArrowheadWidth.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsArcShape_get_BeginArrowheadWidth, self.Ptr)
        objwraped = ShapeArrowWidthType(ret)
        return objwraped

    @BeginArrowheadWidth.setter
    def BeginArrowheadWidth(self, value:'ShapeArrowWidthType'):
        """Sets the width of the arrowhead at the beginning of the arc.
        
        Args:
            value (ShapeArrowWidthType): An enumeration value representing the arrowhead width.
        """
        GetDllLibXls().XlsArcShape_set_BeginArrowheadWidth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsArcShape_set_BeginArrowheadWidth, self.Ptr, value.value)

    @property

    def BeginArrowHeadStyle(self)->'ShapeArrowStyleType':
        """Gets the style of the arrowhead at the beginning of the arc.
        
        Returns:
            ShapeArrowStyleType: An enumeration value representing the arrowhead style.
        """
        GetDllLibXls().XlsArcShape_get_BeginArrowHeadStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_BeginArrowHeadStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsArcShape_get_BeginArrowHeadStyle, self.Ptr)
        objwraped = ShapeArrowStyleType(ret)
        return objwraped

    @BeginArrowHeadStyle.setter
    def BeginArrowHeadStyle(self, value:'ShapeArrowStyleType'):
        """Sets the style of the arrowhead at the beginning of the arc.
        
        Args:
            value (ShapeArrowStyleType): An enumeration value representing the arrowhead style.
        """
        GetDllLibXls().XlsArcShape_set_BeginArrowHeadStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsArcShape_set_BeginArrowHeadStyle, self.Ptr, value.value)

    @property

    def BeginArrowheadLength(self)->'ShapeArrowLengthType':
        """Gets the length of the arrowhead at the beginning of the arc.
        
        Returns:
            ShapeArrowLengthType: An enumeration value representing the arrowhead length.
        """
        GetDllLibXls().XlsArcShape_get_BeginArrowheadLength.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_BeginArrowheadLength.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsArcShape_get_BeginArrowheadLength, self.Ptr)
        objwraped = ShapeArrowLengthType(ret)
        return objwraped

    @BeginArrowheadLength.setter
    def BeginArrowheadLength(self, value:'ShapeArrowLengthType'):
        """Sets the length of the arrowhead at the beginning of the arc.
        
        Args:
            value (ShapeArrowLengthType): An enumeration value representing the arrowhead length.
        """
        GetDllLibXls().XlsArcShape_set_BeginArrowheadLength.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsArcShape_set_BeginArrowheadLength, self.Ptr, value.value)

    @property

    def EndArrowHeadStyle(self)->'ShapeArrowStyleType':
        """Gets the style of the arrowhead at the end of the arc.
        
        Returns:
            ShapeArrowStyleType: An enumeration value representing the arrowhead style.
        """
        GetDllLibXls().XlsArcShape_get_EndArrowHeadStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_EndArrowHeadStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsArcShape_get_EndArrowHeadStyle, self.Ptr)
        objwraped = ShapeArrowStyleType(ret)
        return objwraped

    @EndArrowHeadStyle.setter
    def EndArrowHeadStyle(self, value:'ShapeArrowStyleType'):
        """Sets the style of the arrowhead at the end of the arc.
        
        Args:
            value (ShapeArrowStyleType): An enumeration value representing the arrowhead style.
        """
        GetDllLibXls().XlsArcShape_set_EndArrowHeadStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsArcShape_set_EndArrowHeadStyle, self.Ptr, value.value)

    @property

    def EndArrowheadLength(self)->'ShapeArrowLengthType':
        """Gets the length of the arrowhead at the end of the arc.
        
        Returns:
            ShapeArrowLengthType: An enumeration value representing the arrowhead length.
        """
        GetDllLibXls().XlsArcShape_get_EndArrowheadLength.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_EndArrowheadLength.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsArcShape_get_EndArrowheadLength, self.Ptr)
        objwraped = ShapeArrowLengthType(ret)
        return objwraped

    @EndArrowheadLength.setter
    def EndArrowheadLength(self, value:'ShapeArrowLengthType'):
        """Sets the length of the arrowhead at the end of the arc.
        
        Args:
            value (ShapeArrowLengthType): An enumeration value representing the arrowhead length.
        """
        GetDllLibXls().XlsArcShape_set_EndArrowheadLength.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsArcShape_set_EndArrowheadLength, self.Ptr, value.value)

    @property

    def EndArrowheadWidth(self)->'ShapeArrowWidthType':
        """Gets the width of the arrowhead at the end of the arc.
        
        Returns:
            ShapeArrowWidthType: An enumeration value representing the arrowhead width.
        """
        GetDllLibXls().XlsArcShape_get_EndArrowheadWidth.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_EndArrowheadWidth.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsArcShape_get_EndArrowheadWidth, self.Ptr)
        objwraped = ShapeArrowWidthType(ret)
        return objwraped

    @EndArrowheadWidth.setter
    def EndArrowheadWidth(self, value:'ShapeArrowWidthType'):
        """Sets the width of the arrowhead at the end of the arc.
        
        Args:
            value (ShapeArrowWidthType): An enumeration value representing the arrowhead width.
        """
        GetDllLibXls().XlsArcShape_set_EndArrowheadWidth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsArcShape_set_EndArrowheadWidth, self.Ptr, value.value)

    @property

    def HyLink(self)->'IHyperLink':
        """Gets the hyperlink associated with the arc shape.
        
        Returns:
            IHyperLink: An object representing the hyperlink associated with the arc shape.
        """
        GetDllLibXls().XlsArcShape_get_HyLink.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_HyLink.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsArcShape_get_HyLink, self.Ptr)
        ret = None if intPtr==None else HyperLink(intPtr)
        return ret


    @property

    def PrstShapeType(self)->'PrstGeomShapeType':
        """Gets the preset shape type of the arc shape.
        
        Returns:
            PrstGeomShapeType: An enumeration value representing the preset shape type.
        """
        GetDllLibXls().XlsArcShape_get_PrstShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsArcShape_get_PrstShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsArcShape_get_PrstShapeType, self.Ptr)
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
#        GetDllLibXls().XlsArcShape_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsArcShape_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsArcShape_Clone, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollections)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


