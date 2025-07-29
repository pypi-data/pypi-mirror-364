from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class GradientVariantsType(Enum):
    """
    Represents shape shading variants.

    """
    ShadingVariants1 = 1
    ShadingVariants2 = 2
    ShadingVariants3 = 3
    ShadingVariants4 = 4

