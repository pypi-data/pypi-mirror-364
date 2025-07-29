from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IPivotTable (abc.ABC) :
    """
    Represents a PivotTable in a worksheet.
    """
    @property
    @abc.abstractmethod
    def Name(self)->str:
        """
        Gets or sets the name of the PivotTable.

        Returns:
            str: The name of the PivotTable.
        """
        pass


    @Name.setter
    @abc.abstractmethod
    def Name(self, value:str):
        """
        Sets the name of the PivotTable.

        Args:
            value (str): The new name for the PivotTable.
        """
        pass


    @property
    @abc.abstractmethod
    def PivotFields(self)->'PivotTableFields':
        """
        Gets the collection of fields in the PivotTable.

        Returns:
            PivotTableFields: The collection of fields.
        """
        pass


    @property
    @abc.abstractmethod
    def DataFields(self)->'PivotDataFields':
        """
        Gets the collection of data fields in the PivotTable.

        Returns:
            PivotDataFields: The collection of data fields.
        """
        pass


    @property
    @abc.abstractmethod
    def IsRowGrand(self)->bool:
        """
        Indicates whether row grand totals are displayed in the PivotTable.

        Returns:
            bool: True if row grand totals are displayed; otherwise, False.
        """
        pass


    @IsRowGrand.setter
    @abc.abstractmethod
    def IsRowGrand(self, value:bool):
        """
        Sets whether row grand totals are displayed in the PivotTable.

        Args:
            value (bool): True to display row grand totals; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsColumnGrand(self)->bool:
        """
        Indicates whether column grand totals are displayed in the PivotTable.

        Returns:
            bool: True if column grand totals are displayed; otherwise, False.
        """
        pass


    @IsColumnGrand.setter
    @abc.abstractmethod
    def IsColumnGrand(self, value:bool):
        """
        Sets whether column grand totals are displayed in the PivotTable.

        Args:
            value (bool): True to display column grand totals; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def ShowDrillIndicators(self)->bool:
        """
        Indicates whether drill indicators are shown in the PivotTable.

        Returns:
            bool: True if drill indicators are shown; otherwise, False.
        """
        pass


    @ShowDrillIndicators.setter
    @abc.abstractmethod
    def ShowDrillIndicators(self, value:bool):
        """
        Sets whether drill indicators are shown in the PivotTable.

        Args:
            value (bool): True to show drill indicators; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def DisplayFieldCaptions(self)->bool:
        """
        Indicates whether field captions are displayed in the PivotTable.

        Returns:
            bool: True if field captions are displayed; otherwise, False.
        """
        pass


    @DisplayFieldCaptions.setter
    @abc.abstractmethod
    def DisplayFieldCaptions(self, value:bool):
        """
        Sets whether field captions are displayed in the PivotTable.

        Args:
            value (bool): True to display field captions; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def RepeatItemsOnEachPrintedPage(self)->bool:
        """
        Indicates whether items are repeated on each printed page in the PivotTable.

        Returns:
            bool: True if items are repeated; otherwise, False.
        """
        pass


    @RepeatItemsOnEachPrintedPage.setter
    @abc.abstractmethod
    def RepeatItemsOnEachPrintedPage(self, value:bool):
        """
        Sets whether items are repeated on each printed page in the PivotTable.

        Args:
            value (bool): True to repeat items; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def BuiltInStyle(self)->BuiltInStyles:
        """
        Gets or sets the built-in style of the PivotTable.

        Returns:
            BuiltInStyles: The built-in style.
        """
        pass



    @BuiltInStyle.setter
    @abc.abstractmethod
    def BuiltInStyle(self, value:BuiltInStyles):
        """
        Sets the built-in style of the PivotTable.

        Args:
            value (BuiltInStyles): The built-in style to set.
        """
        pass



    @property
    @abc.abstractmethod
    def ShowRowGrand(self)->bool:
        """
        Indicates whether row grand totals are shown in the PivotTable.

        Returns:
            bool: True if row grand totals are shown; otherwise, False.
        """
        pass


    @ShowRowGrand.setter
    @abc.abstractmethod
    def ShowRowGrand(self, value:bool):
        """
        Sets whether row grand totals are shown in the PivotTable.

        Args:
            value (bool): True to show row grand totals; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def ShowColumnGrand(self)->bool:
        """
        Indicates whether column grand totals are shown in the PivotTable.

        Returns:
            bool: True if column grand totals are shown; otherwise, False.
        """
        pass


    @ShowColumnGrand.setter
    @abc.abstractmethod
    def ShowColumnGrand(self, value:bool):
        """
        Sets whether column grand totals are shown in the PivotTable.

        Args:
            value (bool): True to show column grand totals; otherwise, False.
        """
        pass


    @property
    @abc.abstractmethod
    def CacheIndex(self)->int:
        """
        Gets the index of the cache used by the PivotTable.

        Returns:
            int: The cache index.
        """
        pass


    @property

    @abc.abstractmethod
    def Location(self)->'CellRange':
        """
        Gets or sets the location of the PivotTable in the worksheet.

        Returns:
            CellRange: The location of the PivotTable.
        """
        pass


    @Location.setter
    @abc.abstractmethod
    def Location(self, value:'CellRange'):
        """
        Sets the location of the PivotTable in the worksheet.

        Args:
            value (CellRange): The new location for the PivotTable.
        """
        pass


    @property

    @abc.abstractmethod
    def Options(self)->'IPivotTableOptions':
        """
        Gets the options and settings for the PivotTable.

        Returns:
            IPivotTableOptions: The options and settings.
        """
        pass


    @property
    @abc.abstractmethod
    def RowsPerPage(self)->int:
        """
        Gets or sets the number of rows per page in the PivotTable.

        Returns:
            int: The number of rows per page.
        """
        pass


    @property
    @abc.abstractmethod
    def ColumnsPerPage(self)->int:
        """
        Gets or sets the number of columns per page in the PivotTable.

        Returns:
            int: The number of columns per page.
        """
        pass


    @property

    @abc.abstractmethod
    def CalculatedFields(self)->'IPivotCalculatedFields':
        """
        Gets the collection of calculated fields in the PivotTable.

        Returns:
            IPivotCalculatedFields: The collection of calculated fields.
        """
        pass


    @property

    @abc.abstractmethod
    def PageFields(self)->'IPivotFields':
        """
        Gets the collection of page fields in the PivotTable.

        Returns:
            IPivotFields: The collection of page fields.
        """
        pass


    @property

    @abc.abstractmethod
    def RowFields(self)->'IPivotFields':
        """
        Gets the collection of row fields in the PivotTable.

        Returns:
            IPivotFields: The collection of row fields.
        """
        pass


    @property

    @abc.abstractmethod
    def ColumnFields(self)->'IPivotFields':
        """
        Gets the collection of column fields in the PivotTable.

        Returns:
            IPivotFields: The collection of column fields.
        """
        pass


    @property
    @abc.abstractmethod
    def ShowDataFieldInRow(self)->bool:
        """
        Indicates whether data fields are shown in rows in the PivotTable.

        Returns:
            bool: True if data fields are shown in rows; otherwise, False.
        """
        pass


    @ShowDataFieldInRow.setter
    @abc.abstractmethod
    def ShowDataFieldInRow(self, value:bool):
        """
        Sets whether data fields are shown in rows in the PivotTable.

        Args:
            value (bool): True to show data fields in rows; otherwise, False.
        """
        pass


    @property

    @abc.abstractmethod
    def AutoFormatType(self)->'PivotAutoFomatTypes':
        """
        Gets or sets the auto format type for the PivotTable.

        Returns:
            PivotAutoFomatTypes: The auto format type.
        """
        pass


    @AutoFormatType.setter
    @abc.abstractmethod
    def AutoFormatType(self, value:'PivotAutoFomatTypes'):
        """
        Sets the auto format type for the PivotTable.

        Args:
            value (PivotAutoFomatTypes): The auto format type to set.
        """
        pass


    @property
    @abc.abstractmethod
    def IsCompatibleWithExcel2003(self)->bool:
        """
        Indicates whether the PivotTable is compatible with Excel 2003.

        Returns:
            bool: True if compatible with Excel 2003; otherwise, False.
        """
        pass


    @IsCompatibleWithExcel2003.setter
    @abc.abstractmethod
    def IsCompatibleWithExcel2003(self, value:bool):
        """
        Sets whether the PivotTable is compatible with Excel 2003.

        Args:
            value (bool): True if compatible with Excel 2003; otherwise, False.
        """
        pass


    @abc.abstractmethod
    def Clear(self):
        """
        Clears all data and settings from the PivotTable.
        """
        pass



    @abc.abstractmethod
    def ClearRowFieldFilter(self ,fieldName:str):
        """
        Clears the filter applied to the specified row field.

        Args:
            fieldName (str): The name of the row field to clear the filter from.
        """
        pass



    @abc.abstractmethod
    def ClearColumnFieldFilter(self ,fieldName:str):
        """
        Clears the filter applied to the specified column field.

        Args:
            fieldName (str): The name of the column field to clear the filter from.
        """
        pass



    @abc.abstractmethod
    def ClearFilter(self ,fieldName:str):
        """
        Clears the filter applied to the specified field.

        Args:
            fieldName (str): The name of the field to clear the filter from.
        """
        pass



    @abc.abstractmethod
    def ChangeDataSource(self ,dataSource:'IXLSRange'):
        """
        Changes the data source for the PivotTable.

        Args:
            dataSource (IXLSRange): The new data source range.
        """
        pass


