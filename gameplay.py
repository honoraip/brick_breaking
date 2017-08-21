# gameplay.py
# Honora Ip, hi52
# December 12, 2014
"""Subcontroller module for Breakout

This module contains the subcontroller to manage a single game in the Breakout App.
Instances of Gameplay represent a single game.  If you want to restart a new game,
you are expected to make a new instance of Gameplay.

The subcontroller Gameplay manages the paddle, ball, and bricks.  These are model
objects.  The ball and the bricks are represented by classes stored in models.py.
The paddle does not need a new class (unless you want one), as it is an instance
of GRectangle provided by game2d.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a complicated
issue.  If you do not know, ask on Piazza and we will answer."""
from constants import *
from game2d import *
from models import *


# PRIMARY RULE: Gameplay can only access attributes in models.py via getters/setters
# Gameplay is NOT allowed to access anything in breakout.py (Subcontrollers are not
# permitted to access anything in their parent. To see why, take CS 3152)


class Gameplay(object):
    """An instance controls a single game of breakout.

    This subcontroller has a reference to the ball, paddle, and bricks. It
    animates the ball, removing any bricks as necessary.  When the game is
    won, it stops animating.  You should create a NEW instance of
    Gameplay (in Breakout) if you want to make a new game.

    If you want to pause the game, tell this controller to draw, but do not
    update.  See subcontrollers.py from Lecture 24 for an example.

    INSTANCE ATTRIBUTES:
        _wall   [BrickWall]:  the bricks still remaining
        _paddle [GRectangle]: the paddle to play with
        _ball [Ball, or None if waiting for a serve]:
            the ball to animate
        _last [GPoint, or None if mouse button is not pressed]:
            last mouse position (if Button pressed)
        _tries  [int >= 0]:   the number of tries left

    As you can see, all of these attributes are hidden.  You may find that you
    want to access an attribute in call Breakout. It is okay if you do, but
    you MAY NOT ACCESS THE ATTRIBUTES DIRECTLY. You must use a getter and/or
    setter for any attribute that you need to access in Breakout.  Only add
    the getters and setters that you need for Breakout.

    You may change any of the attributes above as you see fit. For example, you
    might want to make a Paddle class for your paddle.  If you make changes,
    please change the invariants above.  Also, if you add more attributes,
    put them and their invariants below.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
        _initialtouchx  [int]:
                         initial touch x position when first clicking mouse
        _initialpaddlex [int]:
                         initial paddle x position when first clicking mouse
    """

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)

    def __init__(self):
        """Initialize the game state. Create the brick wall and the
        paddle"""

        self._wall = BrickWall()
        self._paddle = GRectangle(
                            x = 0,
                            y = PADDLE_OFFSET,
                            width = PADDLE_WIDTH,
                            height = PADDLE_HEIGHT,
                            fillcolor = colormodel.BLACK,
                            linecolor = colormodel.BLACK
                        )
        self._initialtouchx = 0
        self._initialpaddlex = 0
        self._ball = None

    def draw(self, view):
        """DRAW METHOD TO DRAW THE PADDLES, BALL, AND BRICKS

            :param view: view to draw to
            **Precondition**: an *instance of* `GView`

        Ideally view should be the one provided by `Game`."""

        # Draw paddle

        if self._paddle != None:
            self._paddle.draw(view)

        # Draw ball

        if self._ball != None:
            self._ball.draw(view)

        # Draw bricks

        if self._wall != None:
            self._wall.draw(view)

    # UPDATE METHODS TO MOVE PADDLE, SERVE AND MOVE THE BALL

    def moveBall(self):
        """Returns: True if ball collided with bottom wall. False
        otherwise.

        Handle the movement of the ball by adding the velocity to the
        ball's current position.

        Handle collisions depending on which object the ball collides
        with."""

        # Update ball position

        self._ball.x += self._ball._vx
        self._ball.y += self._ball._vy

        # Get a colliding object

        colliding_object = self._getCollidingObject()

        # If it is a paddle collision, call helper method

        if colliding_object == self._paddle:
            self._ball.handlePaddleCollision()

        # If it is a brick collision, call helper method

        elif colliding_object:
            self._ball.handleBrickCollision()
            self._wall.removeBrick(colliding_object)

        # Otherwise, it is not a collision or it is a wall collision, so
        # use the helper method to return whether the ball collides with
        # the bottom wall or not.

        return self._ball.handleWallCollision()

    def serveBall(self):
        """Serves the ball. This just creates a new ball!"""

        # Create ball
        self._ball = Ball()

    def updatePaddle(self, lasttouch, touch):
        """Update paddle position. This method tracks the initial mouse
        touch position and the initial paddle x position and stores the
        points in attributes. It then uses these attributes to avoid
        teleporting the paddle when the user clicks the mouse.

        The method also does bounds checking to make sure the paddle
        does not go off the screen."""

        # Grab initial touch if this if the first touch
        if lasttouch == None and touch != None:
            self._initialtouchx = touch.x
            self._initialpaddlex = self._paddle.x

        # Use mouse position to set paddle position, offset by initial
        # touch
        if touch != None:
            self._paddle.x = \
                self._initialpaddlex + (touch.x - self._initialtouchx)

        # Make sure paddle stays within the right bound
        if self._paddle.x > (GAME_WIDTH - PADDLE_WIDTH):
            self._paddle.x = (GAME_WIDTH - PADDLE_WIDTH)

        # Make sure paddle stays within the left bound
        if self._paddle.x < 0:
            self._paddle.x = 0


    # HELPER METHODS FOR PHYSICS AND COLLISION DETECTION

    def _getCollidingObject(self):
        """Returns: GObject that has collided with the ball

        This method checks the four corners of the ball, one at a
        time. If one of these points collides with either the paddle
        or a brick, it stops the checking immediately and returns the
        object involved in the collision. It returns None if no
        collision occurred."""

        # Here is a list of the four points to check for ball collisions

        ball_points = [ [self._ball.left, self._ball.bottom],
                        [self._ball.left, self._ball.top],
                        [self._ball.right, self._ball.bottom],
                        [self._ball.right, self._ball.top],
                        ]

        # Check each point for collisions
        for point in ball_points:

            x_pos = point[0]
            y_pos = point[1]

            # Check paddle collision

            if self._paddle.contains(x_pos, y_pos):
                return self._paddle

            # Loop over bricks to check collisions

            bricks = self._wall.getBricks()

            for brick in bricks:
                if brick.contains(x_pos, y_pos):
                    return brick

        # No collision
        return None

    # ADD ANY ADDITIONAL METHODS (FULLY SPECIFIED) HERE

    def checkBricksListEmpty(self):
        """Returns: True if there are no bricks left and False
        otherwise. This is used to check whether the game is over or
        not."""

        # Check the number of bricks left in the list of bricks
        return ( len(self._wall.getBricks()) == 0 )




