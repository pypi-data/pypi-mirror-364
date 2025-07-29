from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartCategoryAxis (  IChartValueAxis, IChartAxis) :
    """Category axis interface for Excel charts.
    
    This interface represents the category (X) axis of a chart in Excel. It provides properties
    and methods to customize the appearance and behavior of the category axis, such as
    setting crossing points, label frequencies, tick mark frequencies, and other formatting options.
    
    Inherits from:
        IChartValueAxis: Provides value axis functionality.
        IChartAxis: Provides base axis functionality.
    """
    @property
    @abc.abstractmethod
    def CrossingPoint(self)->float:
        """Gets the point where the value axis crosses this category axis.
        
        This property specifies the category number where the value axis crosses this category axis.
        Only applicable to 2D charts.
        
        Returns:
            float: The category number where the value axis crosses this category axis.
        """
        pass


    @CrossingPoint.setter
    @abc.abstractmethod
    def CrossingPoint(self, value:float):
        """Sets the point where the value axis crosses this category axis.
        
        This property specifies the category number where the value axis crosses this category axis.
        Only applicable to 2D charts.
        
        Args:
            value (float): The category number where the value axis crosses this category axis.
        """
        pass


    @property
    @abc.abstractmethod
    def LabelFrequency(self)->int:
        """Gets the frequency of the labels on the category axis.
        
        This property specifies how often labels appear on the category axis.
        For example, a value of 2 means every second label is displayed.
        
        Returns:
            int: The frequency of the labels on the category axis.
        """
        pass


    @LabelFrequency.setter
    @abc.abstractmethod
    def LabelFrequency(self, value:int):
        """Sets the frequency of the labels on the category axis.
        
        This property specifies how often labels appear on the category axis.
        For example, a value of 2 means every second label is displayed.
        
        Args:
            value (int): The frequency of the labels on the category axis.
        """
        pass


    @property
    @abc.abstractmethod
    def TickMarksFrequency(self)->int:
        """Gets the frequency of tick marks on the category axis.
        
        This property specifies how often tick marks appear on the category axis.
        For example, a value of 2 means tick marks appear at every second category.
        
        Returns:
            int: The frequency of tick marks on the category axis.
        """
        pass


    @TickMarksFrequency.setter
    @abc.abstractmethod
    def TickMarksFrequency(self, value:int):
        """Sets the frequency of tick marks on the category axis.
        
        This property specifies how often tick marks appear on the category axis.
        For example, a value of 2 means tick marks appear at every second category.
        
        Args:
            value (int): The frequency of tick marks on the category axis.
        """
        pass


    @property
    @abc.abstractmethod
    def TickLabelSpacing(self)->int:
        """Gets the number of categories or series between tick-mark labels.
        
        This property specifies the interval between labels displayed on the category axis.
        For example, a value of 2 means that a label is displayed for every second category.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:F2"]
            #Set chart category axis
            categoryAxis = chart.PrimaryCategoryAxis
            #Set tick label spacing
            categoryAxis.TickLabelSpacing = 2
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            int: The number of categories between tick-mark labels.
        """
        pass


    @TickLabelSpacing.setter
    @abc.abstractmethod
    def TickLabelSpacing(self, value:int):
        """Sets the number of categories or series between tick-mark labels.
        
        This property specifies the interval between labels displayed on the category axis.
        For example, a value of 2 means that a label is displayed for every second category.
        
        Args:
            value (int): The number of categories between tick-mark labels.
        """
        pass


    @property
    @abc.abstractmethod
    def TickMarkSpacing(self)->int:
        """Gets the number of categories or series between tick marks.
        
        This property specifies the interval between tick marks on the category axis.
        For example, a value of 2 means that a tick mark is displayed for every second category.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:F2"]
            #Set chart category axis
            categoryAxis = chart.PrimaryCategoryAxis
            #Set tick mark spacing
            categoryAxis.TickMarkSpacing = 2
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            int: The number of categories between tick marks.
        """
        pass


    @TickMarkSpacing.setter
    @abc.abstractmethod
    def TickMarkSpacing(self, value:int):
        """Sets the number of categories or series between tick marks.
        
        This property specifies the interval between tick marks on the category axis.
        For example, a value of 2 means that a tick mark is displayed for every second category.
        
        Args:
            value (int): The number of categories between tick marks.
        """
        pass


    @property
    @abc.abstractmethod
    def AxisBetweenCategories(self)->bool:
        """Gets whether the value axis crosses the category axis between categories.
        
        When true, the value axis crosses the category axis between categories, which is the default
        for area and surface charts. When false, the value axis crosses the category axis at the
        category values.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart category axis
            categoryAxis = chart.PrimaryCategoryAxis
            #Set category axis IsBetween
            categoryAxis.AxisBetweenCategories = false
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if the value axis crosses between categories, otherwise False.
        """
        pass


    @AxisBetweenCategories.setter
    @abc.abstractmethod
    def AxisBetweenCategories(self, value:bool):
        """Sets whether the value axis crosses the category axis between categories.
        
        When true, the value axis crosses the category axis between categories, which is the default
        for area and surface charts. When false, the value axis crosses the category axis at the
        category values.
        
        Args:
            value (bool): True to cross between categories, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def CategoryLabels(self)->'IXLSRange':
        """Gets the range containing the category labels for the chart.
        
        This property returns the Excel range that contains the labels used for the categories
        on the category axis. This is typically the first row or column of the chart's data range.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart category axis
            categoryAxis = chart.PrimaryCategoryAxis
            #Get category label range . Output will be A1:C1
            print(categoryAxis.CategoryLabels.RangeAddressLocal)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            IXLSRange: The range containing the category labels.
        """
        pass


    @CategoryLabels.setter
    @abc.abstractmethod
    def CategoryLabels(self, value:'IXLSRange'):
        """Sets the range containing the category labels for the chart.
        
        This property sets the Excel range that contains the labels used for the categories
        on the category axis. This is typically the first row or column of the chart's data range.
        
        Args:
            value (IXLSRange): The range containing the category labels.
        """
        pass


    @property
    @abc.abstractmethod
    def EnteredDirectlyCategoryLabels(self)->List['SpireObject']:
        """Gets the collection of category labels that were entered directly.
        
        This property returns the collection of category labels that were manually entered
        instead of being derived from a range in the worksheet. These are custom labels
        that override the default labels.
        
        Returns:
            List[SpireObject]: A list of category label objects that were entered directly.
        """
        pass


    @EnteredDirectlyCategoryLabels.setter
    @abc.abstractmethod
    def EnteredDirectlyCategoryLabels(self, value:List['SpireObject']):
        """Sets the collection of category labels that were entered directly.
        
        This property sets custom category labels that override the default labels.
        These labels are not derived from a range in the worksheet but are entered manually.
        
        Args:
            value (List[SpireObject]): A list of category label objects to set.
        """
        pass


    @property
    @abc.abstractmethod
    def CategoryType(self)->'CategoryType':
        """Gets the category type for the axis.
        
        This property returns the type of category used for the axis, such as automatic,
        time-based, or text-based categories. Time-based categories allow for special
        formatting and scaling options.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart category axis
            categoryAxis = chart.PrimaryCategoryAxis
            #Set category type
            categoryAxis.CategoryType = CategoryType.Time
            #Set base unit
            categoryAxis.BaseUnit = ChartBaseUnitType.Year
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            CategoryType: The category type for the axis.
        """
        pass


    @CategoryType.setter
    @abc.abstractmethod
    def CategoryType(self, value:'CategoryType'):
        """Sets the category type for the axis.
        
        This property sets the type of category used for the axis, such as automatic,
        time-based, or text-based categories. Time-based categories allow for special
        formatting and scaling options.
        
        Args:
            value (CategoryType): The category type to set for the axis.
        """
        pass


    @property
    @abc.abstractmethod
    def Offset(self)->int:
        """Gets the distance between the labels and the axis line.
        
        This property specifies the distance between the category labels and the axis line.
        The value can range from 0 through 1000, where larger values position the labels
        further from the axis line.
        
        Returns:
            int: The distance between the labels and the axis line (0-1000).
        """
        pass


    @Offset.setter
    @abc.abstractmethod
    def Offset(self, value:int):
        """Sets the distance between the labels and the axis line.
        
        This property specifies the distance between the category labels and the axis line.
        The value can range from 0 through 1000, where larger values position the labels
        further from the axis line.
        
        Args:
            value (int): The distance between the labels and the axis line (0-1000).
        """
        pass


    @property
    @abc.abstractmethod
    def BaseUnit(self)->'ChartBaseUnitType':
        """Gets the base unit for the category axis when using time-based categories.
        
        This property specifies the smallest time unit displayed on the category axis
        when CategoryType is set to Time. The base unit can be days, months, years, etc.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart and set range
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart category axis
            categoryAxis = chart.PrimaryCategoryAxis
            #Set category type
            categoryAxis.CategoryType = CategoryType.Time
            #Set base unit
            categoryAxis.BaseUnit = ChartBaseUnitType.Year
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            ChartBaseUnitType: The base unit for the category axis.
        """
        pass


    @BaseUnit.setter
    @abc.abstractmethod
    def BaseUnit(self, value:'ChartBaseUnitType'):
        """Sets the base unit for the category axis when using time-based categories.
        
        This property specifies the smallest time unit displayed on the category axis
        when CategoryType is set to Time. The base unit can be days, months, years, etc.
        
        Args:
            value (ChartBaseUnitType): The base unit to set for the category axis.
        """
        pass


    @property
    @abc.abstractmethod
    def BaseUnitIsAuto(self)->bool:
        """Gets whether the base unit for the category axis is set automatically.
        
        When true, Excel automatically determines the appropriate base unit for the category axis
        based on the data. When false, the base unit is set manually using the BaseUnit property.
        
        Returns:
            bool: True if the base unit is set automatically, otherwise False.
        """
        pass


    @BaseUnitIsAuto.setter
    @abc.abstractmethod
    def BaseUnitIsAuto(self, value:bool):
        """Sets whether the base unit for the category axis is set automatically.
        
        When true, Excel automatically determines the appropriate base unit for the category axis
        based on the data. When false, the base unit is set manually using the BaseUnit property.
        
        Args:
            value (bool): True to set the base unit automatically, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def MajorUnitScale(self)->'ChartBaseUnitType':
        """Gets the major unit scale for the category axis when using time-based categories.
        
        This property specifies the scale of the major unit on the category axis when
        CategoryType is set to Time. For example, if the major unit is 1 and the major unit scale
        is Months, then major tick marks appear every month.
        
        Returns:
            ChartBaseUnitType: The major unit scale for the category axis.
        """
        pass


    @MajorUnitScale.setter
    @abc.abstractmethod
    def MajorUnitScale(self, value:'ChartBaseUnitType'):
        """Sets the major unit scale for the category axis when using time-based categories.
        
        This property specifies the scale of the major unit on the category axis when
        CategoryType is set to Time. For example, if the major unit is 1 and the major unit scale
        is Months, then major tick marks appear every month.
        
        Args:
            value (ChartBaseUnitType): The major unit scale to set for the category axis.
        """
        pass


    @property
    @abc.abstractmethod
    def MinorUnitScale(self)->'ChartBaseUnitType':
        """Gets the minor unit scale for the category axis when using time-based categories.
        
        This property specifies the scale of the minor unit on the category axis when
        CategoryType is set to Time. For example, if the minor unit is 1 and the minor unit scale
        is Days, then minor tick marks appear every day.
        
        Returns:
            ChartBaseUnitType: The minor unit scale for the category axis.
        """
        pass


    @MinorUnitScale.setter
    @abc.abstractmethod
    def MinorUnitScale(self, value:'ChartBaseUnitType'):
        """Sets the minor unit scale for the category axis when using time-based categories.
        
        This property specifies the scale of the minor unit on the category axis when
        CategoryType is set to Time. For example, if the minor unit is 1 and the minor unit scale
        is Days, then minor tick marks appear every day.
        
        Args:
            value (ChartBaseUnitType): The minor unit scale to set for the category axis.
        """
        pass


