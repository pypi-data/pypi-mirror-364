from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsWorksheetBase (  XlsObject, INamedObject, ITabSheet, ICloneParent) :
    """

    """
    

    def GetShapes(self)->'IShapes':
        """
        Gets collection of all shapes in the worksheet.

        Returns:
            IShapes: Collection of shapes including charts, pictures and other objects
        """
        
        GetDllLibXls().XlsWorksheetBase_get_Shapes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_Shapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_Shapes, self.Ptr)
        ret = None if intPtr==None else IShapes(intPtr)
        return ret

    

    def GetGroupShapeCollection(self)->'GroupShapeCollection':
        """
        Gets collection of grouped shapes in the worksheet.

        Returns:
            GroupShapeCollection: Collection of shape groups
        """
        
        GetDllLibXls().XlsWorksheetBase_get_GroupShapeCollection.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_GroupShapeCollection.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_GroupShapeCollection, self.Ptr)
        ret = None if intPtr==None else GroupShapeCollection(intPtr)
        return ret
    @dispatch

    def MoveSheet(self ,destIndex:int):
        """
        Moves sheet into new position, including chartsheet and worksheet.

        Args:
            destIndex: Zero-based destination index to move sheet to
        """
        
        GetDllLibXls().XlsWorksheetBase_MoveSheet.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_MoveSheet, self.Ptr, destIndex)

    @dispatch

    def Unselect(self ,Check:bool):
        """
        Unselects the worksheet in the workbook UI.

        Args:
            Check: Whether to validate selection state
        """
        
        GetDllLibXls().XlsWorksheetBase_Unselect.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_Unselect, self.Ptr, Check)

    @dispatch

    def Protect(self ,password:str,options:SheetProtectionType):
        """
        Protects worksheet with password.

        Args:
            password: Protection password.

        """
        enumoptions:c_int = options.value

        GetDllLibXls().XlsWorksheetBase_ProtectPO.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_ProtectPO, self.Ptr, password,enumoptions)

    @dispatch

    def Protect(self ,password:str):
        """
        Protects worksheet with password.protect the sheet except select lock/unlock cells.

        Args:
            password: Protection password.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Protects the first worksheet's content with password
            worksheet.Protect("123456")
            #Save to file
            workbook.SaveToFile("Protect.xlsx")

        """
        
        GetDllLibXls().XlsWorksheetBase_Protect.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_Protect, self.Ptr, password)


    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """
        Creates a clone of the worksheet.

        Args:
            parent: Parent object for cloning

        Returns:
            SpireObject: Cloned worksheet object
        """
        intPtrparent:c_void_p = parent.Ptr

        GetDllLibXls().XlsWorksheetBase_Clone.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsWorksheetBase_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_Clone, self.Ptr, intPtrparent)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @dispatch
    def Unprotect(self):
        """
        Unprotects this wokrsheet.

        """
        GetDllLibXls().XlsWorksheetBase_Unprotect.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_Unprotect, self.Ptr)

    @dispatch

    def Unprotect(self ,password:str):
        """
        Unprotects this worksheet using specified password.

        Args:
            password: Password to unprotect.

        """
        
        GetDllLibXls().XlsWorksheetBase_UnprotectP.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_UnprotectP, self.Ptr, password)


    def AddTextEffectShape(self ,effect:'PresetTextEffect',text:str,upperLeftRow:int,top:int,upperLeftColumn:int,left:int,height:int,width:int)->'IShape':
        """
        Adds a text effect shape to the worksheet.

        Args:
            effect: Preset text effect style
            text: Text content
            upperLeftRow: Top row index
            top: Top position in pixels
            upperLeftColumn: Left column index
            left: Left position in pixels
            height: Shape height
            width: Shape width

        Returns:
            IShape: Created text effect shape
        """
        enumeffect:c_int = effect.value

        GetDllLibXls().XlsWorksheetBase_AddTextEffectShape.argtypes=[c_void_p ,c_int,c_void_p,c_int,c_int,c_int,c_int,c_int,c_int]
        GetDllLibXls().XlsWorksheetBase_AddTextEffectShape.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_AddTextEffectShape, self.Ptr, enumeffect,text,upperLeftRow,top,upperLeftColumn,left,height,width)
        ret = None if intPtr==None else IShape(intPtr)
        return ret


    def SetChanged(self):
        """
        Marks the worksheet as modified to trigger refresh/resave operations.
        """
        GetDllLibXls().XlsWorksheetBase_SetChanged.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_SetChanged, self.Ptr)

    @property

    def Name(self)->str:
        """
        Returns or sets the name of the object. Read / write String.

        """
        GetDllLibXls().XlsWorksheetBase_get_Name.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorksheetBase_get_Name, self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        GetDllLibXls().XlsWorksheetBase_set_Name.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_Name, self.Ptr, value)

    @property

    def CodeName(self)->str:
        """
        Name used by macros to access workbook items.

        """
        GetDllLibXls().XlsWorksheetBase_get_CodeName.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_CodeName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().XlsWorksheetBase_get_CodeName, self.Ptr))
        return ret


    @CodeName.setter
    def CodeName(self, value:str):
        GetDllLibXls().XlsWorksheetBase_set_CodeName.argtypes=[c_void_p, c_wchar_p]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_CodeName, self.Ptr, value)

    @property
    def Zoom(self)->int:
        """
        Zoom factor of document.

        """
        GetDllLibXls().XlsWorksheetBase_get_Zoom.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_Zoom.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_Zoom, self.Ptr)
        return ret

    @Zoom.setter
    def Zoom(self, value:int):
        GetDllLibXls().XlsWorksheetBase_set_Zoom.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_Zoom, self.Ptr, value)

    @property

    def Visibility(self)->'WorksheetVisibility':
        """
        Controls end user visibility of worksheet.

        """
        GetDllLibXls().XlsWorksheetBase_get_Visibility.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_Visibility.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_Visibility, self.Ptr)
        objwraped = WorksheetVisibility(ret)
        return objwraped

    @Visibility.setter
    def Visibility(self, value:'WorksheetVisibility'):
        GetDllLibXls().XlsWorksheetBase_set_Visibility.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_Visibility, self.Ptr, value.value)

    @property

    def Workbook(self)->'IWorkbook':
        """
        Gets the parent workbook containing this worksheet.

        Returns:
            IWorkbook: Parent workbook object
        """
        GetDllLibXls().XlsWorksheetBase_get_Workbook.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_Workbook.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_Workbook, self.Ptr)
        ret = None if intPtr==None else IWorkbook(intPtr)
        return ret


    @property

    def Charts(self)->'IChartShapes':
        """
        Gets collection of all charts in the worksheet.

        Returns:
            IChartShapes: Collection of chart objects
        """
        GetDllLibXls().XlsWorksheetBase_get_Charts.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_Charts.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_Charts, self.Ptr)
        ret = None if intPtr==None else WorksheetChartsCollection(intPtr)
        return ret


    @property

    def QueryTables(self)->'QueryTableCollection':
        """
        Gets collection of external data query tables in the worksheet.

        Returns:
            QueryTableCollection: Collection of data query objects
        """
        GetDllLibXls().XlsWorksheetBase_get_QueryTables.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_QueryTables.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_QueryTables, self.Ptr)
        ret = None if intPtr==None else QueryTableCollection(intPtr)
        return ret


    @property

    def CheckBoxes(self)->'ICheckBoxes':
        """
        Gets collection of all checkbox controls in the worksheet.

        Returns:
            ICheckBoxes: Collection of checkbox objects
        """
        GetDllLibXls().XlsWorksheetBase_get_CheckBoxes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_CheckBoxes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_CheckBoxes, self.Ptr)
        ret = None if intPtr==None else CheckBoxCollection(intPtr)
        return ret


    @property

    def ButtonShapes(self)->'IButtonShapes':
        """
        Gets collection of all button controls in the worksheet.

        Returns:
            IButtonShapes: Collection of button objects
        """
        GetDllLibXls().XlsWorksheetBase_get_ButtonShapes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_ButtonShapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_ButtonShapes, self.Ptr)
        ret = None if intPtr==None else ButtonShapeCollection(intPtr)
        return ret


    @property

    def LabelShapes(self)->'ILabelShapes':
        """
        Gets collection of all label controls in the worksheet.

        Returns:
            ILabelShapes: Collection of label objects
        """
        GetDllLibXls().XlsWorksheetBase_get_LabelShapes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_LabelShapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_LabelShapes, self.Ptr)
        ret = None if intPtr==None else LabelShapeCollection(intPtr)
        return ret


    @property

    def Lines(self)->'ILines':
        """
        Gets collection of all line shapes in the worksheet.

        Returns:
            ILines: Collection of line objects
        """
        GetDllLibXls().XlsWorksheetBase_get_Lines.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_Lines.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_Lines, self.Ptr)
        ret = None if intPtr==None else LineCollection(intPtr)
        return ret


    @property

    def ListBoxes(self)->'IListBoxes':
        """
        Gets collection of all listbox controls in the worksheet.

        Returns:
            IListBoxes: Collection of listbox objects
        """
        GetDllLibXls().XlsWorksheetBase_get_ListBoxes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_ListBoxes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_ListBoxes, self.Ptr)
        ret = None if intPtr==None else ListBoxCollection(intPtr)
        return ret


    @property

    def ComboBoxes(self)->'IComboBoxes':
        """
        Gets collection of all combobox controls in the worksheet.

        Returns:
            IComboBoxes: Collection of combobox objects
        """
        GetDllLibXls().XlsWorksheetBase_get_ComboBoxes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_ComboBoxes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_ComboBoxes, self.Ptr)
        ret = None if intPtr==None else ComboBoxCollection(intPtr)
        return ret


    @property

    def GroupBoxes(self)->'IGroupBoxes':
        """
        Gets collection of all groupbox controls in the worksheet.

        Returns:
            IGroupBoxes: Collection of groupbox objects
        """
        GetDllLibXls().XlsWorksheetBase_get_GroupBoxes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_GroupBoxes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_GroupBoxes, self.Ptr)
        ret = None if intPtr==None else GroupBoxCollection(intPtr)
        return ret


    @property

    def OvalShapes(self)->'IOvalShapes':
        """
        Gets collection of all oval shapes in the worksheet.

        Returns:
            IOvalShapes: Collection of oval objects
        """
        GetDllLibXls().XlsWorksheetBase_get_OvalShapes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_OvalShapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_OvalShapes, self.Ptr)
        ret = None if intPtr==None else OvalShapeCollection(intPtr)
        return ret


    @property

    def RectangleShapes(self)->'IRectangleShapes':
        """
        Gets collection of all rectangle shapes in the worksheet.

        Returns:
            IRectangleShapes: Collection of rectangle objects
        """
        GetDllLibXls().XlsWorksheetBase_get_RectangleShapes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_RectangleShapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_RectangleShapes, self.Ptr)
        ret = None if intPtr==None else RectangleCollection(intPtr)
        return ret


    @property

    def ScrollBarShapes(self)->'IScrollBarShapes':
        """
        Gets collection of all scrollbar controls in the worksheet.

        Returns:
            IScrollBarShapes: Collection of scrollbar objects
        """
        GetDllLibXls().XlsWorksheetBase_get_ScrollBarShapes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_ScrollBarShapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_ScrollBarShapes, self.Ptr)
        ret = None if intPtr==None else ScrollBarCollection(intPtr)
        return ret


    @property

    def SpinnerShapes(self)->'ISpinnerShapes':
        """
        Gets collection of all spinner controls in the worksheet.

        Returns:
            ISpinnerShapes: Collection of spinner objects
        """
        GetDllLibXls().XlsWorksheetBase_get_SpinnerShapes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_SpinnerShapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_SpinnerShapes, self.Ptr)
        ret = None if intPtr==None else SpinnerShapeCollection(intPtr)
        return ret


    @property

    def ArcShapes(self)->'IArcShapes':
        """
        Gets collection of all arc shapes in the worksheet.

        Returns:
            IArcShapes: Collection of arc objects
        """
        GetDllLibXls().XlsWorksheetBase_get_ArcShapes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_ArcShapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_ArcShapes, self.Ptr)
        ret = None if intPtr==None else ArcShapeCollection(intPtr)
        return ret


    @property

    def Comments(self)->'IComments':
        """
        Gets collection of all cell comments in the worksheet.

        Returns:
            IComments: Collection of comment objects
        """
        GetDllLibXls().XlsWorksheetBase_get_Comments.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_Comments.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_Comments, self.Ptr)
        ret = None if intPtr==None else XlsCommentsCollection(intPtr)
        return ret


    @property

    def GridLineColor(self)->'ExcelColors':
        """
        Grid line color.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set grid lines color
            worksheet.GridLineColor = ExcelColors.Red
            #Save to file
            workbook.SaveToFile("GridLineColor.xlsx")

        """
        GetDllLibXls().XlsWorksheetBase_get_GridLineColor.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_GridLineColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_GridLineColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @GridLineColor.setter
    def GridLineColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsWorksheetBase_set_GridLineColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_GridLineColor, self.Ptr, value.value)

    @property
    def HasPictures(self)->bool:
        """
        Indicates whether the worksheet contains any pictures.

        Returns:
            bool: True if worksheet has pictures, False otherwise
        """
        GetDllLibXls().XlsWorksheetBase_get_HasPictures.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_HasPictures.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_HasPictures, self.Ptr)
        return ret

    @property
    def HasVmlShapes(self)->bool:
        """
        Indicates whether worksheet has vml shapes. Read-only.

        """
        GetDllLibXls().XlsWorksheetBase_get_HasVmlShapes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_HasVmlShapes.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_HasVmlShapes, self.Ptr)
        return ret

    @property

    def HeaderFooterShapes(self)->'XlsHeaderFooterShapeCollection':
        """
        Header / footer shapes collection.

        """
        GetDllLibXls().XlsWorksheetBase_get_HeaderFooterShapes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_HeaderFooterShapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_HeaderFooterShapes, self.Ptr)
        ret = None if intPtr==None else XlsHeaderFooterShapeCollection(intPtr)
        return ret


    @property
    def DefaultGridlineColor(self)->bool:
        """
        Indicates whether gridline color has default value.

        """
        GetDllLibXls().XlsWorksheetBase_get_DefaultGridlineColor.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_DefaultGridlineColor.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_DefaultGridlineColor, self.Ptr)
        return ret

    @property
    def FirstRow(self)->int:
        """
        Gets / sets index of the first row of the worksheet.

        """
        GetDllLibXls().XlsWorksheetBase_get_FirstRow.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_FirstRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_FirstRow, self.Ptr)
        return ret

    @FirstRow.setter
    def FirstRow(self, value:int):
        GetDllLibXls().XlsWorksheetBase_set_FirstRow.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_FirstRow, self.Ptr, value)

    @property
    def FirstColumn(self)->int:
        """
        Gets or sets index of the first column of the worksheet.

        """
        GetDllLibXls().XlsWorksheetBase_get_FirstColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_FirstColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_FirstColumn, self.Ptr)
        return ret

    @FirstColumn.setter
    def FirstColumn(self, value:int):
        GetDllLibXls().XlsWorksheetBase_set_FirstColumn.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_FirstColumn, self.Ptr, value)

    @property
    def FirstDataRow(self)->int:
        """
        Gets index of the first data row of the worksheet.

        """
        GetDllLibXls().XlsWorksheetBase_get_FirstDataRow.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_FirstDataRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_FirstDataRow, self.Ptr)
        return ret

    @property
    def FirstDataColumn(self)->int:
        """
        Gets index of the first data column of the worksheet.

        """
        GetDllLibXls().XlsWorksheetBase_get_FirstDataColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_FirstDataColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_FirstDataColumn, self.Ptr)
        return ret

    @property
    def LastRow(self)->int:
        """
        Gets or sets one-based index of the last row of the worksheet.

        """
        GetDllLibXls().XlsWorksheetBase_get_LastRow.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_LastRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_LastRow, self.Ptr)
        return ret

    @LastRow.setter
    def LastRow(self, value:int):
        GetDllLibXls().XlsWorksheetBase_set_LastRow.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_LastRow, self.Ptr, value)

    @property
    def LastColumn(self)->int:
        """
        Gets or sets index of the last column of the worksheet.

        """
        GetDllLibXls().XlsWorksheetBase_get_LastColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_LastColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_LastColumn, self.Ptr)
        return ret

    @LastColumn.setter
    def LastColumn(self, value:int):
        GetDllLibXls().XlsWorksheetBase_set_LastColumn.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_LastColumn, self.Ptr, value)

    @property
    def LastDataRow(self)->int:
        """
        Gets index of the last data row of the worksheet.

        """
        GetDllLibXls().XlsWorksheetBase_get_LastDataRow.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_LastDataRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_LastDataRow, self.Ptr)
        return ret

    @property
    def LastDataColumn(self)->int:
        """
        Gets index of the last data column of the worksheet.

        """
        GetDllLibXls().XlsWorksheetBase_get_LastDataColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_LastDataColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_LastDataColumn, self.Ptr)
        return ret

    @property
    def IsPasswordProtected(self)->bool:
        """
        Indicates whether the worksheet is password protected.

        Returns:
            bool: True if password protection is enabled, False otherwise
        """
        GetDllLibXls().XlsWorksheetBase_get_IsPasswordProtected.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_IsPasswordProtected.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_IsPasswordProtected, self.Ptr)
        return ret

    @property
    def Index(self)->int:
        """
        Returns the index number of the object within the collection of objects.

        """
        GetDllLibXls().XlsWorksheetBase_get_Index.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_Index.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_Index, self.Ptr)
        return ret

    @Index.setter
    def Index(self, value:int):
        GetDllLibXls().XlsWorksheetBase_set_Index.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_Index, self.Ptr, value)

    @property
    def IsTransitionEvaluation(self)->bool:
        """

        """
        GetDllLibXls().XlsWorksheetBase_get_IsTransitionEvaluation.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_IsTransitionEvaluation.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_IsTransitionEvaluation, self.Ptr)
        return ret

    @IsTransitionEvaluation.setter
    def IsTransitionEvaluation(self, value:bool):
        GetDllLibXls().XlsWorksheetBase_set_IsTransitionEvaluation.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_IsTransitionEvaluation, self.Ptr, value)

    @property
    def LeftVisibleColumn(self)->int:
        """
        Gets/sets left visible column of the worksheet.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set left visible column
            worksheet.LeftVisibleColumn = 3
            #Get left visible column
            Console.Write(worksheet.LeftVisibleColumn)
            #Save to file
            workbook.SaveToFile("LeftVisibleColumn.xlsx")

        """
        GetDllLibXls().XlsWorksheetBase_get_LeftVisibleColumn.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_LeftVisibleColumn.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_LeftVisibleColumn, self.Ptr)
        return ret

    @LeftVisibleColumn.setter
    def LeftVisibleColumn(self, value:int):
        GetDllLibXls().XlsWorksheetBase_set_LeftVisibleColumn.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_LeftVisibleColumn, self.Ptr, value)

    @property
    def RealIndex(self)->int:
        """

        """
        GetDllLibXls().XlsWorksheetBase_get_RealIndex.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_RealIndex.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_RealIndex, self.Ptr)
        return ret

    @RealIndex.setter
    def RealIndex(self, value:int):
        GetDllLibXls().XlsWorksheetBase_set_RealIndex.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_RealIndex, self.Ptr, value)

    @property
    def SheetId(self)->int:
        """
        Gets or sets sheetId for this sheet.

        """
        GetDllLibXls().XlsWorksheetBase_get_SheetId.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_SheetId.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_SheetId, self.Ptr)
        return ret

    @SheetId.setter
    def SheetId(self, value:int):
        GetDllLibXls().XlsWorksheetBase_set_SheetId.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_SheetId, self.Ptr, value)

    @property
    def IsRowColHeadersVisible(self)->bool:
        """
        Gets or sets whether the worksheet will display row and column headers. Default is true.

        """
        GetDllLibXls().XlsWorksheetBase_get_IsRowColHeadersVisible.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_IsRowColHeadersVisible.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_IsRowColHeadersVisible, self.Ptr)
        return ret

    @IsRowColHeadersVisible.setter
    def IsRowColHeadersVisible(self, value:bool):
        GetDllLibXls().XlsWorksheetBase_set_IsRowColHeadersVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_IsRowColHeadersVisible, self.Ptr, value)

    @property
    def IsRightToLeft(self)->bool:
        """
        Indicates whether worksheet is displayed right to left.

        """
        GetDllLibXls().XlsWorksheetBase_get_IsRightToLeft.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_IsRightToLeft.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_IsRightToLeft, self.Ptr)
        return ret

    @IsRightToLeft.setter
    def IsRightToLeft(self, value:bool):
        GetDllLibXls().XlsWorksheetBase_set_IsRightToLeft.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_IsRightToLeft, self.Ptr, value)

    @property

    def ParentWorkbook(self)->'XlsWorkbook':
        """
        Gets the parent workbook that contains this worksheet.

        Returns:
            XlsWorkbook: Parent workbook instance
        """
        GetDllLibXls().XlsWorksheetBase_get_ParentWorkbook.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_ParentWorkbook.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_ParentWorkbook, self.Ptr)
        ret = None if intPtr==None else XlsWorkbook(intPtr)
        return ret


    @property

    def Pictures(self)->'IPictures':
        """
        Gets collection of all pictures in the worksheet.

        Returns:
            IPictures: Collection of picture objects
        """
        GetDllLibXls().XlsWorksheetBase_get_Pictures.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_Pictures.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_Pictures, self.Ptr)
        ret = None if intPtr==None else XlsPicturesCollection(intPtr)
        return ret


    @property

    def RadioButtons(self)->'IRadioButtons':
        """
        Gets collection of all radio button controls in the worksheet.

        Returns:
            IRadioButtons: Collection of radio button objects
        """
        GetDllLibXls().XlsWorksheetBase_get_RadioButtons.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_RadioButtons.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_RadioButtons, self.Ptr)
        ret = None if intPtr==None else RadioButtonCollection(intPtr)
        return ret


    @property

    def TextBoxes(self)->'ITextBoxes':
        """
        Gets collection of all textbox controls in the worksheet (read-only).

        Returns:
            ITextBoxes: Collection of textbox objects
        """
        GetDllLibXls().XlsWorksheetBase_get_TextBoxes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TextBoxes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TextBoxes, self.Ptr)
        ret = None if intPtr==None else TextBoxCollection(intPtr)
        return ret


    @property
    def IsSelected(self)->bool:
        """
        Indicates whether the worksheet tab is currently selected.

        Returns:
            bool: True if the sheet tab is selected, False otherwise
        """
        GetDllLibXls().XlsWorksheetBase_get_IsSelected.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_IsSelected.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_IsSelected, self.Ptr)
        return ret

    @property
    def ProtectContents(self)->bool:
        """
        Indicates whether worksheet contents are protected.

        Returns:
            bool: True if cell contents are protected, False otherwise
        """
        GetDllLibXls().XlsWorksheetBase_get_ProtectContents.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_ProtectContents.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_ProtectContents, self.Ptr)
        return ret

    @property
    def ProtectDrawingObjects(self)->bool:
        """
        Indicates whether shapes and other drawing objects are protected.

        Returns:
            bool: True if drawing objects are protected, False otherwise
        """
        GetDllLibXls().XlsWorksheetBase_get_ProtectDrawingObjects.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_ProtectDrawingObjects.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_ProtectDrawingObjects, self.Ptr)
        return ret

    @property

    def Protection(self)->'SheetProtectionType':
        """
        Gets the sheet protection type specifying which elements are protected.

        Returns:
            SheetProtectionType: Enum value indicating protected elements
        """
        GetDllLibXls().XlsWorksheetBase_get_Protection.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_Protection.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_Protection, self.Ptr)
        objwraped = SheetProtectionType(ret)
        return objwraped

    @property
    def ProtectScenarios(self)->bool:
        """
        Indicates whether worksheet scenarios are protected.

        Returns:
            bool: True if scenarios are protected, False otherwise
        """
        GetDllLibXls().XlsWorksheetBase_get_ProtectScenarios.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_ProtectScenarios.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_ProtectScenarios, self.Ptr)
        return ret

    @property

    def TabColor(self)->'Color':
        """
        Gets or sets the color of the worksheet tab.

        Returns:
            Color: Color object representing the tab color
        """
        GetDllLibXls().XlsWorksheetBase_get_TabColor.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TabColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TabColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @TabColor.setter
    def TabColor(self, value:'Color'):
        GetDllLibXls().XlsWorksheetBase_set_TabColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_TabColor, self.Ptr, value.Ptr)

    @property

    def TabColorObject(self)->'OColor':
        """
        Gets the Office Color object representing the tab color.

        Returns:
            OColor: Office Color object with color properties
        """
        GetDllLibXls().XlsWorksheetBase_get_TabColorObject.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TabColorObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TabColorObject, self.Ptr)
        ret = None if intPtr==None else OColor(intPtr)
        return ret


    @property

    def TabKnownColor(self)->'ExcelColors':
        """
        Gets or sets the predefined Excel color for the worksheet tab.

        Returns:
            ExcelColors: Enum value representing the predefined color
        """
        GetDllLibXls().XlsWorksheetBase_get_TabKnownColor.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TabKnownColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TabKnownColor, self.Ptr)
        objwraped = ExcelColors(ret)
        return objwraped

    @TabKnownColor.setter
    def TabKnownColor(self, value:'ExcelColors'):
        GetDllLibXls().XlsWorksheetBase_set_TabKnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_TabKnownColor, self.Ptr, value.value)

    @property
    def TopVisibleRow(self)->int:
        """
        Gets/sets top visible row of the worksheet.
        Example::

            #Create worksheet
            workbook = Workbook()
            worksheet = workbook.Worksheets[0]
            #Set top visible row
            worksheet.TopVisibleRow = 5
            #Get top visible row
            Console.Write(worksheet.TopVisibleRow)
            #Save to file
            workbook.SaveToFile("TopVisibleRow.xlsx")

        """
        GetDllLibXls().XlsWorksheetBase_get_TopVisibleRow.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TopVisibleRow.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TopVisibleRow, self.Ptr)
        return ret

    @TopVisibleRow.setter
    def TopVisibleRow(self, value:int):
        GetDllLibXls().XlsWorksheetBase_set_TopVisibleRow.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_TopVisibleRow, self.Ptr, value)

    @property

    def TypedCheckBoxes(self)->'CheckBoxCollection':
        """
        Gets strongly-typed collection of checkbox controls.

        Returns:
            CheckBoxCollection: Typed collection of checkbox objects
        """
        GetDllLibXls().XlsWorksheetBase_get_TypedCheckBoxes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TypedCheckBoxes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TypedCheckBoxes, self.Ptr)
        ret = None if intPtr==None else CheckBoxCollection(intPtr)
        return ret


    @property

    def TypedComboBoxes(self)->'ComboBoxCollection':
        """
        Gets strongly-typed collection of combobox controls.

        Returns:
            ComboBoxCollection: Typed collection of combobox objects
        """
        GetDllLibXls().XlsWorksheetBase_get_TypedComboBoxes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TypedComboBoxes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TypedComboBoxes, self.Ptr)
        ret = None if intPtr==None else ComboBoxCollection(intPtr)
        return ret


    @property

    def TypedLines(self)->'LineCollection':
        """
        Returns inner lines collection. Read-only.

        """
        GetDllLibXls().XlsWorksheetBase_get_TypedLines.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TypedLines.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TypedLines, self.Ptr)
        ret = None if intPtr==None else LineCollection(intPtr)
        return ret


    @property

    def TypedRects(self)->'RectangleCollection':
        """
        Returns inner rects collection. Read-only.

        """
        GetDllLibXls().XlsWorksheetBase_get_TypedRects.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TypedRects.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TypedRects, self.Ptr)
        ret = None if intPtr==None else RectangleCollection(intPtr)
        return ret


    @property

    def TypedArcs(self)->'ArcShapeCollection':
        """

        """
        GetDllLibXls().XlsWorksheetBase_get_TypedArcs.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TypedArcs.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TypedArcs, self.Ptr)
        ret = None if intPtr==None else ArcShapeCollection(intPtr)
        return ret


    @property

    def TypedOvals(self)->'OvalShapeCollection':
        """
        Returns inner ovals collection. Read-only.

        """
        GetDllLibXls().XlsWorksheetBase_get_TypedOvals.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TypedOvals.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TypedOvals, self.Ptr)
        ret = None if intPtr==None else OvalShapeCollection(intPtr)
        return ret


    @property

    def TypedButtons(self)->'ButtonShapeCollection':
        """
        Returns inner buttons collection. Read-only.

        """
        GetDllLibXls().XlsWorksheetBase_get_TypedButtons.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TypedButtons.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TypedButtons, self.Ptr)
        ret = None if intPtr==None else ButtonShapeCollection(intPtr)
        return ret


    @property

    def TypedGroupBoxes(self)->'GroupBoxCollection':
        """
        Returns inner gourpboxes collection. Read-only.

        """
        GetDllLibXls().XlsWorksheetBase_get_TypedGroupBoxes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TypedGroupBoxes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TypedGroupBoxes, self.Ptr)
        ret = None if intPtr==None else GroupBoxCollection(intPtr)
        return ret


    @property

    def TypedLabels(self)->'LabelShapeCollection':
        """
        Returns inner labels collection. Read-only.

        """
        GetDllLibXls().XlsWorksheetBase_get_TypedLabels.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TypedLabels.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TypedLabels, self.Ptr)
        ret = None if intPtr==None else LabelShapeCollection(intPtr)
        return ret


    @property

    def TypedListBoxes(self)->'ListBoxCollection':
        """
        Returns inner listboxes collection. Read-only.

        """
        GetDllLibXls().XlsWorksheetBase_get_TypedListBoxes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TypedListBoxes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TypedListBoxes, self.Ptr)
        ret = None if intPtr==None else ListBoxCollection(intPtr)
        return ret


    @property

    def TypedScollBars(self)->'ScrollBarCollection':
        """
        Returns inner scollbars collection. Read-only.

        """
        GetDllLibXls().XlsWorksheetBase_get_TypedScollBars.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TypedScollBars.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TypedScollBars, self.Ptr)
        ret = None if intPtr==None else ScrollBarCollection(intPtr)
        return ret


    @property

    def TypedSpinners(self)->'SpinnerShapeCollection':
        """
        Returns inner spinners collection. Read-only.

        """
        GetDllLibXls().XlsWorksheetBase_get_TypedSpinners.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TypedSpinners.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TypedSpinners, self.Ptr)
        ret = None if intPtr==None else SpinnerShapeCollection(intPtr)
        return ret


    @property

    def TypedRadioButtons(self)->'RadioButtonCollection':
        """
        Gets strongly-typed collection of radio button controls.

        Returns:
            RadioButtonCollection: Typed collection of radio button objects
        """
        GetDllLibXls().XlsWorksheetBase_get_TypedRadioButtons.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TypedRadioButtons.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TypedRadioButtons, self.Ptr)
        ret = None if intPtr==None else RadioButtonCollection(intPtr)
        return ret


    @property

    def TypedTextBoxes(self)->'TextBoxCollection':
        """
        Returns inner textboxes collection. Read-only.

        """
        GetDllLibXls().XlsWorksheetBase_get_TypedTextBoxes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TypedTextBoxes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TypedTextBoxes, self.Ptr)
        ret = None if intPtr==None else TextBoxCollection(intPtr)
        return ret


    @property

    def PrstGeomShapes(self)->'PrstGeomShapeCollection':
        """
        Gets collection of preset geometric shapes in the worksheet.

        Returns:
            PrstGeomShapeCollection: Collection of preset geometry objects
        """
        GetDllLibXls().XlsWorksheetBase_get_PrstGeomShapes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_PrstGeomShapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_PrstGeomShapes, self.Ptr)
        ret = None if intPtr==None else PrstGeomShapeCollection(intPtr)
        return ret


    @property

    def TypedPictures(self)->'PicturesCollection':
        """
        Returns inner pictures collection. Read-only.

        """
        GetDllLibXls().XlsWorksheetBase_get_TypedPictures.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_TypedPictures.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_TypedPictures, self.Ptr)
        ret = None if intPtr==None else PicturesCollection(intPtr)
        return ret


    @property
    def UnknownVmlShapes(self)->bool:
        """
        Indicates whether worksheet contains some unknown vml shapes.

        """
        GetDllLibXls().XlsWorksheetBase_get_UnknownVmlShapes.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_UnknownVmlShapes.restype=c_bool
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_UnknownVmlShapes, self.Ptr)
        return ret

    @UnknownVmlShapes.setter
    def UnknownVmlShapes(self, value:bool):
        GetDllLibXls().XlsWorksheetBase_set_UnknownVmlShapes.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_set_UnknownVmlShapes, self.Ptr, value)

    @property
    def VmlShapesCount(self)->int:
        """
        Gets the total number of VML (Vector Markup Language) shapes in the worksheet.
        """
        GetDllLibXls().XlsWorksheetBase_get_VmlShapesCount.argtypes=[c_void_p]
        GetDllLibXls().XlsWorksheetBase_get_VmlShapesCount.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_get_VmlShapesCount, self.Ptr)
        return ret

    def Activate(self):
        """
        Activates the worksheet, making it the currently selected sheet in the workbook.

        Equivalent to clicking the sheet's tab in Excel UI.
        """
        GetDllLibXls().XlsWorksheetBase_Activate.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_Activate, self.Ptr)

    def Select(self):
        """
        Selects the worksheet in the workbook UI.
        """
        GetDllLibXls().XlsWorksheetBase_Select.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_Select, self.Ptr)

    def SelectTab(self):
        """
        Selects the worksheet tab in the workbook UI.
        """
        GetDllLibXls().XlsWorksheetBase_SelectTab.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_SelectTab, self.Ptr)

    @dispatch
    def Unselect(self):
        """
        Unselects the worksheet in the workbook UI.
        """
        GetDllLibXls().XlsWorksheetBase_Unselect1.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().XlsWorksheetBase_Unselect1, self.Ptr)

    @staticmethod
    def DEF_MIN_COLUMN_INDEX()->int:
        """
        Gets the minimum allowed column index constant for the worksheet.
        """
        #GetDllLibXls().XlsWorksheetBase_DEF_MIN_COLUMN_INDEX.argtypes=[]
        GetDllLibXls().XlsWorksheetBase_DEF_MIN_COLUMN_INDEX.restype=c_int
        ret = CallCFunction(GetDllLibXls().XlsWorksheetBase_DEF_MIN_COLUMN_INDEX)
        return ret

    @property
    def TabIndex(self)->int:
        """
        Gets the zero-based index position of the worksheet tab in the workbook's tab bar.
        """
        ret = GetIntValue(self.Ptr,"TabIndex", "")
        return ret
