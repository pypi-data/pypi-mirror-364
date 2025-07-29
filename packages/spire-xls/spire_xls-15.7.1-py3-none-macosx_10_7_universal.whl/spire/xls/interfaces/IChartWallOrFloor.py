from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IChartWallOrFloor (  IChartFillBorder) :
    """Chart wall or floor interface.
    
    This interface represents the walls or floor of a 3D chart in Excel.
    Chart walls are the back and side surfaces of a 3D chart, while the floor
    is the bottom surface. The interface provides functionality for formatting
    these surfaces, including border properties.
    
    Inherits from:
        IChartFillBorder: Chart fill and border interface
    """
    @property

    @abc.abstractmethod
    def Border(self)->'ChartBorder':
        """Gets the border formatting for the chart wall or floor.
        
        Returns:
            ChartBorder: The border formatting object.
        """
        pass


    @abc.abstractmethod
    def Delete(self):
        """Deletes the chart wall or floor.
        
        This method removes the wall or floor from the chart.
        """
        pass


