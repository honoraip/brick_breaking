# models.py
# Honora Ip, hi52
# December 12, 2014
"""Models module for Breakout

This module contains the model classes for the Breakout game. Anything that you
interact with on the screen is model: the paddle, the ball, and any of the bricks.

Just because something is a model does not mean there has to be a special class for
it.  Unless you need something special for your extra gameplay features, both paddle
and individual bricks can just be instances of GRectangle.  There is no need for a
new class in the case of these objects.

We only need a new class when we have to add extra features to our objects.  That
is why we have classes for Ball and BrickWall.  Ball is usually a subclass of GEllipse,
but it needs extra methods for movement and bouncing.  Similarly, BrickWall needs
methods for accessing and removing individual bricks.

You are free to add new models to this module.  You may wish to do this when you add
new features to your game.  If you are unsure about whether to make a new class or
not, please ask on Piazza."""
import random # To randomly generate the ball velocity
from constants import *
from game2d import *


# PRIMARY RULE: Models are not allowed to access anything in any module other than
# constants.py.  If you need extra information from Gameplay, then it should be
# a parameter in your method, and Gameplay should pass it as a argument when it
# calls the method.


class BrickWall(object):
    """An instance represents the layer of bricks in the game.  When the wall is
    empty, the game is over and the player has won. This model class keeps track of
    all of the bricks in the game, allowing them to be added or removed.

    INSTANCE ATTRIBUTES:
        _bricks [list of GRectangle, can be empty]:
            This is the list of currently active bricks in the game.  When a brick
            is destroyed, it is removed from the list.

    As you can see, this attribute is hidden.  You may find that you want to access
    a brick from class Gameplay. It is okay if you do that,  but you MAY NOT
    ACCESS THE ATTRIBUTE DIRECTLY. You must use a getter and/or setter for any
    attribute that you need to access in GameController.  Only add the getters and
    setters that you need.

    We highly recommend a getter called getBrickAt(x,y).  This method returns the first
    brick it finds for which the point (x,y) is INSIDE the brick.  This is useful for
    collision detection (e.g. it is a helper for _getCollidingObject).

    You will probably want a draw method too.  Otherwise, you need getters in Gameplay
    to draw the individual bricks.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    """

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)

    def getBricks(self):
        return self._bricks

    def removeBrick(self, brick):
        """Removes the given brick from the list."""

        self._bricks.remove(brick)

    def __init__(self):
        """Initialize the game state. This initializer lays out bricks
        on the screen. The list of bricks is held in a list. Constants
        are used to set the number of brick rows, the bricks in a row,
        brick separations and widths and heights, and brick colors.

        After creating each brick, the brick is added to a list."""

        # Create the list of bricks

        self._bricks = []

        # Create all rows of bricks
        row_number = 0
        for row in range(BRICK_ROWS):
            color = ROW_COLORS[row]

            # Create a row of BRICKS_IN_ROW bricks
            for i in range(BRICKS_IN_ROW):

                x_pos = BRICK_SEP_H/2 + i*(BRICK_SEP_H + BRICK_WIDTH)
                y_pos = GAME_HEIGHT - BRICK_Y_OFFSET \
                        - row_number * (BRICK_HEIGHT + BRICK_SEP_V)

                brick = GRectangle(
                            x = x_pos,
                            y = y_pos,
                            width = BRICK_WIDTH,
                            height = BRICK_HEIGHT,
                            fillcolor = color,
                            linecolor = color
                        )

                # Add this brick to the list of bricks
                self._bricks.append( brick )

            # Increment row number
            row_number += 1

    # ADD MORE METHODS (PROPERLY SPECIFIED) AS NECESSARY

    def draw(self, view):
        """Draw this shape in the provide view.

            :param view: view to draw to
            **Precondition**: an *instance of* `GView`

        Ideally view should be the one provided by `Game`."""

        # Loop over bricks and draw each one
        for brick in self._bricks:
            brick.draw(view)

class Ball(GEllipse):
    """Instance is a game ball.

    We extend GEllipse because a ball must have additional attributes for velocity.
    This class adds this attributes and manages them.

    INSTANCE ATTRIBUTES:
        _vx [int or float]: Velocity in x direction
        _vy [int or float]: Velocity in y direction

    The class Gameplay will need to look at these attributes, so you will need
    getters for them.  However, it is possible to write this assignment with no
    setters for the velocities.

    How? The only time the ball can change velocities is if it hits an obstacle
    (paddle or brick) or if it hits a wall.  Why not just write methods for these
    instead of using setters?  This cuts down on the amount of code in Gameplay.

    In addition you must add the following methods in this class: an __init__
    method to set the starting velocity and a method to "move" the ball.  The
    __init__ method will need to use the __init__ from GEllipse as a helper.
    The move method should adjust the ball position according to  the velocity.

    NOTE: The ball does not have to be a GEllipse. It could be an instance
    of GImage (why?). This change is allowed, but you must modify the class
    header up above.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    """

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)

    def __init__(self):
        """Initialize the ball. The ball starts in the center and moves
        at random velocity in the left or right direction. It moves at a
        random velocity downwards."""
        GEllipse.__init__(self,
                          x = 0,
                          y = 0,
                          width = 10,
                          height = 10,
                          fillcolor = colormodel.BLACK,
                          linecolor = colormodel.BLACK
                          )

        # Ball starts in the center
        self.center_x = GAME_WIDTH / 2
        self.center_y = GAME_HEIGHT / 2

        # Ball moves at random velocity left or right
        self._vx = random.uniform(1.0,5.0)
        self._vx = self._vx * random.choice([-1, 1])

        # Ball always heads downward
        self._vy = random.uniform(1.0,5.0)
        self._vy = self._vy * -1


    # METHODS TO MOVE AND/OR BOUNCE THE BALL

    def handleBrickCollision(self):
        """This method reverses the ball's y velocity when it collides
        with a brick."""
        self._vy = -1.0 * self._vy

    def handlePaddleCollision(self):
        """This method reverses the ball's y velocity when it collides
        with the paddle, only if the ball is traveling downwards."""

        if self._vy < 0.0:
            self._vy = -1.0 * self._vy

    def handleWallCollision(self):
        """Returns: True if ball collided with bottom wall and false
        otherwise.

        Handle physics of ball when colliding with a wall. Colliding
        with the left and right walls reverses the vx direction.
        Colliding with the upper wall reverses the vy direction.
        Colliding with the bottom wall is okay if the ball is moving
        upwards to avoid initial bugs. Otherwise, colliding with the
        bottom wall returns True."""

        # If collide with left wall, reverse vx
        if self.left < 0.0:
            self._vx = -1.0 * self._vx

        # If collide with right wall, reverse vx
        elif self.right > GAME_WIDTH:
            self._vx = -1.0 * self._vx

        # If collide with top wall, reverse vy
        elif self.top > GAME_HEIGHT:
            self._vy = -1.0 * self._vy

        # If collide with bottom wall while moving down, return
        elif self.bottom < 0.0 and self._vy < 0.0:
            return True

        return False

    # ADD MORE METHODS (PROPERLY SPECIFIED) AS NECESSARY



# IF YOU NEED ADDITIONAL MODEL CLASSES, THEY GO HERE
