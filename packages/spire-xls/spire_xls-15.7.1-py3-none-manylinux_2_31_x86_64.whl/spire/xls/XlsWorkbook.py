from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsWorkbook (  XlsObject, IWorkbook) :
    """

    """

    def CreateTemplateMarkersProcessor(self)->'IMarkersDesigner':
        """
        Creates and returns a template markers processor for the workbook.

        Returns:
            IMarkersDesigner: The template markers processor instance.
        """
        GetDllLibXls().XlsWorkbook_CreateTemplateMarkersProcessor.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_CreateTemplateMarkersProcessor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_CreateTemplateMarkersProcessor, self.Ptr)
        ret = None if intPtr==None else IMarkersDesigner(intPtr)
        return ret


    @dispatch

    def Close(self ,Filename:str):
        """
        Closes the workbook and saves changes to the specified file.

        Args:
            Filename (str): The file name to save changes to.
        """
        
        GetDllLibXls().XlsWorkbook_Close.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_Close, self.Ptr, Filename)

    @dispatch

    def Close(self ,SaveChanges:bool,Filename:str):
        """
        Closes the workbook, optionally saving changes to the specified file.

        Args:
            SaveChanges (bool): Whether to save changes before closing.
            Filename (str): The file name to save changes to.
        """
        
        GetDllLibXls().XlsWorkbook_CloseSF.argtypes=[c_void_p ,c_bool,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_CloseSF, self.Ptr, SaveChanges,Filename)

    @dispatch

    def Close(self ,saveChanges:bool):
        """
        Closes the workbook, optionally saving changes.

        Args:
            saveChanges (bool): Whether to save changes before closing.
        """
        GetDllLibXls().XlsWorkbook_CloseS.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_CloseS, self.Ptr, saveChanges)

    @dispatch
    def Close(self):
        """
        Closes the workbook without saving changes.
        """
        GetDllLibXls().XlsWorkbook_Close1.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_Close1, self.Ptr)


    def AddFont(self ,fontToAdd:'IFont')->'IFont':
        """
        Adds a font to the workbook and returns the new font object.

        Args:
            fontToAdd (IFont): The font to add.

        Returns:
            IFont: The added font object.
        """
        intPtrfontToAdd:c_void_p = fontToAdd.Ptr

        GetDllLibXls().XlsWorkbook_AddFont.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsWorkbook_AddFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_AddFont, self.Ptr, intPtrfontToAdd)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret


    def Activate(self):
        """
        Activates the workbook window.
        """
        GetDllLibXls().XlsWorkbook_Activate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_Activate, self.Ptr)

