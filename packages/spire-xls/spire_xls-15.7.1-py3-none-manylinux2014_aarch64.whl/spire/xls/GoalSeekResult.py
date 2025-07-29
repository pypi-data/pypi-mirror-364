from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class GoalSeekResult (SpireObject) :
    """Represents the result of a Goal Seek operation in Excel.
    
    This class encapsulates the results of a Goal Seek analysis, including information about
    the target and variable cells, the number of iterations performed, the target value,
    and the calculated result. It provides methods to determine if the operation was successful
    and to access the results of the calculation.
    """

    
    def Determine(self):
        """Determines if the Goal Seek operation was successful.
        
        This method evaluates the results of the Goal Seek operation to determine
        if it successfully found a solution that achieves the target value within
        acceptable tolerance.
        """
        GetDllLibXls().GoalSeekResult_Determine.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().GoalSeekResult_Determine, self.Ptr)

    @property
    def TargetCellName(self)->str:
        """Gets the name or address of the target cell used in the Goal Seek operation.
        
        Returns:
            str: The name or address of the target cell.
        """
        GetDllLibXls().GoalSeekResult_get_TargetCellName.argtypes=[c_void_p]
        GetDllLibXls().GoalSeekResult_get_TargetCellName.restype=c_void_p
        ret = CallCFunction(GetDllLibXls().GoalSeekResult_get_TargetCellName, self.Ptr)
        return PtrToStr(ret)

    @property
    def VariableCellName(self)->str:
        """Gets the name or address of the variable cell used in the Goal Seek operation.
        
        Returns:
            str: The name or address of the variable cell.
        """
        GetDllLibXls().GoalSeekResult_get_VariableCellName.argtypes=[c_void_p]
        GetDllLibXls().GoalSeekResult_get_VariableCellName.restype=c_void_p
        ret = CallCFunction(GetDllLibXls().GoalSeekResult_get_VariableCellName, self.Ptr)
        return PtrToStr(ret)
    

    @property
    def Iterations(self)->int:
        """Gets the number of iterations performed during the Goal Seek operation.
        
        Returns:
            int: The number of iterations performed.
        """
        GetDllLibXls().GoalSeekResult_get_Iterations.argtypes=[c_void_p]
        GetDllLibXls().GoalSeekResult_get_Iterations.restype=c_int
        ret = CallCFunction(GetDllLibXls().GoalSeekResult_get_Iterations, self.Ptr)
        return ret

    @property
    def TargetValue(self)->float:
        """Gets the target value that was specified for the Goal Seek operation.
        
        Returns:
            float: The target value that the operation attempted to achieve.
        """
        GetDllLibXls().GoalSeekResult_get_TargetValue.argtypes=[c_void_p]
        GetDllLibXls().GoalSeekResult_get_TargetValue.restype=c_double
        ret = CallCFunction(GetDllLibXls().GoalSeekResult_get_TargetValue, self.Ptr)
        return ret

    

    @property
    def GuessResult(self)->float:
        """Gets the calculated result value for the variable cell.
        
        Returns:
            float: The value found for the variable cell that best achieves the target value.
        """
        GetDllLibXls().GoalSeekResult_get_GuessResult.argtypes=[c_void_p]
        GetDllLibXls().GoalSeekResult_get_GuessResult.restype=c_double
        ret = CallCFunction(GetDllLibXls().GoalSeekResult_get_GuessResult, self.Ptr)
        return ret