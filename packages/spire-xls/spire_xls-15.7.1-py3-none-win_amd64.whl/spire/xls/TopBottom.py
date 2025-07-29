from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class TopBottom (SpireObject) :
    """Represents a top/bottom conditional formatting rule in Excel.
    
    This class provides functionality for configuring top/bottom conditional formatting
    rules, which highlight cells with values in the top or bottom N values or N percent
    of a range. For example, highlighting the top 10 values or bottom 5% of values.
    """
    @property
    def Rank(self)->int:
        """Gets or sets the rank value for the top/bottom rule.
        
        For example, in a "Top 10" rule, the rank would be 10.
        
        Returns:
            int: The rank value.
        """
        GetDllLibXls().TopBottom_get_Rank.argtypes=[c_void_p]
        GetDllLibXls().TopBottom_get_Rank.restype=c_int
        ret = CallCFunction(GetDllLibXls().TopBottom_get_Rank, self.Ptr)
        return ret

    @Rank.setter
    def Rank(self, value:int):
        GetDllLibXls().TopBottom_set_Rank.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().TopBottom_set_Rank, self.Ptr, value)

    @property

    def Type(self)->'TopBottomType':
        """Gets or sets the type of the top/bottom rule.
        
        Determines whether the rule applies to top or bottom values, and whether
        it uses a count or percentage.
        
        Returns:
            TopBottomType: The top/bottom rule type.
        """
        GetDllLibXls().TopBottom_get_Type.argtypes=[c_void_p]
        GetDllLibXls().TopBottom_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibXls().TopBottom_get_Type, self.Ptr)
        objwraped = TopBottomType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'TopBottomType'):
        GetDllLibXls().TopBottom_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().TopBottom_set_Type, self.Ptr, value.value)

