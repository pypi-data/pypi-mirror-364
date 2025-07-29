from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsShapeLineFormat (  XlsObject, IShapeLineFormat) :
    """Represents the line formatting for a shape in an Excel worksheet.
    
    This class provides properties and methods for manipulating line formatting options
    such as line color, weight, style, arrow settings, and other visual aspects of shape outlines.
    """
    @property
    def Weight(self)->float:
        """Gets or sets the weight (thickness) of the line in points.
        
        Returns:
            float: The weight of the line in points.
        """
        GetDllLibXls().XlsShapeLineFormat_get_Weight.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_Weight.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_Weight, self.Ptr)
        return ret

    @Weight.setter
    def Weight(self, value:float):
        """Sets the weight (thickness) of the line in points.
        
        Args:
            value (float): The weight of the line in points to set.
        """
        GetDllLibXls().XlsShapeLineFormat_set_Weight.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_Weight, self.Ptr, value)

    @property

    def ForeColor(self)->'Color':
        """Gets or sets the foreground color of the line.
        
        Returns:
            Color: A Color object representing the foreground color of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_get_ForeColor.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_ForeColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_ForeColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @ForeColor.setter
    def ForeColor(self, value:'Color'):
        """Sets the foreground color of the line.
        
        Args:
            value (Color): A Color object representing the foreground color to set.
        """
        GetDllLibXls().XlsShapeLineFormat_set_ForeColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_ForeColor, self.Ptr, value.Ptr)

    @property

    def BackColor(self)->'Color':
        """Gets or sets the background color of the line.
        
        Used for patterned lines where both foreground and background colors are needed.
        
        Returns:
            Color: A Color object representing the background color of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_get_BackColor.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_BackColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_BackColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @BackColor.setter
    def BackColor(self, value:'Color'):
        """Sets the background color of the line.
        
        Args:
            value (Color): A Color object representing the background color to set.
        """
        GetDllLibXls().XlsShapeLineFormat_set_BackColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_BackColor, self.Ptr, value.Ptr)

    @property

    def ForeKnownColor(self)->'ExcelColors':
        """Gets or sets the foreground color of the line from a predefined set of Excel colors.
        
        Returns:
            ExcelColors: An enumeration value representing the predefined Excel foreground color.
        """
        GetDllLibXls().XlsShapeLineFormat_get_ForeKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_ForeKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_ForeKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @ForeKnownColor.setter
    def ForeKnownColor(self, value:'ExcelColors'):
        """Sets the foreground color of the line from a predefined set of Excel colors.
        
        Args:
            value (ExcelColors): An enumeration value representing the predefined Excel foreground color to set.
        """
        GetDllLibXls().XlsShapeLineFormat_set_ForeKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_ForeKnownColor, self.Ptr, value.value)

    @property

    def BackKnownColor(self)->'ExcelColors':
        """Gets or sets the background color of the line from a predefined set of Excel colors.
        
        Used for patterned lines where both foreground and background colors are needed.
        
        Returns:
            ExcelColors: An enumeration value representing the predefined Excel background color.
        """
        GetDllLibXls().XlsShapeLineFormat_get_BackKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_BackKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_BackKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @BackKnownColor.setter
    def BackKnownColor(self, value:'ExcelColors'):
        """Sets the background color of the line from a predefined set of Excel colors.
        
        Args:
            value (ExcelColors): An enumeration value representing the predefined Excel background color to set.
        """
        GetDllLibXls().XlsShapeLineFormat_set_BackKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_BackKnownColor, self.Ptr, value.value)

    @property

    def BeginArrowHeadStyle(self)->'ShapeArrowStyleType':
        """Gets or sets the style of the arrowhead at the beginning of the line.
        
        Returns:
            ShapeArrowStyleType: An enumeration value representing the arrowhead style at the beginning of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_get_BeginArrowHeadStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_BeginArrowHeadStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_BeginArrowHeadStyle, self.Ptr)
        objwraped = ShapeArrowStyleType(ret)
        return objwraped

    @BeginArrowHeadStyle.setter
    def BeginArrowHeadStyle(self, value:'ShapeArrowStyleType'):
        """Sets the style of the arrowhead at the beginning of the line.
        
        Args:
            value (ShapeArrowStyleType): An enumeration value representing the arrowhead style to set at the beginning of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_set_BeginArrowHeadStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_BeginArrowHeadStyle, self.Ptr, value.value)

    @property

    def EndArrowHeadStyle(self)->'ShapeArrowStyleType':
        """Gets or sets the style of the arrowhead at the end of the line.
        
        Returns:
            ShapeArrowStyleType: An enumeration value representing the arrowhead style at the end of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_get_EndArrowHeadStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_EndArrowHeadStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_EndArrowHeadStyle, self.Ptr)
        objwraped = ShapeArrowStyleType(ret)
        return objwraped

    @EndArrowHeadStyle.setter
    def EndArrowHeadStyle(self, value:'ShapeArrowStyleType'):
        """Sets the style of the arrowhead at the end of the line.
        
        Args:
            value (ShapeArrowStyleType): An enumeration value representing the arrowhead style to set at the end of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_set_EndArrowHeadStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_EndArrowHeadStyle, self.Ptr, value.value)

    @property

    def BeginArrowheadLength(self)->'ShapeArrowLengthType':
        """Gets or sets the length of the arrowhead at the beginning of the line.
        
        Returns:
            ShapeArrowLengthType: An enumeration value representing the arrowhead length at the beginning of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_get_BeginArrowheadLength.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_BeginArrowheadLength.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_BeginArrowheadLength, self.Ptr)
        objwraped = ShapeArrowLengthType(ret)
        return objwraped

    @BeginArrowheadLength.setter
    def BeginArrowheadLength(self, value:'ShapeArrowLengthType'):
        """Sets the length of the arrowhead at the beginning of the line.
        
        Args:
            value (ShapeArrowLengthType): An enumeration value representing the arrowhead length to set at the beginning of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_set_BeginArrowheadLength.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_BeginArrowheadLength, self.Ptr, value.value)

    @property

    def EndArrowheadLength(self)->'ShapeArrowLengthType':
        """Gets or sets the length of the arrowhead at the end of the line.
        
        Returns:
            ShapeArrowLengthType: An enumeration value representing the arrowhead length at the end of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_get_EndArrowheadLength.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_EndArrowheadLength.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_EndArrowheadLength, self.Ptr)
        objwraped = ShapeArrowLengthType(ret)
        return objwraped

    @EndArrowheadLength.setter
    def EndArrowheadLength(self, value:'ShapeArrowLengthType'):
        """Sets the length of the arrowhead at the end of the line.
        
        Args:
            value (ShapeArrowLengthType): An enumeration value representing the arrowhead length to set at the end of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_set_EndArrowheadLength.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_EndArrowheadLength, self.Ptr, value.value)

    @property

    def BeginArrowheadWidth(self)->'ShapeArrowWidthType':
        """Gets or sets the width of the arrowhead at the beginning of the line.
        
        Returns:
            ShapeArrowWidthType: An enumeration value representing the arrowhead width at the beginning of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_get_BeginArrowheadWidth.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_BeginArrowheadWidth.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_BeginArrowheadWidth, self.Ptr)
        objwraped = ShapeArrowWidthType(ret)
        return objwraped

    @BeginArrowheadWidth.setter
    def BeginArrowheadWidth(self, value:'ShapeArrowWidthType'):
        """Sets the width of the arrowhead at the beginning of the line.
        
        Args:
            value (ShapeArrowWidthType): An enumeration value representing the arrowhead width to set at the beginning of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_set_BeginArrowheadWidth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_BeginArrowheadWidth, self.Ptr, value.value)

    @property

    def EndArrowheadWidth(self)->'ShapeArrowWidthType':
        """Gets or sets the width of the arrowhead at the end of the line.
        
        Returns:
            ShapeArrowWidthType: An enumeration value representing the arrowhead width at the end of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_get_EndArrowheadWidth.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_EndArrowheadWidth.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_EndArrowheadWidth, self.Ptr)
        objwraped = ShapeArrowWidthType(ret)
        return objwraped

    @EndArrowheadWidth.setter
    def EndArrowheadWidth(self, value:'ShapeArrowWidthType'):
        """Sets the width of the arrowhead at the end of the line.
        
        Args:
            value (ShapeArrowWidthType): An enumeration value representing the arrowhead width to set at the end of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_set_EndArrowheadWidth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_EndArrowheadWidth, self.Ptr, value.value)

    @property

    def DashStyle(self)->'ShapeDashLineStyleType':
        """Gets or sets the dash style for the line.
        
        The dash style determines the pattern of dashes and gaps used to draw the line.
        
        Returns:
            ShapeDashLineStyleType: An enumeration value representing the dash style of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_get_DashStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_DashStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_DashStyle, self.Ptr)
        objwraped = ShapeDashLineStyleType(ret)
        return objwraped

    @DashStyle.setter
    def DashStyle(self, value:'ShapeDashLineStyleType'):
        """Sets the dash style for the line.
        
        Args:
            value (ShapeDashLineStyleType): An enumeration value representing the dash style to set for the line.
        """
        GetDllLibXls().XlsShapeLineFormat_set_DashStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_DashStyle, self.Ptr, value.value)

    @property

    def Style(self)->'ShapeLineStyleType':
        """Gets or sets the line style.
        
        The line style determines the appearance of the line, such as single, double, or thick.
        
        Returns:
            ShapeLineStyleType: An enumeration value representing the style of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_get_Style.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_Style.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_Style, self.Ptr)
        objwraped = ShapeLineStyleType(ret)
        return objwraped

    @Style.setter
    def Style(self, value:'ShapeLineStyleType'):
        """Sets the line style.
        
        Args:
            value (ShapeLineStyleType): An enumeration value representing the style to set for the line.
        """
        GetDllLibXls().XlsShapeLineFormat_set_Style.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_Style, self.Ptr, value.value)

    @property
    def Transparency(self)->float:
        """Gets or sets the transparency level of the line.
        
        The value ranges from 0.0 (completely opaque) to 1.0 (completely transparent).
        
        Returns:
            float: The transparency level of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_get_Transparency.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_Transparency.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_Transparency, self.Ptr)
        return ret

    @Transparency.setter
    def Transparency(self, value:float):
        """Sets the transparency level of the line.
        
        Args:
            value (float): The transparency level to set, from 0.0 (completely opaque) to 1.0 (completely transparent).
        """
        GetDllLibXls().XlsShapeLineFormat_set_Transparency.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_Transparency, self.Ptr, value)

    @property
    def Visible(self)->bool:
        """Gets or sets whether the line is visible.
        
        Returns:
            bool: True if the line is visible; otherwise, False.
        """
        GetDllLibXls().XlsShapeLineFormat_get_Visible.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_Visible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_Visible, self.Ptr)
        return ret

    @Visible.setter
    def Visible(self, value:bool):
        """Sets whether the line is visible.
        
        Args:
            value (bool): True to make the line visible; False to hide it.
        """
        GetDllLibXls().XlsShapeLineFormat_set_Visible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_Visible, self.Ptr, value)

    @property

    def Pattern(self)->'GradientPatternType':
        """Gets or sets the pattern type for the line.
        
        Patterns provide a predefined arrangement of foreground and background colors for the line.
        
        Returns:
            GradientPatternType: An enumeration value representing the pattern type of the line.
        """
        GetDllLibXls().XlsShapeLineFormat_get_Pattern.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_Pattern.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_Pattern, self.Ptr)
        objwraped = GradientPatternType(ret)
        return objwraped

    @Pattern.setter
    def Pattern(self, value:'GradientPatternType'):
        """Sets the pattern type for the line.
        
        Args:
            value (GradientPatternType): An enumeration value representing the pattern type to set for the line.
        """
        GetDllLibXls().XlsShapeLineFormat_set_Pattern.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_Pattern, self.Ptr, value.value)

    @property
    def HasPattern(self)->bool:
        """Gets or sets whether the line has a pattern.
        
        Returns:
            bool: True if the line has a pattern; otherwise, False.
        """
        GetDllLibXls().XlsShapeLineFormat_get_HasPattern.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_HasPattern.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_HasPattern, self.Ptr)
        return ret

    @HasPattern.setter
    def HasPattern(self, value:bool):
        """Sets whether the line has a pattern.
        
        Args:
            value (bool): True to enable pattern for the line; False to disable it.
        """
        GetDllLibXls().XlsShapeLineFormat_set_HasPattern.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_HasPattern, self.Ptr, value)

    @property
    def IsRound(self)->bool:
        """Gets or sets whether the line join style is round.
        
        When True, the corners where two line segments meet are rounded.
        When False, the corners are sharp.
        
        Returns:
            bool: True if the line join style is round; otherwise, False.
        """
        GetDllLibXls().XlsShapeLineFormat_get_IsRound.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_IsRound.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_IsRound, self.Ptr)
        return ret

    @IsRound.setter
    def IsRound(self, value:bool):
        """Sets whether the line join style is round.
        
        Args:
            value (bool): True to set round join style; False to set sharp join style.
        """
        GetDllLibXls().XlsShapeLineFormat_set_IsRound.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_IsRound, self.Ptr, value)

    @property
    def NoFill(self)->bool:
        """Gets or sets whether the line has no fill.
        
        When True, the line is transparent regardless of other appearance settings.
        
        Returns:
            bool: True if the line has no fill; otherwise, False.
        """
        GetDllLibXls().XlsShapeLineFormat_get_NoFill.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeLineFormat_get_NoFill.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShapeLineFormat_get_NoFill, self.Ptr)
        return ret

    @NoFill.setter
    def NoFill(self, value:bool):
        """Sets whether the line has no fill.
        
        Args:
            value (bool): True to set the line to have no fill; False to enable fill.
        """
        GetDllLibXls().XlsShapeLineFormat_set_NoFill.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShapeLineFormat_set_NoFill, self.Ptr, value)


    def Clone(self ,parent:'SpireObject')->'XlsShapeLineFormat':
        """Creates a clone of this line format.
        
        This method creates a new line format object with the same properties as this one.
        
        Args:
            parent (SpireObject): The parent object for the cloned line format.
            
        Returns:
            XlsShapeLineFormat: A new line format object that is a copy of this one.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsShapeLineFormat_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsShapeLineFormat_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShapeLineFormat_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else XlsShapeLineFormat(intPtr)
        return ret


