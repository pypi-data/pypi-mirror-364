from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class FileFormat(Enum):
    """Represents possible Excel file formats and versions.
    
    This enum defines the various file formats that can be used when working with
    Excel files, including different Excel versions and other export formats like
    PDF, HTML, etc.
    
    Attributes:
        Xlsb2007: Excel Binary Format for Excel 2007.
        Xlsb2010: Excel Binary Format for Excel 2010.
        ODS: OpenDocument Spreadsheet format.
        CSV: Comma-Separated Values format.
        XML: XML Spreadsheet format.
        PDF: Portable Document Format.
        Bitmap: Bitmap image format.
        XPS: XML Paper Specification format.
        HTML: HyperText Markup Language format.
        Version97to2003: Excel 97-2003 format (.xls).
        Version2007: Excel 2007 format (.xlsx).
        Version2010: Excel 2010 format (.xlsx).
        Version2013: Excel 2013 format (.xlsx).
        Version2016: Excel 2016 format (.xlsx).
        PostScript: PostScript document format.
        OFD: Open Fixed-layout Document format.
        PCL: Printer Command Language format.
        Xlsm: Excel Macro-Enabled Workbook format.
        ET: WPS Spreadsheet format.
        ETT: WPS Spreadsheet Template format.
        UOS: Unified Office Format Spreadsheet.
        XLT: Excel Template format.
        XLTX: Excel Template format (XML-based).
        XLTM: Excel Macro-Enabled Template format.
        Markdown: Markdown text format.
    """
    Xlsb2007 = 0
    Xlsb2010 = 1
    ODS = 2
    CSV = 3
    XML = 4
    PDF = 5
    Bitmap = 6
    XPS = 7
    HTML = 8
    Version97to2003 = 9
    Version2007 = 10
    Version2010 = 11
    Version2013 = 12
    Version2016 = 13
    PostScript = 14
    OFD = 15
    PCL = 16
    Xlsm = 17
    ET = 18
    ETT = 19
    UOS = 20
    XLT = 21
    XLTX = 22
    XLTM = 23
    Markdown = 24

