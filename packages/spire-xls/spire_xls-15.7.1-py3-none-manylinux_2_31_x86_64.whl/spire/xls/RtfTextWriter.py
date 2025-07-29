from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class RtfTextWriter (SpireObject) :
    """Provides functionality for writing Rich Text Format (RTF) content.
    
    This class encapsulates methods for creating and manipulating RTF documents,
    including text formatting, font management, color management, and other RTF features.
    It is used internally by Excel components that need to generate RTF content.
    """

    def ToString(self)->str:
        """Converts the RTF content to a string representation.
        
        Returns:
            str: The RTF content as a string.
        """
        GetDllLibXls().RtfTextWriter_ToString.argtypes=[c_void_p]
        GetDllLibXls().RtfTextWriter_ToString.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibXls().RtfTextWriter_ToString, self.Ptr))
        return ret


    @dispatch

    def Write(self ,value:bool):
        """

        """
        
        GetDllLibXls().RtfTextWriter_Write.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibXls().RtfTextWriter_Write, self.Ptr, value)

    @dispatch

    def Write(self ,value:int):
        """

        """
        
        GetDllLibXls().RtfTextWriter_WriteV.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteV, self.Ptr, value)

#    @dispatch
#
#    def Write(self ,buffer:'Char[]'):
#        """
#
#        """
#        #arraybuffer:ArrayTypebuffer = ""
#        countbuffer = len(buffer)
#        ArrayTypebuffer = c_void_p * countbuffer
#        arraybuffer = ArrayTypebuffer()
#        for i in range(0, countbuffer):
#            arraybuffer[i] = buffer[i].Ptr
#
#
#        GetDllLibXls().RtfTextWriter_WriteB.argtypes=[c_void_p ,ArrayTypebuffer]
#        CallCFunction(GetDllLibXls().RtfTextWriter_WriteB, self.Ptr, arraybuffer)


    @dispatch

    def Write(self ,value:float):
        """

        """
        
        GetDllLibXls().RtfTextWriter_WriteV1.argtypes=[c_void_p ,c_double]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteV1, self.Ptr, value)

    @dispatch

    def Write(self ,value:int):
        """

        """
        
        GetDllLibXls().RtfTextWriter_WriteV11.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteV11, self.Ptr, value)

    @dispatch

    def Write(self ,value:int):
        """

        """
        
        GetDllLibXls().RtfTextWriter_WriteV111.argtypes=[c_void_p ,c_long]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteV111, self.Ptr, value)

    @dispatch

    def Write(self ,value:SpireObject):
        """

        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibXls().RtfTextWriter_WriteV1111.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteV1111, self.Ptr, intPtrvalue)

    @dispatch

    def Write(self ,value:float):
        """

        """
        
        GetDllLibXls().RtfTextWriter_WriteV11111.argtypes=[c_void_p ,c_float]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteV11111, self.Ptr, value)

    @dispatch

    def Write(self ,s:str):
        """

        """
        
        GetDllLibXls().RtfTextWriter_WriteS.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteS, self.Ptr, s)

    @dispatch

    def Write(self ,value:UInt32):
        """

        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibXls().RtfTextWriter_WriteV111111.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteV111111, self.Ptr, intPtrvalue)

    @dispatch

    def Write(self ,format:str,arg0:SpireObject):
        """

        """
        intPtrarg0:c_void_p = arg0.Ptr

        GetDllLibXls().RtfTextWriter_WriteFA.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteFA, self.Ptr, format,intPtrarg0)

    @dispatch

    def Write(self ,format:str,arg:List[SpireObject]):
        """

        """
        #arrayarg:ArrayTypearg = ""
        countarg = len(arg)
        ArrayTypearg = c_void_p * countarg
        arrayarg = ArrayTypearg()
        for i in range(0, countarg):
            arrayarg[i] = arg[i].Ptr


        GetDllLibXls().RtfTextWriter_WriteFA1.argtypes=[c_void_p ,c_void_p,ArrayTypearg,c_int]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteFA1, self.Ptr, format,arrayarg,countarg)

    @dispatch

    def Write(self ,format:str,arg0:SpireObject,arg1:SpireObject):
        """

        """
        intPtrarg0:c_void_p = arg0.Ptr
        intPtrarg1:c_void_p = arg1.Ptr

        GetDllLibXls().RtfTextWriter_WriteFAA.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteFAA, self.Ptr, format,intPtrarg0,intPtrarg1)

