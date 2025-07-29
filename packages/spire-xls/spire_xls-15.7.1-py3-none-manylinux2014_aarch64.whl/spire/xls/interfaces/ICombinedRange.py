from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ICombinedRange (  IXLSRange) :
    """Combined range interface.
    
    This interface represents a range that consists of multiple non-contiguous cell ranges
    combined together. It provides functionality for working with these combined ranges as
    a single entity, including clearing conditional formats, getting the component rectangles,
    and accessing range properties like address and cell count.
    
    Inherits from:
        IXLSRange: Excel range interface
    """
#
#    @abc.abstractmethod
#    def GetNewRangeLocation(self ,names:'Dictionary2',strSheetName:'String&')->str:
#        """
#
#        """
#        pass
#


#
#    @abc.abstractmethod
#    def Clone(self ,parent:'SpireObject',hashNewNames:'Dictionary2',book:'XlsWorkbook')->'IXLSRange':
#        """
#
#        """
#        pass
#


    @abc.abstractmethod
    def ClearConditionalFormats(self):
        """
        Clears all conditional formats in the combined range.
        """
        pass



    @abc.abstractmethod
    def GetRectangles(self)->List['Rectangle']:
        """
        Gets a list of rectangles that make up the combined range.

        Returns:
            List[Rectangle]: A list of rectangle objects.
        """
        pass



    @abc.abstractmethod
    def GetRectanglesCount(self)->int:
        """
        Gets the number of rectangles in the combined range.

        Returns:
            int: The number of rectangles.
        """
        pass


    @property
    @abc.abstractmethod
    def CellsCount(self)->int:
        """
        Gets the number of cells in the combined range.

        Returns:
            int: The number of cells.
        """
        pass


    @property

    @abc.abstractmethod
    def RangeGlobalAddress2007(self)->str:
        """
        Gets the global address of the range in Excel 2007 format.

        Returns:
            str: The global address string.
        """
        pass


    @property

    @abc.abstractmethod
    def WorksheetName(self)->str:
        """
        Gets the name of the worksheet containing the combined range.

        Returns:
            str: The worksheet name.
        """
        pass


