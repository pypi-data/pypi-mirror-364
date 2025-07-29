from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IconSet (SpireObject) :
    """Icon set conditional formatting interface.
    
    This class represents an icon set conditional formatting rule in Excel.
    Icon sets display different icons for different cell values, providing a visual
    indicator of the value's relative magnitude. The class allows customization of
    icon set types, thresholds, order, and display options.
    
    Inherits from:
        SpireObject: Base Spire object class
    """
#    @property
#
#    def IconCriteria(self)->'IList1':
#        """
#    <summary>
#        Gets an IconCriteria collection
#    </summary>
#        """
#        GetDllLibXls().IconSet_get_IconCriteria.argtypes=[c_void_p]
#        GetDllLibXls().IconSet_get_IconCriteria.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().IconSet_get_IconCriteria, self.Ptr)
#        ret = None if intPtr==None else IList1(intPtr)
#        return ret
#


    @property

    def IconSetType(self)->'IconSetType':
        """Gets the icon set type.
        
        Returns:
            IconSetType: The type of icon set used in the conditional formatting.
        """
        GetDllLibXls().IconSet_get_IconSetType.argtypes=[c_void_p]
        GetDllLibXls().IconSet_get_IconSetType.restype=c_int
        ret = CallCFunction(GetDllLibXls().IconSet_get_IconSetType, self.Ptr)
        objwraped = IconSetType(ret)
        return objwraped

    @IconSetType.setter
    def IconSetType(self, value:'IconSetType'):
        """Sets the icon set type.
        
        Args:
            value (IconSetType): The type of icon set to use in the conditional formatting.
        """
        GetDllLibXls().IconSet_set_IconSetType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().IconSet_set_IconSetType, self.Ptr, value.value)

    @property
    def PercentileValues(self)->bool:
        """Gets whether thresholds for an icon set are determined using percentiles.
        
        Returns:
            bool: True if thresholds are determined using percentiles, otherwise False.
        """
        GetDllLibXls().IconSet_get_PercentileValues.argtypes=[c_void_p]
        GetDllLibXls().IconSet_get_PercentileValues.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IconSet_get_PercentileValues, self.Ptr)
        return ret

    @PercentileValues.setter
    def PercentileValues(self, value:bool):
        """Sets whether thresholds for an icon set are determined using percentiles.
        
        Args:
            value (bool): True to determine thresholds using percentiles, otherwise False.
        """
        GetDllLibXls().IconSet_set_PercentileValues.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IconSet_set_PercentileValues, self.Ptr, value)

    @property
    def IsReverseOrder(self)->bool:
        """Gets whether the order of icons is reversed for an icon set.
        
        Returns:
            bool: True if the order of icons is reversed, otherwise False.
        """
        GetDllLibXls().IconSet_get_IsReverseOrder.argtypes=[c_void_p]
        GetDllLibXls().IconSet_get_IsReverseOrder.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IconSet_get_IsReverseOrder, self.Ptr)
        return ret

    @IsReverseOrder.setter
    def IsReverseOrder(self, value:bool):
        """Sets whether the order of icons is reversed for an icon set.
        
        Args:
            value (bool): True to reverse the order of icons, otherwise False.
        """
        GetDllLibXls().IconSet_set_IsReverseOrder.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IconSet_set_IsReverseOrder, self.Ptr, value)

    @property
    def ShowIconOnly(self)->bool:
        """Gets whether only the icon is displayed for an icon set conditional format.
        
        Returns:
            bool: True if only the icon is displayed, otherwise False.
        """
        GetDllLibXls().IconSet_get_ShowIconOnly.argtypes=[c_void_p]
        GetDllLibXls().IconSet_get_ShowIconOnly.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IconSet_get_ShowIconOnly, self.Ptr)
        return ret

    @ShowIconOnly.setter
    def ShowIconOnly(self, value:bool):
        """Sets whether only the icon is displayed for an icon set conditional format.
        
        Args:
            value (bool): True to display only the icon, otherwise False.
        """
        GetDllLibXls().IconSet_set_ShowIconOnly.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IconSet_set_ShowIconOnly, self.Ptr, value)

