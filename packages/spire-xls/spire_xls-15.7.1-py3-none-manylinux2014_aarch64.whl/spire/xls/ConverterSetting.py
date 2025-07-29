from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ConverterSetting (SpireObject) :
    """
    Convert Setting

    """
#    @PrintPageEventHandler.setter
#    def PrintPageEventHandler(self, value:'PrintPageEventHandler'):
#        GetDllLibXls().ConverterSetting_set_PrintPageEventHandler.argtypes=[c_void_p, c_void_p]
#        CallCFunction(GetDllLibXls().ConverterSetting_set_PrintPageEventHandler, self.Ptr, value.Ptr)


#    @property
#
#    def PrintPageEventHandler(self)->'PrintPageEventHandler':
#        """
#    <summary>
#        Print each page using this EventHandler
#    </summary>
#        """
#        GetDllLibXls().ConverterSetting_get_PrintPageEventHandler.argtypes=[c_void_p]
#        GetDllLibXls().ConverterSetting_get_PrintPageEventHandler.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().ConverterSetting_get_PrintPageEventHandler, self.Ptr)
#        ret = None if intPtr==None else PrintPageEventHandler(intPtr)
#        return ret
#


    @property
    def XDpi(self)->int:
        """
        Gets or sets the horizontal resolution, in dots per inch (DPI). Default value is 96.

        """
        GetDllLibXls().ConverterSetting_get_XDpi.argtypes=[c_void_p]
        GetDllLibXls().ConverterSetting_get_XDpi.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConverterSetting_get_XDpi, self.Ptr)
        return ret

    @XDpi.setter
    def XDpi(self, value:int):
        GetDllLibXls().ConverterSetting_set_XDpi.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConverterSetting_set_XDpi, self.Ptr, value)

    @property
    def YDpi(self)->int:
        """
        Gets or sets the vertical resolution, in dots per inch (DPI). Default value is 96.

        """
        GetDllLibXls().ConverterSetting_get_YDpi.argtypes=[c_void_p]
        GetDllLibXls().ConverterSetting_get_YDpi.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConverterSetting_get_YDpi, self.Ptr)
        return ret

    @YDpi.setter
    def YDpi(self, value:int):
        GetDllLibXls().ConverterSetting_set_YDpi.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConverterSetting_set_YDpi, self.Ptr, value)

    @property
    def PrintWithSheetPageSetting(self)->bool:
        """
        If PrintWithSheetPageSetting = false(Default) . printing all pages with default page settings If PrintWithSheetPageSetting = true . printing each page with its owning sheet's page settings

        """
        GetDllLibXls().ConverterSetting_get_PrintWithSheetPageSetting.argtypes=[c_void_p]
        GetDllLibXls().ConverterSetting_get_PrintWithSheetPageSetting.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConverterSetting_get_PrintWithSheetPageSetting, self.Ptr)
        return ret

    @PrintWithSheetPageSetting.setter
    def PrintWithSheetPageSetting(self, value:bool):
        GetDllLibXls().ConverterSetting_set_PrintWithSheetPageSetting.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConverterSetting_set_PrintWithSheetPageSetting, self.Ptr, value)

    @property
    def JPEGQuality(self)->int:
        """
        Gets or sets a value determining the quality.

        """
        GetDllLibXls().ConverterSetting_get_JPEGQuality.argtypes=[c_void_p]
        GetDllLibXls().ConverterSetting_get_JPEGQuality.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConverterSetting_get_JPEGQuality, self.Ptr)
        return ret

    @JPEGQuality.setter
    def JPEGQuality(self, value:int):
        GetDllLibXls().ConverterSetting_set_JPEGQuality.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConverterSetting_set_JPEGQuality, self.Ptr, value)

    #@property

    #def ImageFormat(self)->'ImageFormat':
    #    """

    #    """
    #    GetDllLibXls().ConverterSetting_get_ImageFormat.argtypes=[c_void_p]
    #    GetDllLibXls().ConverterSetting_get_ImageFormat.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibXls().ConverterSetting_get_ImageFormat, self.Ptr)
    #    ret = None if intPtr==None else ImageFormat(intPtr)
    #    return ret


    #@ImageFormat.setter
    #def ImageFormat(self, value:'ImageFormat'):
    #    GetDllLibXls().ConverterSetting_set_ImageFormat.argtypes=[c_void_p, c_void_p]
    #    CallCFunction(GetDllLibXls().ConverterSetting_set_ImageFormat, self.Ptr, value.Ptr)

    @property
    def IsCellAutoFit(self)->bool:
        """
        Indicates whether the width and height of the cells is automatically fitted by cell value. The default value is false.

        """
        GetDllLibXls().ConverterSetting_get_IsCellAutoFit.argtypes=[c_void_p]
        GetDllLibXls().ConverterSetting_get_IsCellAutoFit.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConverterSetting_get_IsCellAutoFit, self.Ptr)
        return ret

    @IsCellAutoFit.setter
    def IsCellAutoFit(self, value:bool):
        GetDllLibXls().ConverterSetting_set_IsCellAutoFit.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConverterSetting_set_IsCellAutoFit, self.Ptr, value)

    @property
    def SheetFitToPage(self)->bool:
        """
        One sheet context render to only one page.

        """
        GetDllLibXls().ConverterSetting_get_SheetFitToPage.argtypes=[c_void_p]
        GetDllLibXls().ConverterSetting_get_SheetFitToPage.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConverterSetting_get_SheetFitToPage, self.Ptr)
        return ret

    @SheetFitToPage.setter
    def SheetFitToPage(self, value:bool):
        GetDllLibXls().ConverterSetting_set_SheetFitToPage.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConverterSetting_set_SheetFitToPage, self.Ptr, value)

    @property
    def SheetFitToPageRetainPaperSize(self)->bool:
        """
        Gets or sets a value indicates whether retain paper size when to one sheet context render to only one page.

        """
        GetDllLibXls().ConverterSetting_get_SheetFitToPageRetainPaperSize.argtypes=[c_void_p]
        GetDllLibXls().ConverterSetting_get_SheetFitToPageRetainPaperSize.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConverterSetting_get_SheetFitToPageRetainPaperSize, self.Ptr)
        return ret

    @SheetFitToPageRetainPaperSize.setter
    def SheetFitToPageRetainPaperSize(self, value:bool):
        GetDllLibXls().ConverterSetting_set_SheetFitToPageRetainPaperSize.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConverterSetting_set_SheetFitToPageRetainPaperSize, self.Ptr, value)

    @property
    def SheetFitToWidth(self)->bool:
        """
        Sheet content fit to page width.

        """
        GetDllLibXls().ConverterSetting_get_SheetFitToWidth.argtypes=[c_void_p]
        GetDllLibXls().ConverterSetting_get_SheetFitToWidth.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConverterSetting_get_SheetFitToWidth, self.Ptr)
        return ret

    @SheetFitToWidth.setter
    def SheetFitToWidth(self, value:bool):
        GetDllLibXls().ConverterSetting_set_SheetFitToWidth.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConverterSetting_set_SheetFitToWidth, self.Ptr, value)

    @property
    def IsReCalculateOnConvert(self)->bool:
        """

        """
        GetDllLibXls().ConverterSetting_get_IsReCalculateOnConvert.argtypes=[c_void_p]
        GetDllLibXls().ConverterSetting_get_IsReCalculateOnConvert.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConverterSetting_get_IsReCalculateOnConvert, self.Ptr)
        return ret

    @IsReCalculateOnConvert.setter
    def IsReCalculateOnConvert(self, value:bool):
        GetDllLibXls().ConverterSetting_set_IsReCalculateOnConvert.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConverterSetting_set_IsReCalculateOnConvert, self.Ptr, value)

    @property
    def IgnoreErrorCalculateResult(self)->bool:
        """
        Ignore error calculate result when calculating formula. Default is false.

        """
        GetDllLibXls().ConverterSetting_get_IgnoreErrorCalculateResult.argtypes=[c_void_p]
        GetDllLibXls().ConverterSetting_get_IgnoreErrorCalculateResult.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConverterSetting_get_IgnoreErrorCalculateResult, self.Ptr)
        return ret

    @IgnoreErrorCalculateResult.setter
    def IgnoreErrorCalculateResult(self, value:bool):
        GetDllLibXls().ConverterSetting_set_IgnoreErrorCalculateResult.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConverterSetting_set_IgnoreErrorCalculateResult, self.Ptr, value)

    @property
    def ClearCacheOnConverted(self)->bool:
        """

        """
        GetDllLibXls().ConverterSetting_get_ClearCacheOnConverted.argtypes=[c_void_p]
        GetDllLibXls().ConverterSetting_get_ClearCacheOnConverted.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConverterSetting_get_ClearCacheOnConverted, self.Ptr)
        return ret

    @ClearCacheOnConverted.setter
    def ClearCacheOnConverted(self, value:bool):
        GetDllLibXls().ConverterSetting_set_ClearCacheOnConverted.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConverterSetting_set_ClearCacheOnConverted, self.Ptr, value)

    @property

    def PdfConformanceLevel(self)->'PdfConformanceLevel':
        """
        Gets or sets the Pdf document's Conformance-level.

        """
        GetDllLibXls().ConverterSetting_get_PdfConformanceLevel.argtypes=[c_void_p]
        GetDllLibXls().ConverterSetting_get_PdfConformanceLevel.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConverterSetting_get_PdfConformanceLevel, self.Ptr)
        objwraped = PdfConformanceLevel(ret)
        return objwraped


    @PdfConformanceLevel.setter
    def PdfConformanceLevel(self, value:'PdfConformanceLevel'):
        GetDllLibXls().ConverterSetting_set_PdfConformanceLevel.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConverterSetting_set_PdfConformanceLevel, self.Ptr, value.value)