#
#    def SplitPageInfo(self ,converterSetting:'ConverterSetting')->'List1':
#        """
#
#        """
#        intPtrconverterSetting:c_void_p = converterSetting.Ptr
#
#        GetDllLibXls().XlsWorkbook_SplitPageInfo.argtypes=[c_void_p ,c_void_p]
#        GetDllLibXls().XlsWorkbook_SplitPageInfo.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_SplitPageInfo, self.Ptr, intPtrconverterSetting)
#        ret = None if intPtr==None else List1(intPtr)
#        return ret
#



    def PixelsToWidth(self ,pixels:float)->float:
        """
        Converts a pixel value to a column width value.

        Args:
            pixels (float): The pixel value to convert.

        Returns:
            float: The corresponding column width.
        """
        
        GetDllLibXls().XlsWorkbook_PixelsToWidth.argtypes=[c_void_p ,c_double]
        GetDllLibXls().XlsWorkbook_PixelsToWidth.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_PixelsToWidth, self.Ptr, pixels)
        return ret


    #def ConvertUnits(self ,value:float,from:MeasureUnits,to:MeasureUnits)->float:
    #    """

    #    """
    #    enumfrom:c_int = from.value
    #    enumto:c_int = to.value

    #    GetDllLibXls().XlsWorkbook_ConvertUnits.argtypes=[c_void_p ,c_double,c_int,c_int]
    #    GetDllLibXls().XlsWorkbook_ConvertUnits.restype=c_double
    #    ret = CallCFunction(GetDllLibXls().XlsWorkbook_ConvertUnits, self.Ptr, value,enumfrom,enumto)
    #    return ret


    def DecodeName(self ,name:str)->str:
        """
        Decodes the specified name string.

        Args:
            name (str): The name to decode.

        Returns:
            str: The decoded name string.
        """
        GetDllLibXls().XlsWorkbook_DecodeName.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsWorkbook_DecodeName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorkbook_DecodeName, self.Ptr, name))
        return ret



    def EncodeName(self ,strName:str)->str:
        """
        Encodes the specified name string.

        Args:
            strName (str): The name to encode.

        Returns:
            str: The encoded name string.
        """
        GetDllLibXls().XlsWorkbook_EncodeName.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsWorkbook_EncodeName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorkbook_EncodeName, self.Ptr, strName))
        return ret



    def GetBookIndex(self ,referenceIndex:int)->int:
        """
        Gets the book index for the specified reference index.

        Args:
            referenceIndex (int): The reference index to look up.

        Returns:
            int: The corresponding book index.
        """
        
        GetDllLibXls().XlsWorkbook_GetBookIndex.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsWorkbook_GetBookIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_GetBookIndex, self.Ptr, referenceIndex)
        return ret


    def IsExternalReference(self ,reference:int)->bool:
        """
        Determines whether the specified reference is an external reference.

        Args:
            reference (int): The reference to check.

        Returns:
            bool: True if the reference is external, otherwise False.
        """
        
        GetDllLibXls().XlsWorkbook_IsExternalReference.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsWorkbook_IsExternalReference.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_IsExternalReference, self.Ptr, reference)
        return ret


    def IsFormatted(self ,xfIndex:int)->bool:
        """
        Checks if the specified XF index is formatted.

        Args:
            xfIndex (int): The XF index to check.

        Returns:
            bool: True if formatted, otherwise False.
        """
        
        GetDllLibXls().XlsWorkbook_IsFormatted.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsWorkbook_IsFormatted.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_IsFormatted, self.Ptr, xfIndex)
        return ret

    def GetMaxDigitWidth(self)->float:
        """
        Gets the maximum digit width for the workbook.

        Returns:
            float: The maximum digit width.
        """
        GetDllLibXls().XlsWorkbook_GetMaxDigitWidth.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_GetMaxDigitWidth.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_GetMaxDigitWidth, self.Ptr)
        return ret

    def Dispose(self):
        """
        Releases all resources used by the workbook.
        """
        GetDllLibXls().XlsWorkbook_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_Dispose, self.Ptr)

    @property
    def IsVScrollBarVisible(self)->bool:
        """
        Indicates whether the vertical scroll bar is visible in the workbook window.

        Returns:
            bool: True if the vertical scroll bar is visible, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_IsVScrollBarVisible.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_IsVScrollBarVisible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_IsVScrollBarVisible, self.Ptr)
        return ret

    @IsVScrollBarVisible.setter
    def IsVScrollBarVisible(self, value:bool):
        GetDllLibXls().XlsWorkbook_set_IsVScrollBarVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_IsVScrollBarVisible, self.Ptr, value)

    @property
    def Loading(self)->bool:
        """
        Indicates whether the workbook is currently loading.

        Returns:
            bool: True if the workbook is loading, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_Loading.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_Loading.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_Loading, self.Ptr)
        return ret

    @property
    def IsWindowProtection(self)->bool:
        """
        Indicates whether window protection is enabled for the workbook.

        Returns:
            bool: True if window protection is enabled, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_IsWindowProtection.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_IsWindowProtection.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_IsWindowProtection, self.Ptr)
        return ret

    @property
    def MaxColumnCount(self)->int:
        """
        Gets the maximum number of columns supported by the workbook.

        Returns:
            int: The maximum column count.
        """
        GetDllLibXls().XlsWorkbook_get_MaxColumnCount.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_MaxColumnCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_MaxColumnCount, self.Ptr)
        return ret

    @property
    def MaxRowCount(self)->int:
        """
        Gets the maximum number of rows supported by the workbook.

        Returns:
            int: The maximum row count.
        """
        GetDllLibXls().XlsWorkbook_get_MaxRowCount.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_MaxRowCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_MaxRowCount, self.Ptr)
        return ret

    @property
    def MaxDigitWidth(self)->float:
        """
        Gets the maximum digit width used in the workbook.

        Returns:
            float: The maximum digit width.
        """
        GetDllLibXls().XlsWorkbook_get_MaxDigitWidth.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_MaxDigitWidth.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_MaxDigitWidth, self.Ptr)
        return ret

    @property

    def PasswordToOpen(self)->str:
        """
        Gets the password required to open the workbook, if set.

        Returns:
            str: The password to open the workbook.
        """
        GetDllLibXls().XlsWorkbook_get_PasswordToOpen.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_PasswordToOpen.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorkbook_get_PasswordToOpen, self.Ptr))
        return ret


    @PasswordToOpen.setter
    def PasswordToOpen(self, value:str):
        GetDllLibXls().XlsWorkbook_set_PasswordToOpen.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_PasswordToOpen, self.Ptr, value)

    @property
    def ReadOnly(self)->bool:
        """
        Indicates whether the workbook is read-only.

        Returns:
            bool: True if the workbook is read-only, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_ReadOnly.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_ReadOnly.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_ReadOnly, self.Ptr)
        return ret

    @property
    def ReadOnlyRecommended(self)->bool:
        """
        Indicates whether the workbook is read-only recommended.

        Returns:
            bool: True if the workbook is read-only recommended, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_ReadOnlyRecommended.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_ReadOnlyRecommended.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_ReadOnlyRecommended, self.Ptr)
        return ret

    @ReadOnlyRecommended.setter
    def ReadOnlyRecommended(self, value:bool):
        GetDllLibXls().XlsWorkbook_set_ReadOnlyRecommended.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_ReadOnlyRecommended, self.Ptr, value)

    @property

    def RowSeparator(self)->str:
        """
        Gets the row separator used in the workbook.

        Returns:
            str: The row separator.
        """
        GetDllLibXls().XlsWorkbook_get_RowSeparator.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_RowSeparator.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorkbook_get_RowSeparator, self.Ptr))
        return ret


    @property

    def Styles(self)->'IStyles':
        """
        Gets the collection of styles in the workbook.

        Returns:
            IStyles: The collection of styles.
        """
        GetDllLibXls().XlsWorkbook_get_Styles.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_Styles.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_get_Styles, self.Ptr)
        ret = None if intPtr==None else IStyles(intPtr)
        return ret


    @property

    def TabSheets(self)->'ITabSheets':
        """
        Gets the collection of tab sheets in the workbook.

        Returns:
            ITabSheets: The collection of tab sheets.
        """
        GetDllLibXls().XlsWorkbook_get_TabSheets.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_TabSheets.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_get_TabSheets, self.Ptr)
        ret = None if intPtr==None else ITabSheets(intPtr)
        return ret


    @property
    def ThrowOnUnknownNames(self)->bool:
        """
        Indicates whether the workbook should throw an exception when encountering unknown names.

        Returns:
            bool: True if the workbook should throw an exception, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_ThrowOnUnknownNames.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_ThrowOnUnknownNames.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_ThrowOnUnknownNames, self.Ptr)
        return ret

    @ThrowOnUnknownNames.setter
    def ThrowOnUnknownNames(self, value:bool):
        GetDllLibXls().XlsWorkbook_set_ThrowOnUnknownNames.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_ThrowOnUnknownNames, self.Ptr, value)


    def ContainsFont(self ,font:'XlsFont')->bool:
        """
        Checks if the workbook contains a specific font.

        Args:
            font (XlsFont): The font to check for.

        Returns:
            bool: True if the font is found, otherwise False.       
        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().XlsWorkbook_ContainsFont.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsWorkbook_ContainsFont.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_ContainsFont, self.Ptr, intPtrfont)
        return ret


    def FileWidthToPixels(self ,fileWidth:float)->float:
        """
        Converts a file width value to a pixel value.

        Args:
            fileWidth (float): The file width value to convert.

        Returns:
            float: The corresponding pixel value.
        """
        
        GetDllLibXls().XlsWorkbook_FileWidthToPixels.argtypes=[c_void_p ,c_double]
        GetDllLibXls().XlsWorkbook_FileWidthToPixels.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_FileWidthToPixels, self.Ptr, fileWidth)
        return ret


    def WidthToFileWidth(self ,width:float)->float:
        """
        Converts a pixel width value to a file width value.

        Args:
            width (float): The pixel width value to convert.

        Returns:
            float: The corresponding file width.    
        """
        
        GetDllLibXls().XlsWorkbook_WidthToFileWidth.argtypes=[c_void_p ,c_double]
        GetDllLibXls().XlsWorkbook_WidthToFileWidth.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_WidthToFileWidth, self.Ptr, width)
        return ret

    def CopyToClipboard(self):
        """
        Copies the workbook to the clipboard.
        """
        GetDllLibXls().XlsWorkbook_CopyToClipboard.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_CopyToClipboard, self.Ptr)


    def SetWriteProtectionPassword(self ,password:str):
        """
        Sets the write protection password for the workbook.

        Args:
            password (str): The password to set for write protection.
        """
        
        GetDllLibXls().XlsWorkbook_SetWriteProtectionPassword.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_SetWriteProtectionPassword, self.Ptr, password)


    def Clone(self)->'IWorkbook':
        """
        Clones the workbook and returns a new workbook object.

        Returns:
            IWorkbook: A new workbook object that is a copy of the current workbook.
        """
        GetDllLibXls().XlsWorkbook_Clone.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_Clone, self.Ptr)
        ret = None if intPtr==None else IWorkbook(intPtr)
        return ret


    @dispatch
    def Unprotect(self):
        """
        Removes write protection from the workbook.
        """
        GetDllLibXls().XlsWorkbook_Unprotect.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_Unprotect, self.Ptr)

    @dispatch

    def Unprotect(self ,password:str):
        """
        Removes write protection from the workbook using a specified password.

        Args:
            password (str): The password used to remove write protection.
        """
        
        GetDllLibXls().XlsWorkbook_UnprotectP.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_UnprotectP, self.Ptr, password)

    @dispatch

    def Protect(self ,bIsProtectWindow:bool,bIsProtectContent:bool):
        """
        Protects the workbook with specified window and content protection settings.

        Args:
            bIsProtectWindow (bool): Whether to protect the workbook window.
            bIsProtectContent (bool): Whether to protect the workbook content.
        """
        
        GetDllLibXls().XlsWorkbook_Protect.argtypes=[c_void_p ,c_bool,c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_Protect, self.Ptr, bIsProtectWindow,bIsProtectContent)

    @dispatch

    def Protect(self ,bIsProtectWindow:bool,bIsProtectContent:bool,password:str):
        """
        Protects the workbook with specified window and content protection settings, using a password.

        Args:
            bIsProtectWindow (bool): Whether to protect the workbook window.
            bIsProtectContent (bool): Whether to protect the workbook content.
            password (str): The password used to protect the workbook.
        """
        
        GetDllLibXls().XlsWorkbook_ProtectBBP.argtypes=[c_void_p ,c_bool,c_bool,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_ProtectBBP, self.Ptr, bIsProtectWindow,bIsProtectContent,password)


    def SetSeparators(self ,argumentsSeparator:int,arrayRowsSeparator:int):
        """
        Sets the separators for the workbook.

        Args:
            argumentsSeparator (int): The separator for arguments.
            arrayRowsSeparator (int): The separator for array rows.
        """
        
        GetDllLibXls().XlsWorkbook_SetSeparators.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_SetSeparators, self.Ptr, argumentsSeparator,arrayRowsSeparator)

    @dispatch

    def SaveAs(self ,stream:Stream,separator:str):
        """
        Saves the workbook to a stream using a specified separator.

        Args:
            stream (Stream): The stream to save the workbook to.
            separator (str): The separator to use for the workbook.
        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibXls().XlsWorkbook_SaveAs.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_SaveAs, self.Ptr, intPtrstream,separator)

    @dispatch

    def SaveAs(self ,fileName:str,separator:str):
        """
        Saves the workbook to a file using a specified separator.

        Args:
            fileName (str): The name of the file to save the workbook to.
            separator (str): The separator to use for the workbook.
        """
        
        GetDllLibXls().XlsWorkbook_SaveAsFS.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_SaveAsFS, self.Ptr, fileName,separator)

    @dispatch

    def SaveAsImages(self ,dpiX:float,dpiY:float)->List[Stream]:
        """
        Saves the workbook as images with specified DPI values.

        Args:
            dpiX (float): The horizontal DPI value.
            dpiY (float): The vertical DPI value.

        Returns:        
            List[Stream]: A list of Stream objects containing the saved images.
        """
        
        GetDllLibXls().XlsWorkbook_SaveAsImages.argtypes=[c_void_p ,c_float,c_float]
        GetDllLibXls().XlsWorkbook_SaveAsImages.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().XlsWorkbook_SaveAsImages, self.Ptr, dpiX,dpiY)
        ret = GetObjVectorFromArray(intPtrArray, Stream)
        return ret


    @dispatch

    def SaveAsImages(self ,sheetIndex:int,dpiX:float,dpiY:float)->Stream:
        """
        Saves the specified sheet of the workbook as an image with specified DPI values.

        Args:
            sheetIndex (int): The index of the sheet to save.
            dpiX (float): The horizontal DPI value.
            dpiY (float): The vertical DPI value.

        Returns:
            Stream: A Stream object containing the saved image.
        """
        
        GetDllLibXls().XlsWorkbook_SaveAsImagesSDD.argtypes=[c_void_p ,c_int,c_float,c_float]
        GetDllLibXls().XlsWorkbook_SaveAsImagesSDD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_SaveAsImagesSDD, self.Ptr, sheetIndex,dpiX,dpiY)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    @dispatch

    def SaveAsImages(self ,sheetIndex:int,firstRow:int,firstColumn:int,lastRow:int,lastColumn:int,dpiX:float,dpiY:float)->Stream:
        """
        Saves the specified range of the workbook as an image with specified DPI values.

        Args:
            sheetIndex (int): The index of the sheet to save.
            firstRow (int): The first row of the range to save.
            firstColumn (int): The first column of the range to save.
            lastRow (int): The last row of the range to save.
            lastColumn (int): The last column of the range to save.
            dpiX (float): The horizontal DPI value.
            dpiY (float): The vertical DPI value.

        Returns:
            Stream: A Stream object containing the saved image.
        """
        
        GetDllLibXls().XlsWorkbook_SaveAsImagesSFFLLDD.argtypes=[c_void_p ,c_int,c_int,c_int,c_int,c_int,c_float,c_float]
        GetDllLibXls().XlsWorkbook_SaveAsImagesSFFLLDD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_SaveAsImagesSFFLLDD, self.Ptr, sheetIndex,firstRow,firstColumn,lastRow,lastColumn,dpiX,dpiY)
        ret = None if intPtr==None else Stream(intPtr)
        return ret



    def SaveAsEmfStream(self ,sheetIndex:int,EmfStream:'Stream',firstRow:int,firstColumn:int,lastRow:int,lastColumn:int):
        """
        Saves the specified range of the workbook as an EMF stream.

        Args:
            sheetIndex (int): The index of the sheet to save.
            EmfStream (Stream): The stream to save the EMF image to.
            firstRow (int): The first row of the range to save. 
            firstColumn (int): The first column of the range to save.
            lastRow (int): The last row of the range to save.
            lastColumn (int): The last column of the range to save.
        """
        intPtrEmfStream:c_void_p = EmfStream.Ptr

        GetDllLibXls().XlsWorkbook_SaveAsEmfStream.argtypes=[c_void_p ,c_int,c_void_p,c_int,c_int,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_SaveAsEmfStream, self.Ptr, sheetIndex,intPtrEmfStream,firstRow,firstColumn,lastRow,lastColumn)


    def SaveChartAsEmfImage(self ,worksheet:'Worksheet',chartIndex:int,imageOrPrintOptions:'ConverterSetting',emfStream:'Stream')->'Stream':
        """
        Saves the specified chart of the worksheet as an EMF image.

        Args:
            worksheet (Worksheet): The worksheet containing the chart.
            chartIndex (int): The index of the chart to save.
            imageOrPrintOptions (ConverterSetting): The options for the image or print.     
            emfStream (Stream): The stream to save the EMF image to.
        """
        intPtrworksheet:c_void_p = worksheet.Ptr
        intPtrimageOrPrintOptions:c_void_p = imageOrPrintOptions.Ptr
        intPtremfStream:c_void_p = emfStream.Ptr

        GetDllLibXls().XlsWorkbook_SaveChartAsEmfImage.argtypes=[c_void_p ,c_void_p,c_int,c_void_p,c_void_p]
        GetDllLibXls().XlsWorkbook_SaveChartAsEmfImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_SaveChartAsEmfImage, self.Ptr, intPtrworksheet,chartIndex,intPtrimageOrPrintOptions,intPtremfStream)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    @dispatch

    def SaveChartAsImage(self ,worksheet:Worksheet,imageOrPrintOptions:ConverterSetting)->List[Stream]:
        """
        Saves the specified chart of the worksheet as an image.

        Args:
            worksheet (Worksheet): The worksheet containing the chart.
            imageOrPrintOptions (ConverterSetting): The options for the image or print.

        Returns:
            List[Stream]: A list of Stream objects containing the saved images.
        """
        intPtrworksheet:c_void_p = worksheet.Ptr
        intPtrimageOrPrintOptions:c_void_p = imageOrPrintOptions.Ptr

        GetDllLibXls().XlsWorkbook_SaveChartAsImage.argtypes=[c_void_p ,c_void_p,c_void_p]
        GetDllLibXls().XlsWorkbook_SaveChartAsImage.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().XlsWorkbook_SaveChartAsImage, self.Ptr, intPtrworksheet,intPtrimageOrPrintOptions)
        ret = GetObjVectorFromArray(intPtrArray, Stream)
        return ret


    @dispatch

    def SaveChartAsImage(self ,chartSheet:ChartSheet,imageOrPrintOptions:ConverterSetting)->Stream:
        """
        Saves the specified chart of the worksheet as an image.

        Args:
            chartSheet (ChartSheet): The chart sheet to save.
            imageOrPrintOptions (ConverterSetting): The options for the image or print.

        Returns:    
            Stream: A Stream object containing the saved image.
        """
        intPtrchartSheet:c_void_p = chartSheet.Ptr
        intPtrimageOrPrintOptions:c_void_p = imageOrPrintOptions.Ptr

        GetDllLibXls().XlsWorkbook_SaveChartAsImageCI.argtypes=[c_void_p ,c_void_p,c_void_p]
        GetDllLibXls().XlsWorkbook_SaveChartAsImageCI.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_SaveChartAsImageCI, self.Ptr, intPtrchartSheet,intPtrimageOrPrintOptions)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    @dispatch

    def SaveChartAsImage(self ,worksheet:Worksheet,charIndex:int,imageOrPrintOptions:ConverterSetting)->Stream:
        """
        Saves the specified chart of the worksheet as an image.

        Args:
            worksheet (Worksheet): The worksheet containing the chart.
            charIndex (int): The index of the chart to save.
            imageOrPrintOptions (ConverterSetting): The options for the image or print.     

        """
        intPtrworksheet:c_void_p = worksheet.Ptr
        intPtrimageOrPrintOptions:c_void_p = imageOrPrintOptions.Ptr

        GetDllLibXls().XlsWorkbook_SaveChartAsImageWCI.argtypes=[c_void_p ,c_void_p,c_int,c_void_p]
        GetDllLibXls().XlsWorkbook_SaveChartAsImageWCI.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_SaveChartAsImageWCI, self.Ptr, intPtrworksheet,charIndex,intPtrimageOrPrintOptions)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    @dispatch

    def FindOne(self ,findValue:float,flags:FindType)->IXLSRange:
        """
        Finds a range in the workbook that contains the specified value.    

        Args:
            findValue (float): The value to find.
            flags (FindType): The flags for the search.

        Returns:
            IXLSRange: The range that contains the specified value.
        """
        enumflags:c_int = flags.value
        GetDllLibXls().XlsWorkbook_FindOne.argtypes=[c_void_p ,c_double,c_int]
        GetDllLibXls().XlsWorkbook_FindOne.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_FindOne, self.Ptr, findValue,enumflags)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def FindOne(self ,findValue:str,flags:FindType)->IXLSRange:
        """
        Finds a range in the workbook that contains the specified value.

        Args:
            findValue (str): The value to find.
            flags (FindType): The flags for the search.

        Returns:    
            IXLSRange: The range that contains the specified value.
        """
        enumflags:c_int = flags.value

        GetDllLibXls().XlsWorkbook_FindOneFF.argtypes=[c_void_p ,c_void_p,c_int]
        GetDllLibXls().XlsWorkbook_FindOneFF.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_FindOneFF, self.Ptr, findValue,enumflags)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def FindOne(self ,findValue:bool)->IXLSRange:
        """
        Finds a range in the workbook that contains the specified value.

        Args:
            findValue (bool): The value to find.

        Returns:
            IXLSRange: The range that contains the specified value.
        """
        
        GetDllLibXls().XlsWorkbook_FindOneF.argtypes=[c_void_p ,c_bool]
        GetDllLibXls().XlsWorkbook_FindOneF.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_FindOneF, self.Ptr, findValue)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def FindOne(self ,findValue:DateTime)->IXLSRange:
        """
        Finds a range in the workbook that contains the specified value.

        Args:
            findValue (DateTime): The value to find.

        Returns:
            IXLSRange: The range that contains the specified value.
        """
        intPtrfindValue:c_void_p = findValue.Ptr

        GetDllLibXls().XlsWorkbook_FindOneF1.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsWorkbook_FindOneF1.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_FindOneF1, self.Ptr, intPtrfindValue)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @dispatch

    def FindOne(self ,findValue:TimeSpan)->IXLSRange:
        """
        Finds a range in the workbook that contains the specified value.

        Args:
            findValue (TimeSpan): The value to find.

        Returns:
            IXLSRange: The range that contains the specified value. 
        """
        intPtrfindValue:c_void_p = findValue.Ptr

        GetDllLibXls().XlsWorkbook_FindOneF11.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsWorkbook_FindOneF11.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_FindOneF11, self.Ptr, intPtrfindValue)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


