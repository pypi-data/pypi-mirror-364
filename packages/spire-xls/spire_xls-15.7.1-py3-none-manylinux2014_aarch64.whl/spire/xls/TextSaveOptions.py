from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class TextSaveOptions (SpireObject) :
    """Options for saving Excel files to text formats.
    
    This class provides configuration options for controlling how Excel files
    are exported to text-based formats such as CSV or TSV. It allows customization
    of separator characters, encoding, and data inclusion settings.
    """
    @property
    def RetainHiddenData(self)->bool:
        """Gets or sets whether to retain hidden data in the output text file.
        
        When set to True, hidden rows, columns, and sheets will be included in the
        exported text file. Default is True.
        
        Returns:
            bool: True if hidden data should be retained; otherwise, False.
        """
        GetDllLibXls().TextSaveOptions_get_RetainHiddenData.argtypes=[c_void_p]
        GetDllLibXls().TextSaveOptions_get_RetainHiddenData.restype=c_bool
        ret = CallCFunction(GetDllLibXls().TextSaveOptions_get_RetainHiddenData, self.Ptr)
        return ret

    @RetainHiddenData.setter
    def RetainHiddenData(self, value:bool):
        GetDllLibXls().TextSaveOptions_set_RetainHiddenData.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().TextSaveOptions_set_RetainHiddenData, self.Ptr, value)

    @property
    def RetainBlankRowsAndCols(self)->bool:
        """Gets or sets whether to retain blank rows and columns in the output text file.
        
        When set to True, empty rows and columns will be included in the exported text file.
        Default is False.
        
        Returns:
            bool: True if blank rows and columns should be retained; otherwise, False.
        """
        GetDllLibXls().TextSaveOptions_get_RetainBlankRowsAndCols.argtypes=[c_void_p]
        GetDllLibXls().TextSaveOptions_get_RetainBlankRowsAndCols.restype=c_bool
        ret = CallCFunction(GetDllLibXls().TextSaveOptions_get_RetainBlankRowsAndCols, self.Ptr)
        return ret

    @RetainBlankRowsAndCols.setter
    def RetainBlankRowsAndCols(self, value:bool):
        GetDllLibXls().TextSaveOptions_set_RetainBlankRowsAndCols.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().TextSaveOptions_set_RetainBlankRowsAndCols, self.Ptr, value)

    @property

    def Separator(self)->str:
        """Gets or sets the separator character for the output text file.
        
        This character is used to separate values in the text file.
        Default is a comma (",").
        
        Returns:
            str: The separator character.
        """
        GetDllLibXls().TextSaveOptions_get_Separator.argtypes=[c_void_p]
        GetDllLibXls().TextSaveOptions_get_Separator.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().TextSaveOptions_get_Separator, self.Ptr))
        return ret


    @Separator.setter
    def Separator(self, value:str):
        GetDllLibXls().TextSaveOptions_set_Separator.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().TextSaveOptions_set_Separator, self.Ptr, value)

    @property

    def Encoding(self)->'Encoding':
        """Gets or sets the character encoding for the output text file.
        
        This determines the character encoding used when writing the text file.
        Default is UTF-8.
        
        Returns:
            Encoding: The character encoding object.
        """
        GetDllLibXls().TextSaveOptions_get_Encoding.argtypes=[c_void_p]
        GetDllLibXls().TextSaveOptions_get_Encoding.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().TextSaveOptions_get_Encoding, self.Ptr)
        ret = None if intPtr==None else Encoding(intPtr)
        return ret


    @Encoding.setter
    def Encoding(self, value:'Encoding'):
        GetDllLibXls().TextSaveOptions_set_Encoding.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().TextSaveOptions_set_Encoding, self.Ptr, value.Ptr)

