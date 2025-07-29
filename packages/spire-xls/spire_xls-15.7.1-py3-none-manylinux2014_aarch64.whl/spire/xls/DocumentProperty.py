from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class DocumentProperty (  SpireObject, IDocumentProperty) :
    """Represents a document property in an Excel workbook.
    
    This class provides functionality to work with built-in and custom document properties
    such as author, title, subject, keywords, etc. It implements the IDocumentProperty
    interface and allows reading and modifying these properties in various data types.
    """
    @property
    def IsBuiltIn(self)->bool:
        """Gets whether this property is a built-in document property.
        
        Returns:
            bool: True if this is a built-in property; otherwise, False.
        """
        GetDllLibXls().DocumentProperty_get_IsBuiltIn.argtypes=[c_void_p]
        GetDllLibXls().DocumentProperty_get_IsBuiltIn.restype=c_bool
        ret = CallCFunction(GetDllLibXls().DocumentProperty_get_IsBuiltIn, self.Ptr)
        return ret

    @property

    def PropertyId(self)->'BuiltInPropertyType':
        """Gets the identifier of the built-in property.
        
        Returns:
            BuiltInPropertyType: An enumeration value identifying the built-in property type.
        """
        GetDllLibXls().DocumentProperty_get_PropertyId.argtypes=[c_void_p]
        GetDllLibXls().DocumentProperty_get_PropertyId.restype=c_int
        ret = CallCFunction(GetDllLibXls().DocumentProperty_get_PropertyId, self.Ptr)
        objwraped = BuiltInPropertyType(ret)
        return objwraped

    @property

    def PropertyType(self)->'PropertyType':
        """Gets the data type of the property.
        
        Returns:
            PropertyType: An enumeration value representing the data type of the property.
        """
        GetDllLibXls().DocumentProperty_get_PropertyType.argtypes=[c_void_p]
        GetDllLibXls().DocumentProperty_get_PropertyType.restype=c_int
        ret = CallCFunction(GetDllLibXls().DocumentProperty_get_PropertyType, self.Ptr)
        objwraped = PropertyType(ret)
        return objwraped

    @property

    def InternalName(self)->str:
        """Gets the internal name of the property.
        
        Returns:
            str: The internal name of the property as used in the document.
        """
        GetDllLibXls().DocumentProperty_get_InternalName.argtypes=[c_void_p]
        GetDllLibXls().DocumentProperty_get_InternalName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().DocumentProperty_get_InternalName, self.Ptr))
        return ret


    @property

    def Name(self)->str:
        """Gets the display name of the property.
        
        Returns:
            str: The display name of the property.
        """
        GetDllLibXls().DocumentProperty_get_Name.argtypes=[c_void_p]
        GetDllLibXls().DocumentProperty_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().DocumentProperty_get_Name, self.Ptr))
        return ret


    @property

    def Value(self)->'SpireObject':
        """Gets or sets the value of the property as a generic object.
        
        Returns:
            SpireObject: The value of the property as a generic object.
        """
        GetDllLibXls().DocumentProperty_get_Value.argtypes=[c_void_p]
        GetDllLibXls().DocumentProperty_get_Value.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().DocumentProperty_get_Value, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @Value.setter
    def Value(self, value:'SpireObject'):
        GetDllLibXls().DocumentProperty_set_Value.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().DocumentProperty_set_Value, self.Ptr, value.Ptr)

#    @property
#
#    def Blob(self)->List['Byte']:
#        """
#
#        """
#        GetDllLibXls().DocumentProperty_get_Blob.argtypes=[c_void_p]
#        GetDllLibXls().DocumentProperty_get_Blob.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibXls().DocumentProperty_get_Blob, self.Ptr)
#        ret = GetVectorFromArray(intPtrArray, Byte)
#        return ret


