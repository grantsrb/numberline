import numpy as np
import math
from numberline.constants import *

"""
The grid class handles are interactions with the actual pixels of the
numberline image. The grid holds an array object (called self.grid)
that is manipulated for the output of any given step in the game.

The grid array is always 100 units long plus a zero pixel at the
lefmost positon plus the 4 operations pixels at the right most
positions of the array. Each unit has a length and width in pixels of
pixel_density. In cases where the pixel_density is equal to 1, each
of the 100 units on the grid are represented as a single pixel. In
cases where the pixel_density is larger than 1, the pixels that make up
each unit are colored except for the rightmost column and lowermost row
of pixels making up the unit. This alows for a visual space between
adjacent units.

The 0 unit is always marked with a special value ZERO. Each of the 10s
units are always marked with a value of MARKER. Every 10 10's units are
marked with a value of 2*MARKER and 10 10's 10's units are 3*MARKER to
infinity.

Color filling is done so that it can be added with any multiple of
MARKER while preserving the filling information.
"""
class Grid:
    def __init__(self,
                 pixel_density: int=1):
        """
        Args:
          pixel_density: int
            the length and width of a unit measured in pixels. If the
            argument is greater than 1, the coordinate is filled in
            the upper most left corner while leaving the column of
            pixels at the rightmost boundary and the row of pixels at
            the lowermost boundary blank (to display a visual
            separation of units to the user).
        """
        self._pixel_density = pixel_density
        self._n_rows = 1
        # REGISTER REQUIRES THIS TO BE AN ODD NUMBER
        self._n_val_units = 101 # zero, 1-100 
        self._n_meta_units = 4 # zoom, operator, operand, trans
        # zero, 1-100, zoom, operator, operand, trans
        self._grid_shape = (
            self.density*self._n_rows,
            self.density*(self._n_val_units + self._n_meta_units)
        )
        self._grid = self.make_grid()

    @property
    def n_val_units(self):
        """
        Returns:
          n_val_units: int
            the number of units that represent values
        """
        return self._n_val_units

    @property
    def n_meta_units(self):
        """
        Returns:
          n_meta_units: int
            the number of units that represent meta information
        """
        return self._n_meta_units

    @property
    def zoom_idx(self):
        """
        Returns:
          zoom_idx: int
            The index of the zoom meta unit.
        """
        return self.n_val_units + 1

    @property
    def operator_idx(self):
        """
        Returns:
          operator_idx: int
            The index of the operator meta unit.
        """
        return self.n_val_units + 2

    @property
    def operand_idx(self):
        """
        Returns:
          operand_idx: int
            The index of the operand meta unit.
        """
        return self.n_val_units + 3

    @property
    def trans_idx(self):
        """
        Returns:
          trans_idx: int
            The index of the translation meta unit.
        """
        return self.n_val_units + 4

    @property
    def density(self):
        """
        Returns:
          pixel_density: int
            the number of pixels per unit
        """
        return self._pixel_density

    @property
    def shape(self):
        """
        GIVES THE SHAPE OF THE GRID IN GRID UNITS EXCLUDING THE META
        UNITS AT THE END OF THE GRID!!!!

        Returns:
          shape: int
            the shape of the grid in terms of units leaving out the
            meta units.
        """
        return (self._n_rows, self.n_val_units)

    @property
    def raw_shape(self):
        """
        Returns:
          shape: int
            the raw shape of the grid
        """
        return self.grid.shape

    @property
    def pixel_shape(self):
        """
        Returns the shape of the grid in terms of pixels rather than grid
        units

        GIVES THE SHAPE OF THE GRID EXCLUDING THE META PIXELS AT THE
        END OF THE GRID!!!!
        
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

    @property
    def middle_col(self):
        """
        Returns the unit index of the col that is considered the center
        of the grid (not including meta units). This is generally
        index 50.

        Returns:
            middle: int
                the index of the center unit on the grid
        """
        return int(self.shape[1]/2)

    @property
    def middle(self):
        """
        Returns the unit index of the col that is considered the center
        of the grid (not including meta units). This is generally
        index 50.

        Returns:
            middle: int
                the index of the center unit on the grid
        """
        return self.middle_col

    def __getitem__(self, coord):
        """
        Returns the color at the (0,0) pixel of the argued coordinate

        Args:
            coord: int or tuple of ints (row, col)
                if int, coord defaults to (0, coord)
        Returns:
            color: float
                The color at the (0,0) pixel of the unit at the argued
                coord
        """
        if isinstance(coord, int):
            prow = 0
            pcol = self.units2pixels(coord)
        else:
            prow, pcol = self.units2pixels(coord)
        return self._grid[prow, pcol]

    def __setitem__(self, coord, color):
        """
        Sets the value the color of a unit at a particular coordinate

        Args:
            coord: tuple of ints (row, col) or int
                if int, col must also be an int
            color: float
        """
        if type(coord)==int: coord = (0,coord)
        self.draw(coord, color, add_color=False)

    def set_zoom_color(self, color):
        """
        Set the color of the zoom unit on the grid
        """
        return self.draw(
            (0,self.zoom_idx),
            color=color,
            add_color=False
        )

    def set_operator_color(self, color):
        """
        Set the color of the operator unit on the grid
        """
        return self.draw(
            (0,self.operator_idx),
            color=color,
            add_color=False
        )

    def set_operand_color(self, color):
        """
        Set the color of the operand unit on the grid
        """
        return self.draw(
            (0,self.operand_idx),
            color=color,
            add_color=False
        )

    def set_trans_color(self, color):
        """
        Returns:
          trans_idx: int
            The index of the translation meta unit.
        """
        return self.draw(
            (0,self.trans_idx),
            color=color,
            add_color=False
        )

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
        return (
          int(pixel_coord[0]/self.density),
          int(pixel_coord[1]/self.density)
        )

    def make_grid(self):
        """
        Creates the grid, each unit containing a square of pixels with
        height and width equal to the pixel density. The ending meta
        units each consist of a unit just like the numerical units.
        
        Returns:
          grid: ndarry (H,W)
            a numpy array representing the grid
        """
        self._grid = np.zeros(self._grid_shape).astype(np.float)
        self._grid = self._grid + COLORS[DEFAULT]
        return self._grid

    def reset(self):
        """
        Resets the grid to the initial specifications with new
        reference to the grid.
        """
        self._grid = self.make_grid()

    def clear_unit(self, coord):
        """
        Clears a single coordinate in place. More efficient than using
        draw to draw zeros
        
        Args:
          coord: list like (row, col)
        """
        self.draw(
            coord,
            color=COLORS[DEFAULT],
            add_color=False
        )

    def clear(self):
        """
        Clears the whole grid in place.
        """
        self._grid[:,:] = COLORS[DEFAULT]

    def draw(self,
             coord: tuple or int,
             color: float,
             add_color: bool=True):
        """
        This function handles the actual drawing on the grid. The argued
        color is drawn to the specified coordinate. Can add the argued
        color to the existing value or can replace the existing color
        with the argued depending on the value of add_color.

        Args:
          coord: tuple of ints (row, col) or int
            the coord is the coordinate on the grid in terms of grid
            units. if an int is argued, this function assumes coord
            to be equal to the column index and fills all rows at this
            column index with the argued color.
          color: float
            the value that should be drawn to the coordinate
          add_color: bool default True
            if true, the argued color is added to the existing value
            rather than replacing it.
        """
        if type(coord)==int:
            coord = (0,coord)
            if self.shape[0] > 1:
                coord2 = (self.shape[0],coord[1]+1)
                self.slice_draw(coord, coord2,color, add_color)
        # Coordinates that are off the grid are simply not drawn
        row,col = self.units2pixels(coord)
        draw_space = max(1,self.density-1)
        if add_color:
            self._grid[row:row+draw_space, col:col+draw_space] += color
        else:
            self._grid[row:row+draw_space, col:col+draw_space] = color
    

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
        coord0 = (max(0, coord0[0]), max(0,coord0[1]))
        coord1 = (
            min(self.shape[0], coord1[0]),
            min(self.shape[1],coord1[1])
        )
        row0,col0 = coord0
        row1,col1 = coord1
        if row0 > row1 or col0 > col1: return
        elif row0 == row1 and col0 == col1:
            self.draw(coord0, color, add_color=add_color)
            return
        elif row0 == row1:
            row1 += 1
            coord1 = (row1, col1)
        elif col0 == col1:
            col1 += 1
            coord1 = (row1, col1)
        # Make unit
        unit = np.zeros((self.density, self.density)) + COLORS[DEFAULT]
        unit = unit.astype(np.float)
        draw_space = max(self.density-1, 1)
        unit[0:draw_space, 0:draw_space] = color
        # Tile the unit
        n_row = int(coord1[0]-coord0[0])
        n_col = int(coord1[1]-coord0[1])
        tiles = np.tile(unit, (n_row, n_col))
        # Draw to the grid
        pxr0, pxc0 = self.units2pixels(coord0)
        pxr1, pxc1 = self.units2pixels(coord1)
        if add_color:
            self._grid[pxr0:pxr1, pxc0:pxc1] += tiles
        else:
            self._grid[pxr0:pxr1, pxc0:pxc1] = tiles

    def draw_fill(self, start_idx, end_idx, row=None):
        """
        Simply adds the color COLORS[FILL] to all columns contained
        within the argued range.

        Args:
            start_idx: int (inclusive)
                the starting index in grid units for the fill
            end_idx: int (exclusive)
                the ending index in grid units for the fill
        """
        if row is not None:
            coord0 = (row, start_idx)
            coord1 = (row+1, end_idx)
        else:
            coord0 = (0, start_idx)
            coord1 = (self.shape[0], end_idx)
        self.slice_draw(
            coord0,
            coord1,
            color=COLORS[FILL],
            add_color=True
        )

    def row_inbounds(self, row: int):
        """
        Determines if the argued row is within the bounds of the grid
        
        Args:
          row: int
            the row index
        Returns:
          inbounds: bool
            true if the object would be in bounds
        """
        return row >= 0 and row < self.shape[0]

    def col_inbounds(self, col:int):
        """
        Determines if the argued col is within the bounds of the grid
        
        Args:
          col: int
        Returns:
          inbounds: bool
            true if col is in bounds
        """
        return col >= 0 and col < self.shape[1]

    def is_inbounds(self, coord: tuple):
        """
        Determines if a coord is within the boundaries of the grid.

        Args:
          coord: list like (row, col)
            the coordinate in grid units
        """
        row, col = coord
        return self.row_inbounds(row) and self.col_inbounds(col)

