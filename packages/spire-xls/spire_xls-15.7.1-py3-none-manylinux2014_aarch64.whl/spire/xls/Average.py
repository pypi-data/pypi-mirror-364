from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class Average (SpireObject) :
    """Represents an average calculation in an Excel worksheet.
    
    This class provides properties and methods for configuring average calculations
    in Excel, such as determining the type of average to calculate (e.g., simple average,
    weighted average, etc.). It extends SpireObject and can be used in various Excel functions
    and conditional formatting scenarios.
    """
    @property

    def Type(self)->'AverageType':
        """Gets or sets the type of average calculation to perform.
        
        This property specifies which averaging method should be used when
        calculating the average value.
        
        Returns:
            AverageType: An enumeration value representing the type of average calculation.
        """
        GetDllLibXls().Average_get_Type.argtypes=[c_void_p]
        GetDllLibXls().Average_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibXls().Average_get_Type, self.Ptr)
        objwraped = AverageType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'AverageType'):
        """Sets the type of average calculation to perform.
        
        Args:
            value (AverageType): An enumeration value representing the type of average calculation.
        """
        GetDllLibXls().Average_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().Average_set_Type, self.Ptr, value.value)