#    @dispatch
#
#    def FindAll(self ,findValue:str,flags:FindType)->ListCellRanges:
#        """
#
#        """
#        enumflags:c_int = flags.value
#
#        GetDllLibXls().XlsWorkbook_FindAll.argtypes=[c_void_p ,c_void_p,c_int]
#        GetDllLibXls().XlsWorkbook_FindAll.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_FindAll, self.Ptr, findValue,enumflags)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret
#


#    @dispatch
#
#    def FindAll(self ,findValue:float,flags:FindType)->ListCellRanges:
#        """
#
#        """
#        enumflags:c_int = flags.value
#
#        GetDllLibXls().XlsWorkbook_FindAllFF.argtypes=[c_void_p ,c_double,c_int]
#        GetDllLibXls().XlsWorkbook_FindAllFF.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_FindAllFF, self.Ptr, findValue,enumflags)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret


#    @dispatch
#
#    def FindAll(self ,findValue:bool)->ListCellRanges:
#        """
#
#        """
#        
#        GetDllLibXls().XlsWorkbook_FindAllF.argtypes=[c_void_p ,c_bool]
#        GetDllLibXls().XlsWorkbook_FindAllF.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_FindAllF, self.Ptr, findValue)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret


#    @dispatch
#
#    def FindAll(self ,findValue:DateTime)->ListCellRanges:
#        """
#
#        """
#        intPtrfindValue:c_void_p = findValue.Ptr
#
#        GetDllLibXls().XlsWorkbook_FindAllF1.argtypes=[c_void_p ,c_void_p]
#        GetDllLibXls().XlsWorkbook_FindAllF1.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_FindAllF1, self.Ptr, intPtrfindValue)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret


