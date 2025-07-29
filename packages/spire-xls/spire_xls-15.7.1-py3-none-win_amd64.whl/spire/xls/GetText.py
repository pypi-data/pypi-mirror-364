from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class GetText(Enum):
    """Represents options for retrieving text from Excel cells.
    
    This enumeration defines the different ways to extract text content
    from Excel cells, either as formatted number text or as raw values.
    
    Attributes:
        NumberText: Get the text as a formatted number string according to the cell's format.
        Value: Get the raw value of the cell without formatting.
    """
    NumberText = 0
    Value = 1