#    @dispatch
#
#    def Write(self ,buffer:'Char[]',index:int,count:int):
#        """
#
#        """
#        #arraybuffer:ArrayTypebuffer = ""
#        countbuffer = len(buffer)
#        ArrayTypebuffer = c_void_p * countbuffer
#        arraybuffer = ArrayTypebuffer()
#        for i in range(0, countbuffer):
#            arraybuffer[i] = buffer[i].Ptr
#
#
#        GetDllLibXls().RtfTextWriter_WriteBIC.argtypes=[c_void_p ,ArrayTypebuffer,c_int,c_int]
#        CallCFunction(GetDllLibXls().RtfTextWriter_WriteBIC, self.Ptr, arraybuffer,index,count)


    @dispatch
    def WriteLine(self):
        """

        """
        GetDllLibXls().RtfTextWriter_WriteLine.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteLine, self.Ptr)

    @dispatch

    def WriteLine(self ,value:bool):
        """

        """
        
        GetDllLibXls().RtfTextWriter_WriteLineV.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteLineV, self.Ptr, value)

    @dispatch

    def WriteLine(self ,value:int):
        """

        """
        
        GetDllLibXls().RtfTextWriter_WriteLineV1.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteLineV1, self.Ptr, value)

#    @dispatch
#
#    def WriteLine(self ,buffer:'Char[]'):
#        """
#
#        """
#        #arraybuffer:ArrayTypebuffer = ""
#        countbuffer = len(buffer)
#        ArrayTypebuffer = c_void_p * countbuffer
#        arraybuffer = ArrayTypebuffer()
#        for i in range(0, countbuffer):
#            arraybuffer[i] = buffer[i].Ptr
#
#
#        GetDllLibXls().RtfTextWriter_WriteLineB.argtypes=[c_void_p ,ArrayTypebuffer]
#        CallCFunction(GetDllLibXls().RtfTextWriter_WriteLineB, self.Ptr, arraybuffer)


    @dispatch

    def WriteLine(self ,value:float):
        """

        """
        
        GetDllLibXls().RtfTextWriter_WriteLineV11.argtypes=[c_void_p ,c_double]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteLineV11, self.Ptr, value)

    @dispatch

    def WriteLine(self ,value:int):
        """

        """
        
        GetDllLibXls().RtfTextWriter_WriteLineV111.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteLineV111, self.Ptr, value)

    @dispatch

    def WriteLine(self ,value:int):
        """

        """
        
        GetDllLibXls().RtfTextWriter_WriteLineV1111.argtypes=[c_void_p ,c_long]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteLineV1111, self.Ptr, value)

    @dispatch

    def WriteLine(self ,value:SpireObject):
        """

        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibXls().RtfTextWriter_WriteLineV11111.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteLineV11111, self.Ptr, intPtrvalue)

    @dispatch

    def WriteLine(self ,value:float):
        """

        """
        
        GetDllLibXls().RtfTextWriter_WriteLineV111111.argtypes=[c_void_p ,c_float]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteLineV111111, self.Ptr, value)

    @dispatch

    def WriteLine(self ,s:str):
        """

        """
        
        GetDllLibXls().RtfTextWriter_WriteLineS.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteLineS, self.Ptr, s)

    @dispatch

    def WriteLine(self ,value:UInt32):
        """

        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibXls().RtfTextWriter_WriteLineV1111111.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteLineV1111111, self.Ptr, intPtrvalue)

    @dispatch

    def WriteLine(self ,format:str,arg:List[SpireObject]):
        """

        """
        #arrayarg:ArrayTypearg = ""
        countarg = len(arg)
        ArrayTypearg = c_void_p * countarg
        arrayarg = ArrayTypearg()
        for i in range(0, countarg):
            arrayarg[i] = arg[i].Ptr


        GetDllLibXls().RtfTextWriter_WriteLineFA.argtypes=[c_void_p ,c_void_p,ArrayTypearg,c_int]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteLineFA, self.Ptr, format,arrayarg,countarg)

    @dispatch

    def WriteLine(self ,format:str,arg0:SpireObject):
        """

        """
        intPtrarg0:c_void_p = arg0.Ptr

        GetDllLibXls().RtfTextWriter_WriteLineFA1.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteLineFA1, self.Ptr, format,intPtrarg0)

    @dispatch

    def WriteLine(self ,format:str,arg0:SpireObject,arg1:SpireObject):
        """

        """
        intPtrarg0:c_void_p = arg0.Ptr
        intPtrarg1:c_void_p = arg1.Ptr

        GetDllLibXls().RtfTextWriter_WriteLineFAA.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteLineFAA, self.Ptr, format,intPtrarg0,intPtrarg1)

