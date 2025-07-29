from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IShapeFill (abc.ABC) :
    """Shape fill formatting interface for Excel shapes.
    
    This interface provides properties and methods to control the fill formatting
    of shapes in Excel, including solid colors, gradients, patterns, textures, and pictures.
    It allows detailed customization of fill effects for shapes, charts, and other objects.
    """
    @property
    @abc.abstractmethod
    def FillType(self)->'ShapeFillType':
        """Gets the fill type of the shape.
        
        This property returns an enumeration value that indicates how the shape is filled,
        such as solid color, gradient, pattern, texture, picture, or no fill.
        
        Returns:
            ShapeFillType: An enumeration value representing the fill type.
        """
        pass


    @FillType.setter
    @abc.abstractmethod
    def FillType(self, value:'ShapeFillType'):
        """Sets the fill type of the shape.
        
        This property sets an enumeration value that indicates how the shape is filled,
        such as solid color, gradient, pattern, texture, picture, or no fill.
        
        Args:
            value (ShapeFillType): An enumeration value representing the fill type to set.
        """
        pass


    @property
    @abc.abstractmethod
    def GradientStyle(self)->'GradientStyleType':
        """Gets the gradient style of the shape fill.
        
        This property returns an enumeration value that defines the style of the gradient fill,
        such as horizontal, vertical, diagonal, radial, etc.
        
        Returns:
            GradientStyleType: An enumeration value representing the gradient style.
        """
        pass


    @GradientStyle.setter
    @abc.abstractmethod
    def GradientStyle(self, value:'GradientStyleType'):
        """Sets the gradient style of the shape fill.
        
        This property sets an enumeration value that defines the style of the gradient fill,
        such as horizontal, vertical, diagonal, radial, etc.
        
        Args:
            value (GradientStyleType): An enumeration value representing the gradient style to set.
        """
        pass


    @property
    @abc.abstractmethod
    def GradientVariant(self)->'GradientVariantsType':
        """Gets the gradient variant of the shape fill.
        
        This property returns an enumeration value that defines the variant of the gradient fill,
        which determines how colors blend together within the gradient.
        
        Returns:
            GradientVariantsType: An enumeration value representing the gradient variant.
        """
        pass


    @GradientVariant.setter
    @abc.abstractmethod
    def GradientVariant(self, value:'GradientVariantsType'):
        """Sets the gradient variant of the shape fill.
        
        This property sets an enumeration value that defines the variant of the gradient fill,
        which determines how colors blend together within the gradient.
        
        Args:
            value (GradientVariantsType): An enumeration value representing the gradient variant to set.
        """
        pass


    @property
    @abc.abstractmethod
    def TransparencyTo(self)->float:
        """Gets the ending transparency value for gradient fills.
        
        This property returns the ending transparency value (from 0.0 to 1.0) for gradient fills,
        where 0.0 is completely opaque and 1.0 is completely transparent.
        This value represents the transparency at the end point of the gradient.
        
        Returns:
            float: The ending transparency value (0.0-1.0).
        """
        pass


    @TransparencyTo.setter
    @abc.abstractmethod
    def TransparencyTo(self, value:float):
        """Sets the ending transparency value for gradient fills.
        
        This property sets the ending transparency value (from 0.0 to 1.0) for gradient fills,
        where 0.0 is completely opaque and 1.0 is completely transparent.
        This value represents the transparency at the end point of the gradient.
        
        Args:
            value (float): The ending transparency value (0.0-1.0).
        """
        pass


    @property
    @abc.abstractmethod
    def TransparencyFrom(self)->float:
        """Gets the starting transparency value for gradient fills.
        
        This property returns the starting transparency value (from 0.0 to 1.0) for gradient fills,
        where 0.0 is completely opaque and 1.0 is completely transparent.
        This value represents the transparency at the start point of the gradient.
        
        Returns:
            float: The starting transparency value (0.0-1.0).
        """
        pass


    @TransparencyFrom.setter
    @abc.abstractmethod
    def TransparencyFrom(self, value:float):
        """Sets the starting transparency value for gradient fills.
        
        This property sets the starting transparency value (from 0.0 to 1.0) for gradient fills,
        where 0.0 is completely opaque and 1.0 is completely transparent.
        This value represents the transparency at the start point of the gradient.
        
        Args:
            value (float): The starting transparency value (0.0-1.0).
        """
        pass


    @property
    @abc.abstractmethod
    def GradientColorType(self)->'GradientColorType':
        """Gets the gradient color type of the shape fill.
        
        This property returns an enumeration value that indicates the type of color
        gradient used, such as one-color or two-color gradient.
        
        Returns:
            GradientColorType: An enumeration value representing the gradient color type.
        """
        pass


    @GradientColorType.setter
    @abc.abstractmethod
    def GradientColorType(self, value:'GradientColorType'):
        """Sets the gradient color type of the shape fill.
        
        This property sets an enumeration value that indicates the type of color
        gradient to use, such as one-color or two-color gradient.
        
        Args:
            value (GradientColorType): An enumeration value representing the gradient color type to set.
        """
        pass


    @property
    @abc.abstractmethod
    def Pattern(self)->'GradientPatternType':
        """Gets the pattern type of the shape fill.
        
        This property returns an enumeration value that defines the pattern type used
        for the shape fill, such as horizontal lines, vertical lines, diagonal lines, dots, etc.
        
        Returns:
            GradientPatternType: An enumeration value representing the pattern type.
        """
        pass


    @Pattern.setter
    @abc.abstractmethod
    def Pattern(self, value:'GradientPatternType'):
        """Sets the pattern type of the shape fill.
        
        This property sets an enumeration value that defines the pattern type to use
        for the shape fill, such as horizontal lines, vertical lines, diagonal lines, dots, etc.
        
        Args:
            value (GradientPatternType): An enumeration value representing the pattern type to set.
        """
        pass


    @property
    @abc.abstractmethod
    def Texture(self)->'GradientTextureType':
        """Gets the texture type of the shape fill.
        
        This property returns an enumeration value that defines the texture type used
        for the shape fill, such as canvas, denim, paper, etc.
        
        Returns:
            GradientTextureType: An enumeration value representing the texture type.
        """
        pass


    @Texture.setter
    @abc.abstractmethod
    def Texture(self, value:'GradientTextureType'):
        """Sets the texture type of the shape fill.
        
        This property sets an enumeration value that defines the texture type to use
        for the shape fill, such as canvas, denim, paper, etc.
        
        Args:
            value (GradientTextureType): An enumeration value representing the texture type to set.
        """
        pass


    @property
    @abc.abstractmethod
    def BackKnownColor(self)->'ExcelColors':
        """Gets the predefined background color of the shape fill.
        
        This property returns an enumeration value that defines a predefined background color
        used for the shape fill. This is applicable for solid fills, patterns, and two-color gradients.
        
        Returns:
            ExcelColors: An enumeration value representing the predefined background color.
        """
        pass


    @BackKnownColor.setter
    @abc.abstractmethod
    def BackKnownColor(self, value:'ExcelColors'):
        """Sets the predefined background color of the shape fill.
        
        This property sets an enumeration value that defines a predefined background color
        to use for the shape fill. This is applicable for solid fills, patterns, and two-color gradients.
        
        Args:
            value (ExcelColors): An enumeration value representing the predefined background color to set.
        """
        pass


    @property
    @abc.abstractmethod
    def ForeKnownColor(self)->'ExcelColors':
        """Gets the predefined foreground color of the shape fill.
        
        This property returns an enumeration value that defines a predefined foreground color
        used for the shape fill. This is applicable for patterns and two-color gradients.
        
        Returns:
            ExcelColors: An enumeration value representing the predefined foreground color.
        """
        pass


    @ForeKnownColor.setter
    @abc.abstractmethod
    def ForeKnownColor(self, value:'ExcelColors'):
        """Sets the predefined foreground color of the shape fill.
        
        This property sets an enumeration value that defines a predefined foreground color
        to use for the shape fill. This is applicable for patterns and two-color gradients.
        
        Args:
            value (ExcelColors): An enumeration value representing the predefined foreground color to set.
        """
        pass


    @property
    @abc.abstractmethod
    def BackColor(self)->'Color':
        """Gets the custom background color of the shape fill.
        
        This property returns a Color object that defines a custom background color
        used for the shape fill. This is applicable for solid fills, patterns, and two-color gradients.
        
        Returns:
            Color: A Color object representing the custom background color.
        """
        pass


    @BackColor.setter
    @abc.abstractmethod
    def BackColor(self, value:'Color'):
        """Sets the custom background color of the shape fill.
        
        This property sets a Color object that defines a custom background color
        to use for the shape fill. This is applicable for solid fills, patterns, and two-color gradients.
        
        Args:
            value (Color): A Color object representing the custom background color to set.
        """
        pass


    @property
    @abc.abstractmethod
    def ForeColor(self)->'Color':
        """Gets the custom foreground color of the shape fill.
        
        This property returns a Color object that defines a custom foreground color
        used for the shape fill. This is applicable for patterns and two-color gradients.
        
        Returns:
            Color: A Color object representing the custom foreground color.
        """
        pass


    @ForeColor.setter
    @abc.abstractmethod
    def ForeColor(self, value:'Color'):
        """Sets the custom foreground color of the shape fill.
        
        This property sets a Color object that defines a custom foreground color
        to use for the shape fill. This is applicable for patterns and two-color gradients.
        
        Args:
            value (Color): A Color object representing the custom foreground color to set.
        """
        pass


    @property
    @abc.abstractmethod
    def PresetGradientType(self)->'GradientPresetType':
        """Gets the preset gradient type of the shape fill.
        
        This property returns an enumeration value that defines a preset gradient type
        used for the shape fill, such as early sunset, fog, daybreak, etc.
        
        Returns:
            GradientPresetType: An enumeration value representing the preset gradient type.
        """
        pass


    @PresetGradientType.setter
    @abc.abstractmethod
    def PresetGradientType(self, value:'GradientPresetType'):
        """Sets the preset gradient type of the shape fill.
        
        This property sets an enumeration value that defines a preset gradient type
        to use for the shape fill, such as early sunset, fog, daybreak, etc.
        
        Args:
            value (GradientPresetType): An enumeration value representing the preset gradient type to set.
        """
        pass


    @property
    @abc.abstractmethod
    def Picture(self)->'Stream':
        """Gets the picture data used for the shape fill.
        
        This property returns a Stream object containing the binary data of the picture
        used for the shape fill when the fill type is set to picture.
        
        Returns:
            Stream: A Stream object containing the picture data.
        """
        pass


    @property
    @abc.abstractmethod
    def PictureName(self)->str:
        """Gets the name of the picture used for the shape fill.
        
        This property returns the name or file path of the picture used for the shape fill
        when the fill type is set to picture.
        
        Returns:
            str: The name or file path of the picture.
        """
        pass


    @property
    @abc.abstractmethod
    def Visible(self)->bool:
        """Gets whether the shape fill is visible.
        
        When true, the fill is visible and the shape is filled according to the fill settings.
        When false, the fill is not visible and the shape appears transparent.
        
        Returns:
            bool: True if the fill is visible, otherwise False.
        """
        pass


    @Visible.setter
    @abc.abstractmethod
    def Visible(self, value:bool):
        """Sets whether the shape fill is visible.
        
        When set to true, the fill will be visible and the shape will be filled according to the fill settings.
        When set to false, the fill will not be visible and the shape will appear transparent.
        
        Args:
            value (bool): True to make the fill visible, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def GradientDegree(self)->float:
        """Gets the degree of the gradient fill.
        
        This property returns the degree (angle) of the gradient fill in degrees.
        This is applicable for linear gradient fills.
        
        Returns:
            float: The degree of the gradient in degrees.
        """
        pass


    @GradientDegree.setter
    @abc.abstractmethod
    def GradientDegree(self, value:float):
        """Sets the degree of the gradient fill.
        
        This property sets the degree (angle) of the gradient fill in degrees.
        This is applicable for linear gradient fills.
        
        Args:
            value (float): The degree of the gradient in degrees.
        """
        pass


    @property
    @abc.abstractmethod
    def Transparency(self)->float:
        """Gets the overall transparency of the shape fill.
        
        This property returns the transparency value (from 0.0 to 1.0) for the entire fill,
        where 0.0 is completely opaque and 1.0 is completely transparent.
        This is different from TransparencyFrom and TransparencyTo which apply to gradient fills.
        
        Returns:
            float: The transparency value (0.0-1.0).
        """
        pass


    @Transparency.setter
    @abc.abstractmethod
    def Transparency(self, value:float):
        """Sets the overall transparency of the shape fill.
        
        This property sets the transparency value (from 0.0 to 1.0) for the entire fill,
        where 0.0 is completely opaque and 1.0 is completely transparent.
        This is different from TransparencyFrom and TransparencyTo which apply to gradient fills.
        
        Args:
            value (float): The transparency value (0.0-1.0).
        """
        pass


    @property
    @abc.abstractmethod
    def PicStretch(self)->'PicStretch':
        """Gets the picture stretch settings for the shape fill.
        
        This property returns an object that defines how the picture is stretched or scaled
        when used as a fill. This is applicable when the fill type is set to picture.
        
        Returns:
            PicStretch: An object representing the picture stretch settings.
        """
        pass


    @PicStretch.setter
    @abc.abstractmethod
    def PicStretch(self, value:'PicStretch'):
        """Sets the picture stretch settings for the shape fill.
        
        This property sets an object that defines how the picture is stretched or scaled
        when used as a fill. This is applicable when the fill type is set to picture.
        
        Args:
            value (PicStretch): An object representing the picture stretch settings to apply.
        """
        pass


    @property
    @abc.abstractmethod
    def Tile(self)->bool:
        """Gets whether the picture fill is tiled.
        
        When true, the picture is tiled (repeated) to fill the shape.
        When false, the picture is stretched to fill the shape.
        This is applicable when the fill type is set to picture.
        
        Returns:
            bool: True if the picture is tiled, otherwise False.
        """
        pass


    @Tile.setter
    @abc.abstractmethod
    def Tile(self, value:bool):
        """Sets whether the picture fill is tiled.
        
        When set to true, the picture will be tiled (repeated) to fill the shape.
        When set to false, the picture will be stretched to fill the shape.
        This is applicable when the fill type is set to picture.
        
        Args:
            value (bool): True to tile the picture, otherwise False.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def CustomPicture(self, path:str):
        """Sets a custom picture fill using a file path.
        
        This method sets the fill type to picture and loads the picture from the specified file path.
        
        Args:
            path (str): The file path of the picture to use as fill.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def CustomPicture(self, im:Stream, name:str):
        """Sets a custom picture fill using a stream and name.
        
        This method sets the fill type to picture and loads the picture from the specified stream.
        
        Args:
            im (Stream): A stream containing the picture data.
            name (str): A name to assign to the picture.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def CustomTexture(self, path:str):
        """Sets a custom texture fill using a file path.
        
        This method sets the fill type to texture and loads the texture from the specified file path.
        
        Args:
            path (str): The file path of the texture image to use as fill.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def CustomTexture(self, im:Stream, name:str):
        """Sets a custom texture fill using a stream and name.
        
        This method sets the fill type to texture and loads the texture from the specified stream.
        
        Args:
            im (Stream): A stream containing the texture image data.
            name (str): A name to assign to the texture.
        """
        pass


    @abc.abstractmethod
    def Patterned(self, pattern:'GradientPatternType'):
        """Sets a pattern fill for the shape.
        
        This method sets the fill type to pattern and applies the specified pattern type.
        
        Args:
            pattern (GradientPatternType): An enumeration value representing the pattern type to apply.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def PresetGradient(self, grad:GradientPresetType):
        """Sets a preset gradient fill using the default style and variant.
        
        This method sets the fill type to gradient and applies the specified preset gradient type
        with default style and variant settings.
        
        Args:
            grad (GradientPresetType): An enumeration value representing the preset gradient type to apply.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def PresetGradient(self, grad:GradientPresetType, shadStyle:GradientStyleType):
        """Sets a preset gradient fill with a specified style.
        
        This method sets the fill type to gradient and applies the specified preset gradient type
        and gradient style with default variant settings.
        
        Args:
            grad (GradientPresetType): An enumeration value representing the preset gradient type to apply.
            shadStyle (GradientStyleType): An enumeration value representing the gradient style to apply.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def PresetGradient(self, grad:GradientPresetType, shadStyle:GradientStyleType, shadVar:GradientVariantsType):
        """Sets a preset gradient fill with specified style and variant.
        
        This method sets the fill type to gradient and applies the specified preset gradient type,
        gradient style, and gradient variant.
        
        Args:
            grad (GradientPresetType): An enumeration value representing the preset gradient type to apply.
            shadStyle (GradientStyleType): An enumeration value representing the gradient style to apply.
            shadVar (GradientVariantsType): An enumeration value representing the gradient variant to apply.
        """
        pass


    @abc.abstractmethod
    def PresetTextured(self, texture:'GradientTextureType'):
        """Sets a preset texture fill for the shape.
        
        This method sets the fill type to texture and applies the specified preset texture type.
        
        Args:
            texture (GradientTextureType): An enumeration value representing the preset texture type to apply.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def TwoColorGradient(self):
        """Sets a two-color gradient fill using the default style and variant.
        
        This method sets the fill type to a two-color gradient with default style and variant settings.
        Use the ForeColor and BackColor properties to set the two colors of the gradient.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def TwoColorGradient(self, style:GradientStyleType):
        """Sets a two-color gradient fill with a specified style.
        
        This method sets the fill type to a two-color gradient with the specified gradient style
        and default variant settings. Use the ForeColor and BackColor properties to set the two colors.
        
        Args:
            style (GradientStyleType): An enumeration value representing the gradient style to apply.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def TwoColorGradient(self, style:GradientStyleType, variant:GradientVariantsType):
        """Sets a two-color gradient fill with specified style and variant.
        
        This method sets the fill type to a two-color gradient with the specified gradient style
        and variant. Use the ForeColor and BackColor properties to set the two colors.
        
        Args:
            style (GradientStyleType): An enumeration value representing the gradient style to apply.
            variant (GradientVariantsType): An enumeration value representing the gradient variant to apply.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def OneColorGradient(self):
        """Sets a one-color gradient fill using the default style and variant.
        
        This method sets the fill type to a one-color gradient with default style and variant settings.
        Use the ForeColor property to set the color of the gradient.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def OneColorGradient(self, style:GradientStyleType):
        """Sets a one-color gradient fill with a specified style.
        
        This method sets the fill type to a one-color gradient with the specified gradient style
        and default variant settings. Use the ForeColor property to set the color.
        
        Args:
            style (GradientStyleType): An enumeration value representing the gradient style to apply.
        """
        pass


    @dispatch
    @abc.abstractmethod
    def OneColorGradient(self, style:GradientStyleType, variant:GradientVariantsType):
        """Sets a one-color gradient fill with specified style and variant.
        
        This method sets the fill type to a one-color gradient with the specified gradient style
        and variant. Use the ForeColor property to set the color.
        
        Args:
            style (GradientStyleType): An enumeration value representing the gradient style to apply.
            variant (GradientVariantsType): An enumeration value representing the gradient variant to apply.
        """
        pass


    @abc.abstractmethod
    def Solid(self):
        """Sets a solid color fill for the shape.
        
        This method sets the fill type to solid color. Use the BackColor property to set the color.
        """
        pass


