from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsDocumentProperty (  IDocumentProperty) :
    """Represents a document property in an Excel workbook.
    
    This class provides properties and methods for accessing and manipulating document
    properties (metadata) in Excel workbooks, such as title, author, creation date, etc.
    It implements the IDocumentProperty interface.
    """
    @property
    def IsBuiltIn(self)->bool:
        """Gets whether the property is a built-in document property.
        
        Returns:
            bool: True if the property is built-in; otherwise, False.
        """
        GetDllLibXls().XlsDocumentProperty_get_IsBuiltIn.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_get_IsBuiltIn.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsDocumentProperty_get_IsBuiltIn, self.Ptr)
        return ret

    @property

    def PropertyId(self)->'BuiltInPropertyType':
        """Gets or sets the ID of the built-in property.
        
        Returns:
            BuiltInPropertyType: An enumeration value representing the built-in property type.
        """
        GetDllLibXls().XlsDocumentProperty_get_PropertyId.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_get_PropertyId.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsDocumentProperty_get_PropertyId, self.Ptr)
        objwraped = BuiltInPropertyType(ret)
        return objwraped

    @PropertyId.setter
    def PropertyId(self, value:'BuiltInPropertyType'):
        """Sets the ID of the built-in property.
        
        Args:
            value (BuiltInPropertyType): An enumeration value representing the built-in property type.
        """
        GetDllLibXls().XlsDocumentProperty_set_PropertyId.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsDocumentProperty_set_PropertyId, self.Ptr, value.value)

    @property

    def Name(self)->str:
        """Gets the name of the document property.
        
        Returns:
            str: The name of the document property.
        """
        GetDllLibXls().XlsDocumentProperty_get_Name.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsDocumentProperty_get_Name, self.Ptr))
        return ret


    @property

    def Value(self)->'SpireObject':
        """Gets or sets the value of the document property as a generic object.
        
        Returns:
            SpireObject: The value of the document property.
        """
        GetDllLibXls().XlsDocumentProperty_get_Value.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_get_Value.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsDocumentProperty_get_Value, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @Value.setter
    def Value(self, value:'SpireObject'):
        """Sets the value of the document property as a generic object.
        
        Args:
            value (SpireObject): The value to set for the document property.
        """
        GetDllLibXls().XlsDocumentProperty_set_Value.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsDocumentProperty_set_Value, self.Ptr, value.Ptr)

    @property
    def Boolean(self)->bool:
        """Gets or sets the value of the document property as a boolean.
        
        Returns:
            bool: The boolean value of the document property.
        """
        GetDllLibXls().XlsDocumentProperty_get_Boolean.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_get_Boolean.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsDocumentProperty_get_Boolean, self.Ptr)
        return ret

    @Boolean.setter
    def Boolean(self, value:bool):
        """Sets the value of the document property as a boolean.
        
        Args:
            value (bool): The boolean value to set for the document property.
        """
        GetDllLibXls().XlsDocumentProperty_set_Boolean.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsDocumentProperty_set_Boolean, self.Ptr, value)

    @property
    def Integer(self)->int:
        """Gets or sets the value of the document property as an integer.
        
        Returns:
            int: The integer value of the document property.
        """
        GetDllLibXls().XlsDocumentProperty_get_Integer.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_get_Integer.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsDocumentProperty_get_Integer, self.Ptr)
        return ret

    @Integer.setter
    def Integer(self, value:int):
        """Sets the value of the document property as an integer.
        
        Args:
            value (int): The integer value to set for the document property.
        """
        GetDllLibXls().XlsDocumentProperty_set_Integer.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsDocumentProperty_set_Integer, self.Ptr, value)

    @property
    def Int32(self)->int:
        """Gets or sets the value of the document property as a 32-bit integer.
        
        Returns:
            int: The 32-bit integer value of the document property.
        """
        GetDllLibXls().XlsDocumentProperty_get_Int32.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_get_Int32.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsDocumentProperty_get_Int32, self.Ptr)
        return ret

    @Int32.setter
    def Int32(self, value:int):
        """Sets the value of the document property as a 32-bit integer.
        
        Args:
            value (int): The 32-bit integer value to set for the document property.
        """
        GetDllLibXls().XlsDocumentProperty_set_Int32.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsDocumentProperty_set_Int32, self.Ptr, value)

    @property
    def Double(self)->float:
        """Gets or sets the value of the document property as a double-precision floating-point number.
        
        Returns:
            float: The double-precision floating-point value of the document property.
        """
        GetDllLibXls().XlsDocumentProperty_get_Double.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_get_Double.restype=c_double
        ret = CallCFunction(GetDllLibXls().XlsDocumentProperty_get_Double, self.Ptr)
        return ret

    @Double.setter
    def Double(self, value:float):
        """Sets the value of the document property as a double-precision floating-point number.
        
        Args:
            value (float): The double-precision floating-point value to set for the document property.
        """
        GetDllLibXls().XlsDocumentProperty_set_Double.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibXls().XlsDocumentProperty_set_Double, self.Ptr, value)

    @property

    def Text(self)->str:
        """Gets or sets the value of the document property as text.
        
        Returns:
            str: The text value of the document property.
        """
        GetDllLibXls().XlsDocumentProperty_get_Text.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsDocumentProperty_get_Text, self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        """Sets the value of the document property as text.
        
        Args:
            value (str): The text value to set for the document property.
        """
        GetDllLibXls().XlsDocumentProperty_set_Text.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsDocumentProperty_set_Text, self.Ptr, value)

    @property

    def DateTime(self)->'DateTime':
        """Gets or sets the value of the document property as a date and time.
        
        Returns:
            DateTime: The date and time value of the document property.
        """
        GetDllLibXls().XlsDocumentProperty_get_DateTime.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_get_DateTime.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsDocumentProperty_get_DateTime, self.Ptr)
        ret = None if intPtr==None else DateTime(intPtr)
        return ret


    @DateTime.setter
    def DateTime(self, value:'DateTime'):
        """Sets the value of the document property as a date and time.
        
        Args:
            value (DateTime): The date and time value to set for the document property.
        """
        GetDllLibXls().XlsDocumentProperty_set_DateTime.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsDocumentProperty_set_DateTime, self.Ptr, value.Ptr)

    @property

    def TimeSpan(self)->'TimeSpan':
        """Gets or sets the value of the document property as a time span.
        
        Returns:
            TimeSpan: The time span value of the document property.
        """
        GetDllLibXls().XlsDocumentProperty_get_TimeSpan.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_get_TimeSpan.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsDocumentProperty_get_TimeSpan, self.Ptr)
        ret = None if intPtr==None else TimeSpan(intPtr)
        return ret


    @TimeSpan.setter
    def TimeSpan(self, value:'TimeSpan'):
        """Sets the value of the document property as a time span.
        
        Args:
            value (TimeSpan): The time span value to set for the document property.
        """
        GetDllLibXls().XlsDocumentProperty_set_TimeSpan.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsDocumentProperty_set_TimeSpan, self.Ptr, value.Ptr)

    #@property

    #def Blob(self)->List['Byte']:
    #    """

    #    """
    #    GetDllLibXls().XlsDocumentProperty_get_Blob.argtypes=[c_void_p]
    #    GetDllLibXls().XlsDocumentProperty_get_Blob.restype=IntPtrArray
    #    intPtrArray = CallCFunction(GetDllLibXls().XlsDocumentProperty_get_Blob, self.Ptr)
    #    ret = GetVectorFromArray(intPtrArray, Byte)
    #    return ret


