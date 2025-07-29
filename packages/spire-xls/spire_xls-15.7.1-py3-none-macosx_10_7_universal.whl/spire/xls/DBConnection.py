from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class DBConnection (  ExternalConnection) :
    """Represents a database connection in an Excel workbook.
    
    This class extends ExternalConnection and provides properties and methods for managing
    connections to database sources, including connection strings, commands, and command types.
    It allows for configuring database-specific connection settings and refresh behavior.
    """
    @property

    def ID(self)->str:
        """

        """
        GetDllLibXls().DBConnection_get_ID.argtypes=[c_void_p]
        GetDllLibXls().DBConnection_get_ID.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().DBConnection_get_ID, self.Ptr))
        return ret


    @property

    def Name(self)->str:
        """

        """
        GetDllLibXls().DBConnection_get_Name.argtypes=[c_void_p]
        GetDllLibXls().DBConnection_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().DBConnection_get_Name, self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        GetDllLibXls().DBConnection_set_Name.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().DBConnection_set_Name, self.Ptr, value)

    @property

    def ConnType(self)->'ConnectionDataSourceType':
        """

        """
        GetDllLibXls().DBConnection_get_ConnType.argtypes=[c_void_p]
        GetDllLibXls().DBConnection_get_ConnType.restype=c_int
        ret = CallCFunction(GetDllLibXls().DBConnection_get_ConnType, self.Ptr)
        objwraped = ConnectionDataSourceType(ret)
        return objwraped

    @property
    def BackgroundRefresh(self)->bool:
        """

        """
        GetDllLibXls().DBConnection_get_BackgroundRefresh.argtypes=[c_void_p]
        GetDllLibXls().DBConnection_get_BackgroundRefresh.restype=c_bool
        ret = CallCFunction(GetDllLibXls().DBConnection_get_BackgroundRefresh, self.Ptr)
        return ret

    @BackgroundRefresh.setter
    def BackgroundRefresh(self, value:bool):
        GetDllLibXls().DBConnection_set_BackgroundRefresh.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().DBConnection_set_BackgroundRefresh, self.Ptr, value)

    @property

    def RefreshedVersion(self)->str:
        """

        """
        GetDllLibXls().DBConnection_get_RefreshedVersion.argtypes=[c_void_p]
        GetDllLibXls().DBConnection_get_RefreshedVersion.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().DBConnection_get_RefreshedVersion, self.Ptr))
        return ret


    @RefreshedVersion.setter
    def RefreshedVersion(self, value:str):
        GetDllLibXls().DBConnection_set_RefreshedVersion.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().DBConnection_set_RefreshedVersion, self.Ptr, value)

    @property
    def SaveData(self)->bool:
        """

        """
        GetDllLibXls().DBConnection_get_SaveData.argtypes=[c_void_p]
        GetDllLibXls().DBConnection_get_SaveData.restype=c_bool
        ret = CallCFunction(GetDllLibXls().DBConnection_get_SaveData, self.Ptr)
        return ret

    @SaveData.setter
    def SaveData(self, value:bool):
        GetDllLibXls().DBConnection_set_SaveData.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().DBConnection_set_SaveData, self.Ptr, value)

    @property

    def OdcFile(self)->str:
        """

        """
        GetDllLibXls().DBConnection_get_OdcFile.argtypes=[c_void_p]
        GetDllLibXls().DBConnection_get_OdcFile.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().DBConnection_get_OdcFile, self.Ptr))
        return ret


    @OdcFile.setter
    def OdcFile(self, value:str):
        GetDllLibXls().DBConnection_set_OdcFile.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().DBConnection_set_OdcFile, self.Ptr, value)

    @property
    def KeepAlive(self)->bool:
        """

        """
        GetDllLibXls().DBConnection_get_KeepAlive.argtypes=[c_void_p]
        GetDllLibXls().DBConnection_get_KeepAlive.restype=c_bool
        ret = CallCFunction(GetDllLibXls().DBConnection_get_KeepAlive, self.Ptr)
        return ret

    @KeepAlive.setter
    def KeepAlive(self, value:bool):
        GetDllLibXls().DBConnection_set_KeepAlive.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().DBConnection_set_KeepAlive, self.Ptr, value)

    @property
    def OnlyUseConnectionFile(self)->bool:
        """

        """
        GetDllLibXls().DBConnection_get_OnlyUseConnectionFile.argtypes=[c_void_p]
        GetDllLibXls().DBConnection_get_OnlyUseConnectionFile.restype=c_bool
        ret = CallCFunction(GetDllLibXls().DBConnection_get_OnlyUseConnectionFile, self.Ptr)
        return ret

    @OnlyUseConnectionFile.setter
    def OnlyUseConnectionFile(self, value:bool):
        GetDllLibXls().DBConnection_set_OnlyUseConnectionFile.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().DBConnection_set_OnlyUseConnectionFile, self.Ptr, value)

    @property

    def Connection(self)->str:
        """Gets or sets the connection string for the database connection.
        
        This property contains the connection string that specifies how to connect
        to the database, including server, database name, authentication details, etc.
        
        Returns:
            str: The connection string for the database.
        """
        GetDllLibXls().DBConnection_get_Connection.argtypes=[c_void_p]
        GetDllLibXls().DBConnection_get_Connection.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().DBConnection_get_Connection, self.Ptr))
        return ret


    @Connection.setter
    def Connection(self, value:str):
        """Sets the connection string for the database connection.
        
        Args:
            value (str): The connection string to set.
        """
        GetDllLibXls().DBConnection_set_Connection.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().DBConnection_set_Connection, self.Ptr, value)

    @property

    def Command(self)->str:
        """Gets or sets the command text for the database connection.
        
        This property contains the SQL query, stored procedure name, or table name
        that is used to retrieve data from the database.
        
        Returns:
            str: The command text for the database connection.
        """
        GetDllLibXls().DBConnection_get_Command.argtypes=[c_void_p]
        GetDllLibXls().DBConnection_get_Command.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().DBConnection_get_Command, self.Ptr))
        return ret


    @Command.setter
    def Command(self, value:str):
        """Sets the command text for the database connection.
        
        Args:
            value (str): The command text to set.
        """
        GetDllLibXls().DBConnection_set_Command.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().DBConnection_set_Command, self.Ptr, value)

    @property

    def CommandType(self)->'OLEDBCommandType':
        """Gets or sets the type of command used in the database connection.
        
        This property specifies how the Command property should be interpreted,
        such as a SQL statement, table name, or stored procedure name.
        
        Returns:
            OLEDBCommandType: An enumeration value representing the command type.
        """
        GetDllLibXls().DBConnection_get_CommandType.argtypes=[c_void_p]
        GetDllLibXls().DBConnection_get_CommandType.restype=c_int
        ret = CallCFunction(GetDllLibXls().DBConnection_get_CommandType, self.Ptr)
        objwraped = OLEDBCommandType(ret)
        return objwraped

    @CommandType.setter
    def CommandType(self, value:'OLEDBCommandType'):
        """Sets the type of command used in the database connection.
        
        Args:
            value (OLEDBCommandType): An enumeration value representing the command type to set.
        """
        GetDllLibXls().DBConnection_set_CommandType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().DBConnection_set_CommandType, self.Ptr, value.value)

