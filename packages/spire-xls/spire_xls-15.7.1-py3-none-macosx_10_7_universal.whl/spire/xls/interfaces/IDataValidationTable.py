from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IDataValidationTable (abc.ABC) :
    """Data validation table interface.
    
    This interface provides functionality for managing data validation rules in an Excel worksheet.
    The data validation table contains a collection of all data validation rules in a worksheet,
    allowing access to validation rules by index, finding validation for specific cells,
    and associating with workbooks and worksheets.
    """
    @property
    @abc.abstractmethod
    def Workbook(self)->'Workbook':
        """
        Gets the workbook associated with the data validation table.

        Returns:
            Workbook: The associated workbook.
        """
        pass

    @property
    @abc.abstractmethod
    def Worksheet(self)->'Worksheet':
        """
        Gets the worksheet associated with the data validation table.

        Returns:
            Worksheet: The associated worksheet.
        """
        pass

    @property
    @abc.abstractmethod
    def ShapesCount(self)->int:
        """
        Gets the number of shapes in the data validation table.

        Returns:
            int: The number of shapes.
        """
        pass

    @abc.abstractmethod
    def get_Item(self ,index:int)->'XlsDataValidationCollection':
        """
        Gets the data validation collection by index.

        Args:
            index (int): The index of the collection.

        Returns:
            XlsDataValidationCollection: The data validation collection at the specified index.
        """
        pass

    @abc.abstractmethod
    def FindDataValidation(self ,iCellIndex:int)->'IDataValidation':
        """
        Finds the data validation by cell index.

        Args:
            iCellIndex (int): The cell index to search for.

        Returns:
            IDataValidation: The data validation for the specified cell index.
        """
        pass

#
#    @abc.abstractmethod
#    def Remove(self ,rectangles:'Rectangle[]'):
#        """
#
#        """
#        pass
#

