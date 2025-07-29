from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class ICloneParent (abc.ABC) :
    """
    Supports cloning, which creates a new instance of a class with the same value as an existing instance.

    """

    @abc.abstractmethod
    def Clone(self ,parent:'SpireObject')->'SpireObject':
        """
        Creates a new object that is a copy of the current instance.

        Args:
            parent: Parent object for a copy of this instance.

        Returns:
            A new object that is a copy of this instance.

        """
        pass


