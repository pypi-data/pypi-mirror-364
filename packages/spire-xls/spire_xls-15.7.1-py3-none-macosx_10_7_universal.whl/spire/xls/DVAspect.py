from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class DVAspect(Enum):
    """Represents the aspects of data that can be viewed in OLE objects.
    
    This enumeration defines the various aspects of data that can be viewed
    when working with OLE (Object Linking and Embedding) objects in Excel.
    
    Attributes:
        DVASPECT_CONTENT: Indicates that the object is displayed as content.
        DVASPECT_ICON: Indicates that the object is displayed as an icon.
    """
    DVASPECT_CONTENT = 0
    DVASPECT_ICON = 1

