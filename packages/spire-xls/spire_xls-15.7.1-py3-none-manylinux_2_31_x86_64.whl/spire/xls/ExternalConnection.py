from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ExternalConnection (SpireObject) :
    """Represents an external connection in an Excel workbook.
    
    This class provides properties and methods for managing external connections
    to data sources, such as databases, web queries, or text files. It allows for
    configuring connection settings and refresh behavior.
    """
    @property

    def ID(self)->str:
        """Gets the unique identifier of the external connection.
        
        Returns:
            str: The unique identifier of the connection.
        """
        GetDllLibXls().ExternalConnection_get_ID.argtypes=[c_void_p]
        GetDllLibXls().ExternalConnection_get_ID.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ExternalConnection_get_ID, self.Ptr))
        return ret


    @property

    def Name(self)->str:
        """Gets or sets the name of the external connection.
        
        Returns:
            str: The name of the connection.
        """
        GetDllLibXls().ExternalConnection_get_Name.argtypes=[c_void_p]
        GetDllLibXls().ExternalConnection_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ExternalConnection_get_Name, self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        """Sets the name of the external connection.
        
        Args:
            value (str): The name to set for the connection.
        """
        GetDllLibXls().ExternalConnection_set_Name.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ExternalConnection_set_Name, self.Ptr, value)

    @property

    def ConnType(self)->'ConnectionDataSourceType':
        """Gets the type of the external connection.
        
        Returns:
            ConnectionDataSourceType: An enumeration value representing the connection type.
        """
        GetDllLibXls().ExternalConnection_get_ConnType.argtypes=[c_void_p]
        GetDllLibXls().ExternalConnection_get_ConnType.restype=c_int
        ret = CallCFunction(GetDllLibXls().ExternalConnection_get_ConnType, self.Ptr)
        objwraped = ConnectionDataSourceType(ret)
        return objwraped

    @property
    def BackgroundRefresh(self)->bool:
        """Gets or sets whether data is refreshed in the background.
        
        When True, data is refreshed asynchronously without blocking the user interface.
        
        Returns:
            bool: True if background refresh is enabled; False otherwise.
        """
        GetDllLibXls().ExternalConnection_get_BackgroundRefresh.argtypes=[c_void_p]
        GetDllLibXls().ExternalConnection_get_BackgroundRefresh.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExternalConnection_get_BackgroundRefresh, self.Ptr)
        return ret

    @BackgroundRefresh.setter
    def BackgroundRefresh(self, value:bool):
        """Sets whether data is refreshed in the background.
        
        Args:
            value (bool): True to enable background refresh; False otherwise.
        """
        GetDllLibXls().ExternalConnection_set_BackgroundRefresh.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExternalConnection_set_BackgroundRefresh, self.Ptr, value)

    @property

    def RefreshedVersion(self)->str:
        """Gets or sets the version of the connection when it was last refreshed.
        
        Returns:
            str: The version string of the connection when last refreshed.
        """
        GetDllLibXls().ExternalConnection_get_RefreshedVersion.argtypes=[c_void_p]
        GetDllLibXls().ExternalConnection_get_RefreshedVersion.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ExternalConnection_get_RefreshedVersion, self.Ptr))
        return ret


    @RefreshedVersion.setter
    def RefreshedVersion(self, value:str):
        """Sets the version of the connection when it was last refreshed.
        
        Args:
            value (str): The version string to set.
        """
        GetDllLibXls().ExternalConnection_set_RefreshedVersion.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ExternalConnection_set_RefreshedVersion, self.Ptr, value)

    @property
    def SaveData(self)->bool:
        """Gets or sets whether to save the external data with the workbook.
        
        When True, the external data is saved with the workbook, allowing offline access.
        
        Returns:
            bool: True if external data is saved with the workbook; False otherwise.
        """
        GetDllLibXls().ExternalConnection_get_SaveData.argtypes=[c_void_p]
        GetDllLibXls().ExternalConnection_get_SaveData.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExternalConnection_get_SaveData, self.Ptr)
        return ret

    @SaveData.setter
    def SaveData(self, value:bool):
        """Sets whether to save the external data with the workbook.
        
        Args:
            value (bool): True to save external data with the workbook; False otherwise.
        """
        GetDllLibXls().ExternalConnection_set_SaveData.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExternalConnection_set_SaveData, self.Ptr, value)

    @property

    def OdcFile(self)->str:
        """Gets or sets the path to the Office Data Connection (ODC) file.
        
        Returns:
            str: The path to the ODC file.
        """
        GetDllLibXls().ExternalConnection_get_OdcFile.argtypes=[c_void_p]
        GetDllLibXls().ExternalConnection_get_OdcFile.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().ExternalConnection_get_OdcFile, self.Ptr))
        return ret


    @OdcFile.setter
    def OdcFile(self, value:str):
        """Sets the path to the Office Data Connection (ODC) file.
        
        Args:
            value (str): The path to the ODC file.
        """
        GetDllLibXls().ExternalConnection_set_OdcFile.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().ExternalConnection_set_OdcFile, self.Ptr, value)

    @property
    def KeepAlive(self)->bool:
        """Gets or sets whether to maintain the connection open.
        
        When True, the connection is kept open after refreshing the data.
        
        Returns:
            bool: True if the connection is kept alive; False otherwise.
        """
        GetDllLibXls().ExternalConnection_get_KeepAlive.argtypes=[c_void_p]
        GetDllLibXls().ExternalConnection_get_KeepAlive.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExternalConnection_get_KeepAlive, self.Ptr)
        return ret

    @KeepAlive.setter
    def KeepAlive(self, value:bool):
        """Sets whether to maintain the connection open.
        
        Args:
            value (bool): True to keep the connection alive; False otherwise.
        """
        GetDllLibXls().ExternalConnection_set_KeepAlive.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExternalConnection_set_KeepAlive, self.Ptr, value)

    @property
    def OnlyUseConnectionFile(self)->bool:
        """Gets or sets whether to use only the connection file.
        
        When True, only the connection file is used for refreshing data,
        ignoring any connection information stored in the workbook.
        
        Returns:
            bool: True if only the connection file is used; False otherwise.
        """
        GetDllLibXls().ExternalConnection_get_OnlyUseConnectionFile.argtypes=[c_void_p]
        GetDllLibXls().ExternalConnection_get_OnlyUseConnectionFile.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ExternalConnection_get_OnlyUseConnectionFile, self.Ptr)
        return ret

    @OnlyUseConnectionFile.setter
    def OnlyUseConnectionFile(self, value:bool):
        """Sets whether to use only the connection file.
        
        Args:
            value (bool): True to use only the connection file; False otherwise.
        """
        GetDllLibXls().ExternalConnection_set_OnlyUseConnectionFile.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ExternalConnection_set_OnlyUseConnectionFile, self.Ptr, value)

