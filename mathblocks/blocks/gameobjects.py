from mathblocks.blocks.constants import *
from mathblocks.blocks.utils import coord_diff, coord_add

class GameObject:
    """
    The GameObject class is the main class for tracking what types of
    objects are on the grid. It contains the current coordinate and
    type of object.
    """
    def __init__(self,
                 obj_type: str,
                 color: float,
                 coord: tuple=(0,0),
                 size: tuple=(1,1)):
        """
        obj_type: str
          the type of object. see OBJECT_TYPES for a list of available
          types.
        color: float
          the color of the object
        coord: tuple (row, col) in grid units
          the initial coordinate of the object
        size: tuple (n_row, n_col) in grid units
          the size of the rectangle representing the object.
        """
        self._obj_type = obj_type
        self._color = color
        assert type(coord) == tuple
        self.coord = coord
        assert type(size) == tuple
        self._size = size
        # used to track changes for drawing to grid
        self.prev_coord = coord

    def move_to(self, coord):
        """
        Moves the object to the argued coordinate.
        """
        self.prev_coord = self.coord
        self.coord = coord

    @property
    def type(self):
        return self._obj_type

    @property
    def color(self):
        return self._color

    @property
    def size(self):
        return self._size

    def __str__(self):
        return self.type

class Player(GameObject):
    """
    The player object has special abilities to hold objects. While a
    player object is holding another object, updates to the player's
    coordinates will affect the object it is holding as well.
    """
    def __init__(self,
                 color: float,
                 coord: tuple=(0,0)):
        """
        color: float
          the color of the object
        coord: tuple (row, col) in grid units
          the initial coordinate of the object
        """
        super().__init__(
            obj_type=PLAYER,
            color=color,
            coord=coord,
            size=(1,1)
        )
        self.held_obj = None

    def grab(self, obj):
        """
        Assists in grabbing a GameObject.

        Args:
            obj: GameObject
        """
        self.held_obj = obj

    def drop(self):
        """
        Assists in dropping a GameObject.
        """
        obj = self.held_obj
        self.held_obj = None
        return obj

    @property
    def is_holding(self):
        return self.held_obj is not None

    @property
    def held_coord(self):
        """
        Returns the coordinate of the held object if the player is
        holding an object.

        Returns:
            coord: tuple of ints or None
        """
        if self.is_holding: return self.held_obj.coord
        return None

    def subj_held_coord(self, subj_player_coord):
        """
        Returns what the coordinate of the held object would be if the
        player were to move to the argued coordinate.

        subj stands for subjunctive.

        Args:
            subj_player_coord: tuple of ints (row,col)
                the would be coordinate of the player. this function
                will determine what the held object's coordinate would
                be if the player were moved to the subj_player_coord
        Returns:
            coord: tuple of ints or None
                returns the coordinate where the held object would be
                if the player were to move to the argued coorindate. 
                returns None if the player is not holding an object.
        """
        if self.held_coord is None: return None
        vector = coord_diff(subj_player_coord, self.coord)
        return coord_add(vector, self.held_coord)

class Pile(GameObject):
    """
    Piles are a special type of gameobject that allow creation of a
    new item of a particular size, color, and representative quantity.
    The Pile class holds the information for all new items created from
    itself.
    """
    def __init__(self, 
                 color: float,
                 block_val: int,
                 block_size: tuple,
                 block_color: float,
                 coord: tuple=(0,0),
                 size: tuple=(1,1)):
        """
        color: float
          the color of the object
        block_val: int
          the representative number that each item created from this
          pile will represent.
        block_size: int
          the size of each block created from this pile
        color: float
          the color of each item created from this pile
        coord: tuple (row, col) in grid units
          the initial coordinate of the object
        size: tuple (n_row, n_col) in grid units
          the size of the rectangle representing the object.
        """
        super().__init__(
            obj_type=PILE+str(block_val),
            color=color,
            coord=coord,
            size=size
        )
        self.block_val = block_val
        assert type(block_size) == tuple
        self.block_size = block_size
        self.block_color = block_color

class Operator(GameObject):
    """
    Operators are a special type of gameobject that represent the
    mathematical operation being performed in the displayed equation.
    """
    @staticmethod
    def operation2size(operation):
        """
        Takes an operation and returns the size that the operator
        should be. Operations are distinguished by the shape of the
        operator object.

        Args:
            operation: str
        Returns:
            size: tuple (n_row,n_col)
        """
        if operation == ADD:
            return (2,1)
        elif operation == SUBTRACT:
            return (1,2)
        elif operation == MULTIPLY:
            return (1,1)
        else:
            raise NotImplemented

    def __init__(self, 
                 color: float,
                 operation: str=ADD,
                 coord: tuple=(0,0)):
        """
        color: float
          the color of the object
        operation: str
            the current operation that this operator represents
        coord: tuple (row, col) in grid units
          the initial coordinate of the object
        """
        self.operation = operation
        size = Operator.operation2size(self.operation)
        super().__init__(
            obj_type=OPERATOR,
            color=color,
            coord=coord,
            size=size
        )

class Block(GameObject):
    """
    Blocks are the building block :) of the game. Each block represents
    a quantity. They can be stacked to build bigger blocks.
    """
    def __init__(self,
                 color: float,
                 val: int,
                 coord: tuple=(0,0),
                 size: tuple=(1,1)):
        """
        Args:
            color: float
              the color of the object
            val: int
              the representative number that each item created from this
              pile will represent.
            coord: tuple (row, col) in grid units
              the initial coordinate of the object
            size: tuple (n_row, n_col) in grid units
              the size of the rectangle representing the object.
        """
        self.val = val
        super().__init__(
            obj_type=BLOCK+str(self.val),
            color=color,
            coord=coord,
            size=size
        )

