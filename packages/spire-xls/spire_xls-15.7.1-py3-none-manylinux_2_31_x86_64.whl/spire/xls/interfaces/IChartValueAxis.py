from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartValueAxis (  IChartAxis) :
    """Chart value axis interface.
    
    This interface represents the value axis (typically the Y-axis) of a chart in Excel.
    The value axis is used to plot the data values in a chart and provides functionality
    for customizing its appearance and behavior, including scale, units, and crossing points.
    
    Inherits from:
        IChartAxis: Base chart axis interface
    """
    @property
    @abc.abstractmethod
    def MinValue(self)->float:
        """Gets the minimum value on the value axis.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart value axis
            valueAxis = chart.PrimaryValueAxis
            #Set min and max value
            valueAxis.MinValue = -20
            valueAxis.MaxValue = 60
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            float: The minimum value on the value axis.
        """
        pass


    @MinValue.setter
    @abc.abstractmethod
    def MinValue(self, value:float):
        """Sets the minimum value on the value axis.
        
        Args:
            value (float): The minimum value to set for the value axis.
        """
        pass


    @property
    @abc.abstractmethod
    def MaxValue(self)->float:
        """Gets the maximum value on the value axis.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart value axis
            valueAxis = chart.PrimaryValueAxis
            #Set min and max value
            valueAxis.MinValue = -20
            valueAxis.MaxValue = 60
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            float: The maximum value on the value axis.
        """
        pass


    @MaxValue.setter
    @abc.abstractmethod
    def MaxValue(self, value:float):
        """Sets the maximum value on the value axis.
        
        Args:
            value (float): The maximum value to set for the value axis.
        """
        pass


    @property
    @abc.abstractmethod
    def MajorUnit(self)->float:
        """Gets the value of the major increment on the value axis.
        
        The major unit determines the spacing between major tick marks and gridlines.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart value axis
            valueAxis = chart.PrimaryValueAxis
            #Set major unit
            valueAxis.MajorUnit = 20
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            float: The value of the major increment.
        """
        pass


    @MajorUnit.setter
    @abc.abstractmethod
    def MajorUnit(self, value:float):
        """Sets the value of the major increment on the value axis.
        
        The major unit determines the spacing between major tick marks and gridlines.
        
        Args:
            value (float): The value of the major increment to set.
        """
        pass


    @property
    @abc.abstractmethod
    def MinorUnit(self)->float:
        """Gets the value of the minor increment on the value axis.
        
        The minor unit determines the spacing between minor tick marks and gridlines.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart value axis
            valueAxis = chart.PrimaryValueAxis
            #Set major unit
            valueAxis.MinorUnit = 8
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            float: The value of the minor increment.
        """
        pass


    @MinorUnit.setter
    @abc.abstractmethod
    def MinorUnit(self, value:float):
        """Sets the value of the minor increment on the value axis.
        
        The minor unit determines the spacing between minor tick marks and gridlines.
        
        Args:
            value (float): The value of the minor increment to set.
        """
        pass


    @property
    @abc.abstractmethod
    def CrossValue(self)->float:
        """Gets the value where the category axis crosses the value axis.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart value axis
            valueAxis = chart.PrimaryValueAxis
            #Set CrossValue
            valueAxis.CrossValue = 15
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            float: The value where the category axis crosses the value axis.
        """
        pass


    @CrossValue.setter
    @abc.abstractmethod
    def CrossValue(self, value:float):
        """Sets the value where the category axis crosses the value axis.
        
        Args:
            value (float): The value where the category axis should cross the value axis.
        """
        pass


    @property
    @abc.abstractmethod
    def CrossesAt(self)->float:
        """Gets the point on the value axis where another axis crosses it.
        
        This property represents the specific value on the value axis where another axis
        (typically the category axis) crosses it.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart value axis
            valueAxis = chart.PrimaryValueAxis
            #Set CrossAt
            valueAxis.CrossesAt = 15
            #Save to file
            workbook.SaveToFile("Chart.xlsx")
            
        Returns:
            float: The point on the value axis where another axis crosses it.
        """
        pass


    @CrossesAt.setter
    @abc.abstractmethod
    def CrossesAt(self, value:float):
        """Sets the point on the value axis where another axis crosses it.
        
        This property sets the specific value on the value axis where another axis
        (typically the category axis) crosses it.
        
        Args:
            value (float): The point on the value axis where another axis should cross it.
        """
        pass


    @property
    @abc.abstractmethod
    def IsAutoMin(self)->bool:
        """Gets whether the minimum value of the axis is set automatically.
        
        When true, Excel automatically determines the minimum value for the axis based on the data.
        When false, the minimum value is set manually using the MinValue property.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart value axis
            valueAxis = chart.PrimaryValueAxis
            #Check IsAutoMin
            print(valueAxis.IsAutoMin)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if the minimum value is set automatically, otherwise False.
        """
        pass


    @IsAutoMin.setter
    @abc.abstractmethod
    def IsAutoMin(self, value:bool):
        """Sets whether the minimum value of the axis is set automatically.
        
        When true, Excel automatically determines the minimum value for the axis based on the data.
        When false, the minimum value is set manually using the MinValue property.
        
        Args:
            value (bool): True to set the minimum value automatically, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsAutoMax(self)->bool:
        """Gets whether the maximum value of the axis is set automatically.
        
        When true, Excel automatically determines the maximum value for the axis based on the data.
        When false, the maximum value is set manually using the MaxValue property.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart value axis
            valueAxis = chart.PrimaryValueAxis
            #Check IsAutoMax
            print(valueAxis.IsAutoMax)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if the maximum value is set automatically, otherwise False.
        """
        pass


    @IsAutoMax.setter
    @abc.abstractmethod
    def IsAutoMax(self, value:bool):
        """Sets whether the maximum value of the axis is set automatically.
        
        When true, Excel automatically determines the maximum value for the axis based on the data.
        When false, the maximum value is set manually using the MaxValue property.
        
        Args:
            value (bool): True to set the maximum value automatically, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsAutoMajor(self)->bool:
        """Gets whether the major unit of the axis is set automatically.
        
        When true, Excel automatically determines the spacing between major tick marks and gridlines.
        When false, the major unit is set manually using the MajorUnit property.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart value axis
            valueAxis = chart.PrimaryValueAxis
            #Check IsAutoMajor
            print(valueAxis.IsAutoMajor)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if the major unit is set automatically, otherwise False.
        """
        pass


    @IsAutoMajor.setter
    @abc.abstractmethod
    def IsAutoMajor(self, value:bool):
        """Sets whether the major unit of the axis is set automatically.
        
        When true, Excel automatically determines the spacing between major tick marks and gridlines.
        When false, the major unit is set manually using the MajorUnit property.
        
        Args:
            value (bool): True to set the major unit automatically, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsAutoMinor(self)->bool:
        """Gets whether the minor unit of the axis is set automatically.
        
        When true, Excel automatically determines the spacing between minor tick marks and gridlines.
        When false, the minor unit is set manually using the MinorUnit property.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart value axis
            valueAxis = chart.PrimaryValueAxis
            #Check IsAutoMinor
            print(valueAxis.IsAutoMinor)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if the minor unit is set automatically, otherwise False.
        """
        pass


    @IsAutoMinor.setter
    @abc.abstractmethod
    def IsAutoMinor(self, value:bool):
        """Sets whether the minor unit of the axis is set automatically.
        
        When true, Excel automatically determines the spacing between minor tick marks and gridlines.
        When false, the minor unit is set manually using the MinorUnit property.
        
        Args:
            value (bool): True to set the minor unit automatically, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsAutoCross(self)->bool:
        """Gets whether the axis crossing point is set automatically.
        
        When true, Excel automatically determines where the axes cross.
        When false, the crossing point is set manually using the CrossesAt property.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart value axis
            valueAxis = chart.PrimaryValueAxis
            #Set CrossAt
            valueAxis.CrossesAt = 15
            #Check IsAutoCross
            print(valueAxis.IsAutoCross)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if the axis crossing point is set automatically, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsLogScale(self)->bool:
        """Gets whether the axis uses a logarithmic scale.
        
        When true, the axis uses a logarithmic scale instead of a linear scale,
        which is useful for displaying data that covers a wide range of values.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart value axis
            valueAxis = chart.PrimaryValueAxis
            #Set IsLogScale
            valueAxis.IsLogScale = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if the axis uses a logarithmic scale, otherwise False.
        """
        pass


    @IsLogScale.setter
    @abc.abstractmethod
    def IsLogScale(self, value:bool):
        """Sets whether the axis uses a logarithmic scale.
        
        When true, the axis uses a logarithmic scale instead of a linear scale,
        which is useful for displaying data that covers a wide range of values.
        
        Args:
            value (bool): True to use a logarithmic scale, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsReverseOrder(self)->bool:
        """Gets whether the values on the axis are displayed in reverse order.
        
        When true, the values on the axis are displayed from high to low instead of the default low to high.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart value axis
            valueAxis = chart.PrimaryValueAxis
            #Set IsReverseOrder
            valueAxis.IsReverseOrder = true
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if the values are displayed in reverse order, otherwise False.
        """
        pass


    @IsReverseOrder.setter
    @abc.abstractmethod
    def IsReverseOrder(self, value:bool):
        """Sets whether the values on the axis are displayed in reverse order.
        
        When true, the values on the axis are displayed from high to low instead of the default low to high.
        
        Args:
            value (bool): True to display values in reverse order, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsMaxCross(self)->bool:
        """Gets whether the category axis crosses at the maximum value.
        
        When true, the category axis crosses the value axis at the maximum value.
        When false, the category axis crosses at the minimum value or at a custom position.
        
        Example::

            #Create worksheet
            workbook = Workbook()
            workbook.LoadFromFile("Sample.xlsx")
            worksheet = workbook.Worksheets[0]
            #Create chart
            chart = worksheet.Charts.Add()
            chart.DataRange = worksheet.Range["A1:C2"]
            #Set chart value axis
            valueAxis = chart.PrimaryValueAxis
            #Get IsMaxCross
            print(valueAxis.IsMaxCross)
            #Save to file
            workbook.SaveToFile("Chart.xlsx")

        Returns:
            bool: True if the category axis crosses at the maximum value, otherwise False.
        """
        pass


