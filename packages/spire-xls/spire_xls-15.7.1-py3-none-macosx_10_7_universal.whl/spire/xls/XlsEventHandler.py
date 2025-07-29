from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class XlsEventHandler (SpireObject) :
    """Represents an event handler for Excel events.
    
    This class provides functionality for handling events in Excel, such as property changes,
    worksheet events, and workbook events. It extends SpireObject and can be used to implement
    custom event handling logic.
    """

    def Invoke(self ,sender:'SpireObject',e:'XlsEventArgs'):
        """Invokes the event handler with the specified sender and event arguments.
        
        Args:
            sender (SpireObject): The object that raised the event.
            e (XlsEventArgs): The event arguments containing information about the event.
        """
        intPtrsender:c_void_p = sender.Ptr
        intPtre:c_void_p = e.Ptr

        GetDllLibXls().XlsEventHandler_Invoke.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().XlsEventHandler_Invoke, self.Ptr, intPtrsender,intPtre)

#
#    def BeginInvoke(self ,sender:'SpireObject',e:'XlsEventArgs',callback:'AsyncCallback',object:'SpireObject')->'IAsyncResult':
#        """
#
#        """
#        intPtrsender:c_void_p = sender.Ptr
#        intPtre:c_void_p = e.Ptr
#        intPtrcallback:c_void_p = callback.Ptr
#        intPtrobject:c_void_p = object.Ptr
#
#        GetDllLibXls().XlsEventHandler_BeginInvoke.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_void_p]
#        GetDllLibXls().XlsEventHandler_BeginInvoke.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibXls().XlsEventHandler_BeginInvoke, self.Ptr, intPtrsender,intPtre,intPtrcallback,intPtrobject)
#        ret = None if intPtr==None else IAsyncResult(intPtr)
#        return ret
#


#
#    def EndInvoke(self ,result:'IAsyncResult'):
#        """
#
#        """
#        intPtrresult:c_void_p = result.Ptr
#
#        GetDllLibXls().XlsEventHandler_EndInvoke.argtypes=[c_void_p ,c_void_p]
#        CallCFunction(GetDllLibXls().XlsEventHandler_EndInvoke, self.Ptr, intPtrresult)


