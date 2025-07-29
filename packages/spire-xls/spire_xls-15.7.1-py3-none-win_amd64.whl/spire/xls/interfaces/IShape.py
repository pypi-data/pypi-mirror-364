from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.xls.common import *
from spire.xls import *
from ctypes import *
import abc

class IShape (  IExcelApplication) :
    """Base shape interface for Excel elements.
    
    This interface represents a shape object in an Excel worksheet, providing
    properties and methods to manipulate the appearance, position, size, and behavior
    of various types of shapes including rectangles, ovals, lines, pictures, charts,
    and other drawing objects.
    
    Inherits from:
        IExcelApplication: Excel application interface
    """
    @property
    @abc.abstractmethod
    def Height(self)->int:
        """Gets the height of the shape in points.
        
        This property returns the height of the shape in points (1/72 inch).
        
        Returns:
            int: The height of the shape in points.
        """
        pass


    @Height.setter
    @abc.abstractmethod
    def Height(self, value:int):
        """Sets the height of the shape in points.
        
        This property sets the height of the shape in points (1/72 inch).
        
        Args:
            value (int): The height of the shape in points.
        """
        pass


    @property
    @abc.abstractmethod
    def ID(self)->int:
        """Gets the unique identifier of the shape.
        
        This property returns an integer that uniquely identifies the shape
        within the worksheet.
        
        Returns:
            int: The unique identifier of the shape.
        """
        pass


    @property
    @abc.abstractmethod
    def Left(self)->int:
        """Gets the position of the left edge of the shape in points.
        
        This property returns the distance in points from the left edge of the
        worksheet to the left edge of the shape.
        
        Returns:
            int: The position of the left edge in points.
        """
        pass


    @Left.setter
    @abc.abstractmethod
    def Left(self, value:int):
        """Sets the position of the left edge of the shape in points.
        
        This property sets the distance in points from the left edge of the
        worksheet to the left edge of the shape.
        
        Args:
            value (int): The position of the left edge in points.
        """
        pass


    @property
    @abc.abstractmethod
    def Name(self)->str:
        """Gets the name of the shape.
        
        This property returns the name assigned to the shape, which can be used
        to identify and reference the shape programmatically.
        
        Returns:
            str: The name of the shape.
        """
        pass


    @Name.setter
    @abc.abstractmethod
    def Name(self, value:str):
        """Sets the name of the shape.
        
        This property sets the name assigned to the shape, which can be used
        to identify and reference the shape programmatically.
        
        Args:
            value (str): The name to assign to the shape.
        """
        pass


    @property
    @abc.abstractmethod
    def Top(self)->int:
        """Gets the position of the top edge of the shape in points.
        
        This property returns the distance in points from the top edge of the
        worksheet to the top edge of the shape.
        
        Returns:
            int: The position of the top edge in points.
        """
        pass


    @Top.setter
    @abc.abstractmethod
    def Top(self, value:int):
        """Sets the position of the top edge of the shape in points.
        
        This property sets the distance in points from the top edge of the
        worksheet to the top edge of the shape.
        
        Args:
            value (int): The position of the top edge in points.
        """
        pass


    @property
    @abc.abstractmethod
    def Width(self)->int:
        """Gets the width of the shape in points.
        
        This property returns the width of the shape in points (1/72 inch).
        
        Returns:
            int: The width of the shape in points.
        """
        pass


    @Width.setter
    @abc.abstractmethod
    def Width(self, value:int):
        """Sets the width of the shape in points.
        
        This property sets the width of the shape in points (1/72 inch).
        
        Args:
            value (int): The width of the shape in points.
        """
        pass


    @property
    @abc.abstractmethod
    def HtmlString(self)->str:
        """Gets the HTML representation of the shape's content.
        
        This property returns an HTML string that contains the data and formatting
        information for the shape's content. This can be useful for extracting
        formatted text or other content from the shape.
        
        Returns:
            str: An HTML string representing the shape's content.
        """
        pass


    @HtmlString.setter
    @abc.abstractmethod
    def HtmlString(self, value:str):
        """Sets the HTML representation of the shape's content.
        
        This property sets the content of the shape using an HTML string,
        allowing for formatted text and other HTML content to be inserted
        into the shape.
        
        Args:
            value (str): An HTML string representing the shape's content.
        """
        pass


    @property
    @abc.abstractmethod
    def ShapeType(self)->'ExcelShapeType':
        """Gets the type of the shape.
        
        This property returns an enumeration value indicating the type of shape,
        such as rectangle, oval, line, picture, chart, etc.
        
        Returns:
            ExcelShapeType: An enumeration value representing the shape type.
        """
        pass


    @property
    @abc.abstractmethod
    def Visible(self)->bool:
        """Gets whether the shape is visible.
        
        When true, the shape is visible in the worksheet.
        When false, the shape is hidden but still exists in the worksheet.
        
        Returns:
            bool: True if the shape is visible, otherwise False.
        """
        pass


    @Visible.setter
    @abc.abstractmethod
    def Visible(self, value:bool):
        """Sets whether the shape is visible.
        
        When set to true, the shape will be visible in the worksheet.
        When set to false, the shape will be hidden but still exists in the worksheet.
        
        Args:
            value (bool): True to make the shape visible, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def AlternativeText(self)->str:
        """Gets the alternative text associated with the shape.
        
        Alternative text (alt text) is descriptive text that explains the content
        and function of a shape for accessibility purposes, particularly for users
        with visual impairments.
        
        Returns:
            str: The alternative text of the shape.
        """
        pass


    @AlternativeText.setter
    @abc.abstractmethod
    def AlternativeText(self, value:str):
        """Sets the alternative text associated with the shape.
        
        Alternative text (alt text) is descriptive text that explains the content
        and function of a shape for accessibility purposes, particularly for users
        with visual impairments.
        
        Args:
            value (str): The alternative text to assign to the shape.
        """
        pass


    @property
    @abc.abstractmethod
    def Fill(self)->'IShapeFill':
        """Gets the fill formatting of the shape.
        
        This property returns an interface that provides access to fill formatting properties
        such as color, pattern, gradient, and transparency for the interior of the shape.
        
        Returns:
            IShapeFill: An interface for accessing and modifying the fill formatting.
        """
        pass


    @property
    @abc.abstractmethod
    def Line(self)->'IShapeLineFormat':
        """Gets the line formatting of the shape.
        
        This property returns an interface that provides access to line formatting properties
        such as color, style, weight, and transparency for the outline of the shape.
        
        Returns:
            IShapeLineFormat: An interface for accessing and modifying the line formatting.
        """
        pass


    @property
    @abc.abstractmethod
    def OnAction(self)->str:
        """Gets the macro name assigned to the shape.
        
        This property returns the name of the macro that is executed when the shape is clicked.
        The macro can be VBA code or other script associated with the shape as an action.
        
        Returns:
            str: The macro name assigned to the shape.
        """
        pass


    @OnAction.setter
    @abc.abstractmethod
    def OnAction(self, value:str):
        """Sets the macro name assigned to the shape.
        
        This property sets the name of the macro that will be executed when the shape is clicked.
        The macro can be VBA code or other script associated with the shape as an action.
        
        Args:
            value (str): The macro name to assign to the shape.
        """
        pass


    @property
    @abc.abstractmethod
    def Shadow(self)->'IShadow':
        """Gets the shadow formatting of the shape.
        
        This property returns an interface that provides access to shadow formatting properties
        such as type, color, transparency, size, blur, angle, and distance.
        
        Returns:
            IShadow: An interface for accessing and modifying the shadow formatting.
        """
        pass


    @property
    @abc.abstractmethod
    def ThreeD(self)->'IFormat3D':
        """Gets the 3D formatting of the shape.
        
        This property returns an interface that provides access to three-dimensional formatting
        properties such as depth, contour, surface, lighting, and rotation for the shape.
        
        Returns:
            IFormat3D: An interface for accessing and modifying the 3D formatting.
        """
        pass


    @property
    @abc.abstractmethod
    def Glow(self)->'IGlow':
        """Gets the glow effect formatting of the shape.
        
        This property returns an interface that provides access to glow effect properties
        such as color, size, and transparency for the shape.
        
        Returns:
            IGlow: An interface for accessing and modifying the glow effect formatting.
        """
        pass


    @property
    @abc.abstractmethod
    def Reflection(self)->'IReflectionEffect':
        """Gets the reflection effect formatting of the shape.
        
        This property returns an interface that provides access to reflection effect properties
        such as transparency, size, distance, and blur for the shape.
        
        Returns:
            IReflectionEffect: An interface for accessing and modifying the reflection effect formatting.
        """
        pass


    @property
    @abc.abstractmethod
    def Rotation(self)->int:
        """Gets the rotation angle of the shape in degrees.
        
        This property returns the rotation angle of the shape in degrees,
        where 0 represents no rotation and positive values represent clockwise rotation.
        
        Returns:
            int: The rotation angle in degrees.
        """
        pass


    @Rotation.setter
    @abc.abstractmethod
    def Rotation(self, value:int):
        """Sets the rotation angle of the shape in degrees.
        
        This property sets the rotation angle of the shape in degrees,
        where 0 represents no rotation and positive values represent clockwise rotation.
        
        Args:
            value (int): The rotation angle in degrees.
        """
        pass


    @property
    @abc.abstractmethod
    def ResizeBehave(self)->'ResizeBehaveType':
        """Gets how the shape behaves when rows/columns are resized.
        
        This property returns an enumeration value that specifies how the shape should 
        be resized or repositioned when the rows and columns between its anchors are 
        resized or when rows/columns are inserted.
        
        Note: For ComboBoxShape, CheckBoxShape, and RadioButtonShape, setting the value
        to MoveAndResize is not valid.
        
        Returns:
            ResizeBehaveType: An enumeration value representing the resize behavior.
        """
        pass


    @ResizeBehave.setter
    @abc.abstractmethod
    def ResizeBehave(self, value:'ResizeBehaveType'):
        """Sets how the shape behaves when rows/columns are resized.
        
        This property sets an enumeration value that specifies how the shape should 
        be resized or repositioned when the rows and columns between its anchors are 
        resized or when rows/columns are inserted.
        
        Note: For ComboBoxShape, CheckBoxShape, and RadioButtonShape, setting the value
        to MoveAndResize is not valid.
        
        Args:
            value (ResizeBehaveType): An enumeration value representing the resize behavior.
        """
        pass


    @property
    @abc.abstractmethod
    def IsLocked(self)->bool:
        """Gets whether the shape is locked.
        
        When true, the shape is locked and cannot be modified when the worksheet
        is protected. When false, the shape can be modified even when the worksheet
        is protected.
        
        Returns:
            bool: True if the shape is locked, otherwise False.
        """
        pass


    @IsLocked.setter
    @abc.abstractmethod
    def IsLocked(self, value:bool):
        """Sets whether the shape is locked.
        
        When set to true, the shape will be locked and cannot be modified when the
        worksheet is protected. When set to false, the shape can be modified even when
        the worksheet is protected.
        
        Args:
            value (bool): True to lock the shape, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsPrintable(self)->bool:
        """Gets whether the shape is printed when the worksheet is printed.
        
        When true, the shape will be included when the worksheet is printed.
        When false, the shape will not be included in the printed output.
        
        Returns:
            bool: True if the shape is printable, otherwise False.
        """
        pass


    @IsPrintable.setter
    @abc.abstractmethod
    def IsPrintable(self, value:bool):
        """Sets whether the shape is printed when the worksheet is printed.
        
        When set to true, the shape will be included when the worksheet is printed.
        When set to false, the shape will not be included in the printed output.
        
        Args:
            value (bool): True to make the shape printable, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsLockAspectRatio(self)->bool:
        """Gets whether the aspect ratio of the shape is locked.
        
        When true, the shape's width and height dimensions are locked into their
        current aspect ratio. When false, the width and height can be changed
        independently of each other.
        
        Returns:
            bool: True if the aspect ratio is locked, otherwise False.
        """
        pass


    @IsLockAspectRatio.setter
    @abc.abstractmethod
    def IsLockAspectRatio(self, value:bool):
        """Sets whether the aspect ratio of the shape is locked.
        
        When set to true, the shape's width and height dimensions will be locked into their
        current aspect ratio. When set to false, the width and height can be changed
        independently of each other.
        
        Args:
            value (bool): True to lock the aspect ratio, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def IsSmartArt(self)->bool:
        """Gets whether the shape is a SmartArt graphic.
        
        SmartArt graphics are pre-designed diagrams that can be used to visually
        communicate information. This property returns true if the shape is a SmartArt
        graphic, and false otherwise.
        
        Returns:
            bool: True if the shape is a SmartArt graphic, otherwise False.
        """
        pass


    @property
    @abc.abstractmethod
    def TextFrame(self)->'ITextFrame':
        """Gets the text frame of the shape.
        
        This property returns an interface that provides access to the text formatting
        and content within the shape. Text frames allow for formatted text to be displayed
        within a shape.
        
        Returns:
            ITextFrame: An interface for accessing and modifying the text frame.
        """
        pass


    @property
    @abc.abstractmethod
    def LinkedCell(self)->'IXLSRange':
        """Gets the cell range linked to the shape's value.
        
        This property returns the cell range that is linked to the shape's value.
        When the value in the linked cell changes, the shape may update accordingly,
        depending on the type of shape.
        
        Returns:
            IXLSRange: The cell range linked to the shape's value.
        """
        pass


    @LinkedCell.setter
    @abc.abstractmethod
    def LinkedCell(self, value:'IXLSRange'):
        """Sets the cell range linked to the shape's value.
        
        This property sets the cell range that is linked to the shape's value.
        When the value in the linked cell changes, the shape may update accordingly,
        depending on the type of shape.
        
        Args:
            value (IXLSRange): The cell range to link to the shape's value.
        """
        pass


    @abc.abstractmethod
    def Remove(self):
        """Removes the shape from the worksheet.
        
        This method permanently removes the shape from the worksheet. After calling
        this method, any references to the shape object should not be used.
        """
        pass


    @abc.abstractmethod
    def Scale(self, scaleWidth:int, scaleHeight:int):
        """Scales the shape by the specified percentages.
        
        This method scales the width and height of the shape by the specified percentages.
        For example, specifying 200 for scaleWidth and 100 for scaleHeight would double
        the width while keeping the height unchanged.
        
        Args:
            scaleWidth (int): The percentage to scale the width (100 = no change).
            scaleHeight (int): The percentage to scale the height (100 = no change).
        """
        pass