#    @Blob.setter
#    def Blob(self, value:List['Byte']):
#        vCount = len(value)
#        ArrayType = c_void_p * vCount
#        vArray = ArrayType()
#        for i in range(0, vCount):
#            vArray[i] = value[i].Ptr
#        GetDllLibXls().XlsDocumentProperty_set_Blob.argtypes=[c_void_p, ArrayType, c_int]
#        CallCFunction(GetDllLibXls().XlsDocumentProperty_set_Blob, self.Ptr, vArray, vCount)


    @property

    def StringArray(self)->List[str]:
        """Gets or sets the value of the document property as an array of strings.
        
        Returns:
            List[str]: The string array value of the document property.
        """
        GetDllLibXls().XlsDocumentProperty_get_StringArray.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_get_StringArray.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().XlsDocumentProperty_get_StringArray, self.Ptr)
        ret = GetVectorFromArray(intPtrArray, c_wchar_p)
        return ret

    @StringArray.setter
    def StringArray(self, value:List[str]):
        """Sets the value of the document property as an array of strings.
        
        Args:
            value (List[str]): The string array value to set for the document property.
        """
        vCount = len(value)
        ArrayType = c_wchar_p * vCount
        vArray = ArrayType()
        for i in range(0, vCount):
            vArray[i] = value[i]
        GetDllLibXls().XlsDocumentProperty_set_StringArray.argtypes=[c_void_p, ArrayType, c_int]
        CallCFunction(GetDllLibXls().XlsDocumentProperty_set_StringArray, self.Ptr, vArray, vCount)

    @property

    def ObjectArray(self)->List['SpireObject']:
        """Gets or sets the value of the document property as an array of objects.
        
        Returns:
            List[SpireObject]: The object array value of the document property.
        """
        GetDllLibXls().XlsDocumentProperty_get_ObjectArray.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_get_ObjectArray.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibXls().XlsDocumentProperty_get_ObjectArray, self.Ptr)
        ret = GetVectorFromArray(intPtrArray, SpireObject)
        return ret

    @ObjectArray.setter
    def ObjectArray(self, value:List['SpireObject']):
        """Sets the value of the document property as an array of objects.
        
        Args:
            value (List[SpireObject]): The object array value to set for the document property.
        """
        vCount = len(value)
        ArrayType = c_void_p * vCount
        vArray = ArrayType()
        for i in range(0, vCount):
            vArray[i] = value[i].Ptr
        GetDllLibXls().XlsDocumentProperty_set_ObjectArray.argtypes=[c_void_p, ArrayType, c_int]
        CallCFunction(GetDllLibXls().XlsDocumentProperty_set_ObjectArray, self.Ptr, vArray, vCount)

    @property

    def PropertyType(self)->'PropertyType':
        """Gets or sets the type of the document property.
        
        Returns:
            PropertyType: An enumeration value representing the property type.
        """
        GetDllLibXls().XlsDocumentProperty_get_PropertyType.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_get_PropertyType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsDocumentProperty_get_PropertyType, self.Ptr)
        objwraped = PropertyType(ret)
        return objwraped

    @PropertyType.setter
    def PropertyType(self, value:'PropertyType'):
        """Sets the type of the document property.
        
        Args:
            value (PropertyType): An enumeration value representing the property type.
        """
        GetDllLibXls().XlsDocumentProperty_set_PropertyType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsDocumentProperty_set_PropertyType, self.Ptr, value.value)

    @property

    def LinkSource(self)->str:
        """Gets or sets the source of the linked document property.
        
        Returns:
            str: The source of the linked document property.
        """
        GetDllLibXls().XlsDocumentProperty_get_LinkSource.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_get_LinkSource.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsDocumentProperty_get_LinkSource, self.Ptr))
        return ret


    @LinkSource.setter
    def LinkSource(self, value:str):
        """Sets the source of the linked document property.
        
        Args:
            value (str): The source of the linked document property.
        """
        GetDllLibXls().XlsDocumentProperty_set_LinkSource.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsDocumentProperty_set_LinkSource, self.Ptr, value)

    @property
    def LinkToContent(self)->bool:
        """Gets or sets whether the document property is linked to content.
        
        Returns:
            bool: True if the property is linked to content; otherwise, False.
        """
        GetDllLibXls().XlsDocumentProperty_get_LinkToContent.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_get_LinkToContent.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsDocumentProperty_get_LinkToContent, self.Ptr)
        return ret

    @LinkToContent.setter
    def LinkToContent(self, value:bool):
        """Sets whether the document property is linked to content.
        
        Args:
            value (bool): True to link the property to content; otherwise, False.
        """
        GetDllLibXls().XlsDocumentProperty_set_LinkToContent.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsDocumentProperty_set_LinkToContent, self.Ptr, value)

    @property

    def InternalName(self)->str:
        """Gets the internal name of the document property.
        
        Returns:
            str: The internal name of the document property.
        """
        GetDllLibXls().XlsDocumentProperty_get_InternalName.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_get_InternalName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsDocumentProperty_get_InternalName, self.Ptr))
        return ret



    def FillPropVariant(self ,variant:'IPropertyData',iPropertyId:int)->bool:
        """Fills a property variant with the document property data.
        
        Args:
            variant (IPropertyData): The property data object to fill.
            iPropertyId (int): The ID of the property.
            
        Returns:
            bool: True if the operation was successful; otherwise, False.
        """
        intPtrvariant:c_void_p = variant.Ptr

        GetDllLibXls().XlsDocumentProperty_FillPropVariant.argtypes=[c_void_p ,c_void_p,c_int]
        GetDllLibXls().XlsDocumentProperty_FillPropVariant.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsDocumentProperty_FillPropVariant, self.Ptr, intPtrvariant,iPropertyId)
        return ret

