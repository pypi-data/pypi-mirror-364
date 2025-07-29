from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsGradientStop (SpireObject) :
    """Represents a gradient stop in an Excel gradient fill.
    
    This class provides properties for manipulating individual color stops within a gradient,
    including position, color, transparency, tint, and shade. Each gradient stop defines a color
    at a specific position in the gradient.
    """
    @property

    def OColor(self)->'OColor':
        """Gets the Office color object for the gradient stop.
        
        Returns:
            OColor: An Office color object representing the color of the gradient stop.
        """
        GetDllLibXls().XlsGradientStop_get_OColor.argtypes=[c_void_p]
        GetDllLibXls().XlsGradientStop_get_OColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsGradientStop_get_OColor, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property
    def Position(self)->int:
        """Gets or sets the position of the gradient stop.
        
        The position is a value between 0 and 100, representing the percentage position
        within the gradient.
        
        Returns:
            int: The position of the gradient stop (0-100).
        """
        GetDllLibXls().XlsGradientStop_get_Position.argtypes=[c_void_p]
        GetDllLibXls().XlsGradientStop_get_Position.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsGradientStop_get_Position, self.Ptr)
        return ret

    @Position.setter
    def Position(self, value:int):
        """Sets the position of the gradient stop.
        
        Args:
            value (int): The position of the gradient stop (0-100).
        """
        GetDllLibXls().XlsGradientStop_set_Position.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsGradientStop_set_Position, self.Ptr, value)

    @property
    def Transparency(self)->int:
        """Gets or sets the transparency of the gradient stop.
        
        The transparency is a value between 0 and 100, where 0 is fully opaque
        and 100 is fully transparent.
        
        Returns:
            int: The transparency value (0-100).
        """
        GetDllLibXls().XlsGradientStop_get_Transparency.argtypes=[c_void_p]
        GetDllLibXls().XlsGradientStop_get_Transparency.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsGradientStop_get_Transparency, self.Ptr)
        return ret

    @Transparency.setter
    def Transparency(self, value:int):
        """Sets the transparency of the gradient stop.
        
        Args:
            value (int): The transparency value (0-100).
        """
        GetDllLibXls().XlsGradientStop_set_Transparency.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsGradientStop_set_Transparency, self.Ptr, value)

    @property
    def Tint(self)->int:
        """Gets or sets the tint of the gradient stop color.
        
        Tint is a positive value that lightens the color. The value represents
        the percentage of white added to the color.
        
        Returns:
            int: The tint value.
        """
        GetDllLibXls().XlsGradientStop_get_Tint.argtypes=[c_void_p]
        GetDllLibXls().XlsGradientStop_get_Tint.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsGradientStop_get_Tint, self.Ptr)
        return ret

    @Tint.setter
    def Tint(self, value:int):
        """Sets the tint of the gradient stop color.
        
        Args:
            value (int): The tint value.
        """
        GetDllLibXls().XlsGradientStop_set_Tint.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsGradientStop_set_Tint, self.Ptr, value)

    @property
    def Shade(self)->int:
        """Gets or sets the shade of the gradient stop color.
        
        Shade is a positive value that darkens the color. The value represents
        the percentage of black added to the color.
        
        Returns:
            int: The shade value.
        """
        GetDllLibXls().XlsGradientStop_get_Shade.argtypes=[c_void_p]
        GetDllLibXls().XlsGradientStop_get_Shade.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsGradientStop_get_Shade, self.Ptr)
        return ret

    @Shade.setter
    def Shade(self, value:int):
        """Sets the shade of the gradient stop color.
        
        Args:
            value (int): The shade value.
        """
        GetDllLibXls().XlsGradientStop_set_Shade.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsGradientStop_set_Shade, self.Ptr, value)

