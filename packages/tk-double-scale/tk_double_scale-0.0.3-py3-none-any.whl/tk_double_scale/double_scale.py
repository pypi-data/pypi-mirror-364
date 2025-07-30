import colorsys
import PIL.ImageColor as ImageColor
import tkinter as tk
import tkinter.font as tkfont
from dataclasses import dataclass


@dataclass
class BoxColors:
    """Holds a base color and computes variants for outlines."""
    base_color: str
    light_factor: float = 1.5
    dark_factor: float = 0.5
    outset: bool = False

    def __post_init__(self):
        self.down = self.adjust_color(self.base_color, self.light_factor)
        self.up = self.adjust_color(self.base_color, self.dark_factor)
        if self.outset:
            self.up, self.down = self.down, self.up

    @staticmethod
    def adjust_color(color_name, factor):
        """
        Adjusts the lightness of the given color by the specified factor.
        Returns a hex color string.
        """
        r, g, b = ImageColor.getrgb(color_name)
        r, g, b = (r / 255, g / 255, b / 255)
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        l = max(0, min(1, l * factor))
        r, g, b = (int(c * 255) for c in colorsys.hls_to_rgb(h, l, s))
        return f'#{r:02x}{g:02x}{b:02x}'


@dataclass
class Cursor:
    width: int
    height: int
    value: float
    y1: int
    y2: int
    text_y: int
    
    def __post_init__(self):
        self.half_width = self.width / 2

    def get_box_coordinates(self, x):
        return [x - self.half_width, self.y1, x + self.half_width, self.y2]


