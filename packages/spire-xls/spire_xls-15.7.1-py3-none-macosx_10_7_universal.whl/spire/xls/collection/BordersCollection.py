from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class BordersCollection (  SpireObject, IBorders) :
    """
    Represents a collection of border objects for an Excel cell or range.
    """

    #def GetEnumerator(self)->'IEnumerator':
    #    """

    #    """
    #    GetDllLibXls().BordersCollection_GetEnumerator.argtypes=[c_void_p]
    #    GetDllLibXls().BordersCollection_GetEnumerator.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibXls().BordersCollection_GetEnumerator, self.Ptr)
    #    ret = None if intPtr==None else IEnumerator(intPtr)
    #    return ret


    @property
    def KnownColor(self)->'ExcelColors':
        """
        Returns or sets the primary excel color of the object.

        Returns:
            ExcelColors: The known color enum value of the border.
        """
        GetDllLibXls().BordersCollection_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().BordersCollection_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().BordersCollection_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        """
        Sets the known color of the border.

        Args:
            value (ExcelColors): The color enum value to set.
        """
        GetDllLibXls().BordersCollection_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().BordersCollection_set_KnownColor, self.Ptr, value.value)

    @property
    def Color(self)->'Color':
        """
        Returns or sets the primary color of the object.

        Returns:
            Color: The color object of the border.
        """
        GetDllLibXls().BordersCollection_get_Color.argtypes=[c_void_p]
        GetDllLibXls().BordersCollection_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().BordersCollection_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        """
        Sets the color of the border.

        Args:
            value (Color): The color object to set.
        """
        GetDllLibXls().BordersCollection_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().BordersCollection_set_Color, self.Ptr, value.Ptr)

    def _create(self, intPtrWithTypeName:IntPtrWithTypeName)->'IBorder':
        """
        Creates an IBorder instance from a pointer with type name.

        Args:
            intPtrWithTypeName (IntPtrWithTypeName): Pointer and type name information.
        Returns:
            IBorder: The created border object or None.
        """
        ret = None
        if intPtrWithTypeName == None :
            return ret
        intPtr = intPtrWithTypeName.intPtr[0] + (intPtrWithTypeName.intPtr[1]<<32)
        strName = PtrToStr(intPtrWithTypeName.typeName)
        if(strName == 'Spire.Xls.Core.Spreadsheet.XlsBorderArrayWrapper'):
            ret = XlsBorderArrayWrapper(intPtr)
        elif (strName == 'Spire.Xls.Core.Spreadsheet.XlsBorder'):
            ret = XlsBorder(intPtr)
        elif (strName == 'Spire.Xls.CellBorder'):
            ret = CellBorder(intPtr)
        else:
            ret = XlsBorder(intPtr)

        return ret
    @dispatch
    def get_Item(self ,Index:BordersLineType)->IBorder:
        """
        Gets border item.

        Args:
            Index (BordersLineType): The border line type enum.
        Returns:
            IBorder: The corresponding border object.
        """
        enumIndex:c_int = Index.value

        GetDllLibXls().BordersCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().BordersCollection_get_Item.restype=IntPtrWithTypeName
        intPtr = CallCFunction(GetDllLibXls().BordersCollection_get_Item, self.Ptr, enumIndex)
        ret = None if intPtr==None else self._create(intPtr)
        return ret


    @property
    def LineStyle(self)->'LineStyleType':
        """
        Returns or sets the line style for the border.

        Returns:
            LineStyleType: The line style enum value of the border.
        """
        GetDllLibXls().BordersCollection_get_LineStyle.argtypes=[c_void_p]
        GetDllLibXls().BordersCollection_get_LineStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().BordersCollection_get_LineStyle, self.Ptr)
        objwraped = LineStyleType(ret)
        return objwraped

    @LineStyle.setter
    def LineStyle(self, value:'LineStyleType'):
        """
        Sets the line style of the border.

        Args:
            value (LineStyleType): The line style enum value to set.
        """
        GetDllLibXls().BordersCollection_set_LineStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().BordersCollection_set_LineStyle, self.Ptr, value.value)

    @property
    def Value(self)->'LineStyleType':
        """
        Gets or sets line style of borders.

        Returns:
            LineStyleType: The line style enum value of the border.
        """
        GetDllLibXls().BordersCollection_get_Value.argtypes=[c_void_p]
        GetDllLibXls().BordersCollection_get_Value.restype=c_int
        ret = CallCFunction(GetDllLibXls().BordersCollection_get_Value, self.Ptr)
        objwraped = LineStyleType(ret)
        return objwraped

    @Value.setter
    def Value(self, value:'LineStyleType'):
        """
        Sets the line style value of the border.

        Args:
            value (LineStyleType): The line style enum value to set.
        """
        GetDllLibXls().BordersCollection_set_Value.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().BordersCollection_set_Value, self.Ptr, value.value)

    @property
    def Count(self)->int:
        """
        Gets count of borders.

        Returns:
            int: The number of borders in the collection.
        """
        GetDllLibXls().BordersCollection_get_Count.argtypes=[c_void_p]
        GetDllLibXls().BordersCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibXls().BordersCollection_get_Count, self.Ptr)
        return ret

    @property
    def Parent(self)->'SpireObject':
        """
        Gets the parent object of the borders collection.

        Returns:
            SpireObject: The parent object.
        """
        GetDllLibXls().BordersCollection_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().BordersCollection_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().BordersCollection_get_Parent, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


