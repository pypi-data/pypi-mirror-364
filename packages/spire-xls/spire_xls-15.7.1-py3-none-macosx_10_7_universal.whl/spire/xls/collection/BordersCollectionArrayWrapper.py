from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class BordersCollectionArrayWrapper (  IBorders) :
    """
    Implements the IBorders interface for manipulating Excel cell border collections.
    """
    @property
    def KnownColor(self)->'ExcelColors':
        """
        Gets the known color of the border.

        Returns:
            ExcelColors: The known color enum value of the border.
        """
        GetDllLibXls().BordersCollectionArrayWrapper_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().BordersCollectionArrayWrapper_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().BordersCollectionArrayWrapper_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        """
        Sets the known color of the border.

        Args:
            value (ExcelColors): The color enum value to set.
        """
        GetDllLibXls().BordersCollectionArrayWrapper_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().BordersCollectionArrayWrapper_set_KnownColor, self.Ptr, value.value)

    @property
    def Color(self)->'Color':
        """
        Gets the color of the border.

        Returns:
            Color: The color object of the border.
        """
        GetDllLibXls().BordersCollectionArrayWrapper_get_Color.argtypes=[c_void_p]
        GetDllLibXls().BordersCollectionArrayWrapper_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().BordersCollectionArrayWrapper_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    @Color.setter
    def Color(self, value:'Color'):
        """
        Sets the color of the border.

        Args:
            value (Color): The color object to set.
        """
        GetDllLibXls().BordersCollectionArrayWrapper_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().BordersCollectionArrayWrapper_set_Color, self.Ptr, value.Ptr)

    def get_Item(self ,Index:'BordersLineType')->'IBorder':
        """
        Gets the border object by border line type.

        Args:
            Index (BordersLineType): The border line type enum.
        Returns:
            IBorder: The corresponding border object.
        """
        enumIndex:c_int = Index.value

        GetDllLibXls().BordersCollectionArrayWrapper_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().BordersCollectionArrayWrapper_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().BordersCollectionArrayWrapper_get_Item, self.Ptr, enumIndex)
        ret = None if intPtr==None else IBorder(intPtr)
        return ret

    @property
    def LineStyle(self)->'LineStyleType':
        """
        Gets the line style of the border.

        Returns:
            LineStyleType: The line style enum value of the border.
        """
        GetDllLibXls().BordersCollectionArrayWrapper_get_LineStyle.argtypes=[c_void_p]
        GetDllLibXls().BordersCollectionArrayWrapper_get_LineStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().BordersCollectionArrayWrapper_get_LineStyle, self.Ptr)
        objwraped = LineStyleType(ret)
        return objwraped

    @LineStyle.setter
    def LineStyle(self, value:'LineStyleType'):
        """
        Sets the line style of the border.

        Args:
            value (LineStyleType): The line style enum value to set.
        """
        GetDllLibXls().BordersCollectionArrayWrapper_set_LineStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().BordersCollectionArrayWrapper_set_LineStyle, self.Ptr, value.value)

    @property
    def Value(self)->'LineStyleType':
        """
        Gets the line style value of the border.

        Returns:
            LineStyleType: The line style enum value of the border.
        """
        GetDllLibXls().BordersCollectionArrayWrapper_get_Value.argtypes=[c_void_p]
        GetDllLibXls().BordersCollectionArrayWrapper_get_Value.restype=c_int
        ret = CallCFunction(GetDllLibXls().BordersCollectionArrayWrapper_get_Value, self.Ptr)
        objwraped = LineStyleType(ret)
        return objwraped

    @Value.setter
    def Value(self, value:'LineStyleType'):
        """
        Sets the line style value of the border.

        Args:
            value (LineStyleType): The line style enum value to set.
        """
        GetDllLibXls().BordersCollectionArrayWrapper_set_Value.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().BordersCollectionArrayWrapper_set_Value, self.Ptr, value.value)

