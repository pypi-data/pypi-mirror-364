from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsStyle (  AddtionalFormatWrapper, INamedObject) :
    """Represents a style in an Excel workbook.
    
    This class extends AddtionalFormatWrapper and implements INamedObject to provide
    functionality for named cell styles in Excel. It allows access to style properties
    and supports operations like cloning and comparing styles.
    """
    @property

    def Name(self)->str:
        """Gets the name of the style.
        
        Returns:
            str: The name of the style.
        """
        GetDllLibXls().XlsStyle_get_Name.argtypes=[c_void_p]
        GetDllLibXls().XlsStyle_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsStyle_get_Name, self.Ptr))
        return ret


    @property
    def IsInitialized(self)->bool:
        """Gets whether the style has been initialized.
        
        Returns:
            bool: True if the style has been initialized; otherwise, False.
        """
        GetDllLibXls().XlsStyle_get_IsInitialized.argtypes=[c_void_p]
        GetDllLibXls().XlsStyle_get_IsInitialized.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsStyle_get_IsInitialized, self.Ptr)
        return ret

    @property
    def BuiltIn(self)->bool:
        """Gets whether the style is a built-in style.
        
        Returns:
            bool: True if the style is a built-in style; otherwise, False.
        """
        GetDllLibXls().XlsStyle_get_BuiltIn.argtypes=[c_void_p]
        GetDllLibXls().XlsStyle_get_BuiltIn.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsStyle_get_BuiltIn, self.Ptr)
        return ret

    @property
    def Index(self)->int:
        """Gets the index of the style in the workbook's style collection.
        
        Returns:
            int: The zero-based index of the style.
        """
        GetDllLibXls().XlsStyle_get_Index.argtypes=[c_void_p]
        GetDllLibXls().XlsStyle_get_Index.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsStyle_get_Index, self.Ptr)
        return ret


    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """Creates a copy of the style.
        
        Args:
            parent (SpireObject): The parent object for the cloned style.
            
        Returns:
            SpireObject: A new instance of the style.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsStyle_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsStyle_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsStyle_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def CompareTo(self ,obj:'SpireObject')->int:
        """Compares this style with another object.
        
        Args:
            obj (SpireObject): The object to compare with this style.
            
        Returns:
            int: A value indicating the relative order of the objects being compared.
                 Less than zero: This instance precedes obj.
                 Zero: This instance equals obj.
                 Greater than zero: This instance follows obj.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibXls().XlsStyle_CompareTo.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsStyle_CompareTo.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsStyle_CompareTo, self.Ptr, intPtrobj)
        return ret

    def BeginUpdate(self):
        """Begins a batch update operation on the style.
        
        This method marks the start of a series of changes to the style properties.
        For better performance, multiple property changes should be made between
        BeginUpdate and EndUpdate calls.
        """
        GetDllLibXls().XlsStyle_BeginUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsStyle_BeginUpdate, self.Ptr)

    def EndUpdate(self):
        """Ends a batch update operation on the style.
        
        This method applies all pending changes to the style properties that were
        made since the last BeginUpdate call.
        """
        GetDllLibXls().XlsStyle_EndUpdate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsStyle_EndUpdate, self.Ptr)

    @staticmethod

    def DEF_DEFAULT_STYLES()->List[str]:
        """Gets a list of default style names.
        
        Returns:
            List[str]: A list containing the names of default styles.
        """
        #GetDllLibXls().XlsStyle_DEF_DEFAULT_STYLES.argtypes=[]
        GetDllLibXls().XlsStyle_DEF_DEFAULT_STYLES.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().XlsStyle_DEF_DEFAULT_STYLES)
        ret = GetVectorFromArray(intPtrArray, c_wchar_p)
        return ret