#    @dispatch
#
#    def FindAll(self ,findValue:TimeSpan)->ListCellRanges:
#        """
#
#        """
#        intPtrfindValue:c_void_p = findValue.Ptr
#
#        GetDllLibXls().XlsWorkbook_FindAllF11.argtypes=[c_void_p ,c_void_p]
#        GetDllLibXls().XlsWorkbook_FindAllF11.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_FindAllF11, self.Ptr, intPtrfindValue)
#        ret = None if intPtr==None else ListCellRanges(intPtr)
#        return ret


    @dispatch

    def Replace(self ,oldValue:str,newValue:str):
        """
        Replaces all occurrences of a specified value with a new value in the workbook.

        Args:
            oldValue (str): The value to replace.
            newValue (str): The new value.  
        """
        
        GetDllLibXls().XlsWorkbook_Replace.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_Replace, self.Ptr, oldValue,newValue)

    @dispatch

    def Replace(self ,oldValue:str,newValue:DateTime):
        """
        Replaces all occurrences of a specified value with a new value in the workbook.

        Args:
            oldValue (str): The value to replace.
            newValue (DateTime): The new value.
        """
        intPtrnewValue:c_void_p = newValue.Ptr

        GetDllLibXls().XlsWorkbook_ReplaceON.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_ReplaceON, self.Ptr, oldValue,intPtrnewValue)

    @dispatch

    def Replace(self ,oldValue:str,newValue:float):
        """
        Replaces all occurrences of a specified value with a new value in the workbook.

        Args:
            oldValue (str): The value to replace.
            newValue (float): The new value.
        """
        
        GetDllLibXls().XlsWorkbook_ReplaceON1.argtypes=[c_void_p ,c_void_p,c_double]
        CallCFunction(GetDllLibXls().XlsWorkbook_ReplaceON1, self.Ptr, oldValue,newValue)

    @dispatch

    def Replace(self ,oldValue:str,newValues:List[str],isVertical:bool):
        """
        Replaces all occurrences of a specified value with a new value in the workbook.

        Args:
            oldValue (str): The value to replace.
            newValues (List[str]): The new values.
            isVertical (bool): Whether the new values are in a vertical format.
        """
        #arraynewValues:ArrayTypenewValues = ""
        countnewValues = len(newValues)
        ArrayTypenewValues = c_wchar_p * countnewValues
        arraynewValues = ArrayTypenewValues()
        for i in range(0, countnewValues):
            arraynewValues[i] = newValues[i]


        GetDllLibXls().XlsWorkbook_ReplaceONI.argtypes=[c_void_p ,c_void_p,ArrayTypenewValues,c_int,c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_ReplaceONI, self.Ptr, oldValue,arraynewValues,countnewValues,isVertical)

    @dispatch

    def Replace(self ,oldValue:str,newValues:List[int],isVertical:bool):
        """
        Replaces all occurrences of a specified value with a new value in the workbook.

        Args:
            oldValue (str): The value to replace.
            newValues (List[int]): The new values.
            isVertical (bool): Whether the new values are in a vertical format.
        """
        #arraynewValues:ArrayTypenewValues = ""
        countnewValues = len(newValues)
        ArrayTypenewValues = c_int * countnewValues
        arraynewValues = ArrayTypenewValues()
        for i in range(0, countnewValues):
            arraynewValues[i] = newValues[i]


        GetDllLibXls().XlsWorkbook_ReplaceONI1.argtypes=[c_void_p ,c_void_p,ArrayTypenewValues,c_int,c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_ReplaceONI1, self.Ptr, oldValue,arraynewValues,countnewValues,isVertical)

    @dispatch

    def Replace(self ,oldValue:str,newValues:List[float],isVertical:bool):
        """
        Replaces all occurrences of a specified value with a new value in the workbook.

        Args:
            oldValue (str): The value to replace.
            newValues (List[float]): The new values.
            isVertical (bool): Whether the new values are in a vertical format. 
        """
        #arraynewValues:ArrayTypenewValues = ""
        countnewValues = len(newValues)
        ArrayTypenewValues = c_double * countnewValues
        arraynewValues = ArrayTypenewValues()
        for i in range(0, countnewValues):
            arraynewValues[i] = newValues[i]


        GetDllLibXls().XlsWorkbook_ReplaceONI11.argtypes=[c_void_p ,c_void_p,ArrayTypenewValues,c_int,c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_ReplaceONI11, self.Ptr, oldValue,arraynewValues,countnewValues,isVertical)

#    @dispatch
#
#    def Replace(self ,oldValue:str,newValues:'DataTable',isFieldNamesShown:bool):
#        """
#
#        """
#        intPtrnewValues:c_void_p = newValues.Ptr
#
#        GetDllLibXls().XlsWorkbook_ReplaceONI111.argtypes=[c_void_p ,c_void_p,c_void_p,c_bool]
#        CallCFunction(GetDllLibXls().XlsWorkbook_ReplaceONI111, self.Ptr, oldValue,intPtrnewValues,isFieldNamesShown)


