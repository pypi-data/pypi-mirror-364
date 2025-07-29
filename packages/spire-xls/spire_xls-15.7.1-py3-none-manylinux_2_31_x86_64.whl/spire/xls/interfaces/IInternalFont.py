from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IInternalFont (  IFont, IExcelApplication, IOptimizedUpdate) :
    """
    Interface for internal font objects in Excel.
    
    This interface extends IFont, IExcelApplication, and IOptimizedUpdate to provide
    access to internal font properties and methods used by the Excel engine.
    """
    @property
    @abc.abstractmethod
    def Index(self)->int:
        """
        Gets the index of the internal font.

        Returns:
            int: The index of the internal font.
        """
        pass

    @property
    @abc.abstractmethod
    def Font(self)->'XlsFont':
        """
        Gets the XlsFont object of the internal font.

        Returns:
            XlsFont: The XlsFont object.
        """
        pass


