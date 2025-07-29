from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class GoalSeek (SpireObject) :
    """Represents a Goal Seek operation in Excel.
    
    This class provides functionality to perform Goal Seek analysis, which is used to find
    the input value needed to achieve a desired result in a formula. Goal Seek works by
    varying the value in one specific cell until a formula that depends on that cell returns
    the desired result.
    """
    @dispatch
    def __init__(self):
        """Initializes a new instance of the GoalSeek class.
        
        Creates a new Goal Seek operation with default settings.
        """
        GetDllLibXls().GoalSeek_CreateGoalSeek.restype = c_void_p
        intPtr = CallCFunction(GetDllLibXls().GoalSeek_CreateGoalSeek)
        super(GoalSeek, self).__init__(intPtr)


    @property
    def MaxIterations(self)->int :
        """Gets or sets the maximum number of iterations for the Goal Seek operation.
        
        This property determines how many calculation attempts the Goal Seek operation
        will make before stopping if it cannot find an exact solution.
        
        Returns:
            int: The maximum number of iterations.
        """
        GetDllLibXls().GoalSeek_get_MaxIterations.argtypes=[c_void_p]
        GetDllLibXls().GoalSeek_get_MaxIterations.restype=c_int
        ret = CallCFunction(GetDllLibXls().GoalSeek_get_MaxIterations, self.Ptr)
        return ret

    @MaxIterations.setter
    def MaxIterations(self, value:int):
        GetDllLibXls().GoalSeek_set_MaxIterations.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().GoalSeek_set_MaxIterations, self.Ptr, value)

    @dispatch
    def TryCalculate(self ,targetCell:'CellRange', targetValue:float , variableCell:'CellRange')->GoalSeekResult:
        """Attempts to perform a Goal Seek calculation with default initial guess.
        
        This method tries to find a value for the variable cell that makes the formula
        in the target cell return the specified target value.
        
        Args:
            targetCell (CellRange): The cell containing the formula whose value you want to set.
            targetValue (float): The value you want the formula to return.
            variableCell (CellRange): The cell whose value will be adjusted to reach the target value.
            
        Returns:
            GoalSeekResult: An object containing the results of the Goal Seek operation.
        """
        intPtrtargetCell:c_void_p = targetCell.Ptr
        intPtrvariableCell:c_void_p = variableCell.Ptr

        GetDllLibXls().GoalSeek_TryCalculate.argtypes=[c_void_p ,c_void_p,c_double,c_void_p]
        GetDllLibXls().GoalSeek_TryCalculate.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().GoalSeek_TryCalculate, self.Ptr, intPtrtargetCell,targetValue ,intPtrvariableCell)
        ret = None if intPtr==None else GoalSeekResult(intPtr)
        return ret

    @dispatch
    def TryCalculate(self ,targetCell:'CellRange', targetValue:float , variableCell:'CellRange',guess:float)->GoalSeekResult:
        """Attempts to perform a Goal Seek calculation with a specified initial guess.
        
        This method tries to find a value for the variable cell that makes the formula
        in the target cell return the specified target value, starting from the specified guess.
        
        Args:
            targetCell (CellRange): The cell containing the formula whose value you want to set.
            targetValue (float): The value you want the formula to return.
            variableCell (CellRange): The cell whose value will be adjusted to reach the target value.
            guess (float): The initial value to use for the variable cell.
            
        Returns:
            GoalSeekResult: An object containing the results of the Goal Seek operation.
        """
        intPtrtargetCell:c_void_p = targetCell.Ptr
        intPtrvariableCell:c_void_p = variableCell.Ptr

        GetDllLibXls().GoalSeek_TryCalculateTTVG.argtypes=[c_void_p ,c_void_p,c_double,c_void_p,c_double]
        GetDllLibXls().GoalSeek_TryCalculateTTVG.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().GoalSeek_TryCalculateTTVG, self.Ptr, intPtrtargetCell,targetValue ,intPtrvariableCell,guess)
        ret = None if intPtr==None else GoalSeekResult(intPtr)
        return ret