#    @dispatch
#
#    def Replace(self ,oldValue:str,newValues:'DataColumn',isFieldNamesShown:bool):
#        """
#
#        """
#        intPtrnewValues:c_void_p = newValues.Ptr
#
#        GetDllLibXls().XlsWorkbook_ReplaceONI1111.argtypes=[c_void_p ,c_void_p,c_void_p,c_bool]
#        CallCFunction(GetDllLibXls().XlsWorkbook_ReplaceONI1111, self.Ptr, oldValue,intPtrnewValues,isFieldNamesShown)


    @dispatch

    def CreateFont(self)->IFont:
        """
        Creates a new font object.

        Returns:
            IFont: The new font object.
        """
        GetDllLibXls().XlsWorkbook_CreateFont.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_CreateFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_CreateFont, self.Ptr)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret


    @dispatch

    def CreateFont(self ,nativeFont:Font)->IFont:
        """
        Creates a new font object using a native font.

        Args:
            nativeFont (Font): The native font to use.

        Returns:
            IFont: The new font object.
        """
        intPtrnativeFont:c_void_p = nativeFont.Ptr

        GetDllLibXls().XlsWorkbook_CreateFontN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsWorkbook_CreateFontN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_CreateFontN, self.Ptr, intPtrnativeFont)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret


    @dispatch

    def CreateFont(self ,baseFont:IFont)->IFont:
        """
        Creates a new font object using a base font.

        Args:
            baseFont (IFont): The base font to use.

        Returns:
            IFont: The new font object.
        """
        intPtrbaseFont:c_void_p = baseFont.Ptr

        GetDllLibXls().XlsWorkbook_CreateFontB.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsWorkbook_CreateFontB.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_CreateFontB, self.Ptr, intPtrbaseFont)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret


    @dispatch
    def CreateFont(self ,baseFont:IFont,bAddToCollection:bool)->IFont:
        """
        Creates a new font based on an existing font, optionally adding it to the workbook's font collection.

        Args:
            baseFont (IFont): The base font to copy properties from.
            bAddToCollection (bool): Whether to add the new font to the workbook's font collection.

        Returns:
            IFont: The newly created font.
        """
        intPtrbaseFont:c_void_p = baseFont.Ptr
        GetDllLibXls().XlsWorkbook_CreateFontBB.argtypes=[c_void_p ,c_void_p,c_bool]
        GetDllLibXls().XlsWorkbook_CreateFontBB.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_CreateFontBB, self.Ptr, intPtrbaseFont,bAddToCollection)
        ret = None if intPtr==None else XlsFont(intPtr)
        return ret


    @dispatch
    def SetColorOrGetNearest(self ,color:Color)->ExcelColors:
        """
        Sets a color in the workbook's palette or returns the nearest matching color if the exact color is not available.

        Args:
            color (Color): The color to set or find nearest match for.

        Returns:
            ExcelColors: The nearest matching Excel color.
        """
        intPtrcolor:c_void_p = color.Ptr
        GetDllLibXls().XlsWorkbook_SetColorOrGetNearest.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsWorkbook_SetColorOrGetNearest.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_SetColorOrGetNearest, self.Ptr, intPtrcolor)
        objwraped = ExcelColors(ret)
        return objwraped


    def SetActiveWorksheet(self ,sheet:'XlsWorksheetBase'):
        """
        Sets the specified worksheet as the active worksheet in the workbook.

        Args:
            sheet (XlsWorksheetBase): The worksheet to set as active.
        """
        intPtrsheet:c_void_p = sheet.Ptr
        GetDllLibXls().XlsWorkbook_SetActiveWorksheet.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_SetActiveWorksheet, self.Ptr, intPtrsheet)

    def SetChanged(self):
        """
        Marks the workbook as having unsaved changes.
        This method is called when modifications are made to the workbook that need to be saved.
        """
        GetDllLibXls().XlsWorkbook_SetChanged.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_SetChanged, self.Ptr)

    @dispatch
    def SetColorOrGetNearest(self ,r:int,g:int,b:int)->ExcelColors:
        """
        Sets a color in the workbook's palette or returns the nearest matching color based on RGB values.

        Args:
            r (int): The red component (0-255).
            g (int): The green component (0-255).
            b (int): The blue component (0-255).

        Returns:
            ExcelColors: The nearest matching Excel color.
        """
        GetDllLibXls().XlsWorkbook_SetColorOrGetNearestRGB.argtypes=[c_void_p ,c_int,c_int,c_int]
        GetDllLibXls().XlsWorkbook_SetColorOrGetNearestRGB.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_SetColorOrGetNearestRGB, self.Ptr, r,g,b)
        objwraped = ExcelColors(ret)
        return objwraped


    def SetMaxDigitWidth(self ,w:int):
        """
        Sets the maximum width of digits in the workbook.

        Args:
            w (int): The maximum digit width to set.
        """
        GetDllLibXls().XlsWorkbook_SetMaxDigitWidth.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_SetMaxDigitWidth, self.Ptr, w)

    @dispatch
    def GetNearestColor(self ,color:Color)->ExcelColors:
        """
        Gets the nearest matching Excel color for the specified color.

        Args:
            color (Color): The color to find the nearest match for.

        Returns:
            ExcelColors: The nearest matching Excel color.
        """
        intPtrcolor:c_void_p = color.Ptr
        GetDllLibXls().XlsWorkbook_GetNearestColor.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsWorkbook_GetNearestColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_GetNearestColor, self.Ptr, intPtrcolor)
        objwraped = ExcelColors(ret)
        return objwraped

    @dispatch
    def GetNearestColor(self ,color:Color,iStartIndex:int)->ExcelColors:
        """
        Gets the nearest matching Excel color for the specified color, starting from a specific index.

        Args:
            color (Color): The color to find the nearest match for.
            iStartIndex (int): The index to start searching from in the color palette.

        Returns:
            ExcelColors: The nearest matching Excel color.
        """
        intPtrcolor:c_void_p = color.Ptr
        GetDllLibXls().XlsWorkbook_GetNearestColorCI.argtypes=[c_void_p ,c_void_p,c_int]
        GetDllLibXls().XlsWorkbook_GetNearestColorCI.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_GetNearestColorCI, self.Ptr, intPtrcolor,iStartIndex)
        objwraped = ExcelColors(ret)
        return objwraped

    @dispatch
    def GetNearestColor(self ,r:int,g:int,b:int)->ExcelColors:
        """
        Gets the nearest matching Excel color for the specified RGB values.

        Args:
            r (int): The red component (0-255).
            g (int): The green component (0-255).
            b (int): The blue component (0-255).

        Returns:
            ExcelColors: The nearest matching Excel color.
        """
        GetDllLibXls().XlsWorkbook_GetNearestColorRGB.argtypes=[c_void_p ,c_int,c_int,c_int]
        GetDllLibXls().XlsWorkbook_GetNearestColorRGB.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_GetNearestColorRGB, self.Ptr, r,g,b)
        objwraped = ExcelColors(ret)
        return objwraped

    def GetPaletteColor(self ,color:'ExcelColors')->'Color':
        """
        Gets the Color object corresponding to the specified Excel color.

        Args:
            color (ExcelColors): The Excel color to get the Color object for.

        Returns:
            Color: The Color object corresponding to the Excel color.
        """
        enumcolor:c_int = color.value
        GetDllLibXls().XlsWorkbook_GetPaletteColor.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsWorkbook_GetPaletteColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_GetPaletteColor, self.Ptr, enumcolor)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    def ResetPalette(self):
        """
        Resets the workbook's color palette to its default state.
        This will restore all colors to their original Excel default values.
        """
        GetDllLibXls().XlsWorkbook_ResetPalette.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_ResetPalette, self.Ptr)

    def SetPaletteColor(self ,index:int,color:'Color'):
        """
        Sets a specific color in the workbook's palette.

        Args:
            index (int): The index in the palette where to set the color.
            color (Color): The color to set in the palette.
        """
        intPtrcolor:c_void_p = color.Ptr
        GetDllLibXls().XlsWorkbook_SetPaletteColor.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_SetPaletteColor, self.Ptr, index,intPtrcolor)

#    @dispatch
#
#    def SaveAs(self ,fileName:str,response:'HttpResponse'):
#        """
#
#        """
#        intPtrresponse:c_void_p = response.Ptr
#
#        GetDllLibXls().XlsWorkbook_SaveAsFR.argtypes=[c_void_p ,c_void_p,c_void_p]
#        CallCFunction(GetDllLibXls().XlsWorkbook_SaveAsFR, self.Ptr, fileName,intPtrresponse)


