from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsCommentsCollection (  CollectionBase[XlsComment],IComments) :
    """
    Represents a collection of comments in an Excel worksheet.
    """
    @dispatch

    def get_Item(self ,index:int)->ICommentShape:
        """
        Gets the comment shape at the specified index.

        Args:
            index (int): The index of the comment shape to retrieve.

        Returns:
            ICommentShape: The comment shape at the specified index.
        """
        
        GetDllLibXls().XlsCommentsCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().XlsCommentsCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsCommentsCollection_get_Item, self.Ptr, index)
        ret = None if intPtr==None else XlsComment(intPtr)
        return ret


    @dispatch

    def get_Item(self ,iRow:int,iColumn:int)->ICommentShape:
        """
        Gets the comment shape at the specified row and column.

        Args:
            iRow (int): The row of the comment.
            iColumn (int): The column of the comment.

        Returns:
            ICommentShape: The comment shape at the specified cell.
        """
        
        GetDllLibXls().XlsCommentsCollection_get_ItemII.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsCommentsCollection_get_ItemII.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsCommentsCollection_get_ItemII, self.Ptr, iRow,iColumn)
        ret = None if intPtr==None else XlsComment(intPtr)
        return ret


    @dispatch

    def get_Item(self ,name:str)->ICommentShape:
        """
        Gets the comment shape by its name.

        Args:
            name (str): The name of the comment shape.

        Returns:
            ICommentShape: The comment shape with the specified name.
        """
        
        GetDllLibXls().XlsCommentsCollection_get_ItemN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().XlsCommentsCollection_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsCommentsCollection_get_ItemN, self.Ptr, name)
        ret = None if intPtr==None else XlsComment(intPtr)
        return ret


    @dispatch

    def AddComment(self ,iRow:int,iColumn:int)->ICommentShape:
        """
        Adds a comment to the specified cell.

        Args:
            iRow (int): The row of the cell to add the comment to.
            iColumn (int): The column of the cell to add the comment to.

        Returns:
            ICommentShape: The newly created comment shape.
        """
        
        GetDllLibXls().XlsCommentsCollection_AddComment.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().XlsCommentsCollection_AddComment.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsCommentsCollection_AddComment, self.Ptr, iRow,iColumn)
        ret = None if intPtr==None else XlsComment(intPtr)
        return ret


    @dispatch

    def AddComment(self ,iRow:int,iColumn:int,bIsParseOptions:bool)->ICommentShape:
        """
        Adds a comment to the specified cell with parse options.

        Args:
            iRow (int): The row of the cell to add the comment to.
            iColumn (int): The column of the cell to add the comment to.
            bIsParseOptions (bool): Whether to parse options when adding the comment.

        Returns:
            ICommentShape: The newly created comment shape.
        """
        
        GetDllLibXls().XlsCommentsCollection_AddCommentIIB.argtypes=[c_void_p ,c_int,c_int,c_bool]
        GetDllLibXls().XlsCommentsCollection_AddCommentIIB.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().XlsCommentsCollection_AddCommentIIB, self.Ptr, iRow,iColumn,bIsParseOptions)
        ret = None if intPtr==None else XlsComment(intPtr)
        return ret


