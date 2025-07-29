from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

@dispatch
def SetLicenseKey(key:str):
    """
    Provides a license by a license key, which will be used for loading license.

    Args:
        key: The value of the Key attribute of the element License of you license xml file.

    """
    
    GetDllLibXls().LicenseProvider_SetLicenseKey.argtypes=[ c_void_p]
    CallCFunction(GetDllLibXls().LicenseProvider_SetLicenseKey, key)

@dispatch
def SetLicenseKey(key:str,useDevOrTestLicense:bool):
    """
    Sets the license key required for license loading, and specifies whether to use a development or test license.

    Args:
        key: The value of the Key attribute of the element License of you license xml file.
        useDevOrTestLicense: Indicates whether to apply a development or test license.

    """
    
    GetDllLibXls().LicenseProvider_SetLicenseKeyKU.argtypes=[ c_void_p,c_bool]
    CallCFunction(GetDllLibXls().LicenseProvider_SetLicenseKeyKU, key,useDevOrTestLicense)

@dispatch
def SetLicense(licenseFileFullPath:str):
    """
    Provides a license by a license file path, which will be used for loading license.
    Args:
        licenseFileFullPath: License file full path.
    """
    
    GetDllLibXls().LicenseProvider_SetLicense.argtypes=[ c_void_p]
    CallCFunction(GetDllLibXls().LicenseProvider_SetLicense, licenseFileFullPath)
    
@dispatch
def SetLicense(licenseFileStream:Stream):
    """
    Provides a license by a license stream, which will be used for loading license.
    Args:
        licenseFileStream: License data stream.
    """
    intPtrlicenseFileStream:c_void_p = licenseFileStream.Ptr
    GetDllLibXls().LicenseProvider_SetLicenseL.argtypes=[ c_void_p]
    CallCFunction(GetDllLibXls().LicenseProvider_SetLicenseL, intPtrlicenseFileStream)

class LicenseProvider (SpireObject) :


    SetLicenseKey = staticmethod(SetLicenseKey)

    SetLicense = staticmethod(SetLicense)

    @staticmethod
    def SetLicenseFileName(licenseFileName:str):
        """
        Sets the license file name, which will be used for loading license.

        Args:
            licenseFileName: License file name.

        """
        
        GetDllLibXls().LicenseProvider_SetLicenseFileName.argtypes=[ c_void_p]
        CallCFunction(GetDllLibXls().LicenseProvider_SetLicenseFileName, licenseFileName)

    @staticmethod
    def ClearLicense():
        """
        Clear all cached license.

        """
        CallCFunction(GetDllLibXls().LicenseProvider_ClearLicense)

    @staticmethod
    def LoadLicense():
        """
        Load the license provided by current setting to the license cache.

        """
        CallCFunction(GetDllLibXls().LicenseProvider_LoadLicense)


    @staticmethod
    def UnbindDevelopmentOrTestingLicenses()->bool:
        """
        Unbinds development or testing licenses of the specified type. This method iterates through all stored licenses, identifies those marked as development or test licenses, resets their state, and attempts to unbind them using the LicenseUtilities.UnbindLicense method. The process stops upon successfully unbinding the first matching license. The approach to lifting development or testing licenses does not allow frequent invocation by the same machine code, mandating a two-hour wait period before it can be invoked again.

        Returns:
            true if a development or test license was found and successfully unbound; otherwise,false.

        """
        GetDllLibXls().LicenseProvider_UnbindDevelopmentOrTestingLicenses.restype=c_bool
        ret = CallCFunction(GetDllLibXls().LicenseProvider_UnbindDevelopmentOrTestingLicenses)
        return ret

