from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsPivotCache (  XlsObject, IPivotCache) :
    """Implementation of the PivotCache interface.
    
    This class provides functionality for managing the cache of data for a PivotTable,
    including data source settings, refresh options, and version information.
    """
    @property
    def Index(self)->int:
        """Gets the index of the pivot cache in the collection.
        
        Returns:
            int: The zero-based index of the pivot cache.
        """
        GetDllLibXls().XlsPivotCache_get_Index.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_Index.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_get_Index, self.Ptr)
        return ret

    @property

    def SourceType(self)->'DataSourceType':
        """Gets the type of data source for the pivot cache.
        
        Returns:
            DataSourceType: An enumeration value representing the data source type.
        """
        GetDllLibXls().XlsPivotCache_get_SourceType.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_SourceType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_get_SourceType, self.Ptr)
        objwraped = DataSourceType(ret)
        return objwraped

    @property

    def SourceRange(self)->'IXLSRange':
        """Gets the source range for the pivot cache when the source type is worksheet.
        
        Returns:
            IXLSRange: The source range object.
        """
        GetDllLibXls().XlsPivotCache_get_SourceRange.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_SourceRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotCache_get_SourceRange, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @property

    def Parent(self)->'XlsPivotCachesCollection':
        """Gets the parent collection of the pivot cache.
        
        Returns:
            XlsPivotCachesCollection: The parent collection object.
        """
        GetDllLibXls().XlsPivotCache_get_Parent.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotCache_get_Parent, self.Ptr)
        ret = None if intPtr==None else XlsPivotCachesCollection(intPtr)
        return ret


    @property
    def IsUpgradeOnRefresh(self)->bool:
        """Gets whether the cache is scheduled for version upgrade on refresh.
        
        Returns:
            bool: True if the cache is scheduled for version upgrade; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_get_IsUpgradeOnRefresh.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_IsUpgradeOnRefresh.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_get_IsUpgradeOnRefresh, self.Ptr)
        return ret

    @IsUpgradeOnRefresh.setter
    def IsUpgradeOnRefresh(self, value:bool):
        """Sets whether the cache is scheduled for version upgrade on refresh.
        
        Args:
            value (bool): True to schedule for version upgrade; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_set_IsUpgradeOnRefresh.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotCache_set_IsUpgradeOnRefresh, self.Ptr, value)

    @property

    def RefreshedBy(self)->str:
        """Gets the name of the user who last refreshed the cache.
        
        Returns:
            str: The name of the user who last refreshed the cache.
        """
        GetDllLibXls().XlsPivotCache_get_RefreshedBy.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_RefreshedBy.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPivotCache_get_RefreshedBy, self.Ptr))
        return ret


    @RefreshedBy.setter
    def RefreshedBy(self, value:str):
        """Sets the name of the user who last refreshed the cache.
        
        Args:
            value (str): The name of the user who last refreshed the cache.
        """
        GetDllLibXls().XlsPivotCache_set_RefreshedBy.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPivotCache_set_RefreshedBy, self.Ptr, value)

    @property
    def IsSupportSubQuery(self)->bool:
        """Gets whether the cache's data source supports subqueries.
        
        Returns:
            bool: True if the data source supports subqueries; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_get_IsSupportSubQuery.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_IsSupportSubQuery.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_get_IsSupportSubQuery, self.Ptr)
        return ret

    @IsSupportSubQuery.setter
    def IsSupportSubQuery(self, value:bool):
        """Sets whether the cache's data source supports subqueries.
        
        Args:
            value (bool): True if the data source supports subqueries; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_set_IsSupportSubQuery.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotCache_set_IsSupportSubQuery, self.Ptr, value)

    @property
    def IsSaveData(self)->bool:
        """Gets whether the pivot records are saved with the cache.
        
        Returns:
            bool: True if pivot records are saved with the cache; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_get_IsSaveData.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_IsSaveData.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_get_IsSaveData, self.Ptr)
        return ret

    @IsSaveData.setter
    def IsSaveData(self, value:bool):
        """Sets whether the pivot records are saved with the cache.
        
        Args:
            value (bool): True to save pivot records with the cache; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_set_IsSaveData.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotCache_set_IsSaveData, self.Ptr, value)

    @property
    def IsOptimizedCache(self)->bool:
        """Gets whether optimizations are applied to reduce memory usage.
        
        Returns:
            bool: True if optimizations are applied; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_get_IsOptimizedCache.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_IsOptimizedCache.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_get_IsOptimizedCache, self.Ptr)
        return ret

    @IsOptimizedCache.setter
    def IsOptimizedCache(self, value:bool):
        """Sets whether optimizations are applied to reduce memory usage.
        
        Args:
            value (bool): True to apply optimizations; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_set_IsOptimizedCache.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotCache_set_IsOptimizedCache, self.Ptr, value)

    @property
    def EnableRefresh(self)->bool:
        """Gets whether the user can refresh the cache.
        
        Returns:
            bool: True if the user can refresh the cache; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_get_EnableRefresh.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_EnableRefresh.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_get_EnableRefresh, self.Ptr)
        return ret

    @EnableRefresh.setter
    def EnableRefresh(self, value:bool):
        """Sets whether the user can refresh the cache.
        
        Args:
            value (bool): True to allow the user to refresh the cache; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_set_EnableRefresh.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotCache_set_EnableRefresh, self.Ptr, value)

    @property
    def IsBackgroundQuery(self)->bool:
        """Gets whether records are retrieved asynchronously from the cache.
        
        Returns:
            bool: True if records are retrieved asynchronously; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_get_IsBackgroundQuery.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_IsBackgroundQuery.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_get_IsBackgroundQuery, self.Ptr)
        return ret

    @IsBackgroundQuery.setter
    def IsBackgroundQuery(self, value:bool):
        """Sets whether records are retrieved asynchronously from the cache.
        
        Args:
            value (bool): True to retrieve records asynchronously; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_set_IsBackgroundQuery.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotCache_set_IsBackgroundQuery, self.Ptr, value)

    @property
    def CreatedVersion(self)->int:
        """Gets the version of the application that created the cache.
        
        Returns:
            int: The version number of the application.
        """
        GetDllLibXls().XlsPivotCache_get_CreatedVersion.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_CreatedVersion.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_get_CreatedVersion, self.Ptr)
        return ret

    @CreatedVersion.setter
    def CreatedVersion(self, value:int):
        """Sets the version of the application that created the cache.
        
        Args:
            value (int): The version number of the application.
        """
        GetDllLibXls().XlsPivotCache_set_CreatedVersion.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotCache_set_CreatedVersion, self.Ptr, value)

    @property
    def CalculatedItemIndex(self)->int:
        """Gets the index of the calculated item in the cache.
        
        Returns:
            int: The index of the calculated item.
        """
        GetDllLibXls().XlsPivotCache_get_CalculatedItemIndex.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_CalculatedItemIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_get_CalculatedItemIndex, self.Ptr)
        return ret

    @property
    def MinRefreshableVersion(self)->int:
        """Gets the earliest version of the application required to refresh the cache.
        
        Returns:
            int: The earliest version number required to refresh the cache.
        """
        GetDllLibXls().XlsPivotCache_get_MinRefreshableVersion.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_MinRefreshableVersion.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_get_MinRefreshableVersion, self.Ptr)
        return ret

    @MinRefreshableVersion.setter
    def MinRefreshableVersion(self, value:int):
        """Sets the earliest version of the application required to refresh the cache.
        
        Args:
            value (int): The earliest version number required to refresh the cache.
        """
        GetDllLibXls().XlsPivotCache_set_MinRefreshableVersion.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotCache_set_MinRefreshableVersion, self.Ptr, value)

    @property
    def RefreshedVersion(self)->int:
        """Gets the version of the application that last refreshed the cache.
        
        This attribute depends on whether the application exposes mechanisms via the user interface
        whereby the end-user can refresh the cache.
        
        Returns:
            int: The version number of the application that last refreshed the cache.
        """
        GetDllLibXls().XlsPivotCache_get_RefreshedVersion.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_RefreshedVersion.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_get_RefreshedVersion, self.Ptr)
        return ret

    @RefreshedVersion.setter
    def RefreshedVersion(self, value:int):
        """Sets the version of the application that last refreshed the cache.
        
        Args:
            value (int): The version number of the application that last refreshed the cache.
        """
        GetDllLibXls().XlsPivotCache_set_RefreshedVersion.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPivotCache_set_RefreshedVersion, self.Ptr, value)

    @property
    def IsInvalidData(self)->bool:
        """Gets whether the cache needs to be refreshed.
        
        Returns:
            bool: True if the cache needs to be refreshed; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_get_IsInvalidData.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_IsInvalidData.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_get_IsInvalidData, self.Ptr)
        return ret

    @IsInvalidData.setter
    def IsInvalidData(self, value:bool):
        """Sets whether the cache needs to be refreshed.
        
        Args:
            value (bool): True if the cache needs to be refreshed; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_set_IsInvalidData.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotCache_set_IsInvalidData, self.Ptr, value)

    @property
    def SupportAdvancedDrill(self)->bool:
        """Gets whether the cache supports advanced drill-down functionality.
        
        Returns:
            bool: True if advanced drill-down is supported; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_get_SupportAdvancedDrill.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_SupportAdvancedDrill.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_get_SupportAdvancedDrill, self.Ptr)
        return ret

    @SupportAdvancedDrill.setter
    def SupportAdvancedDrill(self, value:bool):
        """Sets whether the cache supports advanced drill-down functionality.
        
        Args:
            value (bool): True to enable advanced drill-down support; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_set_SupportAdvancedDrill.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotCache_set_SupportAdvancedDrill, self.Ptr, value)

    @property
    def IsRefreshOnLoad(self)->bool:
        """Gets whether the application will refresh the cache when the workbook is opened.
        
        Returns:
            bool: True if the cache is refreshed on load; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_get_IsRefreshOnLoad.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_IsRefreshOnLoad.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_get_IsRefreshOnLoad, self.Ptr)
        return ret

    @IsRefreshOnLoad.setter
    def IsRefreshOnLoad(self, value:bool):
        """Sets whether the application will refresh the cache when the workbook is opened.
        
        Args:
            value (bool): True to refresh the cache on load; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_set_IsRefreshOnLoad.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPivotCache_set_IsRefreshOnLoad, self.Ptr, value)

    @property
    def NeedDataArray(self)->bool:
        """Gets whether the cache needs a data array for its operations.
        
        Returns:
            bool: True if a data array is needed; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_get_NeedDataArray.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_NeedDataArray.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_get_NeedDataArray, self.Ptr)
        return ret

    @property

    def RefreshDate(self)->'DateTime':
        """Gets the date and time when the cache was last refreshed.
        
        Returns:
            DateTime: The date and time of the last refresh.
        """
        GetDllLibXls().XlsPivotCache_get_RefreshDate.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_RefreshDate.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotCache_get_RefreshDate, self.Ptr)
        ret = None if intPtr==None else DateTime(intPtr)
        return ret


    @RefreshDate.setter
    def RefreshDate(self, value:'DateTime'):
        """Sets the date and time when the cache was last refreshed.
        
        Args:
            value (DateTime): The date and time of the last refresh.
        """
        GetDllLibXls().XlsPivotCache_set_RefreshDate.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsPivotCache_set_RefreshDate, self.Ptr, value.Ptr)

    @property

    def RangeName(self)->str:
        """Gets the name of the pivot cache NamedRange.
        
        Returns:
            str: The name of the pivot cache NamedRange.
        """
        GetDllLibXls().XlsPivotCache_get_RangeName.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_RangeName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPivotCache_get_RangeName, self.Ptr))
        return ret


    @RangeName.setter
    def RangeName(self, value:str):
        """Sets the name of the pivot cache NamedRange.
        
        Args:
            value (str): The name of the pivot cache NamedRange.
        """
        GetDllLibXls().XlsPivotCache_set_RangeName.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPivotCache_set_RangeName, self.Ptr, value)

    @property
    def HasNamedRange(self)->bool:
        """Gets whether the pivot cache has a named range.
        
        Returns:
            bool: True if the pivot cache has a named range; otherwise, False.
        """
        GetDllLibXls().XlsPivotCache_get_HasNamedRange.argtypes=[c_void_p]
        GetDllLibXls().XlsPivotCache_get_HasNamedRange.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_get_HasNamedRange, self.Ptr)
        return ret

    @staticmethod

    def InRange(sourceRange:'IXLSRange',worksheet:'XlsWorksheet',index:int,count:int,isRow:bool)->bool:
        """Determines whether the specified range is within the given worksheet.
        
        Args:
            sourceRange (IXLSRange): The source range to check.
            worksheet (XlsWorksheet): The worksheet to check against.
            index (int): The index position.
            count (int): The count of cells.
            isRow (bool): True to check rows; False to check columns.
            
        Returns:
            bool: True if the range is within the worksheet; otherwise, False.
        """
        intPtrsourceRange:c_void_p = sourceRange.Ptr
        intPtrworksheet:c_void_p = worksheet.Ptr

        GetDllLibXls().XlsPivotCache_InRange.argtypes=[ c_void_p,c_void_p,c_int,c_int,c_bool]
        GetDllLibXls().XlsPivotCache_InRange.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPivotCache_InRange,  intPtrsourceRange,intPtrworksheet,index,count,isRow)
        return ret

    @dispatch

    def Clone(self ,parent:SpireObject)->SpireObject:
        """Creates a clone of this pivot cache.
        
        Args:
            parent (SpireObject): The parent object for the cloned cache.
            
        Returns:
            SpireObject: The cloned pivot cache.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsPivotCache_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsPivotCache_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPivotCache_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


#    @dispatch
#
#    def Clone(self ,parent:SpireObject,hashNewNames:'Dictionary2')->SpireObject:
#        """
#
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrhashNewNames:c_void_p = hashNewNames.Ptr
#
#        GetDllLibXls().XlsPivotCache_ClonePH.argtypes=[c_void_p ,c_void_p,c_void_p]
#        GetDllLibXls().XlsPivotCache_ClonePH.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsPivotCache_ClonePH, self.Ptr, intPtrparent,intPtrhashNewNames)
#        ret = None if intPtr==None else SpireObject(intPtr)
#        return ret
#