#    @dispatch
#
#    def SaveAs(self ,fileName:str,saveType:ExcelSaveType,response:'HttpResponse'):
#        """
#
#        """
#        enumsaveType:c_int = saveType.value
#        intPtrresponse:c_void_p = response.Ptr
#
#        GetDllLibXls().XlsWorkbook_SaveAsFSR.argtypes=[c_void_p ,c_void_p,c_int,c_void_p]
#        CallCFunction(GetDllLibXls().XlsWorkbook_SaveAsFSR, self.Ptr, fileName,enumsaveType,intPtrresponse)


    @dispatch

    def SaveAs(self ,stream:Stream,saveType:ExcelSaveType):
        """
        Saves the workbook to a stream with the specified save type.

        Args:
            stream (Stream): The stream to save the workbook to.
            saveType (ExcelSaveType): The type of Excel file to save as.
        """
        intPtrstream:c_void_p = stream.Ptr
        enumsaveType:c_int = saveType.value

        GetDllLibXls().XlsWorkbook_SaveAsSS.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_SaveAsSS, self.Ptr, intPtrstream,enumsaveType)

    @dispatch
    def SaveAs(self ,stream:Stream,saveType:ExcelSaveType,version:ExcelVersion):
        """
        Saves the workbook to a stream with the specified save type and Excel version.

        Args:
            stream (Stream): The stream to save the workbook to.
            saveType (ExcelSaveType): The type of Excel file to save as.
            version (ExcelVersion): The Excel version to save as.
        """
        intPtrstream:c_void_p = stream.Ptr
        enumsaveType:c_int = saveType.value
        enumversion:c_int = version.value

        GetDllLibXls().XlsWorkbook_SaveAsSSV.argtypes=[c_void_p ,c_void_p,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_SaveAsSSV, self.Ptr, intPtrstream,enumsaveType,enumversion)

    @dispatch
    def SaveAs(self ,stream:Stream):
        """
        Saves the workbook to a stream using the default save type.

        Args:
            stream (Stream): The stream to save the workbook to.
        """
        intPtrstream:c_void_p = stream.Ptr
        GetDllLibXls().XlsWorkbook_SaveAsS.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_SaveAsS, self.Ptr, intPtrstream)

    @dispatch
    def SaveAs(self ,fileName:str,saveType:ExcelSaveType):
        """
        Saves the workbook to a file with the specified save type.

        Args:
            fileName (str): The name of the file to save to.
            saveType (ExcelSaveType): The type of Excel file to save as.
        """
        enumsaveType:c_int = saveType.value

        GetDllLibXls().XlsWorkbook_SaveAsFS1.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_SaveAsFS1, self.Ptr, fileName,enumsaveType)

    @dispatch
    def SaveAs(self ,fileName:str,saveType:ExcelSaveType,version:ExcelVersion):
        """
        Saves the workbook to a file with the specified save type and Excel version.

        Args:
            fileName (str): The name of the file to save to.
            saveType (ExcelSaveType): The type of Excel file to save as.
            version (ExcelVersion): The Excel version to save as.
        """
        enumsaveType:c_int = saveType.value
        enumversion:c_int = version.value

        GetDllLibXls().XlsWorkbook_SaveAsFSV.argtypes=[c_void_p ,c_void_p,c_int,c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_SaveAsFSV, self.Ptr, fileName,enumsaveType,enumversion)

    @dispatch

    def SaveToXlsm(self ,fileName:str):
        """
        Saves the workbook as an XLSM file (Excel workbook with macros).

        Args:
            fileName (str): The name of the file to save to.
        """
        
        GetDllLibXls().XlsWorkbook_SaveToXlsm.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_SaveToXlsm, self.Ptr, fileName)

    @dispatch
    def SaveToXlsm(self ,stream:Stream):
        """
        Saves the workbook as an XLSM file (Excel workbook with macros) to a stream.

        Args:
            stream (Stream): The stream to save the workbook to.
        """
        intPtrstream:c_void_p = stream.Ptr
        GetDllLibXls().XlsWorkbook_SaveToXlsmS.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_SaveToXlsmS, self.Ptr, intPtrstream)

    @dispatch
    def SaveToPdf(self ,stream:Stream):
        """
        Saves the workbook as a PDF file to a stream.

        Args:
            stream (Stream): The stream to save the PDF to.
        """
        intPtrstream:c_void_p = stream.Ptr
        GetDllLibXls().XlsWorkbook_SaveToPdf.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_SaveToPdf, self.Ptr, intPtrstream)

    @dispatch
    def SaveToPdf(self ,fileName:str):
        """
        Saves the workbook as a PDF file.

        Args:
            fileName (str): The name of the PDF file to save to.
        """
        
        GetDllLibXls().XlsWorkbook_SaveToPdfF.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_SaveToPdfF, self.Ptr, fileName)

    @dispatch
    def SaveAsImageOrXps(self ,stream:Stream,fileFormat:FileFormat):
        """
        Saves the workbook as an image or XPS file to a stream.

        Args:
            stream (Stream): The stream to save the file to.
            fileFormat (FileFormat): The format to save the file as (image or XPS).
        """
        intPtrstream:c_void_p = stream.Ptr
        enumfileFormat:c_int = fileFormat.value
        GetDllLibXls().XlsWorkbook_SaveAsImageOrXps.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_SaveAsImageOrXps, self.Ptr, intPtrstream,enumfileFormat)

    @dispatch
    def SaveAsImageOrXps(self ,fileName:str,fileFormat:FileFormat):
        """
        Saves the workbook as an image or XPS file.

        Args:
            fileName (str): The name of the file to save to.
            fileFormat (FileFormat): The format to save the file as (image or XPS).
        """
        enumfileFormat:c_int = fileFormat.value

        GetDllLibXls().XlsWorkbook_SaveAsImageOrXpsFF.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_SaveAsImageOrXpsFF, self.Ptr, fileName,enumfileFormat)


    def SaveAsHtml(self ,fileName:str,saveOption:'HTMLOptions'):
        """
        Saves the workbook as an HTML file with specified options.

        Args:
            fileName (str): The name of the HTML file to save to.
            saveOption (HTMLOptions): The options for saving as HTML.
        """
        intPtrsaveOption:c_void_p = saveOption.Ptr

        GetDllLibXls().XlsWorkbook_SaveAsHtml.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_SaveAsHtml, self.Ptr, fileName,intPtrsaveOption)

    @dispatch
    def SaveAs(self ,FileName:str):
        """
        Saves the workbook to a file using the default save type.

        Args:
            FileName (str): The name of the file to save to.
        """
        
        GetDllLibXls().XlsWorkbook_SaveAsF.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_SaveAsF, self.Ptr, FileName)

    def Save(self):
        """
        Saves the workbook using its current file name and format.
        If the workbook hasn't been saved before, this will throw an exception.
        """
        GetDllLibXls().XlsWorkbook_Save.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_Save, self.Ptr)

    @property
    def StandardRowHeight(self)->float:
        """
        Gets the standard row height of the workbook.

        Returns:
            float: The standard row height.
        """
        GetDllLibXls().XlsWorkbook_get_StandardRowHeight.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_StandardRowHeight.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_StandardRowHeight, self.Ptr)
        return ret

    @StandardRowHeight.setter
    def StandardRowHeight(self, value:float):
        GetDllLibXls().XlsWorkbook_set_StandardRowHeight.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_StandardRowHeight, self.Ptr, value)

    @property
    def StandardRowHeightInPixels(self)->int:
        """
        Gets the standard row height in pixels.

        Returns:
            int: The standard row height in pixels.
        """
        GetDllLibXls().XlsWorkbook_get_StandardRowHeightInPixels.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_StandardRowHeightInPixels.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_StandardRowHeightInPixels, self.Ptr)
        return ret

    @StandardRowHeightInPixels.setter
    def StandardRowHeightInPixels(self, value:int):
        GetDllLibXls().XlsWorkbook_set_StandardRowHeightInPixels.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_StandardRowHeightInPixels, self.Ptr, value)

    @property
    def MaxXFCount(self)->int:
        """
        Gets the maximum number of XF records allowed in the workbook.

        Returns:
            int: The maximum XF count.
        """
        GetDllLibXls().XlsWorkbook_get_MaxXFCount.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_MaxXFCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_MaxXFCount, self.Ptr)
        return ret

    @property
    def MaxIndent(self)->int:
        """
        Gets the maximum indent level allowed in the workbook.

        Returns:
            int: The maximum indent level.
        """
        GetDllLibXls().XlsWorkbook_get_MaxIndent.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_MaxIndent.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_MaxIndent, self.Ptr)
        return ret

    @property

    def Version(self)->'ExcelVersion':
        """
        Gets the Excel version of the workbook.

        Returns:
            ExcelVersion: The Excel version.
        """
        GetDllLibXls().XlsWorkbook_get_Version.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_Version.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_Version, self.Ptr)
        objwraped = ExcelVersion(ret)
        return objwraped

    @Version.setter
    def Version(self, value:'ExcelVersion'):
        GetDllLibXls().XlsWorkbook_set_Version.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_Version, self.Ptr, value.value)

    @property

    def Worksheets(self)->'IWorksheets':
        """
        Gets the collection of worksheets in the workbook.

        Returns:
            IWorksheets: The collection of worksheets.
        """
        GetDllLibXls().XlsWorkbook_get_Worksheets.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_Worksheets.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_get_Worksheets, self.Ptr)
        ret = None if intPtr==None else IWorksheets(intPtr)
        return ret


    @property

    def InnerAddInFunctions(self)->'XlsAddInFunctionsCollection':
        """
        Gets the collection of add-in functions in the workbook.

        Returns:
            XlsAddInFunctionsCollection: The collection of add-in functions.
        """
        GetDllLibXls().XlsWorkbook_get_InnerAddInFunctions.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_InnerAddInFunctions.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_get_InnerAddInFunctions, self.Ptr)
        ret = None if intPtr==None else XlsAddInFunctionsCollection(intPtr)
        return ret


    @property

    def InnerFonts(self)->'XlsFontsCollection':
        """
        Gets the collection of fonts in the workbook.

        Returns:
            XlsFontsCollection: The collection of fonts.
        """
        GetDllLibXls().XlsWorkbook_get_InnerFonts.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_InnerFonts.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_get_InnerFonts, self.Ptr)
        ret = None if intPtr==None else XlsFontsCollection(intPtr)
        return ret


#    @property
#
#    def InnerGraphics(self)->'Graphics':
#        """
#
#        """
#        GetDllLibXls().XlsWorkbook_get_InnerGraphics.argtypes=[c_void_p]
#        GetDllLibXls().XlsWorkbook_get_InnerGraphics.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_get_InnerGraphics, self.Ptr)
#        ret = None if intPtr==None else Graphics(intPtr)
#        return ret
#


