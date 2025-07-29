from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ChartShadow (  XlsObject, IShadow, ICloneParent) :
    """
    Represents the shadow formatting for a chart element, providing properties to customize shadow appearance such as type, color, transparency, size, blur, angle, and distance.
    """
    @property
    def ShadowOuterType(self)->'XLSXChartShadowOuterType':
        """
        Gets or sets the outer shadow type for the chart element.

        Returns:
            XLSXChartShadowOuterType: The outer shadow type.
        """
        GetDllLibXls().ChartShadow_get_ShadowOuterType.argtypes=[c_void_p]
        GetDllLibXls().ChartShadow_get_ShadowOuterType.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartShadow_get_ShadowOuterType, self.Ptr)
        objwraped = XLSXChartShadowOuterType(ret)
        return objwraped

    @ShadowOuterType.setter
    def ShadowOuterType(self, value:'XLSXChartShadowOuterType'):
        GetDllLibXls().ChartShadow_set_ShadowOuterType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ChartShadow_set_ShadowOuterType, self.Ptr, value.value)

    @property
    def ShadowInnerType(self)->'XLSXChartShadowInnerType':
        """
        Gets or sets the inner shadow type for the chart element.

        Returns:
            XLSXChartShadowInnerType: The inner shadow type.
        """
        GetDllLibXls().ChartShadow_get_ShadowInnerType.argtypes=[c_void_p]
        GetDllLibXls().ChartShadow_get_ShadowInnerType.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartShadow_get_ShadowInnerType, self.Ptr)
        objwraped = XLSXChartShadowInnerType(ret)
        return objwraped

    @ShadowInnerType.setter
    def ShadowInnerType(self, value:'XLSXChartShadowInnerType'):
        GetDllLibXls().ChartShadow_set_ShadowInnerType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ChartShadow_set_ShadowInnerType, self.Ptr, value.value)

    @property
    def ShadowPrespectiveType(self)->'XLSXChartPrespectiveType':
        """
        Gets or sets the perspective shadow type for the chart element.

        Returns:
            XLSXChartPrespectiveType: The perspective shadow type.
        """
        GetDllLibXls().ChartShadow_get_ShadowPrespectiveType.argtypes=[c_void_p]
        GetDllLibXls().ChartShadow_get_ShadowPrespectiveType.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartShadow_get_ShadowPrespectiveType, self.Ptr)
        objwraped = XLSXChartPrespectiveType(ret)
        return objwraped

    @ShadowPrespectiveType.setter
    def ShadowPrespectiveType(self, value:'XLSXChartPrespectiveType'):
        GetDllLibXls().ChartShadow_set_ShadowPrespectiveType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ChartShadow_set_ShadowPrespectiveType, self.Ptr, value.value)

    @property
    def HasCustomStyle(self)->bool:
        """
        Gets or sets a value indicating whether the shadow uses a custom style.

        Returns:
            bool: True if the shadow uses a custom style; otherwise, False.
        """
        GetDllLibXls().ChartShadow_get_HasCustomStyle.argtypes=[c_void_p]
        GetDllLibXls().ChartShadow_get_HasCustomStyle.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ChartShadow_get_HasCustomStyle, self.Ptr)
        return ret

    @HasCustomStyle.setter
    def HasCustomStyle(self, value:bool):
        GetDllLibXls().ChartShadow_set_HasCustomStyle.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ChartShadow_set_HasCustomStyle, self.Ptr, value)

    @property
    def Transparency(self)->int:
        """
        Gets or sets the transparency of the shadow.

        Returns:
            int: The transparency value (0-100).
        """
        GetDllLibXls().ChartShadow_get_Transparency.argtypes=[c_void_p]
        GetDllLibXls().ChartShadow_get_Transparency.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartShadow_get_Transparency, self.Ptr)
        return ret

    @Transparency.setter
    def Transparency(self, value:int):
        GetDllLibXls().ChartShadow_set_Transparency.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ChartShadow_set_Transparency, self.Ptr, value)

    @property
    def Size(self)->int:
        """
        Gets or sets the size of the shadow.

        Returns:
            int: The size value.
        """
        GetDllLibXls().ChartShadow_get_Size.argtypes=[c_void_p]
        GetDllLibXls().ChartShadow_get_Size.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartShadow_get_Size, self.Ptr)
        return ret

    @Size.setter
    def Size(self, value:int):
        GetDllLibXls().ChartShadow_set_Size.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ChartShadow_set_Size, self.Ptr, value)

    @property
    def Blur(self)->int:
        """
        Gets or sets the blur value of the shadow.

        Returns:
            int: The blur value.
        """
        GetDllLibXls().ChartShadow_get_Blur.argtypes=[c_void_p]
        GetDllLibXls().ChartShadow_get_Blur.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartShadow_get_Blur, self.Ptr)
        return ret

    @Blur.setter
    def Blur(self, value:int):
        GetDllLibXls().ChartShadow_set_Blur.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ChartShadow_set_Blur, self.Ptr, value)

    @property
    def Angle(self)->int:
        """
        Gets or sets the angle of the shadow.

        Returns:
            int: The angle value in degrees.
        """
        GetDllLibXls().ChartShadow_get_Angle.argtypes=[c_void_p]
        GetDllLibXls().ChartShadow_get_Angle.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartShadow_get_Angle, self.Ptr)
        return ret

    @Angle.setter
    def Angle(self, value:int):
        GetDllLibXls().ChartShadow_set_Angle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ChartShadow_set_Angle, self.Ptr, value)

    @property
    def Distance(self)->int:
        """
        Gets or sets the distance of the shadow from the object.

        Returns:
            int: The distance value.
        """
        GetDllLibXls().ChartShadow_get_Distance.argtypes=[c_void_p]
        GetDllLibXls().ChartShadow_get_Distance.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartShadow_get_Distance, self.Ptr)
        return ret

    @Distance.setter
    def Distance(self, value:int):
        GetDllLibXls().ChartShadow_set_Distance.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ChartShadow_set_Distance, self.Ptr, value)

    @property
    def Color(self)->'Color':
        """
        Gets or sets the color of the shadow.

        Returns:
            Color: The color of the shadow.
        """
        GetDllLibXls().ChartShadow_get_Color.argtypes=[c_void_p]
        GetDllLibXls().ChartShadow_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartShadow_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    @Color.setter
    def Color(self, value:'Color'):
        GetDllLibXls().ChartShadow_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().ChartShadow_set_Color, self.Ptr, value.Ptr)

    @property
    def SoftEdge(self)->int:
        """
        Gets or sets the radius of the soft edge for the shadow.

        Returns:
            int: The radius of the soft edge.
        """
        GetDllLibXls().ChartShadow_get_SoftEdge.argtypes=[c_void_p]
        GetDllLibXls().ChartShadow_get_SoftEdge.restype=c_int
        ret = CallCFunction(GetDllLibXls().ChartShadow_get_SoftEdge, self.Ptr)
        return ret

    @SoftEdge.setter
    def SoftEdge(self, value:int):
        GetDllLibXls().ChartShadow_set_SoftEdge.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ChartShadow_set_SoftEdge, self.Ptr, value)

    @dispatch
    def CustomShadowStyles(self ,iOuter:XLSXChartShadowOuterType,iTransparency:int,iSize:int,iBlur:int,iAngle:int,iDistance:int,iCustomShadowStyle:bool):
        """
        Sets custom shadow styles using outer shadow type and other parameters.

        Args:
            iOuter (XLSXChartShadowOuterType): The outer shadow type.
            iTransparency (int): The transparency value.
            iSize (int): The size value.
            iBlur (int): The blur value.
            iAngle (int): The angle value.
            iDistance (int): The distance value.
            iCustomShadowStyle (bool): Whether to use a custom shadow style.
        """
        enumiOuter:c_int = iOuter.value

        GetDllLibXls().ChartShadow_CustomShadowStyles.argtypes=[c_void_p ,c_int,c_int,c_int,c_int,c_int,c_int,c_bool]
        CallCFunction(GetDllLibXls().ChartShadow_CustomShadowStyles, self.Ptr, enumiOuter,iTransparency,iSize,iBlur,iAngle,iDistance,iCustomShadowStyle)

    @dispatch
    def CustomShadowStyles(self ,iInner:XLSXChartShadowInnerType,iTransparency:int,iBlur:int,iAngle:int,iDistance:int,iCustomShadowStyle:bool):
        """
        Sets custom shadow styles using inner shadow type and other parameters.

        Args:
            iInner (XLSXChartShadowInnerType): The inner shadow type.
            iTransparency (int): The transparency value.
            iBlur (int): The blur value.
            iAngle (int): The angle value.
            iDistance (int): The distance value.
            iCustomShadowStyle (bool): Whether to use a custom shadow style.
        """
        enumiInner:c_int = iInner.value

        GetDllLibXls().ChartShadow_CustomShadowStylesIIIIII.argtypes=[c_void_p ,c_int,c_int,c_int,c_int,c_int,c_bool]
        CallCFunction(GetDllLibXls().ChartShadow_CustomShadowStylesIIIIII, self.Ptr, enumiInner,iTransparency,iBlur,iAngle,iDistance,iCustomShadowStyle)

    @dispatch
    def CustomShadowStyles(self ,iPerspective:XLSXChartPrespectiveType,iTransparency:int,iSize:int,iBlur:int,iAngle:int,iDistance:int,iCustomShadowStyle:bool):
        """
        Sets custom shadow styles using perspective shadow type and other parameters.

        Args:
            iPerspective (XLSXChartPrespectiveType): The perspective shadow type.
            iTransparency (int): The transparency value.
            iSize (int): The size value.
            iBlur (int): The blur value.
            iAngle (int): The angle value.
            iDistance (int): The distance value.
            iCustomShadowStyle (bool): Whether to use a custom shadow style.
        """
        enumiPerspective:c_int = iPerspective.value

        GetDllLibXls().ChartShadow_CustomShadowStylesIIIIIII.argtypes=[c_void_p ,c_int,c_int,c_int,c_int,c_int,c_int,c_bool]
        CallCFunction(GetDllLibXls().ChartShadow_CustomShadowStylesIIIIIII, self.Ptr, enumiPerspective,iTransparency,iSize,iBlur,iAngle,iDistance,iCustomShadowStyle)

    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """
        Creates a copy of the current ChartShadow instance.

        Args:
            parent (SpireObject): The parent object for the cloned shadow.
        Returns:
            SpireObject: The cloned ChartShadow object.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().ChartShadow_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().ChartShadow_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().ChartShadow_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


