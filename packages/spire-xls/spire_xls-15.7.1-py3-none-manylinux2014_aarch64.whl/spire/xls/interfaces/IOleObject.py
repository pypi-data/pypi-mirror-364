from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IOleObject (SpireObject) :
    """OLE (Object Linking and Embedding) object interface in Excel.
    
    This interface represents an OLE object embedded in an Excel worksheet.
    OLE objects can include charts, images, documents, or other objects from
    external applications embedded within Excel. This interface provides
    properties and methods to manipulate these embedded objects.
    
    Inherits from:
        SpireObject: Base class for Spire objects
    """

    @property
    def OriginName(self)->str:
        """Gets the original name of the OLE object.
        
        This property returns the original name or source of the OLE object,
        which typically indicates the application or file from which the object originated.
        
        Returns:
            str: The original name of the OLE object.
        """
        GetDllLibXls().IOleObject_get_OleOriginName.argtypes=[c_void_p]
        GetDllLibXls().IOleObject_get_OleOriginName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().IOleObject_get_OleOriginName, self.Ptr))
        return ret
    @property

    def Location(self)->'IXLSRange':
        """Gets the location of the OLE object in the worksheet.
        
        This property returns the range where the OLE object is positioned within the worksheet.
        The location can be used to determine the position of the object or to move it to a different position.
        
        Returns:
            IXLSRange: The range representing the location of the OLE object.
        """
        GetDllLibXls().IOleObject_get_Location.argtypes=[c_void_p]
        GetDllLibXls().IOleObject_get_Location.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IOleObject_get_Location, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @Location.setter
    def Location(self, value:'IXLSRange'):
        """Sets the location of the OLE object in the worksheet.
        
        This property sets the range where the OLE object is positioned within the worksheet.
        
        Args:
            value (IXLSRange): The range representing the new location for the OLE object.
        """
        GetDllLibXls().IOleObject_set_Location.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().IOleObject_set_Location, self.Ptr, value.Ptr)

    @property

    def Size(self)->'Size':
        """Gets the size of the OLE object.
        
        This property returns the dimensions (width and height) of the OLE object.
        
        Returns:
            Size: An object representing the width and height of the OLE object.
        """
        GetDllLibXls().IOleObject_get_Size.argtypes=[c_void_p]
        GetDllLibXls().IOleObject_get_Size.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IOleObject_get_Size, self.Ptr)
        ret = None if intPtr==None else Size(intPtr)
        return ret


    @Size.setter
    def Size(self, value:'Size'):
        """Sets the size of the OLE object.
        
        This property sets the dimensions (width and height) of the OLE object.
        
        Args:
            value (Size): An object representing the new width and height for the OLE object.
        """
        GetDllLibXls().IOleObject_set_Size.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().IOleObject_set_Size, self.Ptr, value.Ptr)

    @property
    def Picture(self)->'Stream':
        """Gets the picture representation of the OLE object.
        
        This property returns a stream containing the image data that represents the OLE object.
        This can be used to access the visual representation of the object.
        
        Returns:
            Stream: A stream containing the picture data of the OLE object.
        """
        GetDllLibXls().IOleObject_get_Picture.argtypes=[c_void_p]
        GetDllLibXls().IOleObject_get_Picture.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IOleObject_get_Picture, self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    @property
    def Shape(self)->'IPictureShape':
        """Gets the picture shape object that defines the appearance and position of the OLE object.
        
        This property returns the shape object associated with the OLE object, which can be used
        to format the appearance, size, and position of the object within the worksheet.
        
        Returns:
            IPictureShape: The picture shape object associated with the OLE object.
        """
        GetDllLibXls().IOleObject_get_Shape.argtypes=[c_void_p]
        GetDllLibXls().IOleObject_get_Shape.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().IOleObject_get_Shape, self.Ptr)
        ret = None if intPtr==None else XlsBitmapShape(intPtr)
        return ret


    @property
    def DisplayAsIcon(self)->bool:
        """Gets whether the OLE object is displayed as an icon.
        
        When true, the OLE object is displayed as an icon rather than showing its actual content.
        This is commonly used to reduce visual complexity or to represent linked objects.
        
        Returns:
            bool: True if the OLE object is displayed as an icon, otherwise False.
        """
        GetDllLibXls().IOleObject_get_DisplayAsIcon.argtypes=[c_void_p]
        GetDllLibXls().IOleObject_get_DisplayAsIcon.restype=c_bool
        ret = CallCFunction(GetDllLibXls().IOleObject_get_DisplayAsIcon, self.Ptr)
        return ret

    @DisplayAsIcon.setter
    def DisplayAsIcon(self, value:bool):
        """Sets whether the OLE object is displayed as an icon.
        
        When set to true, the OLE object will be displayed as an icon rather than showing its actual content.
        
        Args:
            value (bool): True to display the OLE object as an icon, otherwise False.
        """
        GetDllLibXls().IOleObject_set_DisplayAsIcon.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().IOleObject_set_DisplayAsIcon, self.Ptr, value)

    @property

    def ObjectType(self)->'OleObjectType':
        """Gets the type of the OLE object.
        
        This property returns an enumeration value indicating the type of the OLE object,
        such as embedded object, linked object, or other OLE object types.
        
        Returns:
            OleObjectType: An enumeration value representing the type of the OLE object.
        """
        GetDllLibXls().IOleObject_get_ObjectType.argtypes=[c_void_p]
        GetDllLibXls().IOleObject_get_ObjectType.restype=c_int
        ret = CallCFunction(GetDllLibXls().IOleObject_get_ObjectType, self.Ptr)
        objwraped = OleObjectType(ret)
        return objwraped

    @ObjectType.setter
    def ObjectType(self, value:'OleObjectType'):
        """Sets the type of the OLE object.
        
        This property sets the type of the OLE object to the specified enumeration value.
        
        Args:
            value (OleObjectType): An enumeration value representing the type to set for the OLE object.
        """
        GetDllLibXls().IOleObject_set_ObjectType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().IOleObject_set_ObjectType, self.Ptr, value.value)

    @property
    def OleData(self)->List[c_char]:
        """Gets the native data of the OLE object.
        
        This property returns the raw binary data of the OLE object, which contains
        the actual content and structure information of the embedded object.
        
        Returns:
            List[c_char]: A list of bytes representing the native OLE object data.
        """
        GetDllLibXls().IOleObject_get_OleData.argtypes=[c_void_p]
        GetDllLibXls().IOleObject_get_OleData.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().IOleObject_get_OleData, self.Ptr)
        ret = GetVectorFromArray(intPtrArray, c_char)
        return ret


#    @OleData.setter
#    def OleData(self, value:List['Byte']):
#        vCount = len(value)
#        ArrayType = c_void_p * vCount
#        vArray = ArrayType()
#        for i in range(0, vCount):
#            vArray[i] = value[i].Ptr
#        GetDllLibXls().IOleObject_set_OleData.argtypes=[c_void_p, ArrayType, c_int]
#        CallCFunction(GetDllLibXls().IOleObject_set_OleData, self.Ptr, vArray, vCount)


#    @property
#
#    def OleObjectGuid(self)->'Guid':
#        """
#
#        """
#        GetDllLibXls().IOleObject_get_OleObjectGuid.argtypes=[c_void_p]
#        GetDllLibXls().IOleObject_get_OleObjectGuid.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().IOleObject_get_OleObjectGuid, self.Ptr)
#        ret = None if intPtr==None else Guid(intPtr)
#        return ret
#


