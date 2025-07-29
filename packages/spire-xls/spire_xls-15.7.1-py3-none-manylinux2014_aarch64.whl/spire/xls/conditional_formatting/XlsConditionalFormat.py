from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsConditionalFormat (  XlsObject, IConditionalFormat, ICloneParent) :
    """
    Represents a conditional format in Excel, including its rules and formatting.
    """
    @property

    def IconSet(self)->'IconSet':
        """Gets the icon set associated with this conditional format.
        
        Returns:
            IconSet: An object representing the icon set used in this conditional format.
                    Valid only for conditional format type IconSet.
        """
        GetDllLibXls().XlsConditionalFormat_get_IconSet.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IconSet.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IconSet, self.Ptr)
        ret = None if intPtr==None else IconSet(intPtr)
        return ret


    @property

    def ColorScale(self)->'ColorScale':
        """
        Get the conditional formatting's "ColorScale" instance. The default instance is a "green-red" 2ColorScale . Valid only for type = ColorScale.

        Returns:
            ColorScale instance

        """
        GetDllLibXls().XlsConditionalFormat_get_ColorScale.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_ColorScale.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_ColorScale, self.Ptr)
        ret = None if intPtr==None else ColorScale(intPtr)
        return ret


    @property

    def NumberFormat(self)->str:
        """Gets or sets the number format string for values matching this conditional format.
        
        Returns:
            str: A string representing the number format code.
        """
        GetDllLibXls().XlsConditionalFormat_get_NumberFormat.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_NumberFormat.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsConditionalFormat_get_NumberFormat, self.Ptr))
        return ret


    @NumberFormat.setter
    def NumberFormat(self, value:str):
        GetDllLibXls().XlsConditionalFormat_set_NumberFormat.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_NumberFormat, self.Ptr, value)

    @property
    def IsNumberFormatPresent(self)->bool:
        """Gets whether a number format is defined for this conditional format.
        
        Returns:
            bool: True if a number format is present; otherwise, False.
        """
        GetDllLibXls().XlsConditionalFormat_get_IsNumberFormatPresent.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IsNumberFormatPresent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IsNumberFormatPresent, self.Ptr)
        return ret

    def GetHashCode(self)->int:
        """Returns a hash code for this conditional format.
        
        Returns:
            int: A hash code value for this object.
        """
        GetDllLibXls().XlsConditionalFormat_GetHashCode.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_GetHashCode, self.Ptr)
        return ret


    def Equals(self ,obj:'SpireObject')->bool:
        """Determines whether the specified object is equal to the current object.
        
        Args:
            obj (SpireObject): The object to compare with the current object.
            
        Returns:
            bool: True if the specified object is equal to the current object; otherwise, False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibXls().XlsConditionalFormat_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsConditionalFormat_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_Equals, self.Ptr, intPtrobj)
        return ret


    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """
        Creates a new object that is a copy of the current instance.

        Args:
            parent: Parent object for a copy of this instance.

        Returns:
            A new object that is a copy of this instance.

        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsConditionalFormat_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsConditionalFormat_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @property

    def OColor(self)->'OColor':
        """
        Conditional format color. Read-only.

        """
        GetDllLibXls().XlsConditionalFormat_get_OColor.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_OColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_OColor, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def BackColorObject(self)->'OColor':
        """
        Conditional format background color. Read-only.

        """
        GetDllLibXls().XlsConditionalFormat_get_BackColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_BackColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_BackColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def TopBorderColorObject(self)->'OColor':
        """
        Conditional format top border color. Read-only.

        """
        GetDllLibXls().XlsConditionalFormat_get_TopBorderColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_TopBorderColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_TopBorderColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def BottomBorderColorObject(self)->'OColor':
        """
        Conditional format bottom border color. Read-only.

        """
        GetDllLibXls().XlsConditionalFormat_get_BottomBorderColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_BottomBorderColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_BottomBorderColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def LeftBorderColorObject(self)->'OColor':
        """
        Conditional format left border color. Read-only.

        """
        GetDllLibXls().XlsConditionalFormat_get_LeftBorderColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_LeftBorderColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_LeftBorderColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def RightBorderColorObject(self)->'OColor':
        """
        Conditional format right border color. Read-only.

        """
        GetDllLibXls().XlsConditionalFormat_get_RightBorderColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_RightBorderColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_RightBorderColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def FontColorObject(self)->'OColor':
        """
        Conditional format font color. Read-only.

        """
        GetDllLibXls().XlsConditionalFormat_get_FontColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_FontColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_FontColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @dispatch

    def MakeFormula(self)->str:
        """Creates a formula string for the conditional format without parameters.
        
        Returns:
            str: The formula string for the conditional format.
        """
        GetDllLibXls().XlsConditionalFormat_MakeFormula.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_MakeFormula.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsConditionalFormat_MakeFormula, self.Ptr))
        return ret


    @dispatch

    def MakeFormula(self ,para:str)->str:
        """Creates a formula string for the conditional format with a string parameter.
        
        Args:
            para (str): The string parameter to use in the formula.
            
        Returns:
            str: The formula string for the conditional format.
        """
        
        GetDllLibXls().XlsConditionalFormat_MakeFormulaP.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsConditionalFormat_MakeFormulaP.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsConditionalFormat_MakeFormulaP, self.Ptr, para))
        return ret


    @dispatch

    def MakeFormula(self ,para:float)->str:
        """Creates a formula string for the conditional format with a numeric parameter.
        
        Args:
            para (float): The numeric parameter to use in the formula.
            
        Returns:
            str: The formula string for the conditional format.
        """
        
        GetDllLibXls().XlsConditionalFormat_MakeFormulaP1.argtypes=[c_void_p ,c_double]
        GetDllLibXls().XlsConditionalFormat_MakeFormulaP1.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsConditionalFormat_MakeFormulaP1, self.Ptr, para))
        return ret



    def UpdateFormula(self ,iCurIndex:int,iSourceIndex:int,sourceRect:'Rectangle',iDestIndex:int,destRect:'Rectangle',row:int,column:int):
        """Updates the formula in the conditional format when cells are moved or copied.
        
        This method adjusts the formula references to maintain their validity after
        cells are moved or copied to a new location.
        
        Args:
            iCurIndex (int): The index of the current worksheet.
            iSourceIndex (int): The index of the source worksheet.
            sourceRect (Rectangle): The rectangle representing the source cell range.
            iDestIndex (int): The index of the destination worksheet.
            destRect (Rectangle): The rectangle representing the destination cell range.
            row (int): The row offset.
            column (int): The column offset.
        """
        
        intPtrsourceRect:c_void_p = sourceRect.Ptr
        intPtrdestRect:c_void_p = destRect.Ptr

        GetDllLibXls().XlsConditionalFormat_UpdateFormula.argtypes=[c_void_p ,c_int,c_int,c_void_p,c_int,c_void_p,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_UpdateFormula, self.Ptr, iCurIndex,iSourceIndex,intPtrsourceRect,iDestIndex,intPtrdestRect,row,column)

    @property
    def Priority(self)->int:
        """Gets or sets the priority of the conditional format.
        
        The priority determines the order in which conditional formats are evaluated
        when multiple formats could apply to the same cell. Lower numbers have higher priority.
        
        Returns:
            int: The priority value of the conditional format.
        """
        GetDllLibXls().XlsConditionalFormat_get_Priority.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_Priority.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_Priority, self.Ptr)
        return ret

    @Priority.setter
    def Priority(self, value:int):
        GetDllLibXls().XlsConditionalFormat_set_Priority.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_Priority, self.Ptr, value)

    @property
    def StopIfTrue(self)->bool:
        """Gets or sets whether evaluation of subsequent conditional formats should stop if this format evaluates to true.
        
        When set to True, if this conditional format is satisfied, lower-priority conditional formats
        are not evaluated for the same cell.
        
        Returns:
            bool: True if evaluation should stop when this format is true; otherwise, False.
        """
        GetDllLibXls().XlsConditionalFormat_get_StopIfTrue.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_StopIfTrue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_StopIfTrue, self.Ptr)
        return ret

    @StopIfTrue.setter
    def StopIfTrue(self, value:bool):
        GetDllLibXls().XlsConditionalFormat_set_StopIfTrue.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_StopIfTrue, self.Ptr, value)

    @property
    def DxfId(self)->int:
        """Gets or sets the differential formatting style ID for this conditional format.
        
        The DxfId (Differential Formatting ID) refers to a style definition in the workbook
        that specifies the formatting to apply when this conditional format is satisfied.
        
        Returns:
            int: The differential formatting style ID.
        """
        GetDllLibXls().XlsConditionalFormat_get_DxfId.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_DxfId.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_DxfId, self.Ptr)
        return ret

    @DxfId.setter
    def DxfId(self, value:int):
        GetDllLibXls().XlsConditionalFormat_set_DxfId.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_DxfId, self.Ptr, value)

    @property

    def Average(self)->'Average':
        """

        """
        from spire.xls.Average import Average
        GetDllLibXls().XlsConditionalFormat_get_Average.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_Average.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_Average, self.Ptr)
        ret = None if intPtr==None else Average(intPtr)
        return ret


    @property

    def TopBottom(self)->'TopBottom':
        """

        """
        GetDllLibXls().XlsConditionalFormat_get_TopBottom.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_TopBottom.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_TopBottom, self.Ptr)
        ret = None if intPtr==None else TopBottom(intPtr)
        return ret


    @property

    def LeftBorderKnownColor(self)->'ExcelColors':
        """
        Excel color of the left line.

        """
        GetDllLibXls().XlsConditionalFormat_get_LeftBorderKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_LeftBorderKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_LeftBorderKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @LeftBorderKnownColor.setter
    def LeftBorderKnownColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsConditionalFormat_set_LeftBorderKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_LeftBorderKnownColor, self.Ptr, value.value)

    @property

    def LeftBorderColor(self)->'Color':
        """

        """
        GetDllLibXls().XlsConditionalFormat_get_LeftBorderColor.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_LeftBorderColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_LeftBorderColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @LeftBorderColor.setter
    def LeftBorderColor(self, value:'Color'):
        GetDllLibXls().XlsConditionalFormat_set_LeftBorderColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_LeftBorderColor, self.Ptr, value.Ptr)

    @property

    def LeftBorderStyle(self)->'LineStyleType':
        """
        Left border line style.

        """
        GetDllLibXls().XlsConditionalFormat_get_LeftBorderStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_LeftBorderStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_LeftBorderStyle, self.Ptr)
        objwraped = LineStyleType(ret)
        return objwraped

    @LeftBorderStyle.setter
    def LeftBorderStyle(self, value:'LineStyleType'):
        GetDllLibXls().XlsConditionalFormat_set_LeftBorderStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_LeftBorderStyle, self.Ptr, value.value)

    @property

    def RightBorderKnownColor(self)->'ExcelColors':
        """
        Color of the right line.

        """
        GetDllLibXls().XlsConditionalFormat_get_RightBorderKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_RightBorderKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_RightBorderKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @RightBorderKnownColor.setter
    def RightBorderKnownColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsConditionalFormat_set_RightBorderKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_RightBorderKnownColor, self.Ptr, value.value)

    @property

    def RightBorderColor(self)->'Color':
        """
        Color of the right line.

        """
        GetDllLibXls().XlsConditionalFormat_get_RightBorderColor.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_RightBorderColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_RightBorderColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @RightBorderColor.setter
    def RightBorderColor(self, value:'Color'):
        GetDllLibXls().XlsConditionalFormat_set_RightBorderColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_RightBorderColor, self.Ptr, value.Ptr)

    @property

    def RightBorderStyle(self)->'LineStyleType':
        """
        Right border line style.

        """
        GetDllLibXls().XlsConditionalFormat_get_RightBorderStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_RightBorderStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_RightBorderStyle, self.Ptr)
        objwraped = LineStyleType(ret)
        return objwraped

    @RightBorderStyle.setter
    def RightBorderStyle(self, value:'LineStyleType'):
        GetDllLibXls().XlsConditionalFormat_set_RightBorderStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_RightBorderStyle, self.Ptr, value.value)

    @property

    def TopBorderKnownColor(self)->'ExcelColors':
        """
        Excel color of the top line.

        """
        GetDllLibXls().XlsConditionalFormat_get_TopBorderKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_TopBorderKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_TopBorderKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @TopBorderKnownColor.setter
    def TopBorderKnownColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsConditionalFormat_set_TopBorderKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_TopBorderKnownColor, self.Ptr, value.value)

    @property

    def TopBorderColor(self)->'Color':
        """

        """
        GetDllLibXls().XlsConditionalFormat_get_TopBorderColor.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_TopBorderColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_TopBorderColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @TopBorderColor.setter
    def TopBorderColor(self, value:'Color'):
        GetDllLibXls().XlsConditionalFormat_set_TopBorderColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_TopBorderColor, self.Ptr, value.Ptr)

    @property

    def TopBorderStyle(self)->'LineStyleType':
        """
        Top border line style.

        """
        GetDllLibXls().XlsConditionalFormat_get_TopBorderStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_TopBorderStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_TopBorderStyle, self.Ptr)
        objwraped = LineStyleType(ret)
        return objwraped

    @TopBorderStyle.setter
    def TopBorderStyle(self, value:'LineStyleType'):
        GetDllLibXls().XlsConditionalFormat_set_TopBorderStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_TopBorderStyle, self.Ptr, value.value)

    @property

    def BottomBorderKnownColor(self)->'ExcelColors':
        """
        Excel color of the bottom line.

        """
        GetDllLibXls().XlsConditionalFormat_get_BottomBorderKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_BottomBorderKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_BottomBorderKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @BottomBorderKnownColor.setter
    def BottomBorderKnownColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsConditionalFormat_set_BottomBorderKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_BottomBorderKnownColor, self.Ptr, value.value)

    @property

    def BottomBorderColor(self)->'Color':
        """
        Color of the bottom line.

        """
        GetDllLibXls().XlsConditionalFormat_get_BottomBorderColor.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_BottomBorderColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_BottomBorderColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @BottomBorderColor.setter
    def BottomBorderColor(self, value:'Color'):
        GetDllLibXls().XlsConditionalFormat_set_BottomBorderColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_BottomBorderColor, self.Ptr, value.Ptr)

    @property

    def BottomBorderStyle(self)->'LineStyleType':
        """
        Bottom border line style.

        """
        GetDllLibXls().XlsConditionalFormat_get_BottomBorderStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_BottomBorderStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_BottomBorderStyle, self.Ptr)
        objwraped = LineStyleType(ret)
        return objwraped

    @BottomBorderStyle.setter
    def BottomBorderStyle(self, value:'LineStyleType'):
        GetDllLibXls().XlsConditionalFormat_set_BottomBorderStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_BottomBorderStyle, self.Ptr, value.value)

    @property

    def FirstFormula(self)->str:
        """
        First formula.

        """
        GetDllLibXls().XlsConditionalFormat_get_FirstFormula.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_FirstFormula.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsConditionalFormat_get_FirstFormula, self.Ptr))
        return ret


    @FirstFormula.setter
    def FirstFormula(self, value:str):
        GetDllLibXls().XlsConditionalFormat_set_FirstFormula.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_FirstFormula, self.Ptr, value)

    @property

    def FirstFormulaR1C1(self)->str:
        """
        Gets or sets the first formula in R1C1 notation for the conditional format.

        Returns:
            str: The first formula in R1C1 notation.
        """
        GetDllLibXls().XlsConditionalFormat_get_FirstFormulaR1C1.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_FirstFormulaR1C1.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsConditionalFormat_get_FirstFormulaR1C1, self.Ptr))
        return ret


    @FirstFormulaR1C1.setter
    def FirstFormulaR1C1(self, value:str):
        """
        Sets the first formula in R1C1 notation for the conditional format.

        Args:
            value (str): The first formula in R1C1 notation.
        """
        GetDllLibXls().XlsConditionalFormat_set_FirstFormulaR1C1.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_FirstFormulaR1C1, self.Ptr, value)


    def SetTimePeriod(self ,timePeriod:'TimePeriodType'):
        """

        """
        enumtimePeriod:c_int = timePeriod.value

        GetDllLibXls().XlsConditionalFormat_SetTimePeriod.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_SetTimePeriod, self.Ptr, enumtimePeriod)

    @property

    def SecondFormula(self)->str:
        """
        Second formula.

        """
        GetDllLibXls().XlsConditionalFormat_get_SecondFormula.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_SecondFormula.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsConditionalFormat_get_SecondFormula, self.Ptr))
        return ret


    @SecondFormula.setter
    def SecondFormula(self, value:str):
        GetDllLibXls().XlsConditionalFormat_set_SecondFormula.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_SecondFormula, self.Ptr, value)

    @property

    def SecondFormulaR1C1(self)->str:
        """
        Gets or sets the second formula in R1C1 notation for the conditional format.

        Returns:
            str: The second formula in R1C1 notation.
        """
        GetDllLibXls().XlsConditionalFormat_get_SecondFormulaR1C1.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_SecondFormulaR1C1.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsConditionalFormat_get_SecondFormulaR1C1, self.Ptr))
        return ret


    @SecondFormulaR1C1.setter
    def SecondFormulaR1C1(self, value:str):
        """
        Sets the second formula in R1C1 notation for the conditional format.

        Args:
            value (str): The second formula in R1C1 notation.
        """
        GetDllLibXls().XlsConditionalFormat_set_SecondFormulaR1C1.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_SecondFormulaR1C1, self.Ptr, value)

    @property

    def FormatType(self)->'ConditionalFormatType':
        """

        """
        GetDllLibXls().XlsConditionalFormat_get_FormatType.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_FormatType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_FormatType, self.Ptr)
        objwraped = ConditionalFormatType(ret)
        return objwraped

    @FormatType.setter
    def FormatType(self, value:'ConditionalFormatType'):
        GetDllLibXls().XlsConditionalFormat_set_FormatType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_FormatType, self.Ptr, value.value)

    @property

    def Operator(self)->'ComparisonOperatorType':
        """
        Type of the comparison operator.

        """
        GetDllLibXls().XlsConditionalFormat_get_Operator.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_Operator.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_Operator, self.Ptr)
        objwraped = ComparisonOperatorType(ret)
        return objwraped

    @Operator.setter
    def Operator(self, value:'ComparisonOperatorType'):
        GetDllLibXls().XlsConditionalFormat_set_Operator.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_Operator, self.Ptr, value.value)

    @property
    def IsBold(self)->bool:
        """
        Indicates whether font is bold.

        """
        GetDllLibXls().XlsConditionalFormat_get_IsBold.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IsBold.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IsBold, self.Ptr)
        return ret

    @IsBold.setter
    def IsBold(self, value:bool):
        GetDllLibXls().XlsConditionalFormat_set_IsBold.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_IsBold, self.Ptr, value)

    @property
    def IsItalic(self)->bool:
        """
        Indicates whether font is italic.

        """
        GetDllLibXls().XlsConditionalFormat_get_IsItalic.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IsItalic.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IsItalic, self.Ptr)
        return ret

    @IsItalic.setter
    def IsItalic(self, value:bool):
        GetDllLibXls().XlsConditionalFormat_set_IsItalic.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_IsItalic, self.Ptr, value)

    @property

    def FontKnownColor(self)->'ExcelColors':
        """
        Font excel color.

        """
        GetDllLibXls().XlsConditionalFormat_get_FontKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_FontKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_FontKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @FontKnownColor.setter
    def FontKnownColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsConditionalFormat_set_FontKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_FontKnownColor, self.Ptr, value.value)

    @property

    def FontColor(self)->'Color':
        """

        """
        GetDllLibXls().XlsConditionalFormat_get_FontColor.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_FontColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_FontColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @FontColor.setter
    def FontColor(self, value:'Color'):
        GetDllLibXls().XlsConditionalFormat_set_FontColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_FontColor, self.Ptr, value.Ptr)

    @property

    def Underline(self)->'FontUnderlineType':
        """
        Underline type.

        """
        GetDllLibXls().XlsConditionalFormat_get_Underline.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_Underline.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_Underline, self.Ptr)
        objwraped = FontUnderlineType(ret)
        return objwraped

    @Underline.setter
    def Underline(self, value:'FontUnderlineType'):
        GetDllLibXls().XlsConditionalFormat_set_Underline.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_Underline, self.Ptr, value.value)

    @property
    def IsStrikeThrough(self)->bool:
        """
        Indicates whether font is striked through.

        """
        GetDllLibXls().XlsConditionalFormat_get_IsStrikeThrough.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IsStrikeThrough.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IsStrikeThrough, self.Ptr)
        return ret

    @IsStrikeThrough.setter
    def IsStrikeThrough(self, value:bool):
        GetDllLibXls().XlsConditionalFormat_set_IsStrikeThrough.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_IsStrikeThrough, self.Ptr, value)

    @property
    def IsSuperScript(self)->bool:
        """
        Indicates whether font is superscript.

        """
        GetDllLibXls().XlsConditionalFormat_get_IsSuperScript.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IsSuperScript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IsSuperScript, self.Ptr)
        return ret

    @IsSuperScript.setter
    def IsSuperScript(self, value:bool):
        GetDllLibXls().XlsConditionalFormat_set_IsSuperScript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_IsSuperScript, self.Ptr, value)

    @property
    def IsSubScript(self)->bool:
        """
        Indicates whether font is subscript.

        """
        GetDllLibXls().XlsConditionalFormat_get_IsSubScript.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IsSubScript.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IsSubScript, self.Ptr)
        return ret

    @IsSubScript.setter
    def IsSubScript(self, value:bool):
        GetDllLibXls().XlsConditionalFormat_set_IsSubScript.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_IsSubScript, self.Ptr, value)

    @property

    def KnownColor(self)->'ExcelColors':
        """
        Pattern foreground excel color.

        """
        GetDllLibXls().XlsConditionalFormat_get_KnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_KnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsConditionalFormat_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_KnownColor, self.Ptr, value.value)

    @property

    def Color(self)->'Color':
        """
        Pattern foreground color.

        """
        GetDllLibXls().XlsConditionalFormat_get_Color.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_Color, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        GetDllLibXls().XlsConditionalFormat_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_Color, self.Ptr, value.Ptr)

    @property

    def BackKnownColor(self)->'ExcelColors':
        """
        Pattern background excel color.

        """
        GetDllLibXls().XlsConditionalFormat_get_BackKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_BackKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_BackKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @BackKnownColor.setter
    def BackKnownColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsConditionalFormat_set_BackKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_BackKnownColor, self.Ptr, value.value)

    @property

    def BackColor(self)->'Color':
        """
        Pattern background color.

        """
        GetDllLibXls().XlsConditionalFormat_get_BackColor.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_BackColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_BackColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @BackColor.setter
    def BackColor(self, value:'Color'):
        GetDllLibXls().XlsConditionalFormat_set_BackColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_BackColor, self.Ptr, value.Ptr)

    @property

    def FillPattern(self)->'ExcelPatternType':
        """
        XlsFill pattern type.

        """
        GetDllLibXls().XlsConditionalFormat_get_FillPattern.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_FillPattern.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_FillPattern, self.Ptr)
        objwraped = ExcelPatternType(ret)
        return objwraped

    @FillPattern.setter
    def FillPattern(self, value:'ExcelPatternType'):
        GetDllLibXls().XlsConditionalFormat_set_FillPattern.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_FillPattern, self.Ptr, value.value)

    @property
    def IsFontFormatPresent(self)->bool:
        """
        Indicates whether contains font formatting.

        """
        GetDllLibXls().XlsConditionalFormat_get_IsFontFormatPresent.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IsFontFormatPresent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IsFontFormatPresent, self.Ptr)
        return ret

    @IsFontFormatPresent.setter
    def IsFontFormatPresent(self, value:bool):
        GetDllLibXls().XlsConditionalFormat_set_IsFontFormatPresent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_IsFontFormatPresent, self.Ptr, value)

    @property
    def IsBorderFormatPresent(self)->bool:
        """
        Indicates whether contains border formatting.

        """
        GetDllLibXls().XlsConditionalFormat_get_IsBorderFormatPresent.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IsBorderFormatPresent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IsBorderFormatPresent, self.Ptr)
        return ret

    @IsBorderFormatPresent.setter
    def IsBorderFormatPresent(self, value:bool):
        GetDllLibXls().XlsConditionalFormat_set_IsBorderFormatPresent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_IsBorderFormatPresent, self.Ptr, value)

    @property
    def IsPatternFormatPresent(self)->bool:
        """
        Indicates whether contains pattern formatting.

        """
        GetDllLibXls().XlsConditionalFormat_get_IsPatternFormatPresent.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IsPatternFormatPresent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IsPatternFormatPresent, self.Ptr)
        return ret

    @IsPatternFormatPresent.setter
    def IsPatternFormatPresent(self, value:bool):
        GetDllLibXls().XlsConditionalFormat_set_IsPatternFormatPresent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_IsPatternFormatPresent, self.Ptr, value)

    @property
    def IsFontColorPresent(self)->bool:
        """
        Indicates whether format color present.

        """
        GetDllLibXls().XlsConditionalFormat_get_IsFontColorPresent.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IsFontColorPresent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IsFontColorPresent, self.Ptr)
        return ret

    @IsFontColorPresent.setter
    def IsFontColorPresent(self, value:bool):
        GetDllLibXls().XlsConditionalFormat_set_IsFontColorPresent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_IsFontColorPresent, self.Ptr, value)

    @property
    def IsPatternColorPresent(self)->bool:
        """
        Indicates whether presents pattern color.

        """
        GetDllLibXls().XlsConditionalFormat_get_IsPatternColorPresent.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IsPatternColorPresent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IsPatternColorPresent, self.Ptr)
        return ret

    @IsPatternColorPresent.setter
    def IsPatternColorPresent(self, value:bool):
        GetDllLibXls().XlsConditionalFormat_set_IsPatternColorPresent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_IsPatternColorPresent, self.Ptr, value)

    @property
    def IsPatternStyleModified(self)->bool:
        """
        Indicates whether pattern style was modified.

        """
        GetDllLibXls().XlsConditionalFormat_get_IsPatternStyleModified.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IsPatternStyleModified.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IsPatternStyleModified, self.Ptr)
        return ret

    @IsPatternStyleModified.setter
    def IsPatternStyleModified(self, value:bool):
        GetDllLibXls().XlsConditionalFormat_set_IsPatternStyleModified.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_IsPatternStyleModified, self.Ptr, value)

    @property
    def IsBackgroundColorPresent(self)->bool:
        """
        Indicates whether background color present.

        """
        GetDllLibXls().XlsConditionalFormat_get_IsBackgroundColorPresent.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IsBackgroundColorPresent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IsBackgroundColorPresent, self.Ptr)
        return ret

    @IsBackgroundColorPresent.setter
    def IsBackgroundColorPresent(self, value:bool):
        GetDllLibXls().XlsConditionalFormat_set_IsBackgroundColorPresent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_IsBackgroundColorPresent, self.Ptr, value)

    @property
    def IsLeftBorderModified(self)->bool:
        """
        Indicates whether left border style and color are modified.

        """
        GetDllLibXls().XlsConditionalFormat_get_IsLeftBorderModified.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IsLeftBorderModified.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IsLeftBorderModified, self.Ptr)
        return ret

    @IsLeftBorderModified.setter
    def IsLeftBorderModified(self, value:bool):
        GetDllLibXls().XlsConditionalFormat_set_IsLeftBorderModified.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_IsLeftBorderModified, self.Ptr, value)

    @property
    def IsRightBorderModified(self)->bool:
        """
        Indicates right border style and color modified.

        """
        GetDllLibXls().XlsConditionalFormat_get_IsRightBorderModified.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IsRightBorderModified.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IsRightBorderModified, self.Ptr)
        return ret

    @IsRightBorderModified.setter
    def IsRightBorderModified(self, value:bool):
        GetDllLibXls().XlsConditionalFormat_set_IsRightBorderModified.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_IsRightBorderModified, self.Ptr, value)

    @property
    def IsTopBorderModified(self)->bool:
        """
        Indicates whether top border style and color are modified.

        """
        GetDllLibXls().XlsConditionalFormat_get_IsTopBorderModified.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IsTopBorderModified.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IsTopBorderModified, self.Ptr)
        return ret

    @IsTopBorderModified.setter
    def IsTopBorderModified(self, value:bool):
        GetDllLibXls().XlsConditionalFormat_set_IsTopBorderModified.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_IsTopBorderModified, self.Ptr, value)

    @property
    def IsBottomBorderModified(self)->bool:
        """
        Indicates whether bottom border style and color are modified.

        """
        GetDllLibXls().XlsConditionalFormat_get_IsBottomBorderModified.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_IsBottomBorderModified.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_IsBottomBorderModified, self.Ptr)
        return ret

    @IsBottomBorderModified.setter
    def IsBottomBorderModified(self, value:bool):
        GetDllLibXls().XlsConditionalFormat_set_IsBottomBorderModified.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsConditionalFormat_set_IsBottomBorderModified, self.Ptr, value)

    @property

    def DataBar(self)->'DataBar':
        """Gets the data bar object associated with this conditional format.
        
        The data bar is a visual indicator that shows the relative value of a cell
        compared to other cells in the selected range using a colored bar.
        Valid only for conditional format type DataBar.
        
        Returns:
            DataBar: An object representing the data bar used in this conditional format.
        """
        GetDllLibXls().XlsConditionalFormat_get_DataBar.argtypes=[c_void_p]
        GetDllLibXls().XlsConditionalFormat_get_DataBar.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsConditionalFormat_get_DataBar, self.Ptr)
        ret = None if intPtr==None else DataBar(intPtr)
        return ret


