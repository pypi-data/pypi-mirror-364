from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class InsertMoveOption(Enum):
    """
    Specifies how existing cells should be moved when inserting new cells.
    
    This enum defines the direction in which existing cells move when new cells are inserted.
    """
    MoveDown = 0  # Moves existing cells down when inserting new cells
    MoveRight = 1  # Moves existing cells to the right when inserting new cells

