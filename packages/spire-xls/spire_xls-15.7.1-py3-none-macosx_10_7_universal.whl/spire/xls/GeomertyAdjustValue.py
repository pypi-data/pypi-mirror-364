from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class GeomertyAdjustValue (SpireObject) :
    """Represents a geometry adjustment value for shapes in Excel.
    
    This class provides properties and methods for manipulating geometry
    adjustment values, which control the appearance of adjustable shapes
    in Excel. It allows for setting formulas and parameters that define
    how shapes can be adjusted.
    """
    @property

    def Name(self)->str:
        """Gets the name of the geometry adjustment value.
        
        Returns:
            str: The name of the geometry adjustment value.
        """
        GetDllLibXls().GeomertyAdjustValue_get_Name.argtypes=[c_void_p]
        GetDllLibXls().GeomertyAdjustValue_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().GeomertyAdjustValue_get_Name, self.Ptr))
        return ret


    @property

    def Formula(self)->str:
        """Gets the formula of the geometry adjustment value.
        
        Returns:
            str: The formula string that defines the geometry adjustment.
        """
        GetDllLibXls().GeomertyAdjustValue_get_Formula.argtypes=[c_void_p]
        GetDllLibXls().GeomertyAdjustValue_get_Formula.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().GeomertyAdjustValue_get_Formula, self.Ptr))
        return ret



    def SetFormulaParameter(self ,args:List[float]):
        """Sets the parameters for the formula of the geometry adjustment value.
        
        Args:
            args (List[float]): A list of floating-point values representing the parameters for the formula.
        """
        #arrayargs:ArrayTypeargs = ""
        countargs = len(args)
        ArrayTypeargs = c_double * countargs
        arrayargs = ArrayTypeargs()
        for i in range(0, countargs):
            arrayargs[i] = args[i]


        GetDllLibXls().GeomertyAdjustValue_SetFormulaParameter.argtypes=[c_void_p ,ArrayTypeargs,c_int]
        CallCFunction(GetDllLibXls().GeomertyAdjustValue_SetFormulaParameter, self.Ptr, arrayargs,countargs)


    def FormulaType(self)->'GeomertyAdjustValueFormulaType':
        """Gets the formula type of the geometry adjustment value.
        
        Returns:
            GeomertyAdjustValueFormulaType: An enumeration value representing the formula type.
        """
        GetDllLibXls().GeomertyAdjustValue_FormulaType.argtypes=[c_void_p]
        GetDllLibXls().GeomertyAdjustValue_FormulaType.restype=c_int
        ret = CallCFunction(GetDllLibXls().GeomertyAdjustValue_FormulaType, self.Ptr)
        objwraped = GeomertyAdjustValueFormulaType(ret)
        return objwraped

