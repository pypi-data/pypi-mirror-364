from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsLineShape (  XlsPrstGeomShape, ILineShape) :
    """Represents a line shape in an Excel worksheet.
    
    This class provides properties and methods for manipulating line shapes in Excel,
    including appearance settings such as line style, color, weight, arrow styles, and
    positioning. It extends XlsPrstGeomShape and implements the ILineShape interface.
    """
    @property

    def LineShapeType(self)->'LineShapeType':
        """Gets or sets the type of the line shape.
        
        Returns:
            LineShapeType: An enumeration value representing the type of the line shape.
        """
        GetDllLibXls().XlsLineShape_get_LineShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_LineShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsLineShape_get_LineShapeType, self.Ptr)
        objwraped = LineShapeType(ret)
        return objwraped

    @LineShapeType.setter
    def LineShapeType(self, value:'LineShapeType'):
        """Sets the type of the line shape.
        
        Args:
            value (LineShapeType): An enumeration value representing the type of the line shape.
        """
        GetDllLibXls().XlsLineShape_set_LineShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsLineShape_set_LineShapeType, self.Ptr, value.value)

    @property
    def Weight(self)->float:
        """Gets or sets the weight (thickness) of the line in points.
        
        Returns:
            float: The weight of the line in points.
        """
        GetDllLibXls().XlsLineShape_get_Weight.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_Weight.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsLineShape_get_Weight, self.Ptr)
        return ret

    @Weight.setter
    def Weight(self, value:float):
        """Sets the weight (thickness) of the line in points.
        
        Args:
            value (float): The weight of the line in points.
        """
        GetDllLibXls().XlsLineShape_set_Weight.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsLineShape_set_Weight, self.Ptr, value)

    @property
    def MiddleOffset(self)->int:
        """Gets or sets the middle offset of the line.
        
        Returns:
            int: The middle offset of the line.
        """
        GetDllLibXls().XlsLineShape_get_MiddleOffset.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_MiddleOffset.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsLineShape_get_MiddleOffset, self.Ptr)
        return ret

    @MiddleOffset.setter
    def MiddleOffset(self, value:int):
        """Sets the middle offset of the line.
        
        Args:
            value (int): The middle offset of the line.
        """
        GetDllLibXls().XlsLineShape_set_MiddleOffset.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsLineShape_set_MiddleOffset, self.Ptr, value)

    @property
    def MiddleOffsetPercent(self)->float:
        """Gets or sets the middle offset of the line as a percentage.
        
        Returns:
            float: The middle offset percentage of the line.
        """
        GetDllLibXls().XlsLineShape_get_MiddleOffsetPercent.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_MiddleOffsetPercent.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsLineShape_get_MiddleOffsetPercent, self.Ptr)
        return ret

    @MiddleOffsetPercent.setter
    def MiddleOffsetPercent(self, value:float):
        """Sets the middle offset of the line as a percentage.
        
        Args:
            value (float): The middle offset percentage of the line.
        """
        GetDllLibXls().XlsLineShape_set_MiddleOffsetPercent.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsLineShape_set_MiddleOffsetPercent, self.Ptr, value)

    @property
    def Transparency(self)->float:
        """Gets or sets the transparency of the line.
        
        Returns:
            float: The transparency value of the line (0.0 to 1.0).
        """
        GetDllLibXls().XlsLineShape_get_Transparency.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_Transparency.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsLineShape_get_Transparency, self.Ptr)
        return ret

    @Transparency.setter
    def Transparency(self, value:float):
        """Sets the transparency of the line.
        
        Args:
            value (float): The transparency value of the line (0.0 to 1.0).
        """
        GetDllLibXls().XlsLineShape_set_Transparency.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsLineShape_set_Transparency, self.Ptr, value)

    @property

    def Color(self)->'Color':
        """Gets or sets the color of the line.
        
        Returns:
            Color: A Color object representing the color of the line.
        """
        GetDllLibXls().XlsLineShape_get_Color.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsLineShape_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        """Sets the color of the line.
        
        Args:
            value (Color): A Color object representing the color of the line.
        """
        GetDllLibXls().XlsLineShape_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsLineShape_set_Color, self.Ptr, value.Ptr)

    @property

    def Style(self)->'ShapeLineStyleType':
        """Gets or sets the style of the line.
        
        Returns:
            ShapeLineStyleType: An enumeration value representing the style of the line.
        """
        GetDllLibXls().XlsLineShape_get_Style.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_Style.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsLineShape_get_Style, self.Ptr)
        objwraped = ShapeLineStyleType(ret)
        return objwraped

    @Style.setter
    def Style(self, value:'ShapeLineStyleType'):
        """Sets the style of the line.
        
        Args:
            value (ShapeLineStyleType): An enumeration value representing the style of the line.
        """
        GetDllLibXls().XlsLineShape_set_Style.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsLineShape_set_Style, self.Ptr, value.value)

    @property

    def DashStyle(self)->'ShapeDashLineStyleType':
        """Gets or sets the dash style of the line.
        
        Returns:
            ShapeDashLineStyleType: An enumeration value representing the dash style of the line.
        """
        GetDllLibXls().XlsLineShape_get_DashStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_DashStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsLineShape_get_DashStyle, self.Ptr)
        objwraped = ShapeDashLineStyleType(ret)
        return objwraped

    @DashStyle.setter
    def DashStyle(self, value:'ShapeDashLineStyleType'):
        """Sets the dash style of the line.
        
        Args:
            value (ShapeDashLineStyleType): An enumeration value representing the dash style of the line.
        """
        GetDllLibXls().XlsLineShape_set_DashStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsLineShape_set_DashStyle, self.Ptr, value.value)

    @property

    def BeginArrowheadWidth(self)->'ShapeArrowWidthType':
        """Gets or sets the width of the arrowhead at the beginning of the line.
        
        Returns:
            ShapeArrowWidthType: An enumeration value representing the width of the beginning arrowhead.
        """
        GetDllLibXls().XlsLineShape_get_BeginArrowheadWidth.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_BeginArrowheadWidth.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsLineShape_get_BeginArrowheadWidth, self.Ptr)
        objwraped = ShapeArrowWidthType(ret)
        return objwraped

    @BeginArrowheadWidth.setter
    def BeginArrowheadWidth(self, value:'ShapeArrowWidthType'):
        """Sets the width of the arrowhead at the beginning of the line.
        
        Args:
            value (ShapeArrowWidthType): An enumeration value representing the width of the beginning arrowhead.
        """
        GetDllLibXls().XlsLineShape_set_BeginArrowheadWidth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsLineShape_set_BeginArrowheadWidth, self.Ptr, value.value)

    @property

    def BeginArrowHeadStyle(self)->'ShapeArrowStyleType':
        """Gets or sets the style of the arrowhead at the beginning of the line.
        
        Returns:
            ShapeArrowStyleType: An enumeration value representing the style of the beginning arrowhead.
        """
        GetDllLibXls().XlsLineShape_get_BeginArrowHeadStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_BeginArrowHeadStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsLineShape_get_BeginArrowHeadStyle, self.Ptr)
        objwraped = ShapeArrowStyleType(ret)
        return objwraped

    @BeginArrowHeadStyle.setter
    def BeginArrowHeadStyle(self, value:'ShapeArrowStyleType'):
        """Sets the style of the arrowhead at the beginning of the line.
        
        Args:
            value (ShapeArrowStyleType): An enumeration value representing the style of the beginning arrowhead.
        """
        GetDllLibXls().XlsLineShape_set_BeginArrowHeadStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsLineShape_set_BeginArrowHeadStyle, self.Ptr, value.value)

    @property

    def BeginArrowheadLength(self)->'ShapeArrowLengthType':
        """Gets or sets the length of the arrowhead at the beginning of the line.
        
        Returns:
            ShapeArrowLengthType: An enumeration value representing the length of the beginning arrowhead.
        """
        GetDllLibXls().XlsLineShape_get_BeginArrowheadLength.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_BeginArrowheadLength.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsLineShape_get_BeginArrowheadLength, self.Ptr)
        objwraped = ShapeArrowLengthType(ret)
        return objwraped

    @BeginArrowheadLength.setter
    def BeginArrowheadLength(self, value:'ShapeArrowLengthType'):
        """Sets the length of the arrowhead at the beginning of the line.
        
        Args:
            value (ShapeArrowLengthType): An enumeration value representing the length of the beginning arrowhead.
        """
        GetDllLibXls().XlsLineShape_set_BeginArrowheadLength.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsLineShape_set_BeginArrowheadLength, self.Ptr, value.value)

    @property

    def EndArrowHeadStyle(self)->'ShapeArrowStyleType':
        """Gets or sets the style of the arrowhead at the end of the line.
        
        Returns:
            ShapeArrowStyleType: An enumeration value representing the style of the ending arrowhead.
        """
        GetDllLibXls().XlsLineShape_get_EndArrowHeadStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_EndArrowHeadStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsLineShape_get_EndArrowHeadStyle, self.Ptr)
        objwraped = ShapeArrowStyleType(ret)
        return objwraped

    @EndArrowHeadStyle.setter
    def EndArrowHeadStyle(self, value:'ShapeArrowStyleType'):
        """Sets the style of the arrowhead at the end of the line.
        
        Args:
            value (ShapeArrowStyleType): An enumeration value representing the style of the ending arrowhead.
        """
        GetDllLibXls().XlsLineShape_set_EndArrowHeadStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsLineShape_set_EndArrowHeadStyle, self.Ptr, value.value)

    @property

    def EndArrowheadLength(self)->'ShapeArrowLengthType':
        """Gets or sets the length of the arrowhead at the end of the line.
        
        Returns:
            ShapeArrowLengthType: An enumeration value representing the length of the ending arrowhead.
        """
        GetDllLibXls().XlsLineShape_get_EndArrowheadLength.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_EndArrowheadLength.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsLineShape_get_EndArrowheadLength, self.Ptr)
        objwraped = ShapeArrowLengthType(ret)
        return objwraped

    @EndArrowheadLength.setter
    def EndArrowheadLength(self, value:'ShapeArrowLengthType'):
        """Sets the length of the arrowhead at the end of the line.
        
        Args:
            value (ShapeArrowLengthType): An enumeration value representing the length of the ending arrowhead.
        """
        GetDllLibXls().XlsLineShape_set_EndArrowheadLength.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsLineShape_set_EndArrowheadLength, self.Ptr, value.value)

    @property

    def EndArrowheadWidth(self)->'ShapeArrowWidthType':
        """Gets or sets the width of the arrowhead at the end of the line.
        
        Returns:
            ShapeArrowWidthType: An enumeration value representing the width of the ending arrowhead.
        """
        GetDllLibXls().XlsLineShape_get_EndArrowheadWidth.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_EndArrowheadWidth.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsLineShape_get_EndArrowheadWidth, self.Ptr)
        objwraped = ShapeArrowWidthType(ret)
        return objwraped

    @EndArrowheadWidth.setter
    def EndArrowheadWidth(self, value:'ShapeArrowWidthType'):
        """Sets the width of the arrowhead at the end of the line.
        
        Args:
            value (ShapeArrowWidthType): An enumeration value representing the width of the ending arrowhead.
        """
        GetDllLibXls().XlsLineShape_set_EndArrowheadWidth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsLineShape_set_EndArrowheadWidth, self.Ptr, value.value)

    @property

    def HyLink(self)->'IHyperLink':
        """Gets or sets the hyperlink for the line.
        
        Returns:
            IHyperLink: An IHyperLink object representing the hyperlink for the line.
        """
        GetDllLibXls().XlsLineShape_get_HyLink.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_HyLink.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsLineShape_get_HyLink, self.Ptr)
        ret = None if intPtr==None else HyperLink(intPtr)
        return ret


    @property

    def PrstShapeType(self)->'PrstGeomShapeType':
        """Gets or sets the shape type of the line.
        
        Returns:
            PrstGeomShapeType: An enumeration value representing the shape type of the line.
        """
        GetDllLibXls().XlsLineShape_get_PrstShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_PrstShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsLineShape_get_PrstShapeType, self.Ptr)
        objwraped = PrstGeomShapeType(ret)
        return objwraped

    @property

    def StartPoint(self)->'Point':
        """Gets or sets the start point of the line.
        
        Returns:
            Point: A Point object representing the start point of the line.
        """
        GetDllLibXls().XlsLineShape_get_StartPoint.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_StartPoint.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsLineShape_get_StartPoint, self.Ptr)
        ret = None if intPtr==None else Point(intPtr)
        return ret


    @StartPoint.setter
    def StartPoint(self, value:'Point'):
        """Sets the start point of the line.
        
        Args:
            value (Point): A Point object representing the start point of the line.
        """
        GetDllLibXls().XlsLineShape_set_StartPoint.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsLineShape_set_StartPoint, self.Ptr, value.Ptr)

    @property

    def EndPoint(self)->'Point':
        """Gets or sets the end point of the line.
        
        Returns:
            Point: A Point object representing the end point of the line.
        """
        GetDllLibXls().XlsLineShape_get_EndPoint.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_EndPoint.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsLineShape_get_EndPoint, self.Ptr)
        ret = None if intPtr==None else Point(intPtr)
        return ret


    @EndPoint.setter
    def EndPoint(self, value:'Point'):
        """Sets the end point of the line.
        
        Args:
            value (Point): A Point object representing the end point of the line.
        """
        GetDllLibXls().XlsLineShape_set_EndPoint.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsLineShape_set_EndPoint, self.Ptr, value.Ptr)

    @property
    def FlipH(self)->bool:
        """Gets or sets whether the line is flipped horizontally.
        
        Returns:
            bool: True if the line is flipped horizontally, False otherwise.
        """
        GetDllLibXls().XlsLineShape_get_FlipH.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_FlipH.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsLineShape_get_FlipH, self.Ptr)
        return ret

    @FlipH.setter
    def FlipH(self, value:bool):
        """Sets whether the line is flipped horizontally.
        
        Args:
            value (bool): True if the line is flipped horizontally, False otherwise.
        """
        GetDllLibXls().XlsLineShape_set_FlipH.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsLineShape_set_FlipH, self.Ptr, value)

    @property
    def FlipV(self)->bool:
        """Gets or sets whether the line is flipped vertically.
        
        Returns:
            bool: True if the line is flipped vertically, False otherwise.
        """
        GetDllLibXls().XlsLineShape_get_FlipV.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_FlipV.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsLineShape_get_FlipV, self.Ptr)
        return ret

    @FlipV.setter
    def FlipV(self, value:bool):
        """Sets whether the line is flipped vertically.
        
        Args:
            value (bool): True if the line is flipped vertically, False otherwise.
        """
        GetDllLibXls().XlsLineShape_set_FlipV.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsLineShape_set_FlipV, self.Ptr, value)

    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets or sets the shape type of the line.
        
        Returns:
            ExcelShapeType: An enumeration value representing the shape type of the line.
        """
        GetDllLibXls().XlsLineShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsLineShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsLineShape_get_ShapeType, self.Ptr)
        objwraped = ExcelShapeType(ret)
        return objwraped

#
#    def Clone(self ,parent:'SpireObject',hashNewNames:'Dictionary2',dicFontIndexes:'Dictionary2',addToCollections:bool)->'IShape':
#        """
#        Creates a clone of this line shape.
#
#        Args:
#            parent (SpireObject): The parent object for the cloned shape.
#            hashNewNames (Dictionary2): A dictionary of new names.
#            dicFontIndexes (Dictionary2): A dictionary of font indexes.
#            addToCollections (bool): Whether to add the cloned shape to collections.
#
#        Returns:
#            IShape: A clone of this line shape.
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrhashNewNames:c_void_p = hashNewNames.Ptr
#        intPtrdicFontIndexes:c_void_p = dicFontIndexes.Ptr
#
#        GetDllLibXls().XlsLineShape_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsLineShape_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsLineShape_Clone, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollections)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


