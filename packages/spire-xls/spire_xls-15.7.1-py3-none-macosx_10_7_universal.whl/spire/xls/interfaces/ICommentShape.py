from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ICommentShape (  IComment, ITextBoxShape, ITextBox) :
    """Comment shape interface.
    
    This interface represents a comment shape in Excel worksheets, combining the functionality
    of comments, text boxes, and text formatting. Comment shapes are used to add notes or
    explanations to cells that can be viewed by hovering over the cell or displaying all comments.
    
    Inherits from:
        IComment: Comment interface
        ITextBoxShape: Text box shape interface
        ITextBox: Text box interface
    """
