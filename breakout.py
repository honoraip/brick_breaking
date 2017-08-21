# breakout.py
# Honora Ip, hi52
# December 12, 2014
"""Primary module for Breakout application

This module contains the App controller class for the Breakout application.
There should not be any need for additional classes in this module.
If you need more classes, 99% of the time they belong in either the gameplay
module or the models module. If you are ensure about where a new class should go,
post a question on Piazza."""
from constants import *
from gameplay import *
from game2d import *


# PRIMARY RULE: Breakout can only access attributes in gameplay.py via getters/setters
# Breakout is NOT allowed to access anything in models.py

class Breakout(GameApp):
    """Instance is a Breakout App

    This class extends GameApp and implements the various methods necessary
    for processing the player inputs and starting/running a game.

        Method init starts up the game.

        Method update either changes the state or updates the Gameplay object

        Method draw displays the Gameplay object and any other elements on screen

    Because of some of the weird ways that Kivy works, you SHOULD NOT create an
    initializer __init__ for this class.  Any initialization should be done in
    the init method instead.  This is only for this class.  All other classes
    behave normally.

    Most of the work handling the game is actually provided in the class Gameplay.
    Gameplay should have a minimum of two methods: updatePaddle(touch) which moves
    the paddle, and updateBall() which moves the ball and processes all of the
    game physics. This class should simply call that method in update().

    The primary purpose of this class is managing the game state: when is the
    game started, paused, completed, etc. It keeps track of that in an attribute
    called _state.

    INSTANCE ATTRIBUTES:
        view    [Immutable instance of GView, it is inherited from GameApp]:
            the game view, used in drawing (see examples from class)
        _state  [one of STATE_INACTIVE, STATE_COUNTDOWN, STATE_PAUSED, STATE_ACTIVE]:
            the current state of the game represented a value from constants.py
        _last   [GPoint, or None if mouse button is not pressed]:
            the last mouse position (if Button was pressed)
        _game   [GModel, or None if there is no game currently active]:
            the game controller, which manages the paddle, ball, and bricks

    ADDITIONAL INVARIANTS: Attribute _game is only None if _state is STATE_INACTIVE.

    You may have more attributes if you wish (you might need an attribute to store
    any text messages you display on the screen). If you add new attributes, they
    need to be documented here.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
        _mssg       ['Press to Play', or none if the game is not inactive]:
                     This message is displayed on the welcome screen
                     and instructs user to press the mouse to play.

        _lasttouch  [GPoint, or none if the game is inactive]:
                     Holds the previous value of touch. This is used in
                     GamePlay to detect the first time the user clicks
                     the mouse to move the paddle.

        _timer      [int >= 0 ]:
                     This is a countdown timer that counts frames. It is
                     used to count COUNTDOWN_SECONDS seconds in state
                     countdown.

        _ballcount  [int >= 0]:
                     The number of balls left (initialized to NUMBER_TURNS).

        _pausemssg  [pause message string, or none if the game is not paused]:
                     This message appears when the game is paused between tries.

        _finalmssg  [final message string, or none if the game is not complete]:
                     This message appears on the completion screen and tells
                     the user the game's result.
    """

    # GAMEAPP METHODS
    def init(self):
        """Initialize the game state.

        This method is distinct from the built-in initializer __init__.
        This method is called once the game is running. You should use
        it to initialize any game specific attributes.

        This method should initialize any state attributes as necessary
        to statisfy invariants. When done, set the _state to STATE_INACTIVE
        and create a message (in attribute _mssg) saying that the user should
        press to play a game."""

        self._state = STATE_INACTIVE
        self._last = None
        self._game = None

        self._mssg = GLabel(text = 'Press to Play', font_size = 50)

        self._lasttouch = None
        self._timer = 0
        self._ballcount = NUMBER_TURNS

        self._pausemssg = None
        self._finalmssg = None

    def update(self,dt):
        """Animate a single frame in the game.

        It is the method that does most of the work. Of course, it should
        rely on helper methods in order to keep the method short and easy
        to read.  Some of the helper methods belong in this class, but most
        of the others belong in class Gameplay.

        The first thing this method should do is to check the state of the
        game. We recommend that you have a helper method for every single
        state: STATE_INACTIVE, STATE_COUNTDOWN, STATE_PAUSED,
        STATE_ACTIVE, STATE_COMPLETE.
        The game does different things in each state.

        In STATE_INACTIVE, the method checks to see if the player clicks
        the mouse (_last is None, but view.touch is not None). If so, it
        (re)starts the game and switches to STATE_COUNTDOWN.

        STATE_PAUSED is similar to STATE_INACTIVE. However, instead of
        restarting the game, it simply switches to STATE_COUNTDOWN.

        In STATE_COUNTDOWN, the game counts down until the ball is served.
        The player is allowed to move the paddle, but there is no ball.
        Paddle movement should be handled by class Gameplay (NOT in this class).
        This state should delay at least one second.

        In STATE_ACTIVE, the game plays normally.  The player can move the
        paddle and the ball moves on its own about the board.  Both of these
        should be handled by methods inside of class Gameplay (NOT in this class).
        Gameplay should have methods named updatePaddle and updateBall.

        While in STATE_ACTIVE, if the ball goes off the screen and there
        are tries left, it switches to STATE_PAUSED.  If the ball is lost
        with no tries left, or there are no bricks left on the screen, the
        game is over and it switches to STATE_INACTIVE.  All of these checks
        should be in Gameplay, NOT in this class.

        STATE_COMPLETE displays a message when the game is over. The game shows
        a message _finalmssg when the game is won or lost.

        You are allowed to add more states if you wish. Should you do so,
        you should describe them here.

        Precondition: dt is the time since last update (a float).  This
        parameter can be safely ignored. It is only relevant for debugging
        if your game is running really slowly. If dt > 0.5, you have a
        framerate problem because you are trying to do something too complex."""

        assert type(dt) == float

        # Each state has a helper method

        if self._state == STATE_INACTIVE:
            self._inactive()

        if self._state == STATE_COUNTDOWN:
            self._countdown()

        if self._state == STATE_ACTIVE:
            self._active()

        if self._state == STATE_PAUSED:
            self._paused()

        if self._state == STATE_COMPLETE:
            self._complete()

    def draw(self):
        """Draws the game objects to the view.

        Every single thing you want to draw in this game is a GObject.
        To draw a GObject g, simply use the method g.draw(view).  It is
        that easy!

        Many of the GObjects (such as the paddle, ball, and bricks) are
        attributes in Gameplay. In order to draw them, you either need to
        add getters for these attributes or you need to add a draw method
        to class Gameplay.  We suggest the latter.  See the example
        subcontroller.py from class."""

        # Only draw if the object exists (is not None)!

        if self._mssg != None:
            self._mssg.draw(self.view)

        if self._game != None:
            self._game.draw(self.view)

        if self._pausemssg != None:
            self._pausemssg.draw(self.view)

        if self._finalmssg != None:
            self._finalmssg.draw(self.view)

    # HELPER METHODS FOR THE STATES GO HERE

    def _inactive(self):
        """Checks if player clicks the mouse. If so, the game starts,
        game state is changed to STATE_COUNTDOWN, and the welcome screen is
        dismissed."""

        if self._last == None and self.view.touch != None:
            self._state = STATE_COUNTDOWN
            self._last = self.view.touch
            self._mssg = None
            self._game = Gameplay()

    def _paused(self):
        """Checks if player clicks the mouse. If so, the game state is changed
        to STATE_COUNTDOWN and the pause message disappears."""

        if self.view.touch != None:
            self._pausemssg = None
            self._state = STATE_COUNTDOWN

    def _countdown(self):
        """Updates the paddle movement and counts down seconds until the ball
        is to be released. When countdown ends, the state switches to
        STATE_ACTIVE, the ball is served, and the ball count is decremented."""
        self._game.updatePaddle(self._lasttouch, self.view.touch)
        self._lasttouch = self.view.touch
        self._timer += 1

        # Switch state to active after countdown (60 frames per second)
        if self._timer >= COUNTDOWN_SECONDS*60:
            self._state = STATE_ACTIVE
            self._game.serveBall()
            self._ballcount -= 1

    def _active(self):
        """Updates the paddle movement and moves the ball. If the ball is lost,
        pause in STATE_PAUSED or end the game in STATE_COMPLETE based on how
        many balls are left. Set messages accordingly."""

        self._game.updatePaddle(self._lasttouch, self.view.touch)
        self._lasttouch = self.view.touch

        # Handle lost ball

        lostball = self._game.moveBall()

        if lostball and self._ballcount == 0:
            self._finalmssg = GLabel(text = 'You Lost', font_size = 50)
            self._state = STATE_COMPLETE
        elif lostball and self._ballcount > 0:
            self._pausemssg = GLabel(text = 'Click! Try again', font_size = 50)
            self._state = STATE_PAUSED

        # Check for a screen with no bricks

        completed = self._game.checkBricksListEmpty()

        if completed:
            self._finalmssg = GLabel(text = 'You Win', font_size = 50)
            self._state = STATE_COMPLETE

    def _complete(self):
        """The game is over. Display the completion message."""

        # Nothing to do here. Game is over.
        pass

