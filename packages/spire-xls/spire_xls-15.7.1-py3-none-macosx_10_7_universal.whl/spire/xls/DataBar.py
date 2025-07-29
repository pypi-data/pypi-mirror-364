from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class DataBar (SpireObject) :
    """Represents a data bar conditional formatting rule in an Excel worksheet.
    
    This class provides properties and methods for configuring data bar conditional formatting,
    which displays a colored bar in a cell where the length of the bar represents the value
    in the cell relative to other values in the selected range. It allows for customizing
    appearance settings such as colors, borders, axis position, and fill types.
    """
    @property

    def MinPoint(self)->'ConditionValue':
        """
        The shortest bar is evaluated for a data bar conditional format.

        """
        GetDllLibXls().DataBar_get_MinPoint.argtypes=[c_void_p]
        GetDllLibXls().DataBar_get_MinPoint.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().DataBar_get_MinPoint, self.Ptr)
        ret = None if intPtr==None else ConditionValue(intPtr)
        return ret


    @property

    def MaxPoint(self)->'ConditionValue':
        """
        The longest bar is evaluated for a data bar conditional format.

        """
        GetDllLibXls().DataBar_get_MaxPoint.argtypes=[c_void_p]
        GetDllLibXls().DataBar_get_MaxPoint.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().DataBar_get_MaxPoint, self.Ptr)
        ret = None if intPtr==None else ConditionValue(intPtr)
        return ret


    @property

    def BarColor(self)->'Color':
        """
        Gets or sets the color of the bar in a data bar condition format.

        """
        GetDllLibXls().DataBar_get_BarColor.argtypes=[c_void_p]
        GetDllLibXls().DataBar_get_BarColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().DataBar_get_BarColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @BarColor.setter
    def BarColor(self, value:'Color'):
        GetDllLibXls().DataBar_set_BarColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().DataBar_set_BarColor, self.Ptr, value.Ptr)

    @property
    def PercentMax(self)->int:
        """
        Gets or sets a value that specifies the length of the longest data bar as a percentage of cell width.

        """
        GetDllLibXls().DataBar_get_PercentMax.argtypes=[c_void_p]
        GetDllLibXls().DataBar_get_PercentMax.restype=c_int
        ret = CallCFunction(GetDllLibXls().DataBar_get_PercentMax, self.Ptr)
        return ret

    @PercentMax.setter
    def PercentMax(self, value:int):
        GetDllLibXls().DataBar_set_PercentMax.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().DataBar_set_PercentMax, self.Ptr, value)

    @property
    def PercentMin(self)->int:
        """
        Gets or sets a value that specifies the length of the shortest data bar as a percentage of cell width.

        """
        GetDllLibXls().DataBar_get_PercentMin.argtypes=[c_void_p]
        GetDllLibXls().DataBar_get_PercentMin.restype=c_int
        ret = CallCFunction(GetDllLibXls().DataBar_get_PercentMin, self.Ptr)
        return ret

    @PercentMin.setter
    def PercentMin(self, value:int):
        GetDllLibXls().DataBar_set_PercentMin.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().DataBar_set_PercentMin, self.Ptr, value)

    @property
    def ShowValue(self)->bool:
        """
        Gets or sets a Boolean value that specifies if the value in the cell is displayed.

        """
        GetDllLibXls().DataBar_get_ShowValue.argtypes=[c_void_p]
        GetDllLibXls().DataBar_get_ShowValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().DataBar_get_ShowValue, self.Ptr)
        return ret

    @ShowValue.setter
    def ShowValue(self, value:bool):
        GetDllLibXls().DataBar_set_ShowValue.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().DataBar_set_ShowValue, self.Ptr, value)

    @property

    def AxisColor(self)->'Color':
        """
        Gets the color of the axis for cells with conditional formatting as data bars.

        """
        GetDllLibXls().DataBar_get_AxisColor.argtypes=[c_void_p]
        GetDllLibXls().DataBar_get_AxisColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().DataBar_get_AxisColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @AxisColor.setter
    def AxisColor(self, value:'Color'):
        GetDllLibXls().DataBar_set_AxisColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().DataBar_set_AxisColor, self.Ptr, value.Ptr)

    @property

    def AxisPosition(self)->'DataBarAxisPosition':
        """
        Gets or sets the position of the axis of the data bars specified by a conditional formatting rule.

        """
        GetDllLibXls().DataBar_get_AxisPosition.argtypes=[c_void_p]
        GetDllLibXls().DataBar_get_AxisPosition.restype=c_int
        ret = CallCFunction(GetDllLibXls().DataBar_get_AxisPosition, self.Ptr)
        objwraped = DataBarAxisPosition(ret)
        return objwraped

    @AxisPosition.setter
    def AxisPosition(self, value:'DataBarAxisPosition'):
        GetDllLibXls().DataBar_set_AxisPosition.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().DataBar_set_AxisPosition, self.Ptr, value.value)

    @property

    def BarBorder(self)->'DataBarBorder':
        """
        Gets an object that specifies the border of a data bar.

        """
        GetDllLibXls().DataBar_get_BarBorder.argtypes=[c_void_p]
        GetDllLibXls().DataBar_get_BarBorder.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().DataBar_get_BarBorder, self.Ptr)
        ret = None if intPtr==None else DataBarBorder(intPtr)
        return ret


    @property

    def BarFillType(self)->'DataBarFillType':
        """Gets or sets the fill type for the data bar.
        
        This property determines how the data bar is filled with color,
        such as solid fill or gradient fill.
        
        Returns:
            DataBarFillType: An enumeration value representing the fill type of the data bar.
        """
        GetDllLibXls().DataBar_get_BarFillType.argtypes=[c_void_p]
        GetDllLibXls().DataBar_get_BarFillType.restype=c_int
        ret = CallCFunction(GetDllLibXls().DataBar_get_BarFillType, self.Ptr)
        objwraped = DataBarFillType(ret)
        return objwraped

    @BarFillType.setter
    def BarFillType(self, value:'DataBarFillType'):
        """Sets the fill type for the data bar.
        
        Args:
            value (DataBarFillType): An enumeration value representing the fill type to set.
        """
        GetDllLibXls().DataBar_set_BarFillType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().DataBar_set_BarFillType, self.Ptr, value.value)

    @property

    def Direction(self)->'TextDirectionType':
        """
        Gets or sets the direction the databar is displayed.

        """
        GetDllLibXls().DataBar_get_Direction.argtypes=[c_void_p]
        GetDllLibXls().DataBar_get_Direction.restype=c_int
        ret = CallCFunction(GetDllLibXls().DataBar_get_Direction, self.Ptr)
        objwraped = TextDirectionType(ret)
        return objwraped

    @Direction.setter
    def Direction(self, value:'TextDirectionType'):
        GetDllLibXls().DataBar_set_Direction.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().DataBar_set_Direction, self.Ptr, value.value)

    @property

    def NegativeBarFormat(self)->'NegativeBarFormat':
        """
        Gets the NegativeBarFormat object associated with a data bar conditional formatting rule.

        """
        GetDllLibXls().DataBar_get_NegativeBarFormat.argtypes=[c_void_p]
        GetDllLibXls().DataBar_get_NegativeBarFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().DataBar_get_NegativeBarFormat, self.Ptr)
        ret = None if intPtr==None else NegativeBarFormat(intPtr)
        return ret