@dataclass
class DoubleScale(tk.Canvas): 
    master: tk.Widget
    from_: float = 0        # value min
    to: float = 100         # value max
    length: int = 100       # widget length and thickness in pixels
    thickness: int = 15
    cursor_width: int = 10
    decimals: int = 0       # number of decimals
    bg_color: str = '#bbb'
    cursor_color: str = '#eee'
    text_color: str = 'black'
    font: str = None
    
    def __post_init__(self):
        # Ensure decimals are positive
        self.decimals = abs(self.decimals)

        # Ensure font is a Font object
        self.font = tkfont.Font(font=self.font)

        # Measure text width and calculate offsets
        text_width = self.font.measure(self.to)
        self.offset_x = max(10, text_width / 2 - self.cursor_width / 2)
        self.linespace = self.font.metrics('linespace')

        # Calculate dimensions for the Canvas
        width = self.offset_x * 2 + self.length + self.cursor_width
        height = self.linespace * 1.8 + self.thickness
        super().__init__(self.master, width=width, height=height)

        # Calculate additional offsets and coefficients
        self.inside_offset = self.cursor_width / 2 + 1
        self.cursor_y_delimiter = self.linespace + (self.thickness / 2)
        self.coeff = self.length / (self.to - self.from_)

        # Define cursor dimensions
        cursor_height = (self.thickness - 3) / 2
        text_y = self.font.metrics('ascent') / 2

        # Create cursor objects
        self.cursor_a = Cursor(
            self.cursor_width, 
            cursor_height, 
            value=self.from_, 
            y1=self.linespace + 1, 
            y2=self.cursor_y_delimiter - 1,
            text_y=text_y
        )

        self.cursor_b = Cursor(
            self.cursor_width, 
            cursor_height, 
            value=self.to, 
            y1=self.cursor_y_delimiter, 
            y2=self.linespace + self.thickness - 1,
            text_y=self.linespace + self.thickness + text_y
        )

        # Adjust colors for outlines
        bg_colors = BoxColors(self.bg_color)
        self.cursor_colors = BoxColors(self.cursor_color, outset=True)
        
        # Draw the background
        xb = self.offset_x + self.length + (self.inside_offset * 2)
        yb = self.linespace + self.thickness
        self.draw_3d_box(self.offset_x, self.linespace, xb, yb, bg_colors, 
                         tags='background')

        self.redraw()
        
        # Bind mouse events
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
    
    def get_values(self, return_type=float):
        if not callable(return_type):
            raise ValueError("return_type must be a callable (int, float, ...)")
        
        return [return_type(self.cursor_a.value), 
                return_type(self.cursor_b.value)]
    
    def set_values(self, a, b):
        self.cursor_a.value = self.validate(a)
        self.cursor_b.value = self.validate(b)
        self.redraw()
    
    def validate(self, value):
        """
        Clamp the value between from_ and to, then round according to decimals.
        """
        return round(min(self.to, max(self.from_, value)), self.decimals)

    def value_to_position(self, value):
        """Convert a value to its corresponding position on the scale."""
        return ((value - self.from_) * self.coeff + self.offset_x 
                + self.inside_offset)
    
    def position_to_value(self, position):
        """Convert a position on the scale back to a value."""
        return ((position - self.offset_x - self.inside_offset) / self.coeff 
                + self.from_)
    
    def pos_to_value_rounded(self, position):
        """Convert a position on the scale back to a value, rounded."""
        return self.validate(self.position_to_value(position))
    
    def on_click(self, event):
        """Determine which cursor is being dragged."""
        self.dragged_cursor = None
        
        # Calculate cursor positions
        xa = self.value_to_position(self.cursor_a.value)
        xb = self.value_to_position(self.cursor_b.value)

        # Check if both cursors are at the same position
        if self.cursor_a.value == self.cursor_b.value:
            # Determine which cursor to drag based on their values
            if self.cursor_a.value == self.from_:
                self.dragged_cursor = self.cursor_b
            elif self.cursor_b.value == self.to:
                self.dragged_cursor = self.cursor_a
            elif abs(event.x - xa) < 10:
                # Use y-coordinate to determine which cursor should be moved
                self.dragged_cursor = (self.cursor_a 
                                       if event.y < self.cursor_y_delimiter 
                                       else self.cursor_b)

        # Check if the click is near cursor A
        elif abs(event.x - xa) < 10:
            self.dragged_cursor = self.cursor_a

        # Check if the click is near cursor B
        elif abs(event.x - xb) < 10:
            self.dragged_cursor = self.cursor_b
    
    def on_drag(self, event):
        """Update the value based on the cursor position, and redraw the cursors."""
        if not self.dragged_cursor:
            return

        new_value = self.pos_to_value_rounded(event.x)
        if self.dragged_cursor == self.cursor_a:
            self.cursor_a.value = max(self.from_, 
                                      min(new_value, self.cursor_b.value))
        else:  # Assuming self.dragged_cursor == self.cursor_b
            self.cursor_b.value = min(self.to, 
                                      max(new_value, self.cursor_a.value))

        self.redraw()
    
    def redraw(self):
        """Redraw the cursors."""
        self.delete('cursor')
        self.draw_cursor(self.cursor_a)
        self.draw_cursor(self.cursor_b)
    
    def draw_cursor(self, cursor):
        """Draw the cursor."""
        x = self.value_to_position(cursor.value)
        coords = cursor.get_box_coordinates(x)
        
        self.draw_3d_box(*coords, self.cursor_colors, tags='cursor')
        
        display_value = f'{cursor.value:.{self.decimals}f}'
        self.create_text(x, cursor.text_y, text=display_value, tags='cursor', 
                         font=self.font, fill=self.text_color)

    def draw_3d_box(self, xa, ya, xb, yb, colors, tags):
        """Draw a 3D effect box."""
        self.create_rectangle(xa, ya, xb, yb, fill=colors.base_color, width=0, 
                              tags=tags)
        self.create_line(xa, ya, xb, ya, fill=colors.up, tags=tags)
        self.create_line(xa, ya, xa, yb, fill=colors.up, tags=tags)
        self.create_line(xa, yb, xb, yb, fill=colors.down, tags=tags)
        self.create_line(xb, ya, xb, yb, fill=colors.down, tags=tags)
