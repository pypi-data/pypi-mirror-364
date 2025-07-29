from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsValidation (  IDataValidation, IExcelApplication, IOptimizedUpdate, ICloneParent) :
    """Represents a data validation rule in an Excel worksheet.
    
    This class provides functionality for creating and managing data validation rules
    that restrict the type of data or values users can enter into a cell or range.
    It implements IDataValidation, IExcelApplication, IOptimizedUpdate, and ICloneParent interfaces.
    """
    @property

    def InputTitle(self)->str:
        """Gets or sets the title of the input message box.
        
        The input message appears when a user selects a cell with data validation.
        
        Returns:
            str: The title of the input message box.
        """
        GetDllLibXls().XlsValidation_get_InputTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_InputTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsValidation_get_InputTitle, self.Ptr))
        return ret


    @InputTitle.setter
    def InputTitle(self, value:str):
        """Sets the title of the input message box.
        
        Args:
            value (str): The title text to display in the input message box.
        """
        GetDllLibXls().XlsValidation_set_InputTitle.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsValidation_set_InputTitle, self.Ptr, value)

    @property

    def InputMessage(self)->str:
        """Gets or sets the message of the input message box.
        
        The input message appears when a user selects a cell with data validation.
        
        Returns:
            str: The message content of the input message box.
        """
        GetDllLibXls().XlsValidation_get_InputMessage.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_InputMessage.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsValidation_get_InputMessage, self.Ptr))
        return ret


    @InputMessage.setter
    def InputMessage(self, value:str):
        """Sets the message of the input message box.
        
        Args:
            value (str): The message text to display in the input message box.
        """
        GetDllLibXls().XlsValidation_set_InputMessage.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsValidation_set_InputMessage, self.Ptr, value)

    @property

    def ErrorTitle(self)->str:
        """Gets or sets the title of the error message box.
        
        The error message appears when a user enters invalid data in a cell with validation.
        
        Returns:
            str: The title of the error message box.
        """
        GetDllLibXls().XlsValidation_get_ErrorTitle.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_ErrorTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsValidation_get_ErrorTitle, self.Ptr))
        return ret


    @ErrorTitle.setter
    def ErrorTitle(self, value:str):
        """Sets the title of the error message box.
        
        Args:
            value (str): The title text to display in the error message box.
        """
        GetDllLibXls().XlsValidation_set_ErrorTitle.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsValidation_set_ErrorTitle, self.Ptr, value)

    @property

    def ErrorMessage(self)->str:
        """Gets or sets the message of the error message box.
        
        The error message appears when a user enters invalid data in a cell with validation.
        
        Returns:
            str: The message content of the error message box.
        """
        GetDllLibXls().XlsValidation_get_ErrorMessage.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_ErrorMessage.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsValidation_get_ErrorMessage, self.Ptr))
        return ret


    @ErrorMessage.setter
    def ErrorMessage(self, value:str):
        """Sets the message of the error message box.
        
        Args:
            value (str): The message text to display in the error message box.
        """
        GetDllLibXls().XlsValidation_set_ErrorMessage.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsValidation_set_ErrorMessage, self.Ptr, value)

    @property

    def Formula1(self)->str:
        """Gets or sets the first formula or value for the data validation.
        
        For most validation types, this property sets the minimum value or the only value
        used for validation.
        
        Returns:
            str: The first formula or value for validation.
        """
        GetDllLibXls().XlsValidation_get_Formula1.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_Formula1.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsValidation_get_Formula1, self.Ptr))
        return ret


    @Formula1.setter
    def Formula1(self, value:str):
        """Sets the first formula or value for the data validation.
        
        Args:
            value (str): The first formula or value for validation.
        """
        GetDllLibXls().XlsValidation_set_Formula1.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsValidation_set_Formula1, self.Ptr, value)

    @property

    def DateTime1(self)->'DateTime':
        """Gets or sets the first date/time value for the data validation.
        
        Used when validating date or time values, typically as the minimum value.
        
        Returns:
            DateTime: The first date/time value for validation.
        """
        GetDllLibXls().XlsValidation_get_DateTime1.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_DateTime1.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsValidation_get_DateTime1, self.Ptr)
        ret = None if intPtr==None else DateTime(intPtr)
        return ret


    @DateTime1.setter
    def DateTime1(self, value:'DateTime'):
        """Sets the first date/time value for the data validation.
        
        Args:
            value (DateTime): The first date/time value for validation.
        """
        GetDllLibXls().XlsValidation_set_DateTime1.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsValidation_set_DateTime1, self.Ptr, value.Ptr)

    @property

    def Formula2(self)->str:
        """Gets or sets the second formula or value for the data validation.
        
        For validation types that require a range (like between or not between),
        this property sets the maximum value.
        
        Returns:
            str: The second formula or value for validation.
        """
        GetDllLibXls().XlsValidation_get_Formula2.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_Formula2.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsValidation_get_Formula2, self.Ptr))
        return ret


    @Formula2.setter
    def Formula2(self, value:str):
        """Sets the second formula or value for the data validation.
        
        Args:
            value (str): The second formula or value for validation.
        """
        GetDllLibXls().XlsValidation_set_Formula2.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsValidation_set_Formula2, self.Ptr, value)

    @property

    def DateTime2(self)->'DateTime':
        """Gets or sets the second date/time value for the data validation.
        
        Used when validating date or time values with a range, typically as the maximum value.
        
        Returns:
            DateTime: The second date/time value for validation.
        """
        GetDllLibXls().XlsValidation_get_DateTime2.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_DateTime2.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsValidation_get_DateTime2, self.Ptr)
        ret = None if intPtr==None else DateTime(intPtr)
        return ret


    @DateTime2.setter
    def DateTime2(self, value:'DateTime'):
        """Sets the second date/time value for the data validation.
        
        Args:
            value (DateTime): The second date/time value for validation.
        """
        GetDllLibXls().XlsValidation_set_DateTime2.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsValidation_set_DateTime2, self.Ptr, value.Ptr)

    @property

    def AllowType(self)->'CellDataType':
        """Gets or sets the data type allowed in the cell or range.
        
        This property determines what type of data is valid for the cells with validation.
        
        Returns:
            CellDataType: The data type allowed for validation.
        """
        GetDllLibXls().XlsValidation_get_AllowType.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_AllowType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsValidation_get_AllowType, self.Ptr)
        objwraped = CellDataType(ret)
        return objwraped

    @AllowType.setter
    def AllowType(self, value:'CellDataType'):
        """Sets the data type allowed in the cell or range.
        
        Args:
            value (CellDataType): The data type to allow for validation.
        """
        GetDllLibXls().XlsValidation_set_AllowType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsValidation_set_AllowType, self.Ptr, value.value)

    @property

    def CompareOperator(self)->'ValidationComparisonOperator':
        """Gets or sets the comparison operator for the data validation.
        
        This property determines how the cell's value is compared against the validation criteria.
        
        Returns:
            ValidationComparisonOperator: The comparison operator for validation.
        """
        GetDllLibXls().XlsValidation_get_CompareOperator.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_CompareOperator.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsValidation_get_CompareOperator, self.Ptr)
        objwraped = ValidationComparisonOperator(ret)
        return objwraped

    @CompareOperator.setter
    def CompareOperator(self, value:'ValidationComparisonOperator'):
        """Sets the comparison operator for the data validation.
        
        Args:
            value (ValidationComparisonOperator): The comparison operator to use for validation.
        """
        GetDllLibXls().XlsValidation_set_CompareOperator.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsValidation_set_CompareOperator, self.Ptr, value.value)

    @property
    def IsListInFormula(self)->bool:
        """Gets or sets whether the validation list is in a formula.
        
        When True, the Formula1 property contains a formula that evaluates to a list.
        When False, Formula1 contains a comma-separated list of values.
        
        Returns:
            bool: True if the validation list is in a formula; otherwise, False.
        """
        GetDllLibXls().XlsValidation_get_IsListInFormula.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_IsListInFormula.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsValidation_get_IsListInFormula, self.Ptr)
        return ret

    @IsListInFormula.setter
    def IsListInFormula(self, value:bool):
        """Sets whether the validation list is in a formula.
        
        Args:
            value (bool): True to indicate the validation list is in a formula; otherwise, False.
        """
        GetDllLibXls().XlsValidation_set_IsListInFormula.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsValidation_set_IsListInFormula, self.Ptr, value)

    @property
    def IgnoreBlank(self)->bool:
        """Gets or sets whether blank values are allowed in the validated range.
        
        When True, empty cells are considered valid regardless of the validation criteria.
        
        Returns:
            bool: True if blank values are allowed; otherwise, False.
        """
        GetDllLibXls().XlsValidation_get_IgnoreBlank.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_IgnoreBlank.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsValidation_get_IgnoreBlank, self.Ptr)
        return ret

    @IgnoreBlank.setter
    def IgnoreBlank(self, value:bool):
        """Sets whether blank values are allowed in the validated range.
        
        Args:
            value (bool): True to allow blank values; otherwise, False.
        """
        GetDllLibXls().XlsValidation_set_IgnoreBlank.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsValidation_set_IgnoreBlank, self.Ptr, value)

    @property
    def IsSuppressDropDownArrow(self)->bool:
        """Gets or sets whether to suppress the dropdown arrow for list validation.
        
        When True, the dropdown arrow for list-type validation is not displayed.
        
        Returns:
            bool: True if the dropdown arrow is suppressed; otherwise, False.
        """
        GetDllLibXls().XlsValidation_get_IsSuppressDropDownArrow.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_IsSuppressDropDownArrow.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsValidation_get_IsSuppressDropDownArrow, self.Ptr)
        return ret

    @IsSuppressDropDownArrow.setter
    def IsSuppressDropDownArrow(self, value:bool):
        """Sets whether to suppress the dropdown arrow for list validation.
        
        Args:
            value (bool): True to suppress the dropdown arrow; otherwise, False.
        """
        GetDllLibXls().XlsValidation_set_IsSuppressDropDownArrow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsValidation_set_IsSuppressDropDownArrow, self.Ptr, value)

    @property
    def ShapesCount(self)->int:
        """Gets the count of shapes associated with this validation.
        
        Returns:
            int: The number of shapes associated with this validation.
        """
        GetDllLibXls().XlsValidation_get_ShapesCount.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_ShapesCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsValidation_get_ShapesCount, self.Ptr)
        return ret

    @property
    def ShowInput(self)->bool:
        """Gets or sets whether to display the input message when a cell is selected.
        
        When True, the input message (specified by InputTitle and InputMessage) is displayed
        when the user selects a cell with this validation.
        
        Returns:
            bool: True if the input message is displayed; otherwise, False.
        """
        GetDllLibXls().XlsValidation_get_ShowInput.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_ShowInput.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsValidation_get_ShowInput, self.Ptr)
        return ret

    @ShowInput.setter
    def ShowInput(self, value:bool):
        """Sets whether to display the input message when a cell is selected.
        
        Args:
            value (bool): True to display the input message; otherwise, False.
        """
        GetDllLibXls().XlsValidation_set_ShowInput.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsValidation_set_ShowInput, self.Ptr, value)

    @property
    def ShowError(self)->bool:
        """Gets or sets whether to display an error message when invalid data is entered.
        
        When True, the error message (specified by ErrorTitle and ErrorMessage) is displayed
        when the user enters invalid data in a cell with this validation.
        
        Returns:
            bool: True if the error message is displayed; otherwise, False.
        """
        GetDllLibXls().XlsValidation_get_ShowError.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_ShowError.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsValidation_get_ShowError, self.Ptr)
        return ret

    @ShowError.setter
    def ShowError(self, value:bool):
        """Sets whether to display an error message when invalid data is entered.
        
        Args:
            value (bool): True to display the error message; otherwise, False.
        """
        GetDllLibXls().XlsValidation_set_ShowError.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsValidation_set_ShowError, self.Ptr, value)

    @property
    def PromptBoxHPosition(self)->int:
        """Gets or sets the horizontal position of the input message box.
        
        Specifies the horizontal offset in pixels for the input message box.
        
        Returns:
            int: The horizontal position in pixels.
        """
        GetDllLibXls().XlsValidation_get_PromptBoxHPosition.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_PromptBoxHPosition.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsValidation_get_PromptBoxHPosition, self.Ptr)
        return ret

    @PromptBoxHPosition.setter
    def PromptBoxHPosition(self, value:int):
        """Sets the horizontal position of the input message box.
        
        Args:
            value (int): The horizontal position in pixels.
        """
        GetDllLibXls().XlsValidation_set_PromptBoxHPosition.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsValidation_set_PromptBoxHPosition, self.Ptr, value)

    @property
    def PromptBoxVPosition(self)->int:
        """Gets or sets the vertical position of the input message box.
        
        Specifies the vertical offset in pixels for the input message box.
        
        Returns:
            int: The vertical position in pixels.
        """
        GetDllLibXls().XlsValidation_get_PromptBoxVPosition.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_PromptBoxVPosition.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsValidation_get_PromptBoxVPosition, self.Ptr)
        return ret

    @PromptBoxVPosition.setter
    def PromptBoxVPosition(self, value:int):
        """Sets the vertical position of the input message box.
        
        Args:
            value (int): The vertical position in pixels.
        """
        GetDllLibXls().XlsValidation_set_PromptBoxVPosition.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsValidation_set_PromptBoxVPosition, self.Ptr, value)

    @property
    def IsInputVisible(self)->bool:
        """Gets or sets whether the input message box is visible.
        
        Controls the visibility of the input message box independently of ShowInput.
        
        Returns:
            bool: True if the input message box is visible; otherwise, False.
        """
        GetDllLibXls().XlsValidation_get_IsInputVisible.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_IsInputVisible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsValidation_get_IsInputVisible, self.Ptr)
        return ret

    @IsInputVisible.setter
    def IsInputVisible(self, value:bool):
        """Sets whether the input message box is visible.
        
        Args:
            value (bool): True to make the input message box visible; otherwise, False.
        """
        GetDllLibXls().XlsValidation_set_IsInputVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsValidation_set_IsInputVisible, self.Ptr, value)

    @property
    def IsInputPositionFixed(self)->bool:
        """Gets or sets whether the input message box position is fixed.
        
        When True, the input message box appears at the position specified by
        PromptBoxHPosition and PromptBoxVPosition. When False, the position is
        determined automatically.
        
        Returns:
            bool: True if the input message box position is fixed; otherwise, False.
        """
        GetDllLibXls().XlsValidation_get_IsInputPositionFixed.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_IsInputPositionFixed.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsValidation_get_IsInputPositionFixed, self.Ptr)
        return ret

    @IsInputPositionFixed.setter
    def IsInputPositionFixed(self, value:bool):
        """Sets whether the input message box position is fixed.
        
        Args:
            value (bool): True to fix the input message box position; otherwise, False.
        """
        GetDllLibXls().XlsValidation_set_IsInputPositionFixed.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsValidation_set_IsInputPositionFixed, self.Ptr, value)

    @property

    def AlertStyle(self)->'AlertStyleType':
        """Gets or sets the style of the error alert.
        
        Determines the icon and buttons displayed in the error message box
        when invalid data is entered.
        
        Returns:
            AlertStyleType: The style of the error alert.
        """
        GetDllLibXls().XlsValidation_get_AlertStyle.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_AlertStyle.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsValidation_get_AlertStyle, self.Ptr)
        objwraped = AlertStyleType(ret)
        return objwraped

    @AlertStyle.setter
    def AlertStyle(self, value:'AlertStyleType'):
        """Sets the style of the error alert.
        
        Args:
            value (AlertStyleType): The style of the error alert to use.
        """
        GetDllLibXls().XlsValidation_set_AlertStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsValidation_set_AlertStyle, self.Ptr, value.value)

    @property

    def Values(self)->List[str]:
        """Gets or sets the list of valid values for list-type validation.
        
        For list-type validation, this property contains the list of values
        that are considered valid.
        
        Returns:
            List[str]: The list of valid values.
        """
        GetDllLibXls().XlsValidation_get_Values.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_Values.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().XlsValidation_get_Values, self.Ptr)
        ret = GetVectorFromArray(intPtrArray, c_wchar_p)
        return ret

    @Values.setter
    def Values(self, value:List[str]):
        """Sets the list of valid values for list-type validation.
        
        Args:
            value (List[str]): The list of valid values.
        """
        vCount = len(value)
        ArrayType = c_wchar_p * vCount
        vArray = ArrayType()
        for i in range(0, vCount):
            vArray[i] = value[i]
        GetDllLibXls().XlsValidation_set_Values.argtypes=[c_void_p, ArrayType, c_int]
        CallCFunction(GetDllLibXls().XlsValidation_set_Values, self.Ptr, vArray, vCount)

    @property

    def DataRange(self)->'IXLSRange':
        """Gets or sets the cell range to which the data validation applies.
        
        This property specifies the range of cells that will have this validation rule applied.
        
        Returns:
            IXLSRange: The cell range with this validation rule.
        """
        GetDllLibXls().XlsValidation_get_DataRange.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_DataRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsValidation_get_DataRange, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @DataRange.setter
    def DataRange(self, value:'IXLSRange'):
        """Sets the cell range to which the data validation applies.
        
        Args:
            value (IXLSRange): The cell range to apply this validation rule to.
        """
        GetDllLibXls().XlsValidation_set_DataRange.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsValidation_set_DataRange, self.Ptr, value.Ptr)

    @dispatch

    def AddRange(self ,dv:'XlsValidation'):
        """Adds the range from another validation object to this validation.
        
        This method combines the range of cells from another validation object
        with the range of cells in this validation.
        
        Args:
            dv (XlsValidation): The validation object whose range to add.
        """
        intPtrdv:c_void_p = dv.Ptr

        GetDllLibXls().XlsValidation_AddRange.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsValidation_AddRange, self.Ptr, intPtrdv)

    @dispatch

    def AddRange(self ,range:XlsRange):
        """Adds a range of cells to this validation.
        
        This method extends the validation rule to apply to the specified range of cells.
        
        Args:
            range (XlsRange): The range of cells to add to this validation.
        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().XlsValidation_AddRangeR.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsValidation_AddRangeR, self.Ptr, intPtrrange)

#    @dispatch
#
#    def RemoveRange(self ,rectangles:'Rectangle[]'):
#        """
#
#        """
#        #arrayrectangles:ArrayTyperectangles = ""
#        countrectangles = len(rectangles)
#        ArrayTyperectangles = c_void_p * countrectangles
#        arrayrectangles = ArrayTyperectangles()
#        for i in range(0, countrectangles):
#            arrayrectangles[i] = rectangles[i].Ptr
#
#
#        GetDllLibXls().XlsValidation_RemoveRange.argtypes=[c_void_p ,ArrayTyperectangles]
#        CallCFunction(GetDllLibXls().XlsValidation_RemoveRange, self.Ptr, arrayrectangles)


    @dispatch

    def RemoveRange(self ,range:XlsRange):
        """Removes a range of cells from this validation.
        
        This method excludes the specified range of cells from this validation rule.
        
        Args:
            range (XlsRange): The range of cells to remove from this validation.
        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().XlsValidation_RemoveRangeR.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsValidation_RemoveRangeR, self.Ptr, intPtrrange)

    @property

    def Worksheet(self)->'XlsWorksheet':
        """Gets the worksheet that contains this validation rule.
        
        Returns:
            XlsWorksheet: The worksheet containing this validation rule.
        """
        GetDllLibXls().XlsValidation_get_Worksheet.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_Worksheet.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsValidation_get_Worksheet, self.Ptr)
        ret = None if intPtr==None else XlsWorksheet(intPtr)
        return ret



    def ContainsCell(self ,lCellIndex:int)->bool:
        """Determines whether the validation rule applies to a specific cell.
        
        Args:
            lCellIndex (int): The index of the cell to check.
            
        Returns:
            bool: True if the validation rule applies to the specified cell; otherwise, False.
        """
        
        GetDllLibXls().XlsValidation_ContainsCell.argtypes=[c_void_p ,c_long]
        GetDllLibXls().XlsValidation_ContainsCell.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsValidation_ContainsCell, self.Ptr, lCellIndex)
        return ret


    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """Creates a copy of this validation rule with the specified parent object.
        
        Args:
            parent (SpireObject): The parent object for the cloned validation rule.
            
        Returns:
            SpireObject: The cloned validation rule.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsValidation_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsValidation_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsValidation_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @property

    def Parent(self)->'SpireObject':
        """Gets the parent object of this validation rule.
        
        Returns:
            SpireObject: The parent object of this validation rule.
        """
        GetDllLibXls().XlsValidation_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsValidation_get_Parent, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @property

    def ParentCollection(self)->'XlsDataValidationCollection':
        """Gets or sets the collection that contains this validation rule.
        
        Returns:
            XlsDataValidationCollection: The collection containing this validation rule.
        """
        GetDllLibXls().XlsValidation_get_ParentCollection.argtypes=[c_void_p]
        GetDllLibXls().XlsValidation_get_ParentCollection.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsValidation_get_ParentCollection, self.Ptr)
        ret = None if intPtr==None else XlsDataValidationCollection(intPtr)
        return ret


    @ParentCollection.setter
    def ParentCollection(self, value:'XlsDataValidationCollection'):
        """Sets the collection that contains this validation rule.
        
        Args:
            value (XlsDataValidationCollection): The collection to contain this validation rule.
        """
        GetDllLibXls().XlsValidation_set_ParentCollection.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsValidation_set_ParentCollection, self.Ptr, value.Ptr)

    def BeginUpdate(self):
        """Begins a batch update operation on the validation rule.
        
        Call this method before making multiple changes to the validation rule
        to improve performance. Call EndUpdate when finished.
        """
        GetDllLibXls().XlsValidation_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsValidation_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """Ends a batch update operation on the validation rule.
        
        Call this method after calling BeginUpdate and making multiple changes
        to the validation rule.
        """
        GetDllLibXls().XlsValidation_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsValidation_EndUpdate, self.Ptr)

