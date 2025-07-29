from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsHyperLink (  XlsObject, IHyperLink, ICloneParent) :
    """Represents a hyperlink in an Excel worksheet.
    
    This class provides properties and methods for manipulating hyperlinks in Excel,
    including address, text display, screen tip, and range settings. It extends
    XlsObject and implements the IHyperLink and ICloneParent interfaces.
    """
    @property

    def Address(self)->str:
        """Gets or sets the URL or path of the hyperlink.
        
        Returns:
            str: The URL or path of the hyperlink.
        """
        GetDllLibXls().XlsHyperLink_get_Address.argtypes=[c_void_p]
        GetDllLibXls().XlsHyperLink_get_Address.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsHyperLink_get_Address, self.Ptr))
        return ret


    @Address.setter
    def Address(self, value:str):
        """Sets the URL or path of the hyperlink.
        
        Args:
            value (str): The URL or path of the hyperlink.
        """
        GetDllLibXls().XlsHyperLink_set_Address.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsHyperLink_set_Address, self.Ptr, value)

    @property

    def Name(self)->str:
        """Gets the name of the hyperlink.
        
        Returns:
            str: The name of the hyperlink.
        """
        GetDllLibXls().XlsHyperLink_get_Name.argtypes=[c_void_p]
        GetDllLibXls().XlsHyperLink_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsHyperLink_get_Name, self.Ptr))
        return ret


    @property

    def Range(self)->'IXLSRange':
        """Gets or sets the range that contains the hyperlink.
        
        Returns:
            IXLSRange: The range that contains the hyperlink.
        """
        from .XlsRange import XlsRange
        GetDllLibXls().XlsHyperLink_get_Range.argtypes=[c_void_p]
        GetDllLibXls().XlsHyperLink_get_Range.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsHyperLink_get_Range, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @Range.setter
    def Range(self, value:'IXLSRange'):
        """Sets the range that contains the hyperlink.
        
        Args:
            value (IXLSRange): The range that contains the hyperlink.
        """
        GetDllLibXls().XlsHyperLink_set_Range.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsHyperLink_set_Range, self.Ptr, value.Ptr)

    @property

    def ScreenTip(self)->str:
        """Gets or sets the screen tip text for the hyperlink.
        
        Returns:
            str: The screen tip text for the hyperlink.
        """
        GetDllLibXls().XlsHyperLink_get_ScreenTip.argtypes=[c_void_p]
        GetDllLibXls().XlsHyperLink_get_ScreenTip.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsHyperLink_get_ScreenTip, self.Ptr))
        return ret


    @ScreenTip.setter
    def ScreenTip(self, value:str):
        """Sets the screen tip text for the hyperlink.
        
        Args:
            value (str): The screen tip text for the hyperlink.
        """
        GetDllLibXls().XlsHyperLink_set_ScreenTip.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsHyperLink_set_ScreenTip, self.Ptr, value)

    @property

    def SubAddress(self)->str:
        """Gets or sets the sub-address of the hyperlink.
        
        The sub-address is typically used to link to a specific location within a document,
        such as a named range, bookmark, or cell reference.
        
        Returns:
            str: The sub-address of the hyperlink.
        """
        GetDllLibXls().XlsHyperLink_get_SubAddress.argtypes=[c_void_p]
        GetDllLibXls().XlsHyperLink_get_SubAddress.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsHyperLink_get_SubAddress, self.Ptr))
        return ret


    @SubAddress.setter
    def SubAddress(self, value:str):
        """Sets the sub-address of the hyperlink.
        
        Args:
            value (str): The sub-address of the hyperlink.
        """
        GetDllLibXls().XlsHyperLink_set_SubAddress.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsHyperLink_set_SubAddress, self.Ptr, value)


    def SetAddress(self ,strAddress:str,bSetText:bool):
        """Sets the address of the hyperlink and optionally updates the display text.
        
        Args:
            strAddress (str): The URL or path of the hyperlink.
            bSetText (bool): True to update the display text to match the address; otherwise, False.
        """
        
        GetDllLibXls().XlsHyperLink_SetAddress.argtypes=[c_void_p ,c_void_p,c_bool]
        CallCFunction(GetDllLibXls().XlsHyperLink_SetAddress, self.Ptr, strAddress,bSetText)


    def SetSubAddress(self ,strSubAddress:str):
        """Sets the sub-address of the hyperlink.
        
        Args:
            strSubAddress (str): The sub-address of the hyperlink.
        """
        
        GetDllLibXls().XlsHyperLink_SetSubAddress.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsHyperLink_SetSubAddress, self.Ptr, strSubAddress)

    @property

    def TextToDisplay(self)->str:
        """Gets or sets the text to be displayed for the hyperlink.
        
        The default value is the address of the hyperlink.
        
        Returns:
            str: The text to be displayed for the hyperlink.
        """
        GetDllLibXls().XlsHyperLink_get_TextToDisplay.argtypes=[c_void_p]
        GetDllLibXls().XlsHyperLink_get_TextToDisplay.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsHyperLink_get_TextToDisplay, self.Ptr))
        return ret


    @TextToDisplay.setter
    def TextToDisplay(self, value:str):
        """Sets the text to be displayed for the hyperlink.
        
        Args:
            value (str): The text to be displayed for the hyperlink.
        """
        GetDllLibXls().XlsHyperLink_set_TextToDisplay.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsHyperLink_set_TextToDisplay, self.Ptr, value)

    @property

    def Type(self)->'HyperLinkType':
        """Gets or sets the type of the hyperlink.
        
        Returns:
            HyperLinkType: An enumeration value representing the type of the hyperlink.
        """
        GetDllLibXls().XlsHyperLink_get_Type.argtypes=[c_void_p]
        GetDllLibXls().XlsHyperLink_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsHyperLink_get_Type, self.Ptr)
        objwraped = HyperLinkType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'HyperLinkType'):
        """Sets the type of the hyperlink.
        
        Args:
            value (HyperLinkType): An enumeration value representing the type of the hyperlink.
        """
        GetDllLibXls().XlsHyperLink_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsHyperLink_set_Type, self.Ptr, value.value)

    @property
    def FirstRow(self)->int:
        """Gets the first row of the range containing the hyperlink.
        
        Returns:
            int: The zero-based index of the first row.
        """
        GetDllLibXls().XlsHyperLink_get_FirstRow.argtypes=[c_void_p]
        GetDllLibXls().XlsHyperLink_get_FirstRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsHyperLink_get_FirstRow, self.Ptr)
        return ret

    @property
    def FirstColumn(self)->int:
        """Gets the first column of the range containing the hyperlink.
        
        Returns:
            int: The zero-based index of the first column.
        """
        GetDllLibXls().XlsHyperLink_get_FirstColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsHyperLink_get_FirstColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsHyperLink_get_FirstColumn, self.Ptr)
        return ret

    @property
    def LastRow(self)->int:
        """Gets the last row of the range containing the hyperlink.
        
        Returns:
            int: The zero-based index of the last row.
        """
        GetDllLibXls().XlsHyperLink_get_LastRow.argtypes=[c_void_p]
        GetDllLibXls().XlsHyperLink_get_LastRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsHyperLink_get_LastRow, self.Ptr)
        return ret

    @property

    def UnicodePath(self)->str:
        """Gets or sets the Unicode file path for the hyperlink.
        
        This property is only valid when the Type property is HyperLinkType.File.
        
        Returns:
            str: The Unicode file path for the hyperlink.
        """
        GetDllLibXls().XlsHyperLink_get_UnicodePath.argtypes=[c_void_p]
        GetDllLibXls().XlsHyperLink_get_UnicodePath.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsHyperLink_get_UnicodePath, self.Ptr))
        return ret


    @UnicodePath.setter
    def UnicodePath(self, value:str):
        """Sets the Unicode file path for the hyperlink.
        
        Args:
            value (str): The Unicode file path for the hyperlink.
        """
        GetDllLibXls().XlsHyperLink_set_UnicodePath.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsHyperLink_set_UnicodePath, self.Ptr, value)

    @property
    def LastColumn(self)->int:
        """Gets the last column of the range containing the hyperlink.
        
        Returns:
            int: The zero-based index of the last column.
        """
        GetDllLibXls().XlsHyperLink_get_LastColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsHyperLink_get_LastColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsHyperLink_get_LastColumn, self.Ptr)
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

        GetDllLibXls().XlsHyperLink_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsHyperLink_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsHyperLink_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


