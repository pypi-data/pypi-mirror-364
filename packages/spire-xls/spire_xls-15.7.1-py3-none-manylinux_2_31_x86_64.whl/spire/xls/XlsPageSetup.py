from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsPageSetup (  XlsPageSetupBase, IPageSetup) :
    """Represents the page setup settings for a worksheet in Excel.
    
    This class extends XlsPageSetupBase and implements IPageSetup to provide
    functionality for configuring page layout options such as print area,
    print titles, gridlines, and other page-related settings.
    """
    @property
    def IsPrintGridlines(self)->bool:
        """Gets or sets whether gridlines are printed.
        
        Returns:
            bool: True if gridlines are printed; otherwise, False.
        """
        GetDllLibXls().XlsPageSetup_get_IsPrintGridlines.argtypes=[c_void_p]
        GetDllLibXls().XlsPageSetup_get_IsPrintGridlines.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPageSetup_get_IsPrintGridlines, self.Ptr)
        return ret

    @IsPrintGridlines.setter
    def IsPrintGridlines(self, value:bool):
        GetDllLibXls().XlsPageSetup_set_IsPrintGridlines.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPageSetup_set_IsPrintGridlines, self.Ptr, value)

    @property
    def IsPrintHeadings(self)->bool:
        """Gets or sets whether row and column headings are printed.
        
        Returns:
            bool: True if row and column headings are printed; otherwise, False.
        """
        GetDllLibXls().XlsPageSetup_get_IsPrintHeadings.argtypes=[c_void_p]
        GetDllLibXls().XlsPageSetup_get_IsPrintHeadings.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPageSetup_get_IsPrintHeadings, self.Ptr)
        return ret

    @IsPrintHeadings.setter
    def IsPrintHeadings(self, value:bool):
        GetDllLibXls().XlsPageSetup_set_IsPrintHeadings.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPageSetup_set_IsPrintHeadings, self.Ptr, value)

    @property

    def PrintArea(self)->str:
        """Gets or sets the range to print, specified as a string using A1-style references.
        
        Returns:
            str: The print area as an A1-style range reference.
        """
        GetDllLibXls().XlsPageSetup_get_PrintArea.argtypes=[c_void_p]
        GetDllLibXls().XlsPageSetup_get_PrintArea.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPageSetup_get_PrintArea, self.Ptr))
        return ret


    @PrintArea.setter
    def PrintArea(self, value:str):
        GetDllLibXls().XlsPageSetup_set_PrintArea.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPageSetup_set_PrintArea, self.Ptr, value)

    @property

    def PrintTitleColumns(self)->str:
        """Gets or sets the columns that contain the cells to be repeated on the left side of each page.
        
        Returns:
            str: The title columns as an A1-style reference.
        """
        GetDllLibXls().XlsPageSetup_get_PrintTitleColumns.argtypes=[c_void_p]
        GetDllLibXls().XlsPageSetup_get_PrintTitleColumns.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPageSetup_get_PrintTitleColumns, self.Ptr))
        return ret


    @PrintTitleColumns.setter
    def PrintTitleColumns(self, value:str):
        GetDllLibXls().XlsPageSetup_set_PrintTitleColumns.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPageSetup_set_PrintTitleColumns, self.Ptr, value)

    @property

    def PrintTitleRows(self)->str:
        """Gets or sets the rows that contain the cells to be repeated at the top of each page.
        
        Returns:
            str: The title rows as an A1-style reference.
        """
        GetDllLibXls().XlsPageSetup_get_PrintTitleRows.argtypes=[c_void_p]
        GetDllLibXls().XlsPageSetup_get_PrintTitleRows.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPageSetup_get_PrintTitleRows, self.Ptr))
        return ret


    @PrintTitleRows.setter
    def PrintTitleRows(self, value:str):
        GetDllLibXls().XlsPageSetup_set_PrintTitleRows.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsPageSetup_set_PrintTitleRows, self.Ptr, value)

    @property

    def RelationId(self)->str:
        """Gets or sets relation id to the printer settings part.
        
        Returns:
            str: The relation ID for printer settings.
        """
        GetDllLibXls().XlsPageSetup_get_RelationId.argtypes=[c_void_p]
        GetDllLibXls().XlsPageSetup_get_RelationId.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsPageSetup_get_RelationId, self.Ptr))
        return ret


    @property
    def IsSummaryRowBelow(self)->bool:
        """Gets or sets whether summary rows appear below detail rows in an outline.
        
        Returns:
            bool: True if summary rows appear below detail; otherwise, False.
        """
        GetDllLibXls().XlsPageSetup_get_IsSummaryRowBelow.argtypes=[c_void_p]
        GetDllLibXls().XlsPageSetup_get_IsSummaryRowBelow.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPageSetup_get_IsSummaryRowBelow, self.Ptr)
        return ret

    @IsSummaryRowBelow.setter
    def IsSummaryRowBelow(self, value:bool):
        GetDllLibXls().XlsPageSetup_set_IsSummaryRowBelow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPageSetup_set_IsSummaryRowBelow, self.Ptr, value)

    @property
    def IsSummaryColumnRight(self)->bool:
        """Gets or sets whether summary columns appear to the right of detail columns in an outline.
        
        Returns:
            bool: True if summary columns appear to the right; otherwise, False.
        """
        GetDllLibXls().XlsPageSetup_get_IsSummaryColumnRight.argtypes=[c_void_p]
        GetDllLibXls().XlsPageSetup_get_IsSummaryColumnRight.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPageSetup_get_IsSummaryColumnRight, self.Ptr)
        return ret

    @IsSummaryColumnRight.setter
    def IsSummaryColumnRight(self, value:bool):
        GetDllLibXls().XlsPageSetup_set_IsSummaryColumnRight.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPageSetup_set_IsSummaryColumnRight, self.Ptr, value)

    @property
    def IsFitToPage(self)->bool:
        """Gets or sets whether the worksheet is scaled to fit a single page when printed.
        
        Returns:
            bool: True if the worksheet is scaled to fit a page; otherwise, False.
        """
        GetDllLibXls().XlsPageSetup_get_IsFitToPage.argtypes=[c_void_p]
        GetDllLibXls().XlsPageSetup_get_IsFitToPage.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPageSetup_get_IsFitToPage, self.Ptr)
        return ret

    @IsFitToPage.setter
    def IsFitToPage(self, value:bool):
        GetDllLibXls().XlsPageSetup_set_IsFitToPage.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPageSetup_set_IsFitToPage, self.Ptr, value)

    @property
    def NeedDataArray(self)->bool:
        """Gets whether data array is needed for this page setup.
        
        Returns:
            bool: True if data array is needed; otherwise, False.
        """
        GetDllLibXls().XlsPageSetup_get_NeedDataArray.argtypes=[c_void_p]
        GetDllLibXls().XlsPageSetup_get_NeedDataArray.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPageSetup_get_NeedDataArray, self.Ptr)
        return ret

    @property
    def DefaultRowHeight(self)->int:
        """Gets or sets the default row height for the worksheet.
        
        Returns:
            int: The default row height in points.
        """
        GetDllLibXls().XlsPageSetup_get_DefaultRowHeight.argtypes=[c_void_p]
        GetDllLibXls().XlsPageSetup_get_DefaultRowHeight.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPageSetup_get_DefaultRowHeight, self.Ptr)
        return ret

    @DefaultRowHeight.setter
    def DefaultRowHeight(self, value:int):
        GetDllLibXls().XlsPageSetup_set_DefaultRowHeight.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsPageSetup_set_DefaultRowHeight, self.Ptr, value)

    @property
    def DefaultRowHeightFlag(self)->bool:
        """Gets or sets whether the default row height is enabled.
        
        Returns:
            bool: True if default row height is enabled; otherwise, False.
        """
        GetDllLibXls().XlsPageSetup_get_DefaultRowHeightFlag.argtypes=[c_void_p]
        GetDllLibXls().XlsPageSetup_get_DefaultRowHeightFlag.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsPageSetup_get_DefaultRowHeightFlag, self.Ptr)
        return ret

    @DefaultRowHeightFlag.setter
    def DefaultRowHeightFlag(self, value:bool):
        GetDllLibXls().XlsPageSetup_set_DefaultRowHeightFlag.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsPageSetup_set_DefaultRowHeightFlag, self.Ptr, value)


    def Clone(self ,parent:'SpireObject')->'XlsPageSetup':
        """Creates a copy of the page setup.
        
        Args:
            parent (SpireObject): The parent object for the cloned page setup.
            
        Returns:
            XlsPageSetup: A new instance of the page setup.
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsPageSetup_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsPageSetup_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsPageSetup_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else XlsPageSetup(intPtr)
        return ret



    def GetStoreSize(self ,version:'ExcelVersion')->int:
        """Gets the storage size required for this page setup with the specified Excel version.
        
        Args:
            version (ExcelVersion): The Excel version to determine storage size for.
            
        Returns:
            int: The storage size in bytes.
        """
        enumversion:c_int = version.value

        GetDllLibXls().XlsPageSetup_GetStoreSize.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsPageSetup_GetStoreSize.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsPageSetup_GetStoreSize, self.Ptr, enumversion)
        return ret

