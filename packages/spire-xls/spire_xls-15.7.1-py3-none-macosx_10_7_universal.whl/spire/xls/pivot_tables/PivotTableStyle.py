from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class PivotTableStyle (SpireObject) :
    """Represents the style of a PivotTable.
    
    This class provides functionality for managing the overall style of a PivotTable,
    including whether it uses default styling and its name.
    """

    def SetConverter(self ,converter:'SpireObject'):
        """Sets the converter for the PivotTable style.
        
        Args:
            converter (SpireObject): The converter object to set.
        """
        intPtrconverter:c_void_p = converter.Ptr

        GetDllLibXls().PivotTableStyle_SetConverter.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().PivotTableStyle_SetConverter, self.Ptr, intPtrconverter)

    @property
    def IsDefaultStyle(self)->bool:
        """Gets whether the style is the default PivotTable style.
        
        Returns:
            bool: True if the style is the default style; otherwise, False.
        """
        GetDllLibXls().PivotTableStyle_get_IsDefaultStyle.argtypes=[c_void_p]
        GetDllLibXls().PivotTableStyle_get_IsDefaultStyle.restype=c_bool
        ret = CallCFunction(GetDllLibXls().PivotTableStyle_get_IsDefaultStyle, self.Ptr)
        return ret

    @IsDefaultStyle.setter
    def IsDefaultStyle(self, value:bool):
        """Sets whether the style is the default PivotTable style.
        
        Args:
            value (bool): True to set as the default style; otherwise, False.
        """
        GetDllLibXls().PivotTableStyle_set_IsDefaultStyle.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().PivotTableStyle_set_IsDefaultStyle, self.Ptr, value)

    @property

    def Name(self)->str:
        """Gets the name of the PivotTable style.
        
        Returns:
            str: The name of the PivotTable style.
        """
        GetDllLibXls().PivotTableStyle_get_Name.argtypes=[c_void_p]
        GetDllLibXls().PivotTableStyle_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().PivotTableStyle_get_Name, self.Ptr))
        return ret


#    @property
#
#    def Styles(self)->'Dictionary2':
#        """
#
#        """
#        GetDllLibXls().PivotTableStyle_get_Styles.argtypes=[c_void_p]
#        GetDllLibXls().PivotTableStyle_get_Styles.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().PivotTableStyle_get_Styles, self.Ptr)
#        ret = None if intPtr==None else Dictionary2(intPtr)
#        return ret
#


