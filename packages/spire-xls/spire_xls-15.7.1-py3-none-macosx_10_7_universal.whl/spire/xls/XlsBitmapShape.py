from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsBitmapShape (  XlsShape, IPictureShape) :
    """Represents a bitmap/picture shape in an Excel worksheet.
    
    This class provides properties and methods for manipulating picture shapes in Excel,
    including image manipulation, cropping, and formatting. It extends XlsShape and
    implements the IPictureShape interface.
    """

    @dispatch
    def Remove(self ,removeImage:bool):
        """Removes the bitmap shape from the worksheet.
        
        Args:
            removeImage (bool): True to remove the underlying image data; False to keep it.
        """
        
        GetDllLibXls().XlsBitmapShape_Remove.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibXls().XlsBitmapShape_Remove, self.Ptr, removeImage)

    @property

    def BlipId(self)->'UInt32':
        """Gets the blip identifier for the bitmap.
        
        Returns:
            UInt32: The blip identifier for the bitmap.
        """
        GetDllLibXls().XlsBitmapShape_get_BlipId.argtypes=[c_void_p]
        GetDllLibXls().XlsBitmapShape_get_BlipId.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsBitmapShape_get_BlipId, self.Ptr)
        ret = None if intPtr==None else UInt32(intPtr)
        return ret


    @property

    def ColorTo(self)->'Color':
        """Gets or sets the ending color for gradient effect.
        
        Returns:
            Color: The ending color for gradient effect.
        """
        GetDllLibXls().XlsBitmapShape_get_ColorTo.argtypes=[c_void_p]
        GetDllLibXls().XlsBitmapShape_get_ColorTo.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsBitmapShape_get_ColorTo, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @ColorTo.setter
    def ColorTo(self, value:'Color'):
        """Sets the ending color for gradient effect.
        
        Args:
            value (Color): The ending color for gradient effect.
        """
        GetDllLibXls().XlsBitmapShape_set_ColorTo.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsBitmapShape_set_ColorTo, self.Ptr, value.Ptr)

    @property

    def RefRange(self)->str:
        """Gets or sets the reference range for the bitmap shape.
        
        Returns:
            str: The reference range for the bitmap shape.
        """
        GetDllLibXls().XlsBitmapShape_get_RefRange.argtypes=[c_void_p]
        GetDllLibXls().XlsBitmapShape_get_RefRange.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsBitmapShape_get_RefRange, self.Ptr))
        return ret


    @RefRange.setter
    def RefRange(self, value:str):
        """Sets the reference range for the bitmap shape.
        
        Args:
            value (str): The reference range for the bitmap shape.
        """
        GetDllLibXls().XlsBitmapShape_set_RefRange.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsBitmapShape_set_RefRange, self.Ptr, value)

    @property
    def IsDDE(self)->bool:
        """Gets or sets whether the bitmap is a DDE (Dynamic Data Exchange) object.
        
        Returns:
            bool: True if the bitmap is a DDE object; otherwise, False.
        """
        GetDllLibXls().XlsBitmapShape_get_IsDDE.argtypes=[c_void_p]
        GetDllLibXls().XlsBitmapShape_get_IsDDE.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsBitmapShape_get_IsDDE, self.Ptr)
        return ret

    @IsDDE.setter
    def IsDDE(self, value:bool):
        """Sets whether the bitmap is a DDE (Dynamic Data Exchange) object.
        
        Args:
            value (bool): True to set as DDE object; otherwise, False.
        """
        GetDllLibXls().XlsBitmapShape_set_IsDDE.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsBitmapShape_set_IsDDE, self.Ptr, value)

    @property
    def IsCamera(self)->bool:
        """Gets or sets whether the bitmap is a camera object.
        
        Returns:
            bool: True if the bitmap is a camera object; otherwise, False.
        """
        GetDllLibXls().XlsBitmapShape_get_IsCamera.argtypes=[c_void_p]
        GetDllLibXls().XlsBitmapShape_get_IsCamera.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsBitmapShape_get_IsCamera, self.Ptr)
        return ret

    @IsCamera.setter
    def IsCamera(self, value:bool):
        """Sets whether the bitmap is a camera object.
        
        Args:
            value (bool): True to set as camera object; otherwise, False.
        """
        GetDllLibXls().XlsBitmapShape_set_IsCamera.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsBitmapShape_set_IsCamera, self.Ptr, value)

    @property

    def ColorFrom(self)->'Color':
        """Gets or sets the starting color for gradient effect.
        
        Returns:
            Color: The starting color for gradient effect.
        """
        GetDllLibXls().XlsBitmapShape_get_ColorFrom.argtypes=[c_void_p]
        GetDllLibXls().XlsBitmapShape_get_ColorFrom.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsBitmapShape_get_ColorFrom, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @ColorFrom.setter
    def ColorFrom(self, value:'Color'):
        """Sets the starting color for gradient effect.
        
        Args:
            value (Color): The starting color for gradient effect.
        """
        GetDllLibXls().XlsBitmapShape_set_ColorFrom.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsBitmapShape_set_ColorFrom, self.Ptr, value.Ptr)

    @property

    def FileName(self)->str:
        """Gets or sets the file name of the bitmap image.
        
        Returns:
            str: The file name of the bitmap image.
        """
        GetDllLibXls().XlsBitmapShape_get_FileName.argtypes=[c_void_p]
        GetDllLibXls().XlsBitmapShape_get_FileName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsBitmapShape_get_FileName, self.Ptr))
        return ret


    @FileName.setter
    def FileName(self, value:str):
        """Sets the file name of the bitmap image.
        
        Args:
            value (str): The file name of the bitmap image.
        """
        GetDllLibXls().XlsBitmapShape_set_FileName.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsBitmapShape_set_FileName, self.Ptr, value)

    @property

    def Picture(self)->'Stream':
        """Gets or sets the picture data as a stream.
        
        Returns:
            Stream: The picture data as a stream.
        """
        GetDllLibXls().XlsBitmapShape_get_Picture.argtypes=[c_void_p]
        GetDllLibXls().XlsBitmapShape_get_Picture.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsBitmapShape_get_Picture, self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    @Picture.setter
    def Picture(self, value:'Stream'):
        """Sets the picture data from a stream.
        
        Args:
            value (Stream): The picture data as a stream.
        """
        GetDllLibXls().XlsBitmapShape_set_Picture.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsBitmapShape_set_Picture, self.Ptr, value.Ptr)


    def Compress(self ,quality:int):
        """Compresses the picture quality to reduce file size.

        Args:
            quality (int): Picture quality, range is 0-100 (higher values mean better quality).
        """
        
        GetDllLibXls().XlsBitmapShape_Compress.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsBitmapShape_Compress, self.Ptr, quality)

    @property
    def CropLeftOffset(self)->int:
        """Gets or sets the left cropping offset in pixels.
        
        Returns:
            int: The left cropping offset in pixels.
        """
        GetDllLibXls().XlsBitmapShape_get_CropLeftOffset.argtypes=[c_void_p]
        GetDllLibXls().XlsBitmapShape_get_CropLeftOffset.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsBitmapShape_get_CropLeftOffset, self.Ptr)
        return ret

    @CropLeftOffset.setter
    def CropLeftOffset(self, value:int):
        """Sets the left cropping offset in pixels.
        
        Args:
            value (int): The left cropping offset in pixels.
        """
        GetDllLibXls().XlsBitmapShape_set_CropLeftOffset.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsBitmapShape_set_CropLeftOffset, self.Ptr, value)

    @property
    def CropRightOffset(self)->int:
        """Gets or sets the right cropping offset in pixels.
        
        Returns:
            int: The right cropping offset in pixels.
        """
        GetDllLibXls().XlsBitmapShape_get_CropRightOffset.argtypes=[c_void_p]
        GetDllLibXls().XlsBitmapShape_get_CropRightOffset.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsBitmapShape_get_CropRightOffset, self.Ptr)
        return ret

    @CropRightOffset.setter
    def CropRightOffset(self, value:int):
        """Sets the right cropping offset in pixels.
        
        Args:
            value (int): The right cropping offset in pixels.
        """
        GetDllLibXls().XlsBitmapShape_set_CropRightOffset.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsBitmapShape_set_CropRightOffset, self.Ptr, value)

    @property
    def CropBottomOffset(self)->int:
        """Gets or sets the bottom cropping offset in pixels.
        
        Returns:
            int: The bottom cropping offset in pixels.
        """
        GetDllLibXls().XlsBitmapShape_get_CropBottomOffset.argtypes=[c_void_p]
        GetDllLibXls().XlsBitmapShape_get_CropBottomOffset.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsBitmapShape_get_CropBottomOffset, self.Ptr)
        return ret

    @CropBottomOffset.setter
    def CropBottomOffset(self, value:int):
        """Sets the bottom cropping offset in pixels.
        
        Args:
            value (int): The bottom cropping offset in pixels.
        """
        GetDllLibXls().XlsBitmapShape_set_CropBottomOffset.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsBitmapShape_set_CropBottomOffset, self.Ptr, value)

    @property
    def CropTopOffset(self)->int:
        """Gets or sets the top cropping offset in pixels.
        
        Returns:
            int: The top cropping offset in pixels.
        """
        GetDllLibXls().XlsBitmapShape_get_CropTopOffset.argtypes=[c_void_p]
        GetDllLibXls().XlsBitmapShape_get_CropTopOffset.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsBitmapShape_get_CropTopOffset, self.Ptr)
        return ret

    @CropTopOffset.setter
    def CropTopOffset(self, value:int):
        """Sets the top cropping offset in pixels.
        
        Args:
            value (int): The top cropping offset in pixels.
        """
        GetDllLibXls().XlsBitmapShape_set_CropTopOffset.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsBitmapShape_set_CropTopOffset, self.Ptr, value)

    @property

    def Macro(self)->str:
        """Gets or sets the macro associated with the bitmap shape.
        
        Returns:
            str: The macro associated with the bitmap shape.
        """
        GetDllLibXls().XlsBitmapShape_get_Macro.argtypes=[c_void_p]
        GetDllLibXls().XlsBitmapShape_get_Macro.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsBitmapShape_get_Macro, self.Ptr))
        return ret


    @Macro.setter
    def Macro(self, value:str):
        """Sets the macro associated with the bitmap shape.
        
        Args:
            value (str): The macro associated with the bitmap shape.
        """
        GetDllLibXls().XlsBitmapShape_set_Macro.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsBitmapShape_set_Macro, self.Ptr, value)

    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets the type of the shape.
        
        Returns:
            ExcelShapeType: An enumeration value representing the type of the shape.
        """
        GetDllLibXls().XlsBitmapShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsBitmapShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsBitmapShape_get_ShapeType, self.Ptr)
        objwraped = ExcelShapeType(ret)
        return objwraped

    def Dispose(self):
        """Releases all resources used by the bitmap shape.
        
        This method performs cleanup operations and releases memory resources used by the bitmap shape.
        """
        GetDllLibXls().XlsBitmapShape_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsBitmapShape_Dispose, self.Ptr)


    def SetHyperLink(self ,linkString:str,isExternal:bool):
        """Sets a hyperlink for the bitmap shape.
        
        Args:
            linkString (str): The URL or file path for the hyperlink.
            isExternal (bool): True if the link is to an external resource; False if it's an internal link.
        """
        
        GetDllLibXls().XlsBitmapShape_SetHyperLink.argtypes=[c_void_p ,c_void_p,c_bool]
        CallCFunction(GetDllLibXls().XlsBitmapShape_SetHyperLink, self.Ptr, linkString,isExternal)

    def GetHyperLink(self)->'HyperLink':
        """Gets the hyperlink associated with the bitmap shape.
        
        Returns:
            HyperLink: An object representing the hyperlink associated with the bitmap shape.
        """
        from spire.xls import HyperLink
        GetDllLibXls().XlsBitmapShape_get_HyperLink.argtypes=[c_void_p]
        GetDllLibXls().XlsBitmapShape_get_HyperLink.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsBitmapShape_get_HyperLink, self.Ptr)
        ret = None if intPtr==None else HyperLink(intPtr)
        return ret
#
#    def Clone(self ,parent:'SpireObject',hashNewNames:'Dictionary2',dicFontIndexes:'Dictionary2',addToCollection:bool)->'IShape':
#        """
#
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrhashNewNames:c_void_p = hashNewNames.Ptr
#        intPtrdicFontIndexes:c_void_p = dicFontIndexes.Ptr
#
#        GetDllLibXls().XlsBitmapShape_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsBitmapShape_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsBitmapShape_Clone, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollection)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


