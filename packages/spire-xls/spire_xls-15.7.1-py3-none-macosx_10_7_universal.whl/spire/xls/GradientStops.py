from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class GradientStops (SpireObject) :
    """Represents a collection of gradient stops in Excel.
    
    This class provides properties and methods for managing gradient stops,
    which define the color transitions in a gradient fill. It allows for
    manipulating gradient properties such as angle, type, and color stops.
    """
    @property
    def Angle(self)->int:
        """Gets or sets the angle of the gradient in degrees.
        
        Returns:
            int: The angle of the gradient in degrees.
        """
        GetDllLibXls().GradientStops_get_Angle.argtypes=[c_void_p]
        GetDllLibXls().GradientStops_get_Angle.restype=c_int
        ret = CallCFunction(GetDllLibXls().GradientStops_get_Angle, self.Ptr)
        return ret

    @Angle.setter
    def Angle(self, value:int):
        """Sets the angle of the gradient in degrees.
        
        Args:
            value (int): The angle of the gradient in degrees.
        """
        GetDllLibXls().GradientStops_set_Angle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().GradientStops_set_Angle, self.Ptr, value)

    @property

    def GradientType(self)->'GradientType':
        """Gets or sets the type of the gradient.
        
        Returns:
            GradientType: An enumeration value representing the gradient type.
        """
        GetDllLibXls().GradientStops_get_GradientType.argtypes=[c_void_p]
        GetDllLibXls().GradientStops_get_GradientType.restype=c_int
        ret = CallCFunction(GetDllLibXls().GradientStops_get_GradientType, self.Ptr)
        objwraped = GradientType(ret)
        return objwraped

    @GradientType.setter
    def GradientType(self, value:'GradientType'):
        """Sets the type of the gradient.
        
        Args:
            value (GradientType): An enumeration value representing the gradient type.
        """
        GetDllLibXls().GradientStops_set_GradientType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().GradientStops_set_GradientType, self.Ptr, value.value)

    @property

    def FillToRect(self)->'Rectangle':
        """Gets or sets the rectangle that defines the end point of the gradient.
        
        Returns:
            Rectangle: A Rectangle object representing the end point of the gradient.
        """
        GetDllLibXls().GradientStops_get_FillToRect.argtypes=[c_void_p]
        GetDllLibXls().GradientStops_get_FillToRect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().GradientStops_get_FillToRect, self.Ptr)
        ret = None if intPtr==None else Rectangle(intPtr)
        return ret


    @FillToRect.setter
    def FillToRect(self, value:'Rectangle'):
        """Sets the rectangle that defines the end point of the gradient.
        
        Args:
            value (Rectangle): A Rectangle object representing the end point of the gradient.
        """
        GetDllLibXls().GradientStops_set_FillToRect.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().GradientStops_set_FillToRect, self.Ptr, value.Ptr)

    @property
    def IsDoubled(self)->bool:
        """Gets a value indicating whether the gradient stops are doubled.
        
        Returns:
            bool: True if the gradient stops are doubled; otherwise, False.
        """
        GetDllLibXls().GradientStops_get_IsDoubled.argtypes=[c_void_p]
        GetDllLibXls().GradientStops_get_IsDoubled.restype=c_bool
        ret = CallCFunction(GetDllLibXls().GradientStops_get_IsDoubled, self.Ptr)
        return ret

    def DoubleGradientStops(self):
        """Doubles the gradient stops.
        
        This method creates a mirror image of the gradient stops, effectively
        doubling the number of color transitions in the gradient.
        """
        GetDllLibXls().GradientStops_DoubleGradientStops.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().GradientStops_DoubleGradientStops, self.Ptr)

    def InvertGradientStops(self):
        """Inverts the gradient stops.
        
        This method reverses the order of the gradient stops, effectively
        inverting the color transitions in the gradient.
        """
        GetDllLibXls().GradientStops_InvertGradientStops.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().GradientStops_InvertGradientStops, self.Ptr)


    def ShrinkGradientStops(self)->'GradientStops':
        """Shrinks the gradient stops.
        
        This method reduces the number of gradient stops by combining
        similar adjacent stops.
        
        Returns:
            GradientStops: A new GradientStops object with reduced stops.
        """
        GetDllLibXls().GradientStops_ShrinkGradientStops.argtypes=[c_void_p]
        GetDllLibXls().GradientStops_ShrinkGradientStops.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().GradientStops_ShrinkGradientStops, self.Ptr)
        ret = None if intPtr==None else GradientStops(intPtr)
        return ret



    def Clone(self)->'GradientStops':
        """Creates a clone of this GradientStops object.
        
        Returns:
            GradientStops: A new GradientStops object that is a copy of this instance.
        """
        GetDllLibXls().GradientStops_Clone.argtypes=[c_void_p]
        GetDllLibXls().GradientStops_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().GradientStops_Clone, self.Ptr)
        ret = None if intPtr==None else GradientStops(intPtr)
        return ret


    @dispatch

    def Add(self ,stop:XlsGradientStop):
        """Adds a gradient stop to the collection.
        
        Args:
            stop (XlsGradientStop): The gradient stop to add.
        """
        intPtrstop:c_void_p = stop.Ptr

        GetDllLibXls().GradientStops_Add.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().GradientStops_Add, self.Ptr, intPtrstop)

    @dispatch

    def Add(self ,color:Color,position:int,transparency:int,tint:int,shade:int)->XlsGradientStop:
        """Adds a gradient stop with specified properties to the collection.
        
        Args:
            color (Color): The color of the gradient stop.
            position (int): The position of the gradient stop.
            transparency (int): The transparency level of the gradient stop.
            tint (int): The tint value of the gradient stop.
            shade (int): The shade value of the gradient stop.
            
        Returns:
            XlsGradientStop: The newly created gradient stop.
        """
        intPtrcolor:c_void_p = color.Ptr

        GetDllLibXls().GradientStops_AddCPTTS.argtypes=[c_void_p ,c_void_p,c_int,c_int,c_int,c_int]
        GetDllLibXls().GradientStops_AddCPTTS.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().GradientStops_AddCPTTS, self.Ptr, intPtrcolor,position,transparency,tint,shade)
        ret = None if intPtr==None else XlsGradientStop(intPtr)
        return ret



    def Serialize(self ,stream:'Stream'):
        """Serializes the gradient stops to a stream.
        
        Args:
            stream (Stream): The stream to which the gradient stops will be serialized.
        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibXls().GradientStops_Serialize.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().GradientStops_Serialize, self.Ptr, intPtrstream)

