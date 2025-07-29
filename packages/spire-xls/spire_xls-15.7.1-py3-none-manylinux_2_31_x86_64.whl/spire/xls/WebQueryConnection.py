from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class WebQueryConnection (  ExternalConnection) :
    """Represents a web query connection in Excel.
    
    This class extends ExternalConnection and provides functionality for managing
    web query connections, which allow Excel to retrieve data from web pages.
    It includes properties for configuring connection settings such as URL,
    refresh options, and data handling preferences.
    """
    @property

    def ID(self)->str:
        """Gets the unique identifier for the web query connection.
        
        Returns:
            str: The connection ID string.
        """
        GetDllLibXls().WebQueryConnection_get_ID.argtypes=[c_void_p]
        GetDllLibXls().WebQueryConnection_get_ID.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().WebQueryConnection_get_ID, self.Ptr))
        return ret


    @property

    def Name(self)->str:
        """Gets or sets the name of the web query connection.
        
        Returns:
            str: The connection name.
        """
        GetDllLibXls().WebQueryConnection_get_Name.argtypes=[c_void_p]
        GetDllLibXls().WebQueryConnection_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().WebQueryConnection_get_Name, self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        GetDllLibXls().WebQueryConnection_set_Name.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().WebQueryConnection_set_Name, self.Ptr, value)

    @property

    def ConnType(self)->'ConnectionDataSourceType':
        """Gets the data source type for the connection.
        
        Returns:
            ConnectionDataSourceType: The connection data source type.
        """
        GetDllLibXls().WebQueryConnection_get_ConnType.argtypes=[c_void_p]
        GetDllLibXls().WebQueryConnection_get_ConnType.restype=c_int
        ret = CallCFunction(GetDllLibXls().WebQueryConnection_get_ConnType, self.Ptr)
        objwraped = ConnectionDataSourceType(ret)
        return objwraped

    @property
    def BackgroundRefresh(self)->bool:
        """Gets or sets whether data should be refreshed in the background.
        
        When set to True, Excel will refresh the data in the background without
        blocking the user interface.
        
        Returns:
            bool: True if background refresh is enabled; otherwise, False.
        """
        GetDllLibXls().WebQueryConnection_get_BackgroundRefresh.argtypes=[c_void_p]
        GetDllLibXls().WebQueryConnection_get_BackgroundRefresh.restype=c_bool
        ret = CallCFunction(GetDllLibXls().WebQueryConnection_get_BackgroundRefresh, self.Ptr)
        return ret

    @BackgroundRefresh.setter
    def BackgroundRefresh(self, value:bool):
        GetDllLibXls().WebQueryConnection_set_BackgroundRefresh.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().WebQueryConnection_set_BackgroundRefresh, self.Ptr, value)

    @property

    def RefreshedVersion(self)->str:
        """Gets or sets the version of the connection when it was last refreshed.
        
        Returns:
            str: The version string.
        """
        GetDllLibXls().WebQueryConnection_get_RefreshedVersion.argtypes=[c_void_p]
        GetDllLibXls().WebQueryConnection_get_RefreshedVersion.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().WebQueryConnection_get_RefreshedVersion, self.Ptr))
        return ret


    @RefreshedVersion.setter
    def RefreshedVersion(self, value:str):
        GetDllLibXls().WebQueryConnection_set_RefreshedVersion.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().WebQueryConnection_set_RefreshedVersion, self.Ptr, value)

    @property
    def SaveData(self)->bool:
        """Gets or sets whether to save the external data with the workbook.
        
        When set to True, the data retrieved from the web query will be saved
        with the workbook.
        
        Returns:
            bool: True if data should be saved with the workbook; otherwise, False.
        """
        GetDllLibXls().WebQueryConnection_get_SaveData.argtypes=[c_void_p]
        GetDllLibXls().WebQueryConnection_get_SaveData.restype=c_bool
        ret = CallCFunction(GetDllLibXls().WebQueryConnection_get_SaveData, self.Ptr)
        return ret

    @SaveData.setter
    def SaveData(self, value:bool):
        GetDllLibXls().WebQueryConnection_set_SaveData.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().WebQueryConnection_set_SaveData, self.Ptr, value)

    @property

    def OdcFile(self)->str:
        """Gets or sets the path to the Office Data Connection (ODC) file.
        
        Returns:
            str: The path to the ODC file.
        """
        GetDllLibXls().WebQueryConnection_get_OdcFile.argtypes=[c_void_p]
        GetDllLibXls().WebQueryConnection_get_OdcFile.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().WebQueryConnection_get_OdcFile, self.Ptr))
        return ret


    @OdcFile.setter
    def OdcFile(self, value:str):
        GetDllLibXls().WebQueryConnection_set_OdcFile.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().WebQueryConnection_set_OdcFile, self.Ptr, value)

    @property
    def KeepAlive(self)->bool:
        """Gets or sets whether to maintain the HTTP connection.
        
        When set to True, the HTTP connection will be kept alive between requests.
        
        Returns:
            bool: True if the connection should be kept alive; otherwise, False.
        """
        GetDllLibXls().WebQueryConnection_get_KeepAlive.argtypes=[c_void_p]
        GetDllLibXls().WebQueryConnection_get_KeepAlive.restype=c_bool
        ret = CallCFunction(GetDllLibXls().WebQueryConnection_get_KeepAlive, self.Ptr)
        return ret

    @KeepAlive.setter
    def KeepAlive(self, value:bool):
        GetDllLibXls().WebQueryConnection_set_KeepAlive.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().WebQueryConnection_set_KeepAlive, self.Ptr, value)

    @property
    def OnlyUseConnectionFile(self)->bool:
        """

        """
        GetDllLibXls().WebQueryConnection_get_OnlyUseConnectionFile.argtypes=[c_void_p]
        GetDllLibXls().WebQueryConnection_get_OnlyUseConnectionFile.restype=c_bool
        ret = CallCFunction(GetDllLibXls().WebQueryConnection_get_OnlyUseConnectionFile, self.Ptr)
        return ret

    @OnlyUseConnectionFile.setter
    def OnlyUseConnectionFile(self, value:bool):
        GetDllLibXls().WebQueryConnection_set_OnlyUseConnectionFile.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().WebQueryConnection_set_OnlyUseConnectionFile, self.Ptr, value)

    @property
    def SourceData(self)->bool:
        """

        """
        GetDllLibXls().WebQueryConnection_get_SourceData.argtypes=[c_void_p]
        GetDllLibXls().WebQueryConnection_get_SourceData.restype=c_bool
        ret = CallCFunction(GetDllLibXls().WebQueryConnection_get_SourceData, self.Ptr)
        return ret

    @SourceData.setter
    def SourceData(self, value:bool):
        GetDllLibXls().WebQueryConnection_set_SourceData.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().WebQueryConnection_set_SourceData, self.Ptr, value)

    @property
    def ParsePre(self)->bool:
        """

        """
        GetDllLibXls().WebQueryConnection_get_ParsePre.argtypes=[c_void_p]
        GetDllLibXls().WebQueryConnection_get_ParsePre.restype=c_bool
        ret = CallCFunction(GetDllLibXls().WebQueryConnection_get_ParsePre, self.Ptr)
        return ret

    @ParsePre.setter
    def ParsePre(self, value:bool):
        GetDllLibXls().WebQueryConnection_set_ParsePre.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().WebQueryConnection_set_ParsePre, self.Ptr, value)

    @property
    def Consecutive(self)->bool:
        """

        """
        GetDllLibXls().WebQueryConnection_get_Consecutive.argtypes=[c_void_p]
        GetDllLibXls().WebQueryConnection_get_Consecutive.restype=c_bool
        ret = CallCFunction(GetDllLibXls().WebQueryConnection_get_Consecutive, self.Ptr)
        return ret

    @Consecutive.setter
    def Consecutive(self, value:bool):
        GetDllLibXls().WebQueryConnection_set_Consecutive.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().WebQueryConnection_set_Consecutive, self.Ptr, value)

    @property
    def Xl2000(self)->bool:
        """

        """
        GetDllLibXls().WebQueryConnection_get_Xl2000.argtypes=[c_void_p]
        GetDllLibXls().WebQueryConnection_get_Xl2000.restype=c_bool
        ret = CallCFunction(GetDllLibXls().WebQueryConnection_get_Xl2000, self.Ptr)
        return ret

    @Xl2000.setter
    def Xl2000(self, value:bool):
        GetDllLibXls().WebQueryConnection_set_Xl2000.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().WebQueryConnection_set_Xl2000, self.Ptr, value)

    @property

    def Url(self)->str:
        """Gets or sets the URL for the web query.
        
        This is the web address from which data will be retrieved.
        
        Returns:
            str: The URL string.
        """
        GetDllLibXls().WebQueryConnection_get_Url.argtypes=[c_void_p]
        GetDllLibXls().WebQueryConnection_get_Url.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().WebQueryConnection_get_Url, self.Ptr))
        return ret


    @Url.setter
    def Url(self, value:str):
        GetDllLibXls().WebQueryConnection_set_Url.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().WebQueryConnection_set_Url, self.Ptr, value)