#    @property
#
#    def PdfSecurity(self)->'PdfSecurity':
#        """
#    <summary>
#        Represents the security settings of the PDF document.
#    </summary>
#        """
#        GetDllLibXls().ConverterSetting_get_PdfSecurity.argtypes=[c_void_p]
#        GetDllLibXls().ConverterSetting_get_PdfSecurity.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().ConverterSetting_get_PdfSecurity, self.Ptr)
#        ret = None if intPtr==None else PdfSecurity(intPtr)
#        return ret
#


    #@property

    #def ChartImageType(self)->'ImageFormat':
    #    """
    #<summary>
    #     Indicate the chart render image type.
    # </summary>
    #    """
    #    GetDllLibXls().ConverterSetting_get_ChartImageType.argtypes=[c_void_p]
    #    GetDllLibXls().ConverterSetting_get_ChartImageType.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibXls().ConverterSetting_get_ChartImageType, self.Ptr)
    #    ret = None if intPtr==None else ImageFormat(intPtr)
    #    return ret


    #@ChartImageType.setter
    #def ChartImageType(self, value:'ImageFormat'):
    #    GetDllLibXls().ConverterSetting_set_ChartImageType.argtypes=[c_void_p, c_void_p]
    #    CallCFunction(GetDllLibXls().ConverterSetting_set_ChartImageType, self.Ptr, value.Ptr)

    @property
    def IsRegionClip(self)->bool:
        """
        Enables or disables clipping the image to the region

        """
        GetDllLibXls().ConverterSetting_get_IsRegionClip.argtypes=[c_void_p]
        GetDllLibXls().ConverterSetting_get_IsRegionClip.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConverterSetting_get_IsRegionClip, self.Ptr)
        return ret

    @IsRegionClip.setter
    def IsRegionClip(self, value:bool):
        GetDllLibXls().ConverterSetting_set_IsRegionClip.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConverterSetting_set_IsRegionClip, self.Ptr, value)

    @property
    def MaxConvertPages(self)->int:
        """
        Sets or gets the maximum number of pages for the conversion.

        """
        GetDllLibXls().ConverterSetting_get_MaxConvertPages.argtypes=[c_void_p]
        GetDllLibXls().ConverterSetting_get_MaxConvertPages.restype=c_int
        ret = CallCFunction(GetDllLibXls().ConverterSetting_get_MaxConvertPages, self.Ptr)
        return ret

    @MaxConvertPages.setter
    def MaxConvertPages(self, value:int):
        GetDllLibXls().ConverterSetting_set_MaxConvertPages.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().ConverterSetting_set_MaxConvertPages, self.Ptr, value)

    @property
    def ToImageWithoutMargins(self)->bool:
        """
        To image without margins. Default false.

        """
        GetDllLibXls().ConverterSetting_get_ToImageWithoutMargins.argtypes=[c_void_p]
        GetDllLibXls().ConverterSetting_get_ToImageWithoutMargins.restype=c_bool
        ret = CallCFunction(GetDllLibXls().ConverterSetting_get_ToImageWithoutMargins, self.Ptr)
        return ret

    @ToImageWithoutMargins.setter
    def ToImageWithoutMargins(self, value:bool):
        GetDllLibXls().ConverterSetting_set_ToImageWithoutMargins.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().ConverterSetting_set_ToImageWithoutMargins, self.Ptr, value)
