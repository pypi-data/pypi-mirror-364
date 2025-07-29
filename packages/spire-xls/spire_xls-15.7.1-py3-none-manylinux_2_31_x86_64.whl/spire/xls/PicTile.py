from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class PicTile (SpireObject) :
    """Represents picture tiling settings for a fill picture in Excel.
    
    This class encapsulates the properties that control how a picture is tiled
    when used as a fill for shapes, cells, or other Excel objects. It allows for configuring
    the picture's offset and scaling when tiled across an area.
    """
    @property
    def OffsetX(self)->float:
        """Gets or sets the horizontal offset for the tiled picture.
        
        This value represents the horizontal displacement of the picture from its default position
        when tiled. A value of 0.0 indicates no horizontal offset.
        
        Returns:
            float: The horizontal offset as a decimal value.
        """
        GetDllLibXls().PicTile_get_OffsetX.argtypes=[c_void_p]
        GetDllLibXls().PicTile_get_OffsetX.restype=c_double
        ret = CallCFunction(GetDllLibXls().PicTile_get_OffsetX, self.Ptr)
        return ret

    @OffsetX.setter
    def OffsetX(self, value:float):
        GetDllLibXls().PicTile_set_OffsetX.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().PicTile_set_OffsetX, self.Ptr, value)

    @property
    def OffsetY(self)->float:
        """Gets or sets the vertical offset for the tiled picture.
        
        This value represents the vertical displacement of the picture from its default position
        when tiled. A value of 0.0 indicates no vertical offset.
        
        Returns:
            float: The vertical offset as a decimal value.
        """
        GetDllLibXls().PicTile_get_OffsetY.argtypes=[c_void_p]
        GetDllLibXls().PicTile_get_OffsetY.restype=c_double
        ret = CallCFunction(GetDllLibXls().PicTile_get_OffsetY, self.Ptr)
        return ret

    @OffsetY.setter
    def OffsetY(self, value:float):
        GetDllLibXls().PicTile_set_OffsetY.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().PicTile_set_OffsetY, self.Ptr, value)

    @property
    def ScaleX(self)->float:
        """Gets or sets the horizontal scale factor for the tiled picture.
        
        This value determines how the picture is stretched or compressed horizontally when tiled.
        A value of 1.0 represents 100% (original size). Values greater than 1.0 enlarge
        the picture, while values less than 1.0 reduce it.
        
        Returns:
            float: The horizontal scale factor as a decimal value.
        """
        GetDllLibXls().PicTile_get_ScaleX.argtypes=[c_void_p]
        GetDllLibXls().PicTile_get_ScaleX.restype=c_double
        ret = CallCFunction(GetDllLibXls().PicTile_get_ScaleX, self.Ptr)
        return ret

    @ScaleX.setter
    def ScaleX(self, value:float):
        GetDllLibXls().PicTile_set_ScaleX.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().PicTile_set_ScaleX, self.Ptr, value)

    @property
    def ScaleY(self)->float:
        """Gets or sets the vertical scale factor for the tiled picture.
        
        This value determines how the picture is stretched or compressed vertically when tiled.
        A value of 1.0 represents 100% (original size). Values greater than 1.0 enlarge
        the picture, while values less than 1.0 reduce it.
        
        Returns:
            float: The vertical scale factor as a decimal value.
        """
        GetDllLibXls().PicTile_get_ScaleY.argtypes=[c_void_p]
        GetDllLibXls().PicTile_get_ScaleY.restype=c_double
        ret = CallCFunction(GetDllLibXls().PicTile_get_ScaleY, self.Ptr)
        return ret

    @ScaleY.setter
    def ScaleY(self, value:float):
        GetDllLibXls().PicTile_set_ScaleY.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().PicTile_set_ScaleY, self.Ptr, value)

