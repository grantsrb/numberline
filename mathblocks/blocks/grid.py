import numpy as np
import math
from mathblocks.blocks.constants import PLAYER, TARG, PILE, ITEM, DIVIDER, BUTTON, OBJECT_TYPES, STAY, UP, RIGHT, DOWN, LEFT, DIRECTIONS, COLORS, EVENTS, STEP, BUTTON, FULL, DEFAULT

"""
The grid class handles the drawing of objects to the image. It enables
setting the pixel density, size of the grid, preventing out of bounds 
erros, and protecting the image info.

Coordinates are recorded as (Row, Col) to keep in line with ndarray
thinking. For instance, the coordinate (1,2) will get drawn one row
down from the top and 3 rows over from the left. Coordinates refer
to grid units, NOT PIXELS.
"""
class Grid:
    def __init__(self,
                 grid_size: int or tuple=(31,31),
                 pixel_density: int=1,
                 divide: bool=True):
        """
        Args:
          grid_size: int or tuple (n_row, n_col)
            the dimensions of the grid. An integer arg creates a square,
            otherwise a tuple creates an n_row X n_col grid.
            Height X Width
          pixel_density: int
            the number of pixels per coordinate. If the argument is
            greater than 1, the coordinate is filled in the upper most
            left corner while leaving one pixel at the lower and
            rightmost boundaries blank.
          divide: bool
            if true, a divider is drawn horizontally across the middle 
            of the grid. If even number of rows, the divder is rounded
            up after dividing the height by two
        """
        self._divided = divide
        if type(grid_size) == int:
            self._grid_size = (grid_size, grid_size)
        else:
            self._grid_size = grid_size
        self._pixel_density = pixel_density
        self._grid = self.make_grid(self._divided)
    
    @property
    def density(self):
        """
        Returns:
          pixel_density: int
            the number of pixels per unit
        """
        return self._pixel_density
    
    @property
    def is_divided(self):
        """
        Returns:
          bool
            true if grid is divided
        """
        return self._divided
    
    @property
    def shape(self):
        """
        Returns the shape of the grid in terms of units
        
        Returns:
          _grid_size: tuple (n_row, n_col)
        """
        return self._grid_size
    
    @property
    def pixel_shape(self):
        """
        Returns the shape of the grid in terms of pixels rather than grid
        units
        
        Returns:
          pixel_shape: tuple (n_row, n_col)
        """
        return self.units2pixels(self.shape)
    
    @property
    def grid(self):
        return self._grid.copy()

    @property
    def middle_row(self):
        """
        Returns the row that is considered the middle row
        """
        return int(self.shape[0]/2)

    def units2pixels(self, coord):
        """
        Converts coordinate units to pixels
        
        Args:
          coord: int or array like (row from top, column from left)
            the coord is the coordinate on the grid in terms of grid
            units if an int is argued, only that converted value is
            returned
        """
        if type(coord) == int or type(coord) == float:
          return int(coord*self.density)
        return (
          int(coord[0]*self.density),
          int(coord[1]*self.density)
        )
    
    def pixels2units(self, pixel_coord):
        """
        Converts a pixel coordinate to the unit coordinate. Rounds down
        to nearest coord
        
        Args:
          pixel_coord: array like (row from top, column from left)
            this is the coordinate on the grid in terms of pixels
        """
        shape = self.shape
        return (
          int(pixel_coord[0]/self.density),
          int(pixel_coord[1]/self.density)
        )
    
    def make_grid(self, do_divide=True):
        """
        Creates the grid to the specified unit dimensions, each unit
        containing a square of pixels with height and width equal to the
        pixel density.
        
        Args:
          do_divide: bool
            if true, a divider is drawn across the middle of the grid.
        Returns:
          grid: ndarry (H,W)
            a numpy array representing the grid
        """
        self._grid = np.zeros(self.pixel_shape).astype(np.float)
        self._grid = self._grid + COLORS[DEFAULT]
        if do_divide:
            self.draw_divider()
        return self._grid
    
    def reset(self):
        """
        Resets the grid to the initial specifications with new
        reference to the grid.
        """
        self._grid = self.make_grid(do_divide=self.is_divided)

    def clear_unit(self, coord):
        """
        Clears a single coordinate in place. More efficient than using
        draw to draw zeros
        
        Args:
          coord: list like (row, col)
        """
        prow,pcol = self.units2pixels(coord)
        self._grid[prow:prow+self.density, pcol:pcol+self.density] = COLORS[DEFAULT]
    
    def clear_playable_space(self):
        """
        Clears the playable space of the grid in place. This means it
        zeros all information above the dividing line. If you want to 
        clear the whole grid in place, use self.clear
        """
        middle = self.units2pixels(self.middle_row)
        self._grid[:middle,:] = COLORS[DEFAULT]
    
    def clear(self, remove_divider=False):
        """
        Clears the whole grid in place.

        Args:
            remove_divider: bool
                if true, the divider is wiped from the grid as well.
                only applies if self.is_divided is true
        """
        self._grid[:,:] = COLORS[DEFAULT]
        if self.is_divided and not remove_divider:
            self.draw_divider()

    def draw(self,
            coord: tuple,
            size: tuple,
            color: float,
            add_color: bool=True):
        """
        This function handles the actual drawing on the grid. The argued
        color is drawn to the specified coordinate. Can add the argued
        color to the existing value or can replace the existing color
        with the argued depending on the value of add_color.

        Args:
          coord: array like of length 2 (row from top, column from left)
            the coord is the coordinate on the grid in terms of grid
            units
          size: tuple (n_rows, n_cols)
            the size of the object being drawn.
          color: float
            the value that should be drawn to the coordinate
          add_color: bool default True
            if true, the argued color is added to the existing value
            rather than replacing it.
        """
        # Coordinates that are off the grid are simply not drawn
        if not self.is_inbounds(coord, size): return
        coord1 = (coord[0]+size[0], coord[1]+size[1])
        self.slice_draw(coord, coord1, color, add_color)

    def slice_draw(self,
                   coord0: tuple,
                   coord1: tuple,
                   color: float,
                   add_color: bool=True):
        """
        Slice draws the color across a range of coordinates. It acts
        much like a numpy slice:

          numpy_array[row0:row1, col0:col1] = color

        Args:
          coord0: list like (row0, col0) (unit values)
          coord1: list like (row1, col1) (unit values) (non-inclusive)
          color: float
          add_color: bool
            if true, the argued color is added to the existing color
            instead of replacing it.
                ndarray[row0:row1, col0:col1] += color
        """
        # Ensure coordinates are appropriate
        coord0 = (max(0, coord0[0]), max(0,coord0[1]))
        coord1 = (
            min(self.shape[0], coord1[0]),
            min(self.shape[1], coord1[1])
        )
        row0,col0 = coord0
        row1,col1 = coord1
        if row0 > row1 or col0 > col1: return
        if row0 == row1:
            row1 += 1
            coord1 = (row1, col1)
        if col0 == col1:
            col1 += 1
            coord1 = (row1, col1)

        pxr0,pxc0 = self.units2pixels(coord0)
        pxr1,pxc1 = self.units2pixels(coord1)
        empty = min(1,self.density-1)
        if add_color:
            self._grid[pxr0:pxr1-empty, pxc0:pxc1-empty] += color
        else:
            self._grid[pxr0:pxr1-empty, pxc0:pxc1-empty] = color

    def draw_divider(self):
        """
        Draws a divider across the middle row of the grid. Rounds up if
        even number of rows in grid.
        """
        middle = self.middle_row
        edge = self.shape[1]
        self.slice_draw(
            (middle, 0),
            (middle, edge),
            color=COLORS[DIVIDER],
            add_color=False
        )

    def row_inbounds(self, row: int, size: int):
        """
        Determines if the argued row is within the bounds of the grid
        
        Args:
          row: int
            the row index
          size: int
            the size of the object being checked
        Returns:
          inbounds: bool
            true if the object would be in bounds
        """
        return row >= 0 and row+(size-1) < self.shape[0]

    def col_inbounds(self, col:int, size:int):
        """
        Determines if the argued col is within the bounds of the grid
        
        Args:
          col: int
          size: int
            the size of the object being checked
        Returns:
          inbounds: bool
            true if col is in bounds
        """
        return col >= 0 and col+(size-1) < self.shape[1]

    def is_inbounds(self, coord: tuple, size: tuple):
        """
        Takes a coord and a size and determines if the object would be
        within the boundaries of the grid.

        Args:
          coord: list like (row, col)
            the coordinate in grid units
          size: list like (n_row, n_col)
            the size of the object
        """
        row, col = coord
        inbounds = self.row_inbounds(row, size[0])
        return inbounds and self.col_inbounds(col, size[1])

    def row_inhalfbounds(self, row, size):
        """
        Determines if the row is within the divided boundaries of
        the grid.
        
        Args:
          row: int
          size: int
        Returns:
          inbounds: bool
            true if the argued row is visually above the divided bounds
            of the grid
        """
        return row >= 0 and row+(size-1) < self.middle_row
    
    def is_inhalfbounds(self, coord, size):
        """
        Takes a coord and determines if it is within the divided
        boundaries of the grid.
        
        Args:
          coord: list like (row, col)
            the coordinate in grid units
          size: list like (n_row, n_col)
            the size of the object in grid units
        """
        row,col = coord
        inbounds = self.row_inhalfbounds(row, size[0])
        return inbounds and self.col_inbounds(col, size[1])
    
    def is_playable(self, coord, size=(1,1)):
        """
        Takes a coord and determines if it is within the divided
        boundaries of the grid if the grid is divided, or simply
        within the boundaries of the grid if the grid is not divided.

        Args:
          coord: list like (row, col)
            the coordinate in grid units
          size: tuple (n_row, n_col)
            the size of the player object
        """
        if self.is_divided: return self.is_inhalfbounds(coord, size)
        return self.is_inbounds(coord, size)

    def is_innonplaybounds(self, coord, size):
        """
        Takes a coord and determines if it is within the non-playable
        divided boundaries of the grid if the grid is divided, or simply
        within the boundaries of the grid if the grid is not divided.

        Args:
          coord: list like (row, col)
            the coordinate in grid units
          size: list like (n_row, n_col)
            the size of the object in grid units
        Returns:
            inbounds: bool
                true if the coord-size combo is within the nonplayable
                bounds.
        """
        row, col = coord
        if self.is_divided:
            row_inbounds = row+(size[0]-1) < self.shape[0]
            row_inbounds = row_inbounds and row > self.middle_row
            return row_inbounds and self.col_inbounds(col, size[1])
        return self.is_inbounds(coord, size)

    @staticmethod
    def all_coords(coord, size):
        """
        Returns a set of all coords that are included in the rectangle
        who's upper left corner is located ontop of the argued coord
        and has a vertical length of size[0] and a horizontal width of
        size[1]

        Args:
            coord: tuple of ints (row, col)
                coord in grid units
            size: tuple of ints (n_row downward, n_col rightward)
                the size of an imaginary rectangle with height given
                by size[0] and width given by size[1]. The rectangle's
                upper left corner is on top of the argued coord.
        Returns:
            coords: set
                a set of all coordinates (in grid units) that are 
                contained within the area of the rectangle.
        """
        coords = set()
        for row in range(size[0]):
            for col in range(size[1]):
                c = (coord[0]+row, coord[1]+col)
                coords.add(c)
        return coords



