from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ExternalLink (  XlsObject) :
    """Represents an external link in an Excel workbook.
    
    This class provides functionality to manage external links to other workbooks or data sources.
    External links allow data to be referenced from external sources and updated when the workbook
    is opened or when links are refreshed.
    """
    @property

    def DataSource(self)->str:
        """Gets or sets the data source path for the external link.
        
        The data source typically represents the path to the external workbook or data file.
        
        Returns:
            str: The path to the external data source.
        """
        GetDllLibXls().ExternalLink_get_DataSource.argtypes=[c_void_p]
        GetDllLibXls().ExternalLink_get_DataSource.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ExternalLink_get_DataSource, self.Ptr))
        return ret


    @DataSource.setter
    def DataSource(self, value:str):
        GetDllLibXls().ExternalLink_set_DataSource.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ExternalLink_set_DataSource, self.Ptr, value)

    @property
    def IsReferred(self)->bool:
        """Gets whether the external link is being referenced by any formulas or other elements.
        
        Returns:
            bool: True if the external link is being referenced; otherwise, False.
        """
        GetDllLibXls().ExternalLink_get_IsReferred.argtypes=[c_void_p]
        GetDllLibXls().ExternalLink_get_IsReferred.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExternalLink_get_IsReferred, self.Ptr)
        return ret

    @property
    def IsVisible(self)->bool:
        """Gets whether the external link is visible in the workbook.
        
        Returns:
            bool: True if the external link is visible; otherwise, False.
        """
        GetDllLibXls().ExternalLink_get_IsVisible.argtypes=[c_void_p]
        GetDllLibXls().ExternalLink_get_IsVisible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExternalLink_get_IsVisible, self.Ptr)
        return ret


    def AddExternalName(self ,text:str,referTo:str):
        """Adds an external name to the external link.
        
        External names are defined names that reference cells or ranges in external workbooks.
        
        Args:
            text (str): The name of the external reference.
            referTo (str): The formula or reference that the external name points to.
        """
        
        GetDllLibXls().ExternalLink_AddExternalName.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().ExternalLink_AddExternalName, self.Ptr, text,referTo)

