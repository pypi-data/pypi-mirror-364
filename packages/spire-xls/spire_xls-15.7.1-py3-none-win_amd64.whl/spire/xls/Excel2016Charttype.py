from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class Excel2016Charttype(Enum):
    """Represents the chart types introduced in Excel 2016.
    
    This enumeration defines the various chart types that were added in Excel 2016,
    including specialized visualization types such as funnel charts, box and whisker plots,
    waterfall charts, and treemaps.
    
    Attributes:
        funnel: A funnel chart that shows values across multiple stages in a process.
        boxWhisker: A box and whisker plot that shows distribution of data sets.
        clusteredColumn: A clustered column chart that compares values across categories.
        paretoLine: A Pareto chart that combines columns and a line to show cumulative total.
        sunburst: A sunburst chart that shows hierarchical data as concentric rings.
        treemap: A treemap chart that shows hierarchical data as nested rectangles.
        waterfall: A waterfall chart that shows how an initial value is affected by positive and negative values.
    """
    funnel = 74
    boxWhisker = 76
    clusteredColumn = 77
    paretoLine = 78
    sunburst = 80
    treemap = 79
    waterfall = 75

