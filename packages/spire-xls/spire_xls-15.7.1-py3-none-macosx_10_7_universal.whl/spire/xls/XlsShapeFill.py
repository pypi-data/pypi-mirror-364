from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsShapeFill (  XlsObject, IShapeFill) :
    """Represents the fill formatting for a shape in an Excel worksheet.
    
    This class provides properties and methods for manipulating fill formatting options
    such as solid colors, gradients, textures, patterns, and pictures. It allows for
    customization of fill appearance, transparency, and other visual aspects of shapes.
    """
    @property

    def GradientStops(self)->'GradientStops':
        """Gets the collection of gradient stops for the shape fill.
        
        Gradient stops define the colors and positions used in a gradient fill.
        
        Returns:
            GradientStops: A collection of gradient stops used in the gradient fill.
        """
        GetDllLibXls().XlsShapeFill_get_GradientStops.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_GradientStops.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShapeFill_get_GradientStops, self.Ptr)
        ret = None if intPtr==None else GradientStops(intPtr)
        return ret


    @property

    def FillType(self)->'ShapeFillType':
        """Gets or sets the fill type for the shape.
        
        The fill type determines how the shape is filled, such as solid color,
        gradient, pattern, texture, or picture.
        
        Returns:
            ShapeFillType: An enumeration value representing the fill type.
        """
        GetDllLibXls().XlsShapeFill_get_FillType.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_FillType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_get_FillType, self.Ptr)
        objwraped = ShapeFillType(ret)
        return objwraped

    @FillType.setter
    def FillType(self, value:'ShapeFillType'):
        """Sets the fill type for the shape.
        
        Args:
            value (ShapeFillType): An enumeration value representing the fill type to set.
        """
        GetDllLibXls().XlsShapeFill_set_FillType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_FillType, self.Ptr, value.value)

    @property

    def GradientStyle(self)->'GradientStyleType':
        """Gets or sets the gradient style for the shape fill.
        
        The gradient style defines the direction or pattern of the gradient,
        such as horizontal, vertical, diagonal, or radial.
        
        Returns:
            GradientStyleType: An enumeration value representing the gradient style.
        """
        GetDllLibXls().XlsShapeFill_get_GradientStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_GradientStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_get_GradientStyle, self.Ptr)
        objwraped = GradientStyleType(ret)
        return objwraped

    @GradientStyle.setter
    def GradientStyle(self, value:'GradientStyleType'):
        """Sets the gradient style for the shape fill.
        
        Args:
            value (GradientStyleType): An enumeration value representing the gradient style to set.
        """
        GetDllLibXls().XlsShapeFill_set_GradientStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_GradientStyle, self.Ptr, value.value)

    @property

    def GradientVariant(self)->'GradientVariantsType':
        """Gets or sets the gradient variant for the shape fill.
        
        The gradient variant modifies the appearance of the gradient style,
        providing additional variations for each gradient style.
        
        Returns:
            GradientVariantsType: An enumeration value representing the gradient variant.
        """
        GetDllLibXls().XlsShapeFill_get_GradientVariant.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_GradientVariant.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_get_GradientVariant, self.Ptr)
        objwraped = GradientVariantsType(ret)
        return objwraped

    @GradientVariant.setter
    def GradientVariant(self, value:'GradientVariantsType'):
        """Sets the gradient variant for the shape fill.
        
        Args:
            value (GradientVariantsType): An enumeration value representing the gradient variant to set.
        """
        GetDllLibXls().XlsShapeFill_set_GradientVariant.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_GradientVariant, self.Ptr, value.value)

    @property
    def Transparency(self)->float:
        """Gets or sets the transparency level of the shape fill.
        
        The value ranges from 0.0 (completely opaque) to 1.0 (completely transparent).
        
        Returns:
            float: The transparency level of the shape fill.
        """
        GetDllLibXls().XlsShapeFill_get_Transparency.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_Transparency.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_get_Transparency, self.Ptr)
        return ret

    @Transparency.setter
    def Transparency(self, value:float):
        """Sets the transparency level of the shape fill.
        
        Args:
            value (float): The transparency level to set, from 0.0 (completely opaque) to 1.0 (completely transparent).
        """
        GetDllLibXls().XlsShapeFill_set_Transparency.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_Transparency, self.Ptr, value)

    @property
    def TransparencyFrom(self)->float:
        """Gets or sets the starting transparency level for gradient fills.
        
        Used in gradient fills to define the transparency at the starting point of the gradient.
        The value ranges from 0.0 (completely opaque) to 1.0 (completely transparent).
        
        Returns:
            float: The starting transparency level for gradient fills.
        """
        GetDllLibXls().XlsShapeFill_get_TransparencyFrom.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_TransparencyFrom.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_get_TransparencyFrom, self.Ptr)
        return ret

    @TransparencyFrom.setter
    def TransparencyFrom(self, value:float):
        """Sets the starting transparency level for gradient fills.
        
        Args:
            value (float): The starting transparency level to set, from 0.0 (completely opaque) to 1.0 (completely transparent).
        """
        GetDllLibXls().XlsShapeFill_set_TransparencyFrom.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_TransparencyFrom, self.Ptr, value)

    @property
    def TransparencyTo(self)->float:
        """Gets or sets the ending transparency level for gradient fills.
        
        Used in gradient fills to define the transparency at the ending point of the gradient.
        The value ranges from 0.0 (completely opaque) to 1.0 (completely transparent).
        
        Returns:
            float: The ending transparency level for gradient fills.
        """
        GetDllLibXls().XlsShapeFill_get_TransparencyTo.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_TransparencyTo.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_get_TransparencyTo, self.Ptr)
        return ret

    @TransparencyTo.setter
    def TransparencyTo(self, value:float):
        """Sets the ending transparency level for gradient fills.
        
        Args:
            value (float): The ending transparency level to set, from 0.0 (completely opaque) to 1.0 (completely transparent).
        """
        GetDllLibXls().XlsShapeFill_set_TransparencyTo.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_TransparencyTo, self.Ptr, value)

    @property
    def Visible(self)->bool:
        """Gets or sets whether the shape fill is visible.
        
        Returns:
            bool: True if the shape fill is visible; otherwise, False.
        """
        GetDllLibXls().XlsShapeFill_get_Visible.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_Visible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_get_Visible, self.Ptr)
        return ret

    @Visible.setter
    def Visible(self, value:bool):
        """Sets whether the shape fill is visible.
        
        Args:
            value (bool): True to make the shape fill visible; False to hide it.
        """
        GetDllLibXls().XlsShapeFill_set_Visible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_Visible, self.Ptr, value)

    @property

    def BackKnownColor(self)->'ExcelColors':
        """Gets or sets the background color from a predefined set of Excel colors.
        
        Returns:
            ExcelColors: An enumeration value representing the predefined Excel background color.
        """
        GetDllLibXls().XlsShapeFill_get_BackKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_BackKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_get_BackKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @BackKnownColor.setter
    def BackKnownColor(self, value:'ExcelColors'):
        """Sets the background color from a predefined set of Excel colors.
        
        Args:
            value (ExcelColors): An enumeration value representing the predefined Excel background color to set.
        """
        GetDllLibXls().XlsShapeFill_set_BackKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_BackKnownColor, self.Ptr, value.value)

    @property

    def ForeKnownColor(self)->'ExcelColors':
        """Gets or sets the foreground color from a predefined set of Excel colors.
        
        Used in patterns and gradients where both foreground and background colors are needed.
        
        Returns:
            ExcelColors: An enumeration value representing the predefined Excel foreground color.
        """
        GetDllLibXls().XlsShapeFill_get_ForeKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_ForeKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_get_ForeKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @ForeKnownColor.setter
    def ForeKnownColor(self, value:'ExcelColors'):
        """Sets the foreground color from a predefined set of Excel colors.
        
        Args:
            value (ExcelColors): An enumeration value representing the predefined Excel foreground color to set.
        """
        GetDllLibXls().XlsShapeFill_set_ForeKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_ForeKnownColor, self.Ptr, value.value)

    @property

    def BackColor(self)->'Color':
        """Gets or sets the background color of the shape fill.
        
        Provides access to a Color object for custom background color settings.
        
        Returns:
            Color: A Color object representing the background color.
        """
        GetDllLibXls().XlsShapeFill_get_BackColor.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_BackColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShapeFill_get_BackColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @BackColor.setter
    def BackColor(self, value:'Color'):
        """Sets the background color of the shape fill.
        
        Args:
            value (Color): A Color object representing the background color to set.
        """
        GetDllLibXls().XlsShapeFill_set_BackColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_BackColor, self.Ptr, value.Ptr)

    @property

    def ForeColor(self)->'Color':
        """Gets or sets the foreground color of the shape fill.
        
        Provides access to a Color object for custom foreground color settings.
        Used in patterns and gradients where both foreground and background colors are needed.
        
        Returns:
            Color: A Color object representing the foreground color.
        """
        GetDllLibXls().XlsShapeFill_get_ForeColor.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_ForeColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShapeFill_get_ForeColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @ForeColor.setter
    def ForeColor(self, value:'Color'):
        """Sets the foreground color of the shape fill.
        
        Args:
            value (Color): A Color object representing the foreground color to set.
        """
        GetDllLibXls().XlsShapeFill_set_ForeColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_ForeColor, self.Ptr, value.Ptr)

    @property

    def BackColorObject(self)->'OColor':
        """Gets the Office color object for the background color of the shape fill.
        
        Provides access to advanced color properties and settings for the background color.
        
        Returns:
            OColor: An Office color object representing the background color.
        """
        GetDllLibXls().XlsShapeFill_get_BackColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_BackColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShapeFill_get_BackColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def ForeColorObject(self)->'OColor':
        """Gets the Office color object for the foreground color of the shape fill.
        
        Provides access to advanced color properties and settings for the foreground color.
        
        Returns:
            OColor: An Office color object representing the foreground color.
        """
        GetDllLibXls().XlsShapeFill_get_ForeColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_ForeColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShapeFill_get_ForeColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def GradientColorType(self)->'GradientColorType':
        """Gets or sets the color type for gradient fills.
        
        Determines how colors are applied in a gradient fill, such as one color or two colors.
        
        Returns:
            GradientColorType: An enumeration value representing the gradient color type.
        """
        GetDllLibXls().XlsShapeFill_get_GradientColorType.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_GradientColorType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_get_GradientColorType, self.Ptr)
        objwraped = GradientColorType(ret)
        return objwraped

    @GradientColorType.setter
    def GradientColorType(self, value:'GradientColorType'):
        """Sets the color type for gradient fills.
        
        Args:
            value (GradientColorType): An enumeration value representing the gradient color type to set.
        """
        GetDllLibXls().XlsShapeFill_set_GradientColorType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_GradientColorType, self.Ptr, value.value)

    @property

    def Texture(self)->'GradientTextureType':
        """Gets or sets the texture type for the shape fill.
        
        Textures provide a predefined pattern that can be applied to the shape fill.
        
        Returns:
            GradientTextureType: An enumeration value representing the texture type.
        """
        GetDllLibXls().XlsShapeFill_get_Texture.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_Texture.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_get_Texture, self.Ptr)
        objwraped = GradientTextureType(ret)
        return objwraped

    @Texture.setter
    def Texture(self, value:'GradientTextureType'):
        """Sets the texture type for the shape fill.
        
        Args:
            value (GradientTextureType): An enumeration value representing the texture type to set.
        """
        GetDllLibXls().XlsShapeFill_set_Texture.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_Texture, self.Ptr, value.value)

    @property

    def Pattern(self)->'GradientPatternType':
        """Gets or sets the pattern type for the shape fill.
        
        Patterns provide a predefined arrangement of foreground and background colors.
        
        Returns:
            GradientPatternType: An enumeration value representing the pattern type.
        """
        GetDllLibXls().XlsShapeFill_get_Pattern.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_Pattern.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_get_Pattern, self.Ptr)
        objwraped = GradientPatternType(ret)
        return objwraped

    @Pattern.setter
    def Pattern(self, value:'GradientPatternType'):
        """Sets the pattern type for the shape fill.
        
        Args:
            value (GradientPatternType): An enumeration value representing the pattern type to set.
        """
        GetDllLibXls().XlsShapeFill_set_Pattern.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_Pattern, self.Ptr, value.value)

    @property

    def PresetGradientType(self)->'GradientPresetType':
        """Gets or sets the preset gradient type for the shape fill.
        
        Preset gradients are predefined gradient configurations that can be applied to the shape.
        
        Returns:
            GradientPresetType: An enumeration value representing the preset gradient type.
        """
        GetDllLibXls().XlsShapeFill_get_PresetGradientType.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_PresetGradientType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_get_PresetGradientType, self.Ptr)
        objwraped = GradientPresetType(ret)
        return objwraped

    @PresetGradientType.setter
    def PresetGradientType(self, value:'GradientPresetType'):
        """Sets the preset gradient type for the shape fill.
        
        Args:
            value (GradientPresetType): An enumeration value representing the preset gradient type to set.
        """
        GetDllLibXls().XlsShapeFill_set_PresetGradientType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_PresetGradientType, self.Ptr, value.value)

    @property

    def Picture(self)->'Stream':
        """Gets the picture used for the shape fill.
        
        When the fill type is set to picture, this property provides access to the image data.
        
        Returns:
            Stream: A stream containing the picture data.
        """
        GetDllLibXls().XlsShapeFill_get_Picture.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_Picture.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShapeFill_get_Picture, self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    @property

    def PictureName(self)->str:
        """Gets the name of the picture used for the shape fill.
        
        When the fill type is set to picture, this property provides the name of the image.
        
        Returns:
            str: The name of the picture.
        """
        GetDllLibXls().XlsShapeFill_get_PictureName.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_PictureName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsShapeFill_get_PictureName, self.Ptr))
        return ret


    @property
    def GradientDegree(self)->float:
        """Gets or sets the degree (angle) of the gradient fill.
        
        This property defines the angle at which the gradient is applied, measured in degrees.
        
        Returns:
            float: The angle of the gradient in degrees.
        """
        GetDllLibXls().XlsShapeFill_get_GradientDegree.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_GradientDegree.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_get_GradientDegree, self.Ptr)
        return ret

    @GradientDegree.setter
    def GradientDegree(self, value:float):
        """Sets the degree (angle) of the gradient fill.
        
        Args:
            value (float): The angle of the gradient in degrees to set.
        """
        GetDllLibXls().XlsShapeFill_set_GradientDegree.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_GradientDegree, self.Ptr, value)

    @property
    def IsGradientSupported(self)->bool:
        """Gets or sets whether gradient fills are supported for this shape.
        
        Some shape types may not support gradient fills, and this property indicates that capability.
        
        Returns:
            bool: True if gradient fills are supported; otherwise, False.
        """
        GetDllLibXls().XlsShapeFill_get_IsGradientSupported.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_IsGradientSupported.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_get_IsGradientSupported, self.Ptr)
        return ret

    @IsGradientSupported.setter
    def IsGradientSupported(self, value:bool):
        """Sets whether gradient fills are supported for this shape.
        
        Args:
            value (bool): True to enable gradient fill support; False to disable it.
        """
        GetDllLibXls().XlsShapeFill_set_IsGradientSupported.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_IsGradientSupported, self.Ptr, value)

    @property
    def Tile(self)->bool:
        """Gets or sets whether the picture fill is tiled.
        
        When True, the picture is repeated to fill the shape area. When False, the picture is stretched.
        
        Returns:
            bool: True if the picture fill is tiled; otherwise, False.
        """
        GetDllLibXls().XlsShapeFill_get_Tile.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_Tile.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_get_Tile, self.Ptr)
        return ret

    @Tile.setter
    def Tile(self, value:bool):
        """Sets whether the picture fill is tiled.
        
        Args:
            value (bool): True to enable picture tiling; False to disable it.
        """
        GetDllLibXls().XlsShapeFill_set_Tile.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_Tile, self.Ptr, value)

    @property

    def PicStretch(self)->'PicStretch':
        """Gets or sets the stretch settings for the picture fill.
        
        When the picture is not tiled, this property controls how the picture is stretched to fill the shape.
        
        Returns:
            PicStretch: An object that controls the picture stretch settings.
        """
        GetDllLibXls().XlsShapeFill_get_PicStretch.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_PicStretch.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShapeFill_get_PicStretch, self.Ptr)
        ret = None if intPtr==None else PicStretch(intPtr)
        return ret


    @PicStretch.setter
    def PicStretch(self, value:'PicStretch'):
        """Sets the stretch settings for the picture fill.
        
        Args:
            value (PicStretch): An object that controls the picture stretch settings.
        """
        GetDllLibXls().XlsShapeFill_set_PicStretch.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_PicStretch, self.Ptr, value.Ptr)

    @property

    def PicTile(self)->'PicTile':
        """Gets or sets the tiling settings for the picture fill.
        
        When the picture is tiled, this property controls how the picture is repeated to fill the shape.
        
        Returns:
            PicTile: An object that controls the picture tiling settings.
        """
        GetDllLibXls().XlsShapeFill_get_PicTile.argtypes=[c_void_p]
        GetDllLibXls().XlsShapeFill_get_PicTile.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShapeFill_get_PicTile, self.Ptr)
        ret = None if intPtr==None else PicTile(intPtr)
        return ret


    @PicTile.setter
    def PicTile(self, value:'PicTile'):
        """Sets the tiling settings for the picture fill.
        
        Args:
            value (PicTile): An object that controls the picture tiling settings.
        """
        GetDllLibXls().XlsShapeFill_set_PicTile.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsShapeFill_set_PicTile, self.Ptr, value.Ptr)

    @staticmethod

    def IsDoubled(gradientStyle:'GradientStyleType',variant:'GradientVariantsType')->bool:
        """Determines if the specified gradient style and variant combination results in a doubled gradient.
        
        A doubled gradient repeats the gradient pattern twice within the shape.
        
        Args:
            gradientStyle (GradientStyleType): The gradient style to check.
            variant (GradientVariantsType): The gradient variant to check.
            
        Returns:
            bool: True if the combination results in a doubled gradient; otherwise, False.
        """
        enumgradientStyle:c_int = gradientStyle.value
        enumvariant:c_int = variant.value

        GetDllLibXls().XlsShapeFill_IsDoubled.argtypes=[ c_int,c_int]
        GetDllLibXls().XlsShapeFill_IsDoubled.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_IsDoubled,  enumgradientStyle,enumvariant)
        return ret

    @staticmethod

    def IsInverted(gradientStyle:'GradientStyleType',variant:'GradientVariantsType')->bool:
        """Determines if the specified gradient style and variant combination results in an inverted gradient.
        
        An inverted gradient reverses the direction of the color transition.
        
        Args:
            gradientStyle (GradientStyleType): The gradient style to check.
            variant (GradientVariantsType): The gradient variant to check.
            
        Returns:
            bool: True if the combination results in an inverted gradient; otherwise, False.
        """
        enumgradientStyle:c_int = gradientStyle.value
        enumvariant:c_int = variant.value

        GetDllLibXls().XlsShapeFill_IsInverted.argtypes=[ c_int,c_int]
        GetDllLibXls().XlsShapeFill_IsInverted.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_IsInverted,  enumgradientStyle,enumvariant)
        return ret


    def CompareTo(self ,twin:'IGradient')->int:
        """Compares this shape fill with another gradient object.
        
        This method is used to determine the relative order of two gradient objects.
        
        Args:
            twin (IGradient): The gradient object to compare with this shape fill.
            
        Returns:
            int: A value that indicates the relative order of the objects being compared.
                 Less than zero: This instance precedes the specified object.
                 Zero: This instance equals the specified object.
                 Greater than zero: This instance follows the specified object.
        """
        intPtrtwin:c_void_p = twin.Ptr

        GetDllLibXls().XlsShapeFill_CompareTo.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsShapeFill_CompareTo.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsShapeFill_CompareTo, self.Ptr, intPtrtwin)
        return ret

    @dispatch

    def CustomPicture(self ,path:str):
        """Sets a custom picture for the shape fill using a file path.
        
        This method changes the fill type to picture and loads the image from the specified file.
        
        Args:
            path (str): The file path of the image to use as the fill.
        """
        
        GetDllLibXls().XlsShapeFill_CustomPicture.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsShapeFill_CustomPicture, self.Ptr, path)

    @dispatch

    def CustomPicture(self ,im:Stream,name:str):
        """Sets a custom picture for the shape fill using a stream and name.
        
        This method changes the fill type to picture and loads the image from the provided stream.
        
        Args:
            im (Stream): A stream containing the image data.
            name (str): The name to assign to the picture.
        """
        intPtrim:c_void_p = im.Ptr

        GetDllLibXls().XlsShapeFill_CustomPictureIN.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsShapeFill_CustomPictureIN, self.Ptr, intPtrim,name)

    @dispatch

    def CustomTexture(self ,path:str):
        """Sets a custom texture for the shape fill using a file path.
        
        This method changes the fill type to texture and loads the texture from the specified file.
        
        Args:
            path (str): The file path of the image to use as the texture.
        """
        
        GetDllLibXls().XlsShapeFill_CustomTexture.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsShapeFill_CustomTexture, self.Ptr, path)

    @dispatch

    def CustomTexture(self ,im:Stream,name:str):
        """Sets a custom texture for the shape fill using a stream and name.
        
        This method changes the fill type to texture and loads the texture from the provided stream.
        
        Args:
            im (Stream): A stream containing the texture image data.
            name (str): The name to assign to the texture.
        """
        intPtrim:c_void_p = im.Ptr

        GetDllLibXls().XlsShapeFill_CustomTextureIN.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsShapeFill_CustomTextureIN, self.Ptr, intPtrim,name)


    def Patterned(self ,pattern:'GradientPatternType'):
        """Sets a pattern fill for the shape.
        
        This method changes the fill type to pattern and applies the specified pattern type.
        
        Args:
            pattern (GradientPatternType): The pattern type to apply to the shape fill.
        """
        enumpattern:c_int = pattern.value

        GetDllLibXls().XlsShapeFill_Patterned.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_Patterned, self.Ptr, enumpattern)

    @dispatch

    def PresetGradient(self ,grad:GradientPresetType):
        """Sets a preset gradient fill for the shape.
        
        This method changes the fill type to gradient and applies the specified preset gradient.
        
        Args:
            grad (GradientPresetType): The preset gradient type to apply to the shape fill.
        """
        enumgrad:c_int = grad.value

        GetDllLibXls().XlsShapeFill_PresetGradient.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_PresetGradient, self.Ptr, enumgrad)

    @dispatch

    def PresetGradient(self ,grad:GradientPresetType,shadStyle:GradientStyleType):
        """Sets a preset gradient fill with a specific style for the shape.
        
        This method changes the fill type to gradient and applies the specified preset gradient with the given style.
        
        Args:
            grad (GradientPresetType): The preset gradient type to apply to the shape fill.
            shadStyle (GradientStyleType): The gradient style to apply (e.g., horizontal, vertical, diagonal).
        """
        enumgrad:c_int = grad.value
        enumshadStyle:c_int = shadStyle.value

        GetDllLibXls().XlsShapeFill_PresetGradientGS.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_PresetGradientGS, self.Ptr, enumgrad,enumshadStyle)

    @dispatch

    def PresetGradient(self ,grad:GradientPresetType,shadStyle:GradientStyleType,shadVar:GradientVariantsType):
        """Sets a preset gradient fill with specific style and variant for the shape.
        
        This method changes the fill type to gradient and applies the specified preset gradient with the given style and variant.
        
        Args:
            grad (GradientPresetType): The preset gradient type to apply to the shape fill.
            shadStyle (GradientStyleType): The gradient style to apply (e.g., horizontal, vertical, diagonal).
            shadVar (GradientVariantsType): The gradient variant to apply, which modifies the appearance of the gradient.
        """
        enumgrad:c_int = grad.value
        enumshadStyle:c_int = shadStyle.value
        enumshadVar:c_int = shadVar.value

        GetDllLibXls().XlsShapeFill_PresetGradientGSS.argtypes=[c_void_p ,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_PresetGradientGSS, self.Ptr, enumgrad,enumshadStyle,enumshadVar)


    def PresetTextured(self ,texture:'GradientTextureType'):
        """Sets a preset texture fill for the shape.
        
        This method changes the fill type to texture and applies the specified preset texture.
        
        Args:
            texture (GradientTextureType): The preset texture type to apply to the shape fill.
        """
        enumtexture:c_int = texture.value

        GetDllLibXls().XlsShapeFill_PresetTextured.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_PresetTextured, self.Ptr, enumtexture)

    @dispatch
    def TwoColorGradient(self):
        """Sets a two-color gradient fill for the shape with default settings.
        
        This method changes the fill type to a two-color gradient using the default style and variant.
        The gradient transitions between the foreground and background colors.
        """
        GetDllLibXls().XlsShapeFill_TwoColorGradient.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsShapeFill_TwoColorGradient, self.Ptr)

    @dispatch

    def TwoColorGradient(self ,style:GradientStyleType):
        """Sets a two-color gradient fill with a specific style for the shape.
        
        This method changes the fill type to a two-color gradient using the specified style.
        The gradient transitions between the foreground and background colors.
        
        Args:
            style (GradientStyleType): The gradient style to apply (e.g., horizontal, vertical, diagonal).
        """
        enumstyle:c_int = style.value

        GetDllLibXls().XlsShapeFill_TwoColorGradientS.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_TwoColorGradientS, self.Ptr, enumstyle)

    @dispatch

    def TwoColorGradient(self ,style:GradientStyleType,variant:GradientVariantsType):
        """Sets a two-color gradient fill with specific style and variant for the shape.
        
        This method changes the fill type to a two-color gradient using the specified style and variant.
        The gradient transitions between the foreground and background colors.
        
        Args:
            style (GradientStyleType): The gradient style to apply (e.g., horizontal, vertical, diagonal).
            variant (GradientVariantsType): The gradient variant to apply, which modifies the appearance of the gradient.
        """
        enumstyle:c_int = style.value
        enumvariant:c_int = variant.value

        GetDllLibXls().XlsShapeFill_TwoColorGradientSV.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_TwoColorGradientSV, self.Ptr, enumstyle,enumvariant)

    @dispatch
    def OneColorGradient(self):
        """Sets a one-color gradient fill for the shape with default settings.
        
        This method changes the fill type to a one-color gradient using the default style and variant.
        The gradient transitions from the foreground color to a lighter or darker shade.
        """
        GetDllLibXls().XlsShapeFill_OneColorGradient.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsShapeFill_OneColorGradient, self.Ptr)

    @dispatch

    def OneColorGradient(self ,style:GradientStyleType):
        """Sets a one-color gradient fill with a specific style for the shape.
        
        This method changes the fill type to a one-color gradient using the specified style.
        The gradient transitions from the foreground color to a lighter or darker shade.
        
        Args:
            style (GradientStyleType): The gradient style to apply (e.g., horizontal, vertical, diagonal).
        """
        enumstyle:c_int = style.value

        GetDllLibXls().XlsShapeFill_OneColorGradientS.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_OneColorGradientS, self.Ptr, enumstyle)

    @dispatch

    def OneColorGradient(self ,style:GradientStyleType,variant:GradientVariantsType):
        """Sets a one-color gradient fill with specific style and variant for the shape.
        
        This method changes the fill type to a one-color gradient using the specified style and variant.
        The gradient transitions from the foreground color to a lighter or darker shade.
        
        Args:
            style (GradientStyleType): The gradient style to apply (e.g., horizontal, vertical, diagonal).
            variant (GradientVariantsType): The gradient variant to apply, which modifies the appearance of the gradient.
        """
        enumstyle:c_int = style.value
        enumvariant:c_int = variant.value

        GetDllLibXls().XlsShapeFill_OneColorGradientSV.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsShapeFill_OneColorGradientSV, self.Ptr, enumstyle,enumvariant)

    def Solid(self):
        """Sets a solid color fill for the shape.
        
        This method changes the fill type to solid color using the current foreground color.
        """
        GetDllLibXls().XlsShapeFill_Solid.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsShapeFill_Solid, self.Ptr)


    def Clone(self ,parent:'SpireObject')->'XlsShapeFill':
        """Creates a clone of this shape fill.
        
        This method creates a new shape fill object with the same properties as this one.
        
        Args:
            parent (SpireObject): The parent object for the cloned shape fill.
            
        Returns:
            XlsShapeFill: A new shape fill object that is a copy of this one.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsShapeFill_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsShapeFill_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsShapeFill_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else XlsShapeFill(intPtr)
        return ret


