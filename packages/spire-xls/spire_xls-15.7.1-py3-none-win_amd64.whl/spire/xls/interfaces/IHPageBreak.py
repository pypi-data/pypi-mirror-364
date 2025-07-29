from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IHPageBreak (abc.ABC) :
    """Horizontal page break interface.
    
    This interface represents a horizontal page break in an Excel worksheet.
    Horizontal page breaks are used to control where a page ends when printing
    a worksheet, creating a manual break in the horizontal direction (between rows).
    """
    @property
    @abc.abstractmethod
    def Parent(self)->'SpireObject':
        """Gets the parent object of the horizontal page break.
        
        Returns:
            SpireObject: The parent object that contains this page break.
        """
        pass


