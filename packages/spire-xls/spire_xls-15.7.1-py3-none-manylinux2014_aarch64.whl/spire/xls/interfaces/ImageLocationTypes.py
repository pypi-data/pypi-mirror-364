from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ImageLocationTypes(Enum):
    """
    Defines the location types for images in Excel.
    
    This enum specifies how image positions are interpreted within Excel documents.
    """
    GlobalAbsolute = 0  # Image position is absolute within the document
    TableRelative = 1   # Image position is relative to a table