#    @staticmethod
#
#    def CorrectIndex(propertyId:'BuiltInPropertyType',bSummary:'Boolean&')->int:
#        """
#
#        """
#        enumpropertyId:c_int = propertyId.value
#        intPtrbSummary:c_void_p = bSummary.Ptr
#
#        GetDllLibXls().XlsDocumentProperty_CorrectIndex.argtypes=[ c_int,c_void_p]
#        GetDllLibXls().XlsDocumentProperty_CorrectIndex.restype=c_int
#        ret = CallCFunction(GetDllLibXls().XlsDocumentProperty_CorrectIndex,  enumpropertyId,intPtrbSummary)
#        return ret



    def SetLinkSource(self ,variant:'IPropertyData'):
        """Sets the link source for the document property using property data.
        
        Args:
            variant (IPropertyData): The property data containing the link source.
        """
        intPtrvariant:c_void_p = variant.Ptr

        GetDllLibXls().XlsDocumentProperty_SetLinkSource.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsDocumentProperty_SetLinkSource, self.Ptr, intPtrvariant)


    def Clone(self)->'SpireObject':
        """Creates a clone of this document property.
        
        Returns:
            SpireObject: A new instance of the document property with the same values.
        """
        GetDllLibXls().XlsDocumentProperty_Clone.argtypes=[c_void_p]
        GetDllLibXls().XlsDocumentProperty_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsDocumentProperty_Clone, self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @staticmethod
    def DEF_FILE_TIME_START_YEAR()->int:
        """Gets the default file time start year constant.
        
        Returns:
            int: The default file time start year (typically 1601).
        """
        #GetDllLibXls().XlsDocumentProperty_DEF_FILE_TIME_START_YEAR.argtypes=[]
        GetDllLibXls().XlsDocumentProperty_DEF_FILE_TIME_START_YEAR.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsDocumentProperty_DEF_FILE_TIME_START_YEAR)
        return ret

