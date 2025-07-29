from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsListBoxShape (  XlsShape, IListBox) :
    """Represents a list box shape in an Excel worksheet.
    
    This class provides properties and methods for manipulating list box shapes in Excel,
    including display settings, cell linking, selection types, and other list box-specific
    functionality. It extends XlsShape and implements the IListBox interface.
    """
    @property
    def Display3DShading(self)->bool:
        """Gets or sets whether 3D shading is displayed for the list box.
        
        Returns:
            bool: True if 3D shading is displayed, False otherwise.
        """
        GetDllLibXls().XlsListBoxShape_get_Display3DShading.argtypes=[c_void_p]
        GetDllLibXls().XlsListBoxShape_get_Display3DShading.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsListBoxShape_get_Display3DShading, self.Ptr)
        return ret

    @Display3DShading.setter
    def Display3DShading(self, value:bool):
        """Sets whether 3D shading is displayed for the list box.
        
        Args:
            value (bool): True to display 3D shading, False otherwise.
        """
        GetDllLibXls().XlsListBoxShape_set_Display3DShading.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsListBoxShape_set_Display3DShading, self.Ptr, value)

    @property

    def LinkedCell(self)->'IXLSRange':
        """Gets or sets the cell linked to the list box selection.
        
        Returns:
            IXLSRange: The cell range linked to the list box selection.
        """
        GetDllLibXls().XlsListBoxShape_get_LinkedCell.argtypes=[c_void_p]
        GetDllLibXls().XlsListBoxShape_get_LinkedCell.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsListBoxShape_get_LinkedCell, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @LinkedCell.setter
    def LinkedCell(self, value:'IXLSRange'):
        """Sets the cell linked to the list box selection.
        
        Args:
            value (IXLSRange): The cell range to link to the list box selection.
        """
        GetDllLibXls().XlsListBoxShape_set_LinkedCell.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsListBoxShape_set_LinkedCell, self.Ptr, value.Ptr)

    @property

    def ListFillRange(self)->'IXLSRange':
        """Gets or sets the range containing the list box items.
        
        Returns:
            IXLSRange: The cell range containing the list box items.
        """
        GetDllLibXls().XlsListBoxShape_get_ListFillRange.argtypes=[c_void_p]
        GetDllLibXls().XlsListBoxShape_get_ListFillRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsListBoxShape_get_ListFillRange, self.Ptr)
        ret = None if intPtr==None else XlsRange(intPtr)
        return ret


    @ListFillRange.setter
    def ListFillRange(self, value:'IXLSRange'):
        """Sets the range containing the list box items.
        
        Args:
            value (IXLSRange): The cell range containing the list box items.
        """
        GetDllLibXls().XlsListBoxShape_set_ListFillRange.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsListBoxShape_set_ListFillRange, self.Ptr, value.Ptr)

    @property
    def SelectedIndex(self)->int:
        """Gets or sets the index of the selected item in the list box.
        
        Returns:
            int: The zero-based index of the selected item.
        """
        GetDllLibXls().XlsListBoxShape_get_SelectedIndex.argtypes=[c_void_p]
        GetDllLibXls().XlsListBoxShape_get_SelectedIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsListBoxShape_get_SelectedIndex, self.Ptr)
        return ret

    @SelectedIndex.setter
    def SelectedIndex(self, value:int):
        """Sets the index of the selected item in the list box.
        
        Args:
            value (int): The zero-based index of the item to select.
        """
        GetDllLibXls().XlsListBoxShape_set_SelectedIndex.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsListBoxShape_set_SelectedIndex, self.Ptr, value)

    @property

    def SelectionType(self)->'SelectionType':
        """Gets or sets the selection type of the list box.
        
        Returns:
            SelectionType: An enumeration value representing the selection type of the list box.
        """
        GetDllLibXls().XlsListBoxShape_get_SelectionType.argtypes=[c_void_p]
        GetDllLibXls().XlsListBoxShape_get_SelectionType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsListBoxShape_get_SelectionType, self.Ptr)
        objwraped = SelectionType(ret)
        return objwraped

    @SelectionType.setter
    def SelectionType(self, value:'SelectionType'):
        """Sets the selection type of the list box.
        
        Args:
            value (SelectionType): An enumeration value representing the selection type of the list box.
        """
        GetDllLibXls().XlsListBoxShape_set_SelectionType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsListBoxShape_set_SelectionType, self.Ptr, value.value)

    @property

    def ShapeType(self)->'ExcelShapeType':
        """Gets the shape type of the list box.
        
        Returns:
            ExcelShapeType: An enumeration value representing the shape type of the list box.
        """
        GetDllLibXls().XlsListBoxShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibXls().XlsListBoxShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsListBoxShape_get_ShapeType, self.Ptr)
        objwraped = ExcelShapeType(ret)
        return objwraped

#
#    def Clone(self ,parent:'SpireObject',hashNewNames:'Dictionary2',dicFontIndexes:'Dictionary2',addToCollections:bool)->'IShape':
#        """
#        Creates a clone of this list box shape.
#
#        Args:
#            parent (SpireObject): The parent object for the cloned shape.
#            hashNewNames (Dictionary2): A dictionary of new names.
#            dicFontIndexes (Dictionary2): A dictionary of font indexes.
#            addToCollections (bool): Whether to add the cloned shape to collections.
#
#        Returns:
#            IShape: A clone of this list box shape.
#        """
#        intPtrparent:c_void_p = parent.Ptr
#        intPtrhashNewNames:c_void_p = hashNewNames.Ptr
#        intPtrdicFontIndexes:c_void_p = dicFontIndexes.Ptr
#
#        GetDllLibXls().XlsListBoxShape_Clone.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_bool]
#        GetDllLibXls().XlsListBoxShape_Clone.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsListBoxShape_Clone, self.Ptr, intPtrparent,intPtrhashNewNames,intPtrdicFontIndexes,addToCollections)
#        ret = None if intPtr==None else IShape(intPtr)
#        return ret
#


