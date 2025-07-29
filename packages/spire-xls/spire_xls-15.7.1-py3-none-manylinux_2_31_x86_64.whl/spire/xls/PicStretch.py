from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class PicStretch (SpireObject) :
    """Represents picture stretching settings for a fill picture in Excel.
    
    This class encapsulates the properties that control how a picture is stretched or positioned
    when used as a fill for shapes, cells, or other Excel objects. It allows for configuring
    the picture's positioning, scaling, and display type.
    """
    @property

    def Type(self)->'FillPictureType':
        """Gets or sets the type of picture fill.
        
        Determines how the picture is displayed within the filled area, such as
        stretched, tiled, or positioned at specific locations.
        
        Returns:
            FillPictureType: An enumeration value representing the picture fill type.
        """
        GetDllLibXls().PicStretch_get_Type.argtypes=[c_void_p]
        GetDllLibXls().PicStretch_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibXls().PicStretch_get_Type, self.Ptr)
        objwraped = FillPictureType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'FillPictureType'):
        GetDllLibXls().PicStretch_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().PicStretch_set_Type, self.Ptr, value.value)

    @property
    def Scale(self)->float:
        """Gets or sets the scale factor for the picture.
        
        A value of 1.0 represents 100% (original size). Values greater than 1.0 enlarge
        the picture, while values less than 1.0 reduce it.
        
        Returns:
            float: The scale factor as a decimal value.
        """
        GetDllLibXls().PicStretch_get_Scale.argtypes=[c_void_p]
        GetDllLibXls().PicStretch_get_Scale.restype=c_double
        ret = CallCFunction(GetDllLibXls().PicStretch_get_Scale, self.Ptr)
        return ret

    @Scale.setter
    def Scale(self, value:float):
        GetDllLibXls().PicStretch_set_Scale.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().PicStretch_set_Scale, self.Ptr, value)

    @property
    def Left(self)->float:
        """Gets or sets the left offset of the picture as a percentage of the fill area.
        
        A value of 0.0 aligns the left edge of the picture with the left edge of the fill area.
        Values are between 0.0 and 1.0, where 1.0 represents 100% of the fill area width.
        
        Returns:
            float: The left offset as a decimal value.
        """
        GetDllLibXls().PicStretch_get_Left.argtypes=[c_void_p]
        GetDllLibXls().PicStretch_get_Left.restype=c_double
        ret = CallCFunction(GetDllLibXls().PicStretch_get_Left, self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibXls().PicStretch_set_Left.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().PicStretch_set_Left, self.Ptr, value)

    @property
    def Top(self)->float:
        """Gets or sets the top offset of the picture as a percentage of the fill area.
        
        A value of 0.0 aligns the top edge of the picture with the top edge of the fill area.
        Values are between 0.0 and 1.0, where 1.0 represents 100% of the fill area height.
        
        Returns:
            float: The top offset as a decimal value.
        """
        GetDllLibXls().PicStretch_get_Top.argtypes=[c_void_p]
        GetDllLibXls().PicStretch_get_Top.restype=c_double
        ret = CallCFunction(GetDllLibXls().PicStretch_get_Top, self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibXls().PicStretch_set_Top.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().PicStretch_set_Top, self.Ptr, value)

    @property
    def Bottom(self)->float:
        """Gets or sets the bottom offset of the picture as a percentage of the fill area.
        
        A value of 1.0 aligns the bottom edge of the picture with the bottom edge of the fill area.
        Values are between 0.0 and 1.0, where 1.0 represents 100% of the fill area height.
        
        Returns:
            float: The bottom offset as a decimal value.
        """
        GetDllLibXls().PicStretch_get_Bottom.argtypes=[c_void_p]
        GetDllLibXls().PicStretch_get_Bottom.restype=c_double
        ret = CallCFunction(GetDllLibXls().PicStretch_get_Bottom, self.Ptr)
        return ret

    @Bottom.setter
    def Bottom(self, value:float):
        GetDllLibXls().PicStretch_set_Bottom.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().PicStretch_set_Bottom, self.Ptr, value)

    @property
    def Right(self)->float:
        """Gets or sets the right offset of the picture as a percentage of the fill area.
        
        A value of 1.0 aligns the right edge of the picture with the right edge of the fill area.
        Values are between 0.0 and 1.0, where 1.0 represents 100% of the fill area width.
        
        Returns:
            float: The right offset as a decimal value.
        """
        GetDllLibXls().PicStretch_get_Right.argtypes=[c_void_p]
        GetDllLibXls().PicStretch_get_Right.restype=c_double
        ret = CallCFunction(GetDllLibXls().PicStretch_get_Right, self.Ptr)
        return ret

    @Right.setter
    def Right(self, value:float):
        GetDllLibXls().PicStretch_set_Right.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().PicStretch_set_Right, self.Ptr, value)

