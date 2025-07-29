from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsChartWallOrFloor (  XlsObject, IChartWallOrFloor, IChartFillBorder) :
    """

    """
    @property

    def Border(self)->'ChartBorder':
        """
        Gets the border of the chart wall or floor.

        Returns:
            ChartBorder: The border of the chart wall or floor.
        """
        GetDllLibXls().XlsChartWallOrFloor_get_Border.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_Border.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_Border, self.Ptr)
        ret = None if intPtr==None else ChartBorder(intPtr)
        return ret


    @property
    def HasInterior(self)->bool:
        """
        Gets whether the chart wall or floor has an interior.

        Returns:
            bool: True if the chart wall or floor has an interior; otherwise, False.
        """
        GetDllLibXls().XlsChartWallOrFloor_get_HasInterior.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_HasInterior.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_HasInterior, self.Ptr)
        return ret

    @property
    def HasLineProperties(self)->bool:
        """
        Gets whether the chart wall or floor has line properties.

        Returns:
            bool: True if the chart wall or floor has line properties; otherwise, False.
        """
        GetDllLibXls().XlsChartWallOrFloor_get_HasLineProperties.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_HasLineProperties.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_HasLineProperties, self.Ptr)
        return ret

    @property
    def HasFormat3D(self)->bool:
        """
        Gets whether the chart wall or floor has 3D formatting.

        Returns:
            bool: True if the chart wall or floor has 3D formatting; otherwise, False.
        """
        GetDllLibXls().XlsChartWallOrFloor_get_HasFormat3D.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_HasFormat3D.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_HasFormat3D, self.Ptr)
        return ret

    @property
    def HasShadow(self)->bool:
        """
        Gets whether the chart wall or floor has a shadow.

        Returns:
            bool: True if the chart wall or floor has a shadow; otherwise, False.
        """
        GetDllLibXls().XlsChartWallOrFloor_get_HasShadow.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_HasShadow.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_HasShadow, self.Ptr)
        return ret

    @property

    def LineProperties(self)->'ChartBorder':
        """
        Gets the line properties of the chart wall or floor.

        Returns:
            ChartBorder: The line properties of the chart wall or floor.
        """
        GetDllLibXls().XlsChartWallOrFloor_get_LineProperties.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_LineProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_LineProperties, self.Ptr)
        ret = None if intPtr==None else ChartBorder(intPtr)
        return ret


    @property

    def Interior(self)->'IChartInterior':
        """
        Gets the interior of the chart wall or floor.

        Returns:
            IChartInterior: The interior of the chart wall or floor.
        """
        GetDllLibXls().XlsChartWallOrFloor_get_Interior.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_Interior.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_Interior, self.Ptr)
        ret = None if intPtr==None else IChartInterior(intPtr)
        return ret


    @property

    def Fill(self)->'IShapeFill':
        """
        Gets the fill of the chart wall or floor.

        Returns:
            IShapeFill: The fill of the chart wall or floor.
        """
        GetDllLibXls().XlsChartWallOrFloor_get_Fill.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_Fill, self.Ptr)
        ret = None if intPtr==None else XlsShapeFill(intPtr)
        return ret


    @property

    def Format3D(self)->'Format3D':
        """
        Gets the 3D format of the chart wall or floor.

        Returns:
            Format3D: The 3D format of the chart wall or floor.
        """
        GetDllLibXls().XlsChartWallOrFloor_get_Format3D.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_Format3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_Format3D, self.Ptr)
        ret = None if intPtr==None else Format3D(intPtr)
        return ret


    @property

    def Shadow(self)->'ChartShadow':
        """
        Gets the shadow of the chart wall or floor.

        Returns:
            ChartShadow: The shadow of the chart wall or floor.
        """
        GetDllLibXls().XlsChartWallOrFloor_get_Shadow.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_Shadow.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_Shadow, self.Ptr)
        ret = None if intPtr==None else ChartShadow(intPtr)
        return ret


    def Delete(self):
        """
        Deletes the chart wall or floor.
        """
        GetDllLibXls().XlsChartWallOrFloor_Delete.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsChartWallOrFloor_Delete, self.Ptr)


    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """
        Clones the chart wall or floor.

        Args:
            parent (SpireObject): The parent object.

        Returns:
            SpireObject: The cloned chart wall or floor.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsChartWallOrFloor_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    def SetToDefault(self):
        """
        Sets the chart wall or floor to its default state.
        """
        GetDllLibXls().XlsChartWallOrFloor_SetToDefault.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsChartWallOrFloor_SetToDefault, self.Ptr)

    @property

    def ForeGroundColor(self)->'Color':
        """
        Represents foreground color.

        """
        GetDllLibXls().XlsChartWallOrFloor_get_ForeGroundColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_ForeGroundColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_ForeGroundColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @ForeGroundColor.setter
    def ForeGroundColor(self, value:'Color'):
        GetDllLibXls().XlsChartWallOrFloor_set_ForeGroundColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChartWallOrFloor_set_ForeGroundColor, self.Ptr, value.Ptr)

    @property

    def ForeGroundKnownColor(self)->'ExcelColors':
        """
        Represents foreground color.

        """
        GetDllLibXls().XlsChartWallOrFloor_get_ForeGroundKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_ForeGroundKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_ForeGroundKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @ForeGroundKnownColor.setter
    def ForeGroundKnownColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsChartWallOrFloor_set_ForeGroundKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartWallOrFloor_set_ForeGroundKnownColor, self.Ptr, value.value)

    @property

    def ForeGroundColorObject(self)->'OColor':
        """
        Represents foreground color.

        """
        GetDllLibXls().XlsChartWallOrFloor_get_ForeGroundColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_ForeGroundColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_ForeGroundColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def BackGroundColor(self)->'Color':
        """
        Gets the background color of the chart wall or floor.

        Returns:
            Color: The background color of the chart wall or floor.
        """
        GetDllLibXls().XlsChartWallOrFloor_get_BackGroundColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_BackGroundColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_BackGroundColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @BackGroundColor.setter
    def BackGroundColor(self, value:'Color'):
        GetDllLibXls().XlsChartWallOrFloor_set_BackGroundColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsChartWallOrFloor_set_BackGroundColor, self.Ptr, value.Ptr)

    @property

    def BackGroundKnownColor(self)->'ExcelColors':
        """
        Gets the known background color of the chart wall or floor.

        Returns:
        """
        GetDllLibXls().XlsChartWallOrFloor_get_BackGroundKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_BackGroundKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_BackGroundKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @BackGroundKnownColor.setter
    def BackGroundKnownColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsChartWallOrFloor_set_BackGroundKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartWallOrFloor_set_BackGroundKnownColor, self.Ptr, value.value)

    @property

    def BackGroundColorObject(self)->'OColor':
        """
        Represents background color.

        """
        GetDllLibXls().XlsChartWallOrFloor_get_BackGroundColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_BackGroundColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_BackGroundColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def Pattern(self)->'ExcelPatternType':
        """
        Represents pattern.

        """
        GetDllLibXls().XlsChartWallOrFloor_get_Pattern.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_Pattern.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_Pattern, self.Ptr)
        objwraped = ExcelPatternType(ret)
        return objwraped

    @Pattern.setter
    def Pattern(self, value:'ExcelPatternType'):
        GetDllLibXls().XlsChartWallOrFloor_set_Pattern.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsChartWallOrFloor_set_Pattern, self.Ptr, value.value)

    @property
    def IsAutomaticFormat(self)->bool:
        """
        Represents if use automatic format.

        """
        GetDllLibXls().XlsChartWallOrFloor_get_IsAutomaticFormat.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_IsAutomaticFormat.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_IsAutomaticFormat, self.Ptr)
        return ret

    @IsAutomaticFormat.setter
    def IsAutomaticFormat(self, value:bool):
        GetDllLibXls().XlsChartWallOrFloor_set_IsAutomaticFormat.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartWallOrFloor_set_IsAutomaticFormat, self.Ptr, value)

    @property
    def Visible(self)->bool:
        """
        Represents visible.

        """
        GetDllLibXls().XlsChartWallOrFloor_get_Visible.argtypes=[c_void_p]
        GetDllLibXls().XlsChartWallOrFloor_get_Visible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsChartWallOrFloor_get_Visible, self.Ptr)
        return ret

    @Visible.setter
    def Visible(self, value:bool):
        GetDllLibXls().XlsChartWallOrFloor_set_Visible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsChartWallOrFloor_set_Visible, self.Ptr, value)

