from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IgnoreErrorType(Enum):
    """
    Represents flags of excel ignore error indicator.

    """
    none = 0
    EvaluateToError = 1
    EmptyCellReferences = 2
    NumberAsText = 4
    OmittedCells = 8
    InconsistentFormula = 16
    TextDate = 32
    UnlockedFormulaCells = 64
    All = 127

