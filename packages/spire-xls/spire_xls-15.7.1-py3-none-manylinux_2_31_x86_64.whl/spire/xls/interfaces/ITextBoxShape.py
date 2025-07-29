from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ITextBoxShape (  ITextBox, IShape) :
    """Interface for text box shapes in Excel worksheets.
    
    This interface combines the functionality of text boxes and shapes,
    representing a text box that also has shape properties. It provides
    access to line formatting for the text box border.
    """
    @property

    @abc.abstractmethod
    def Line(self)->'IShapeLineFormat':
        """Gets the line formatting of the text box shape border.
        
        Returns:
            IShapeLineFormat: An object that represents the line formatting of the text box border.
        """
        pass