#    @Blob.setter
#    def Blob(self, value:List['Byte']):
#        vCount = len(value)
#        ArrayType = c_void_p * vCount
#        vArray = ArrayType()
#        for i in range(0, vCount):
#            vArray[i] = value[i].Ptr
#        GetDllLibXls().DocumentProperty_set_Blob.argtypes=[c_void_p, ArrayType, c_int]
#        CallCFunction(GetDllLibXls().DocumentProperty_set_Blob, self.Ptr, vArray, vCount)


    @property
    def Boolean(self)->bool:
        """Gets or sets the value of the property as a boolean.
        
        Returns:
            bool: The boolean value of the property.
        """
        GetDllLibXls().DocumentProperty_get_Boolean.argtypes=[c_void_p]
        GetDllLibXls().DocumentProperty_get_Boolean.restype=c_bool
        ret = CallCFunction(GetDllLibXls().DocumentProperty_get_Boolean, self.Ptr)
        return ret

    @Boolean.setter
    def Boolean(self, value:bool):
        GetDllLibXls().DocumentProperty_set_Boolean.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().DocumentProperty_set_Boolean, self.Ptr, value)

    @property
    def Integer(self)->int:
        """Gets or sets the value of the property as an integer.
        
        Returns:
            int: The integer value of the property.
        """
        GetDllLibXls().DocumentProperty_get_Integer.argtypes=[c_void_p]
        GetDllLibXls().DocumentProperty_get_Integer.restype=c_int
        ret = CallCFunction(GetDllLibXls().DocumentProperty_get_Integer, self.Ptr)
        return ret

    @Integer.setter
    def Integer(self, value:int):
        GetDllLibXls().DocumentProperty_set_Integer.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().DocumentProperty_set_Integer, self.Ptr, value)

    @property
    def Int32(self)->int:
        """Gets or sets the value of the property as a 32-bit integer.
        
        Returns:
            int: The 32-bit integer value of the property.
        """
        GetDllLibXls().DocumentProperty_get_Int32.argtypes=[c_void_p]
        GetDllLibXls().DocumentProperty_get_Int32.restype=c_int
        ret = CallCFunction(GetDllLibXls().DocumentProperty_get_Int32, self.Ptr)
        return ret

    @Int32.setter
    def Int32(self, value:int):
        GetDllLibXls().DocumentProperty_set_Int32.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().DocumentProperty_set_Int32, self.Ptr, value)

    @property
    def Double(self)->float:
        """Gets or sets the value of the property as a double-precision floating-point number.
        
        Returns:
            float: The double-precision floating-point value of the property.
        """
        GetDllLibXls().DocumentProperty_get_Double.argtypes=[c_void_p]
        GetDllLibXls().DocumentProperty_get_Double.restype=c_double
        ret = CallCFunction(GetDllLibXls().DocumentProperty_get_Double, self.Ptr)
        return ret

    @Double.setter
    def Double(self, value:float):
        GetDllLibXls().DocumentProperty_set_Double.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().DocumentProperty_set_Double, self.Ptr, value)

    @property

    def Text(self)->str:
        """Gets or sets the value of the property as a text string.
        
        Returns:
            str: The text string value of the property.
        """
        GetDllLibXls().DocumentProperty_get_Text.argtypes=[c_void_p]
        GetDllLibXls().DocumentProperty_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().DocumentProperty_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        GetDllLibXls().DocumentProperty_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().DocumentProperty_set_Text, self.Ptr, value)

    @property

    def DateTime(self)->'DateTime':
        """Gets or sets the value of the property as a DateTime object.
        
        Returns:
            DateTime: The DateTime value of the property.
        """
        GetDllLibXls().DocumentProperty_get_DateTime.argtypes=[c_void_p]
        GetDllLibXls().DocumentProperty_get_DateTime.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().DocumentProperty_get_DateTime, self.Ptr)
        ret = None if intPtr==None else DateTime(intPtr)
        return ret


    @DateTime.setter
    def DateTime(self, value:'DateTime'):
        GetDllLibXls().DocumentProperty_set_DateTime.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().DocumentProperty_set_DateTime, self.Ptr, value.Ptr)

    @property

    def TimeSpan(self)->'TimeSpan':
        """Gets or sets the value of the property as a TimeSpan object.
        
        A TimeSpan represents a time interval (duration of time or elapsed time).
        
        Returns:
            TimeSpan: The TimeSpan value of the property.
        """
        GetDllLibXls().DocumentProperty_get_TimeSpan.argtypes=[c_void_p]
        GetDllLibXls().DocumentProperty_get_TimeSpan.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().DocumentProperty_get_TimeSpan, self.Ptr)
        ret = None if intPtr==None else TimeSpan(intPtr)
        return ret


    @TimeSpan.setter
    def TimeSpan(self, value:'TimeSpan'):
        GetDllLibXls().DocumentProperty_set_TimeSpan.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().DocumentProperty_set_TimeSpan, self.Ptr, value.Ptr)

    @property

    def LinkSource(self)->str:
        """Gets or sets the source of the linked property.
        
        For a linked property, this is the source from which the property value is obtained.
        
        Returns:
            str: The source of the linked property.
        """
        GetDllLibXls().DocumentProperty_get_LinkSource.argtypes=[c_void_p]
        GetDllLibXls().DocumentProperty_get_LinkSource.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().DocumentProperty_get_LinkSource, self.Ptr))
        return ret


    @LinkSource.setter
    def LinkSource(self, value:str):
        GetDllLibXls().DocumentProperty_set_LinkSource.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().DocumentProperty_set_LinkSource, self.Ptr, value)

    @property
    def LinkToContent(self)->bool:
        """Gets or sets whether the property is linked to content in the document.
        
        When a property is linked to content, its value is updated automatically
        when the linked content changes.
        
        Returns:
            bool: True if the property is linked to content; otherwise, False.
        """
        GetDllLibXls().DocumentProperty_get_LinkToContent.argtypes=[c_void_p]
        GetDllLibXls().DocumentProperty_get_LinkToContent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().DocumentProperty_get_LinkToContent, self.Ptr)
        return ret

    @LinkToContent.setter
    def LinkToContent(self, value:bool):
        GetDllLibXls().DocumentProperty_set_LinkToContent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().DocumentProperty_set_LinkToContent, self.Ptr, value)


    def Clone(self)->'SpireObject':
        """Creates a copy of the current document property.
        
        Returns:
            SpireObject: A new object that is a copy of this document property.
        """
        GetDllLibXls().DocumentProperty_Clone.argtypes=[c_void_p]
        GetDllLibXls().DocumentProperty_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().DocumentProperty_Clone, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def SetLinkSource(self ,variant:'IPropertyData'):
        """Sets the source of the linked property using property data.
        
        Args:
            variant (IPropertyData): The property data to use as the link source.
        """
        intPtrvariant:c_void_p = variant.Ptr

        GetDllLibXls().DocumentProperty_SetLinkSource.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().DocumentProperty_SetLinkSource, self.Ptr, intPtrvariant)

#    @staticmethod
#
#    def CorrectIndex(propertyId:'BuiltInPropertyType',bSummary:'Boolean&')->int:
#        """
#
#        """
#        enumpropertyId:c_int = propertyId.value
#        intPtrbSummary:c_void_p = bSummary.Ptr
#
#        GetDllLibXls().DocumentProperty_CorrectIndex.argtypes=[ c_int,c_void_p]
#        GetDllLibXls().DocumentProperty_CorrectIndex.restype=c_int
#        ret = CallCFunction(GetDllLibXls().DocumentProperty_CorrectIndex,  enumpropertyId,intPtrbSummary)
#        return ret


    @staticmethod
    def DEF_FILE_TIME_START_YEAR()->int:
        """Gets the default file time start year used for date calculations.
        
        This is typically 1899 or 1904, depending on the workbook settings.
        
        Returns:
            int: The default file time start year.
        """
        #GetDllLibXls().DocumentProperty_DEF_FILE_TIME_START_YEAR.argtypes=[]
        GetDllLibXls().DocumentProperty_DEF_FILE_TIME_START_YEAR.restype=c_int
        ret = CallCFunction(GetDllLibXls().DocumentProperty_DEF_FILE_TIME_START_YEAR)
        return ret

