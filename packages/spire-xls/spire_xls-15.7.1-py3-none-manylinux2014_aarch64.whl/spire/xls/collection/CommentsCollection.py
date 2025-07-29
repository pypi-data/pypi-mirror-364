from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class CommentsCollection (  XlsCommentsCollection) :
    """
    Represents a collection of comments in an Excel worksheet, providing methods to add, remove, and access comments.
    """
    @dispatch

    def AddComment(self ,range:CellRange)->ExcelComment:
        """
        Adds a comment to the specified range.

        Args:
            range (CellRange): The range to which the comment will be added.

        Returns:
            ExcelComment: The created comment object.

        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibXls().CommentsCollection_AddComment.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().CommentsCollection_AddComment.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CommentsCollection_AddComment, self.Ptr, intPtrrange)
        ret = None if intPtr==None else ExcelComment(intPtr)
        return ret


    @dispatch

    def AddComment(self ,rowIndex:int,columnIndex:int)->ExcelComment:
        """
        Adds a comment to the specified row and column.

        Args:
            rowIndex (int): The row index.
            columnIndex (int): The column index.

        Returns:
            ExcelComment: The created comment object.

        """
        
        GetDllLibXls().CommentsCollection_AddCommentRC.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().CommentsCollection_AddCommentRC.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CommentsCollection_AddCommentRC, self.Ptr, rowIndex,columnIndex)
        ret = None if intPtr==None else ExcelComment(intPtr)
        return ret



    def Remove(self ,comment:'ExcelComment'):
        """
        Removes a comment object from the collection.

        Args:
            comment (ExcelComment): The comment to remove.

        """
        intPtrcomment:c_void_p = comment.Ptr

        GetDllLibXls().CommentsCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().CommentsCollection_Remove, self.Ptr, intPtrcomment)

    @dispatch

    def get_Item(self ,index:int)->ExcelComment:
        """
        Gets a comment object by its index.

        Args:
            index (int): The index of the comment.

        Returns:
            ExcelComment: The comment object at the specified index.

        """
        
        GetDllLibXls().CommentsCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibXls().CommentsCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CommentsCollection_get_Item, self.Ptr, index)
        ret = None if intPtr==None else ExcelComment(intPtr)
        return ret


    @dispatch

    def get_Item(self ,name:str)->ExcelComment:
        """
        Gets a comment object by its name.

        Args:
            name (str): The name of the comment.

        Returns:
            ExcelComment: The comment object with the specified name.

        """
        
        GetDllLibXls().CommentsCollection_get_ItemN.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().CommentsCollection_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CommentsCollection_get_ItemN, self.Ptr, name)
        ret = None if intPtr==None else ExcelComment(intPtr)
        return ret


    @dispatch

    def get_Item(self ,Row:int,Column:int)->ExcelComment:
        """
        Gets a comment object by its row and column.

        Args:
            Row (int): The row index of the comment.
            Column (int): The column index of the comment.

        Returns:
            ExcelComment: The comment object at the specified cell.

        """
        
        GetDllLibXls().CommentsCollection_get_ItemRC.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibXls().CommentsCollection_get_ItemRC.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().CommentsCollection_get_ItemRC, self.Ptr, Row,Column)
        ret = None if intPtr==None else ExcelComment(intPtr)
        return ret