#    @property
#
#    def InnerPalette(self)->'List1':
#        """
#
#        """
#        GetDllLibXls().XlsWorkbook_get_InnerPalette.argtypes=[c_void_p]
#        GetDllLibXls().XlsWorkbook_get_InnerPalette.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_get_InnerPalette, self.Ptr)
#        ret = None if intPtr==None else List1(intPtr)
#        return ret
#


    @property

    def Names(self)->'INameRanges':
        """
        Gets the collection of named ranges in the workbook.

        Returns:
            INameRanges: The collection of named ranges.
        """
        GetDllLibXls().XlsWorkbook_get_Names.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_Names.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_get_Names, self.Ptr)
        ret = None if intPtr==None else INameRanges(intPtr)
        return ret


    @property

    def DataConns(self)->'DataConnections':
        """
        Gets the collection of data connections in the workbook.

        Returns:
            DataConnections: The collection of data connections.
        """
        GetDllLibXls().XlsWorkbook_get_DataConns.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_DataConns.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_get_DataConns, self.Ptr)
        ret = None if intPtr==None else DataConnections(intPtr)
        return ret


    @property

    def ExternalLinks(self)->'ExternalLinkCollection':
        """
        Gets the collection of external links in the workbook.

        Returns:
            ExternalLinkCollection: The collection of external links.
        """
        GetDllLibXls().XlsWorkbook_get_ExternalLinks.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_ExternalLinks.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_get_ExternalLinks, self.Ptr)
        ret = None if intPtr==None else ExternalLinkCollection(intPtr)
        return ret


    @property
    def ObjectCount(self)->int:
        """
        Gets the total number of objects in the workbook.

        Returns:
            int: The total number of objects.
        """
        GetDllLibXls().XlsWorkbook_get_ObjectCount.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_ObjectCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_ObjectCount, self.Ptr)
        return ret

    @property

    def OleSize(self)->'IXLSRange':
        """
        Gets or sets the OLE size range of the workbook.

        Returns:
            IXLSRange: The OLE size range.
        """
        GetDllLibXls().XlsWorkbook_get_OleSize.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_OleSize.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_get_OleSize, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @OleSize.setter
    def OleSize(self, value:'IXLSRange'):
        GetDllLibXls().XlsWorkbook_set_OleSize.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_OleSize, self.Ptr, value.Ptr)

    @property

    def ActiveSheet(self)->'IWorksheet':
        """

        """
        GetDllLibXls().XlsWorkbook_get_ActiveSheet.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_ActiveSheet.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_get_ActiveSheet, self.Ptr)
        ret = None if intPtr==None else XlsWorksheet(intPtr)
        return ret


    @property
    def ActiveSheetIndex(self)->int:
        """

        """
        GetDllLibXls().XlsWorkbook_get_ActiveSheetIndex.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_ActiveSheetIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_ActiveSheetIndex, self.Ptr)
        return ret

    @ActiveSheetIndex.setter
    def ActiveSheetIndex(self, value:int):
        GetDllLibXls().XlsWorkbook_set_ActiveSheetIndex.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_ActiveSheetIndex, self.Ptr, value)

    @property

    def CodeName(self)->str:
        """

        """
        GetDllLibXls().XlsWorkbook_get_CodeName.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_CodeName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorkbook_get_CodeName, self.Ptr))
        return ret


    @CodeName.setter
    def CodeName(self, value:str):
        GetDllLibXls().XlsWorkbook_set_CodeName.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_CodeName, self.Ptr, value)

    @property

    def Palette(self)->List['Color']:
        """

        """
        GetDllLibXls().XlsWorkbook_get_Palette.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_Palette.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().XlsWorkbook_get_Palette, self.Ptr)
        ret = GetVectorFromArray(intPtrArray, Color)
        return ret


    @property
    def Date1904(self)->bool:
        """

        """
        GetDllLibXls().XlsWorkbook_get_Date1904.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_Date1904.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_Date1904, self.Ptr)
        return ret

    @Date1904.setter
    def Date1904(self, value:bool):
        GetDllLibXls().XlsWorkbook_set_Date1904.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_Date1904, self.Ptr, value)

    @property

    def StandardFont(self)->str:
        """

        """
        GetDllLibXls().XlsWorkbook_get_StandardFont.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_StandardFont.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorkbook_get_StandardFont, self.Ptr))
        return ret


    @StandardFont.setter
    def StandardFont(self, value:str):
        GetDllLibXls().XlsWorkbook_set_StandardFont.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_StandardFont, self.Ptr, value)

    @property
    def StandardFontSize(self)->float:
        """

        """
        GetDllLibXls().XlsWorkbook_get_StandardFontSize.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_StandardFontSize.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_StandardFontSize, self.Ptr)
        return ret

    @StandardFontSize.setter
    def StandardFontSize(self, value:float):
        GetDllLibXls().XlsWorkbook_set_StandardFontSize.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_StandardFontSize, self.Ptr, value)

    @property
    def DisableMacrosStart(self)->bool:
        """
        Gets or sets whether macros are disabled when the workbook starts.

        Returns:
            bool: True if macros are disabled on startup, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_DisableMacrosStart.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_DisableMacrosStart.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_DisableMacrosStart, self.Ptr)
        return ret

    @DisableMacrosStart.setter
    def DisableMacrosStart(self, value:bool):
        GetDllLibXls().XlsWorkbook_set_DisableMacrosStart.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_DisableMacrosStart, self.Ptr, value)

    @property
    def FirstCharSize(self)->int:
        """
        Gets or sets the size of the first character in the workbook.

        Returns:
            int: The size of the first character.
        """
        GetDllLibXls().XlsWorkbook_get_FirstCharSize.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_FirstCharSize.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_FirstCharSize, self.Ptr)
        return ret

    @FirstCharSize.setter
    def FirstCharSize(self, value:int):
        GetDllLibXls().XlsWorkbook_set_FirstCharSize.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_FirstCharSize, self.Ptr, value)

    @property
    def SecondCharSize(self)->int:
        """
        Gets or sets the size of the second character in the workbook.

        Returns:
            int: The size of the second character.
        """
        GetDllLibXls().XlsWorkbook_get_SecondCharSize.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_SecondCharSize.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_SecondCharSize, self.Ptr)
        return ret

    @SecondCharSize.setter
    def SecondCharSize(self, value:int):
        GetDllLibXls().XlsWorkbook_set_SecondCharSize.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_SecondCharSize, self.Ptr, value)

    @property

    def FullFileName(self)->str:
        """
        Gets the full path and name of the workbook file.

        Returns:
            str: The complete file path and name.
        """
        GetDllLibXls().XlsWorkbook_get_FullFileName.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_FullFileName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorkbook_get_FullFileName, self.Ptr))
        return ret


    @property
    def HasDuplicatedNames(self)->bool:
        """
        Gets or sets whether the workbook contains duplicate named ranges.

        Returns:
            bool: True if the workbook has duplicate names, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_HasDuplicatedNames.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_HasDuplicatedNames.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_HasDuplicatedNames, self.Ptr)
        return ret

    @HasDuplicatedNames.setter
    def HasDuplicatedNames(self, value:bool):
        GetDllLibXls().XlsWorkbook_set_HasDuplicatedNames.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_HasDuplicatedNames, self.Ptr, value)

    @property
    def HasMacros(self)->bool:
        """
        Gets whether the workbook contains macros.

        Returns:
            bool: True if the workbook has macros, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_HasMacros.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_HasMacros.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_HasMacros, self.Ptr)
        return ret

    @property
    def Saved(self)->bool:
        """
        Gets or sets whether the workbook has been saved.

        Returns:
            bool: True if the workbook has been saved, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_Saved.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_Saved.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_Saved, self.Ptr)
        return ret

    @Saved.setter
    def Saved(self, value:bool):
        GetDllLibXls().XlsWorkbook_set_Saved.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_Saved, self.Ptr, value)

    @property
    def Saving(self)->bool:
        """
        Gets whether the workbook is currently being saved.

        Returns:
            bool: True if the workbook is being saved, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_Saving.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_Saving.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_Saving, self.Ptr)
        return ret

    @property

    def Author(self)->str:
        """
        Gets or sets the author of the workbook.

        Returns:
            str: The name of the workbook author.
        """
        GetDllLibXls().XlsWorkbook_get_Author.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_Author.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorkbook_get_Author, self.Ptr))
        return ret


    @Author.setter
    def Author(self, value:str):
        GetDllLibXls().XlsWorkbook_set_Author.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_Author, self.Ptr, value)

    @property

    def AddInFunctions(self)->'IAddInFunctions':
        """
        Gets the collection of add-in functions in the workbook.

        Returns:
            IAddInFunctions: The collection of add-in functions.
        """
        GetDllLibXls().XlsWorkbook_get_AddInFunctions.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_AddInFunctions.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_get_AddInFunctions, self.Ptr)
        ret = None if intPtr==None else IAddInFunctions(intPtr)
        return ret


    @property
    def Allow3DRangesInDataValidation(self)->bool:
        """
        Gets or sets whether 3D ranges are allowed in data validation.

        Returns:
            bool: True if 3D ranges are allowed, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_Allow3DRangesInDataValidation.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_Allow3DRangesInDataValidation.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_Allow3DRangesInDataValidation, self.Ptr)
        return ret

    @Allow3DRangesInDataValidation.setter
    def Allow3DRangesInDataValidation(self, value:bool):
        GetDllLibXls().XlsWorkbook_set_Allow3DRangesInDataValidation.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_Allow3DRangesInDataValidation, self.Ptr, value)

    @property

    def ArgumentsSeparator(self)->str:
        """
        Gets the separator used for function arguments in the workbook.

        Returns:
            str: The arguments separator character.
        """
        GetDllLibXls().XlsWorkbook_get_ArgumentsSeparator.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_ArgumentsSeparator.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorkbook_get_ArgumentsSeparator, self.Ptr))
        return ret


    @property

    def BuiltInDocumentProperties(self)->'IBuiltInDocumentProperties':
        """
        Gets the collection of built-in document properties.

        Returns:
            IBuiltInDocumentProperties: The collection of built-in document properties.
        """
        GetDllLibXls().XlsWorkbook_get_BuiltInDocumentProperties.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_BuiltInDocumentProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_get_BuiltInDocumentProperties, self.Ptr)
        ret = None if intPtr==None else IBuiltInDocumentProperties(intPtr)
        return ret


    @property

    def Charts(self)->'ICharts':
        """
        Gets the collection of charts in the workbook.

        Returns:
            ICharts: The collection of charts.
        """
        GetDllLibXls().XlsWorkbook_get_Charts.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_Charts.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_get_Charts, self.Ptr)
        ret = None if intPtr==None else ICharts(intPtr)
        return ret


    @property

    def CustomDocumentProperties(self)->'ICustomDocumentProperties':
        """
        Gets the collection of custom document properties.

        Returns:
            ICustomDocumentProperties: The collection of custom document properties.
        """
        GetDllLibXls().XlsWorkbook_get_CustomDocumentProperties.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_CustomDocumentProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_get_CustomDocumentProperties, self.Ptr)
        ret = None if intPtr==None else ICustomDocumentProperties(intPtr)
        return ret


    @property
    def CurrentObjectId(self)->int:
        """
        Gets or sets the current object ID in the workbook.

        Returns:
            int: The current object ID.
        """
        GetDllLibXls().XlsWorkbook_get_CurrentObjectId.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_CurrentObjectId.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_CurrentObjectId, self.Ptr)
        return ret

    @CurrentObjectId.setter
    def CurrentObjectId(self, value:int):
        GetDllLibXls().XlsWorkbook_set_CurrentObjectId.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_CurrentObjectId, self.Ptr, value)

    @property
    def CurrentShapeId(self)->int:
        """
        Gets or sets the current shape ID in the workbook.

        Returns:
            int: The current shape ID.
        """
        GetDllLibXls().XlsWorkbook_get_CurrentShapeId.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_CurrentShapeId.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_CurrentShapeId, self.Ptr)
        return ret

    @CurrentShapeId.setter
    def CurrentShapeId(self, value:int):
        GetDllLibXls().XlsWorkbook_set_CurrentShapeId.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_CurrentShapeId, self.Ptr, value)

    @property
    def CurrentHeaderId(self)->int:
        """
        Gets or sets the current header ID in the workbook.

        Returns:
            int: The current header ID.
        """
        GetDllLibXls().XlsWorkbook_get_CurrentHeaderId.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_CurrentHeaderId.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_CurrentHeaderId, self.Ptr)
        return ret

    @CurrentHeaderId.setter
    def CurrentHeaderId(self, value:int):
        GetDllLibXls().XlsWorkbook_set_CurrentHeaderId.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_CurrentHeaderId, self.Ptr, value)

    @property
    def DefaultXFIndex(self)->int:
        """
        Gets or sets the default XF (extended format) index in the workbook.

        Returns:
            int: The default XF index.
        """
        GetDllLibXls().XlsWorkbook_get_DefaultXFIndex.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_DefaultXFIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_DefaultXFIndex, self.Ptr)
        return ret

    @DefaultXFIndex.setter
    def DefaultXFIndex(self, value:int):
        GetDllLibXls().XlsWorkbook_set_DefaultXFIndex.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_DefaultXFIndex, self.Ptr, value)

    @property
    def DetectDateTimeInValue(self)->bool:
        """
        Gets or sets whether to automatically detect date/time values in cell values.

        Returns:
            bool: True if date/time detection is enabled, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_DetectDateTimeInValue.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_DetectDateTimeInValue.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_DetectDateTimeInValue, self.Ptr)
        return ret

    @DetectDateTimeInValue.setter
    def DetectDateTimeInValue(self, value:bool):
        GetDllLibXls().XlsWorkbook_set_DetectDateTimeInValue.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_DetectDateTimeInValue, self.Ptr, value)

    @property
    def DisplayedTab(self)->int:
        """
        Gets or sets the index of the currently displayed tab.

        Returns:
            int: The index of the displayed tab.
        """
        GetDllLibXls().XlsWorkbook_get_DisplayedTab.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_DisplayedTab.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_DisplayedTab, self.Ptr)
        return ret

    @DisplayedTab.setter
    def DisplayedTab(self, value:int):
        GetDllLibXls().XlsWorkbook_set_DisplayedTab.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_DisplayedTab, self.Ptr, value)

    @property
    def DisplayWorkbookTabs(self)->bool:
        """
        Gets or sets whether to display workbook tabs.

        Returns:
            bool: True if workbook tabs are displayed, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_DisplayWorkbookTabs.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_DisplayWorkbookTabs.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_DisplayWorkbookTabs, self.Ptr)
        return ret

    @DisplayWorkbookTabs.setter
    def DisplayWorkbookTabs(self, value:bool):
        GetDllLibXls().XlsWorkbook_set_DisplayWorkbookTabs.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_DisplayWorkbookTabs, self.Ptr, value)

    @property
    def IsCellProtection(self)->bool:
        """
        Gets whether cell protection is enabled in the workbook.

        Returns:
            bool: True if cell protection is enabled, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_IsCellProtection.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_IsCellProtection.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_IsCellProtection, self.Ptr)
        return ret

    @property
    def IsDisplayPrecision(self)->bool:
        """
        Gets or sets whether to display values with full precision.

        Returns:
            bool: True if full precision display is enabled, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_IsDisplayPrecision.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_IsDisplayPrecision.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_IsDisplayPrecision, self.Ptr)
        return ret

    @IsDisplayPrecision.setter
    def IsDisplayPrecision(self, value:bool):
        GetDllLibXls().XlsWorkbook_set_IsDisplayPrecision.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_IsDisplayPrecision, self.Ptr, value)

    @property
    def IsHScrollBarVisible(self)->bool:
        """
        Gets or sets whether the horizontal scroll bar is visible.

        Returns:
            bool: True if the horizontal scroll bar is visible, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_IsHScrollBarVisible.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_IsHScrollBarVisible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_IsHScrollBarVisible, self.Ptr)
        return ret

    @IsHScrollBarVisible.setter
    def IsHScrollBarVisible(self, value:bool):
        GetDllLibXls().XlsWorkbook_set_IsHScrollBarVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_IsHScrollBarVisible, self.Ptr, value)

    @property
    def IsLoaded(self)->bool:
        """
        Gets whether the workbook is currently loaded.

        Returns:
            bool: True if the workbook is loaded, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_IsLoaded.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_IsLoaded.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_IsLoaded, self.Ptr)
        return ret

    @property
    def IsRightToLeft(self)->bool:
        """
        Gets or sets whether the workbook uses right-to-left text direction.

        Returns:
            bool: True if right-to-left text direction is enabled, otherwise False.
        """
        GetDllLibXls().XlsWorkbook_get_IsRightToLeft.argtypes=[c_void_p]
        GetDllLibXls().XlsWorkbook_get_IsRightToLeft.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_get_IsRightToLeft, self.Ptr)
        return ret

    @IsRightToLeft.setter
    def IsRightToLeft(self, value:bool):
        GetDllLibXls().XlsWorkbook_set_IsRightToLeft.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorkbook_set_IsRightToLeft, self.Ptr, value)

    @staticmethod

    def DEF_COMENT_PARSE_COLOR()->'Color':
        """
        Gets the default color used for parsing comments.

        Returns:
            Color: The default comment parse color.
        """
        #GetDllLibXls().XlsWorkbook_DEF_COMENT_PARSE_COLOR.argtypes=[]
        GetDllLibXls().XlsWorkbook_DEF_COMENT_PARSE_COLOR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorkbook_DEF_COMENT_PARSE_COLOR)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @staticmethod
    def DEF_FIRST_USER_COLOR()->int:
        """
        Gets the index of the first user-modifiable color in the palette.

        Returns:
            int: Index of the first user color (8 in default Excel palette).
        """
        #GetDllLibXls().XlsWorkbook_DEF_FIRST_USER_COLOR.argtypes=[]
        GetDllLibXls().XlsWorkbook_DEF_FIRST_USER_COLOR.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorkbook_DEF_FIRST_USER_COLOR)
        return ret

    @staticmethod

    def DEF_BAD_SHEET_NAME()->str:
        """
        Gets the placeholder name used for invalid sheet names.

        Returns:
            str: Default bad sheet name placeholder.
        """
        #GetDllLibXls().XlsWorkbook_DEF_BAD_SHEET_NAME.argtypes=[]
        GetDllLibXls().XlsWorkbook_DEF_BAD_SHEET_NAME.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorkbook_DEF_BAD_SHEET_NAME))
        return ret



