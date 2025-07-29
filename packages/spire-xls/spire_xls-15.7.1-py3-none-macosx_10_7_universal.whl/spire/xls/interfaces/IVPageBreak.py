from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IVPageBreak (abc.ABC) :
    """Vertical page break interface.
    
    This interface represents a vertical page break in an Excel worksheet.
    Vertical page breaks are used to control where a page ends when printing
    a worksheet, creating a manual break in the vertical direction (between columns).
    """
    @property
    @abc.abstractmethod
    def Parent(self)->'SpireObject':
        """Gets the parent object of the vertical page break.
        
        Returns:
            SpireObject: The parent object that contains this page break.
        """
        pass