#    @dispatch
#
#    def WriteLine(self ,buffer:'Char[]',index:int,count:int):
#        """
#
#        """
#        #arraybuffer:ArrayTypebuffer = ""
#        countbuffer = len(buffer)
#        ArrayTypebuffer = c_void_p * countbuffer
#        arraybuffer = ArrayTypebuffer()
#        for i in range(0, countbuffer):
#            arraybuffer[i] = buffer[i].Ptr
#
#
#        GetDllLibXls().RtfTextWriter_WriteLineBIC.argtypes=[c_void_p ,ArrayTypebuffer,c_int,c_int]
#        CallCFunction(GetDllLibXls().RtfTextWriter_WriteLineBIC, self.Ptr, arraybuffer,index,count)



    def AddFont(self ,font:'Font')->int:
        """Adds a font to the RTF document's font table.
        
        This method registers a font in the RTF document's font table,
        making it available for use in text formatting.
        
        Args:
            font (Font): The font to add to the font table.
            
        Returns:
            int: The index of the added font in the font table.
        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RtfTextWriter_AddFont.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().RtfTextWriter_AddFont.restype=c_int
        ret = CallCFunction(GetDllLibXls().RtfTextWriter_AddFont, self.Ptr, intPtrfont)
        return ret


    def AddColor(self ,color:'Color')->int:
        """Adds a color to the RTF document's color table.
        
        This method registers a color in the RTF document's color table,
        making it available for use in text and background formatting.
        
        Args:
            color (Color): The color to add to the color table.
            
        Returns:
            int: The index of the added color in the color table.
        """
        intPtrcolor:c_void_p = color.Ptr

        GetDllLibXls().RtfTextWriter_AddColor.argtypes=[c_void_p ,c_void_p]
        GetDllLibXls().RtfTextWriter_AddColor.restype=c_int
        ret = CallCFunction(GetDllLibXls().RtfTextWriter_AddColor, self.Ptr, intPtrcolor)
        return ret

    def WriteFontTable(self):
        """Writes the font table to the RTF document.
        
        This method outputs the RTF font table header and all registered fonts
        to the RTF document. The font table must be written before any text
        that uses those fonts.
        """
        GetDllLibXls().RtfTextWriter_WriteFontTable.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteFontTable, self.Ptr)

    def WriteColorTable(self):
        """Writes the color table to the RTF document.
        
        This method outputs the RTF color table header and all registered colors
        to the RTF document. The color table must be written before any text
        that uses those colors.
        """
        GetDllLibXls().RtfTextWriter_WriteColorTable.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteColorTable, self.Ptr)

    @dispatch

    def WriteText(self ,font:Font,strText:str):
        """Writes text with the specified font to the RTF document.
        
        Args:
            font (Font): The font to apply to the text.
            strText (str): The text to write.
        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RtfTextWriter_WriteText.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteText, self.Ptr, intPtrfont,strText)

    @dispatch

    def WriteText(self ,font:Font,foreColor:Color,strText:str):
        """Writes text with the specified font and foreground color to the RTF document.
        
        Args:
            font (Font): The font to apply to the text.
            foreColor (Color): The foreground color to apply to the text.
            strText (str): The text to write.
        """
        intPtrfont:c_void_p = font.Ptr
        intPtrforeColor:c_void_p = foreColor.Ptr

        GetDllLibXls().RtfTextWriter_WriteTextFFS.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteTextFFS, self.Ptr, intPtrfont,intPtrforeColor,strText)

    @dispatch

    def WriteText(self ,font:Font,foreColor:Color,backColor:Color,strText:str):
        """Writes text with the specified font, foreground color, and background color to the RTF document.
        
        Args:
            font (Font): The font to apply to the text.
            foreColor (Color): The foreground color to apply to the text.
            backColor (Color): The background color to apply to the text.
            strText (str): The text to write.
        """
        intPtrfont:c_void_p = font.Ptr
        intPtrforeColor:c_void_p = foreColor.Ptr
        intPtrbackColor:c_void_p = backColor.Ptr

        GetDllLibXls().RtfTextWriter_WriteTextFFBS.argtypes=[c_void_p ,c_void_p,c_void_p,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteTextFFBS, self.Ptr, intPtrfont,intPtrforeColor,intPtrbackColor,strText)

    @dispatch

    def WriteText(self ,font:IFont,strText:str):
        """

        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RtfTextWriter_WriteTextFS.argtypes=[c_void_p ,c_void_p,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteTextFS, self.Ptr, intPtrfont,strText)


    def WriteFontAttribute(self ,font:'Font'):
        """

        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RtfTextWriter_WriteFontAttribute.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteFontAttribute, self.Ptr, intPtrfont)

    @dispatch

    def WriteFont(self ,font:Font):
        """

        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RtfTextWriter_WriteFont.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteFont, self.Ptr, intPtrfont)

    @dispatch

    def WriteFont(self ,font:IFont):
        """

        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RtfTextWriter_WriteFontF.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteFontF, self.Ptr, intPtrfont)


    def WriteSubSuperScript(self ,font:'XlsFont'):
        """

        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RtfTextWriter_WriteSubSuperScript.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteSubSuperScript, self.Ptr, intPtrfont)


    def WriteFontItalicBoldStriked(self ,font:'Font'):
        """

        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RtfTextWriter_WriteFontItalicBoldStriked.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteFontItalicBoldStriked, self.Ptr, intPtrfont)


    def WriteUnderline(self ,font:'XlsFont'):
        """

        """
        intPtrfont:c_void_p = font.Ptr

        GetDllLibXls().RtfTextWriter_WriteUnderline.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteUnderline, self.Ptr, intPtrfont)

    @dispatch
    def WriteUnderlineAttribute(self):
        """

        """
        GetDllLibXls().RtfTextWriter_WriteUnderlineAttribute.argtypes=[c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteUnderlineAttribute, self.Ptr)

    @dispatch

    def WriteUnderlineAttribute(self ,style:UnderlineStyle):
        """

        """
        enumstyle:c_int = style.value

        GetDllLibXls().RtfTextWriter_WriteUnderlineAttributeS.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteUnderlineAttributeS, self.Ptr, enumstyle)


    def WriteStrikeThrough(self ,style:'StrikeThroughStyle'):
        """

        """
        enumstyle:c_int = style.value

        GetDllLibXls().RtfTextWriter_WriteStrikeThrough.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteStrikeThrough, self.Ptr, enumstyle)


    def WriteBackColorAttribute(self ,color:'Color'):
        """

        """
        intPtrcolor:c_void_p = color.Ptr

        GetDllLibXls().RtfTextWriter_WriteBackColorAttribute.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteBackColorAttribute, self.Ptr, intPtrcolor)


    def WriteForeColorAttribute(self ,color:'Color'):
        """

        """
        intPtrcolor:c_void_p = color.Ptr

        GetDllLibXls().RtfTextWriter_WriteForeColorAttribute.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteForeColorAttribute, self.Ptr, intPtrcolor)


    def WriteLineNoTabs(self ,s:str):
        """

        """
        
        GetDllLibXls().RtfTextWriter_WriteLineNoTabs.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteLineNoTabs, self.Ptr, s)

    @dispatch

    def WriteTag(self ,tag:RtfTags):
        """

        """
        enumtag:c_int = tag.value

        GetDllLibXls().RtfTextWriter_WriteTag.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteTag, self.Ptr, enumtag)

    @dispatch

    def WriteTag(self ,tag:RtfTags,arrParams:List[SpireObject]):
        """

        """
        enumtag:c_int = tag.value
        #arrayarrParams:ArrayTypearrParams = ""
        countarrParams = len(arrParams)
        ArrayTypearrParams = c_void_p * countarrParams
        arrayarrParams = ArrayTypearrParams()
        for i in range(0, countarrParams):
            arrayarrParams[i] = arrParams[i].Ptr


        GetDllLibXls().RtfTextWriter_WriteTagTA.argtypes=[c_void_p ,c_int,ArrayTypearrParams,c_int]
        CallCFunction(GetDllLibXls().RtfTextWriter_WriteTagTA, self.Ptr, enumtag,arrayarrParams,countarrParams)

    @property
    def Escape(self)->bool:
        """Gets or sets whether special characters should be escaped in the RTF output.
        
        When set to True, special characters like braces, backslashes, etc. will be
        escaped with a backslash in the RTF output.
        
        Returns:
            bool: True if special characters should be escaped; otherwise, False.
        """
        GetDllLibXls().RtfTextWriter_get_Escape.argtypes=[c_void_p]
        GetDllLibXls().RtfTextWriter_get_Escape.restype=c_bool
        ret = CallCFunction(GetDllLibXls().RtfTextWriter_get_Escape, self.Ptr)
        return ret

    @Escape.setter
    def Escape(self, value:bool):
        GetDllLibXls().RtfTextWriter_set_Escape.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibXls().RtfTextWriter_set_Escape, self.Ptr, value)

    @property

    def Encoding(self)->'Encoding':
        """Gets the character encoding used for the RTF document.
        
        Returns:
            Encoding: The character encoding used for the RTF document.
        """
        GetDllLibXls().RtfTextWriter_get_Encoding.argtypes=[c_void_p]
        GetDllLibXls().RtfTextWriter_get_Encoding.restype=c_void_p
        intPtr = CallCFunction(GetDllLibXls().RtfTextWriter_get_Encoding, self.Ptr)
        ret = None if intPtr==None else Encoding(intPtr)
        return ret


