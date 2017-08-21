# game2d.py
# Walker M. White (wmw2)
# November 14, 2013
"""Module to provide simple 2D game support.

This module provides all of the classes that are to use (or subclass) 
to create your game. DO NOT MODIFY THE CODE IN THIS FILE.  See the
online documentation in Assignment 6 for more guidance.  It includes
information not displayed in this module."""

# Basic Kivy Modules
import kivy
import kivy.app
import kivy.uix.label

# Lower-level kivy modules to support animation
from kivy.config import *
from kivy.clock import Clock
from kivy.graphics import *
from kivy.graphics.instructions import *
from kivy.config import Config

# Widgets necessary for some technical workarounds
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

# Additional miscellaneous modules
import os
import os.path
import numpy
import random
import colormodel
import pygame.mixer
import sys

# User-defined resources
FONT_PATH  = str(os.path.join(os.path.dirname(__file__), 'Fonts'))
SOUND_PATH = str(os.path.join(os.path.dirname(__file__), 'Sounds'))
IMAGE_PATH = str(os.path.join(os.path.dirname(__file__), 'Images'))

import kivy.resources
kivy.resources.resource_add_path(FONT_PATH)
kivy.resources.resource_add_path(SOUND_PATH)
kivy.resources.resource_add_path(IMAGE_PATH)

# Initialize the sound engine.
FREQUENCY = 44100
BITSIZE   = -16
CHANNELS  = 2
BUFFER    = 1024
pygame.mixer.init(FREQUENCY,BITSIZE,CHANNELS,BUFFER)

#### CONSTANTS ####

# Data caching for graphics objects
CACHE_ALL    = 0
CACHE_POS    = 1
CACHE_SIZE   = 2
CACHE_COLOR  = 3
CACHE_SOURCE = 4

# LINE SIZE
LINE_SIZE = 1

#### HIDDEN HELPER FUNCTIONS ####
def  _same_side(p1, p2, a, b):
    """Return: True is p1, p2 are on the same side of segment ba.
    
    Precondition: p1, p2, a, b are all 2d tuples of int or float."""
    ba = numpy.append(numpy.subtract(b,a),[0])
    cp1 = numpy.cross(ba,numpy.subtract(p1,a))
    cp2 = numpy.cross(ba,numpy.subtract(p2,a))
    return numpy.dot(cp1,cp2) >= 0


def _in_triangle(p, t):
    """Return: True if p is in triangle t
    
    Precondition: p is a 2d tuple of int or float.
    t is a 6-element tuple of int or float."""
    return (_same_side(p, t[0:2], t[2:4], t[4:6]) and
            _same_side(p, t[2:4], t[0:2], t[4:6]) and
            _same_side(p, t[4:6], t[0:2], t[2:4]))


def _and(x,y):
    """Return: x and y (used for reduce)"""
    return x and y


def _is_num(x):
    """Return: True if x is an int or float"""
    return type(x) in [int,float]


def _is_color(x):
    """Return: True if x represents a color"""
    if type(x) in [colormodel.RGB, colormodel.HSV]:
        return True
    
    if type(x) in [tuple, list] and 3 <= len(x) <= 4:
        return reduce(_and, map(lambda x: type(x) in [int, float] and 0 <= x <= 1, x)) 
    
    return False


def _is_image_file(name):
    """Return: True if name is the name of an image file"""
    if type(name) != str:
        return False
    
    return os.path.exists(IMAGE_PATH+'/'+name)


def _is_font_file(name):
    """Return: True if name is the name of an font file"""
    if type(name) != str:
        return False
    
    return os.path.exists(FONT_PATH+'/'+name)


def _is_sound_file(name):
    """Return: True if name is the name of an font file"""
    if type(name) != str:
        return False
    
    return os.path.exists(SOUND_PATH+'/'+name)


#### FUNCTIONS ####

def Sound(filename):
    """Creates a new Sound object for the given file.
    
    This function is a proxy for the pygame.mixer.Sound class.  That class requires
    some finicky initialization in order to work properly.  In order to hide that from
    you, we have given you this function to use instead.  Treat this function just
    like a constructor (except that the object type is pygame.mixer.Sound, not Sound).
    
        :param filename: string providing the name of a sound file
    
    See the online documentation for more information."""
    assert _is_sound_file(filename), `filename`+' is not a sound file'
    absname = filename if os.path.isabs(filename) else str(os.path.join(SOUND_PATH, filename))
    return pygame.mixer.Sound(absname)


class SoundLibrary(object):
    """Instances are a dictionary that maps sounds to Sound objects.
    
    This class implements to the dictionary interface to make it easier to load
    sounds and manage them.  To load a sound, simply assign it to the library
    object, as follows:
    
        soundlib['soundname'] = 'soundfile.wav'
    
    The sound library will load the sound and map it to 'soundname' as the key.
    To play the sound, we access it as follows:
    
        soundlib['soundname'].play()
    
    Instance Attributes (Hidden):
        data: Dictionary mapping sound names to sound files
    """
    
    def __init__(self):
        """**Constructor**: Create a new, empty sound library."""
        if not _INITIALIZED:
            init()
        self._data = {}
    
    def __len__(self):
        """**Returns**: The number of sounds in this library."""
        return len(self._data)
    
    def __getitem__(self, key):
        """**Returns**: The Sound object for the given sound name.
            
            :param key: The key identifying a sound object
            **Precondition**:: key is a string.
        """
        return self._data[key]
    
    def __setitem__(self, key, filename):
        """Creates a sound object from the file filename and assigns it the given name.
            
            :param key: The key identifying a sound object
            **Precondition**:: key is a string.
            
            :param filename: The name of the file containing the sound source
            **Precondition**:: filename is the name of a valid sound file.
        
        """
        assert is_sound_file(filename), `filename`+' is not a sound file'
        self._data[key] = Sound(filename)
    
    def __delitem__(self, key):
        """Deletes the Sound object for the given sound name.
            
            :param key: The key identifying a sound object
            **Precondition**:: key is a string.
        """
        del self._data[key]
    
    def __iter__(self):
        """**Returns**: The iterator for this sound dictionary."""
        return self._data.iterkeys()
    
    def iterkeys(self):
        """**Returns**: The key iterator for this sound dictionary."""
        return self._data.iterkeys()


#### GEOMETRY CLASSES ####

class GPoint(object):
    """Instances are a Point in 2D space.
    
    This class is used primarily for recording and handling mouse locations."""
    
    # PROPERTIES 
    @property
    def x(self):
        """The x coordinate of the point.
        
        **Invariant**: Must be an int or float."""
        return self._x
    
    @x.setter
    def x(self,value):
        assert type(value) in [int, float], `value`+' is not a number'
        self._x = float(value)
    
    @property
    def y(self):
        """The y coordinate of the point.
        
        **Invariant**: Must be an int or float."""
        return self._y
    
    @y.setter
    def y(self,value):
        assert type(value) in [int, float], `value`+' is not a number'
        self._y = float(value)
    
    # METHODS
    def __init__(self, x=0, y=0):
        """**Constructor**: creates a new GPoint value (x,y).
        
            :param x: initial x value
            **Precondition**: value is an int or float.
        
            :param y: initial y value
            **Precondition**: value is an int or float.
        
        All values are 0.0 by default.        
        """
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        """**Returns**: True if self and other are equivalent GPoint. 
        
        This method uses numpy to test whether the coordinates are 
        "close enough".  It does not require exact equality for floats.
        
            :param other: value to compare against
        """        
        return (type(other) == GPoint and numpy.allclose(self.list(),other.list()))
    
    def __ne__(self, other):
        """**Returns**: True if self and other are not equivalent GPoint. 
        
            :param other: value to compare against
        """
        return not self == other
    
    def __str__(self):
        """**Returns**: Readable String representation of this GPoint. """
        return "("+str(self.x)+","+str(self.y)+")"
    
    def __repr__(self):
        """**Returns**: Unambiguous String representation of this GPoint. """
        return "%s%s" % (self.__class__,self.__str__())
    
    def list(self):
        """**Returns**: A python list with the contents of this GPoint."""
        return [self.x,self.y]
    
    def __add__(self, other):
        """**Returns**: the sum of self and other.
        
        The value returned has the same type as self (so it is either
        a GPoint or is a subclass of GPoint).  The contents of this object
        are not altered.
        
            :param other: tuple value to add
            **Precondition**: value has the same type as self.
        """
        assert (type(other) == type(self)), "value %(value)s is not a of type %(type)s" % {'value': `other`, 'type':`type(self)`}
        result = copy.copy(self)
        result.x += other.x
        result.y += other.y
        return result
    
    def __sub__(self, other):
        """**Returns**: the vector from tail to self.
        
        The value returned is a GPoint representing a vector with this point at its head.
        
            :param other: the tail value for the new Vector
            **Precondition**: value is a Point object.
        """
        assert (type(other) == type(self)), "value %(value)s is not a of type %(type)s" % {'value': `other`, 'type':`type(self)`}
        result = copy.copy(self)
        result.x -= other.x
        result.y -= other.y
        return result
    
    def __mul__(self, scalar):
        """**Returns**: the scalar multiple of self and other.
        
        The value returned is a new GPoint.  The contents of this GPoint
        are not altered.
        
            :param scalar: scalar to multiply by
            **Precondition**: value is an int or float.
        """
        assert (type(scalar) in [int,float]), "value %s is not a number" % `scalar`
        result = copy.copy(self)
        result.x *= scalar
        result.y *= scalar
        result.z *= scalar
        return result
    
    def __rmul__(self, scalar):
        """**Returns**: the scalar multiple of self and other.
        
        The value returned is a new GPoint.  The contents of this GPoint
        are not altered.
        
            :param scalar: scalar to multiply by
            **Precondition**: value is an int or float.
        """
        return self.__mul__(scalar)
    
    def interpolate(self, other, alpha):
        """**Returns**: the interpolation of self and other via alpha.
        
        The value returned has the same type as self (so it is either
        a GPoint or is a subclass of GPoint).  The contents of this object
        are not altered. The resulting value is 
        
            alpha*self+(1-alpha)*other 
        
        according to GPoint addition and scalar multiplication.
        
            :param other: tuple value to interpolate with
            **Precondition**: value has the same type as self.
        
            :param alpha: scalar to interpolate by
            **Precondition**: value is an int or float.
        """
        assert (type(other) == type(self)), "value %(value)s is not a of type %(type)s" % {'value': `other`, 'type':`type(self)`}
        assert (type(alpha) in [int,float]), "value %s is not a number" % `alpha`
        return alpha*self+(1-alpha)*other
    
    def distanceTo(self, other):
        """**Returns**: the Euclidean distance from this point to other
        
            :param other: value to compare against
            **Precondition**: value is a Tuple3D object.
        """
        return numpy.sqrt((self.x-other.x)*(self.x-other.x)+
                          (self.y-other.y)*(self.y-other.y))


class GObject(object):
    """Instances provide basic geometry information for drawing to a `GView`
    
    You should never make a GObject directly.  Instead, you should use one 
    of the subclasses: GRectangle, GEllipse, GLine, GTriangle, GPolygon, GImage, 
    and GLabel."""
    
    # PROPERTIES 
    @property
    def x(self):
        """The horizontal coordinate of the left hand side.
        
        **Invariant**: Must be an int or float. It is equivalent to attribute `left`."""
        return self._x
    
    @x.setter
    def x(self,value):
        assert type(value) in [int, float], `value`+' is not a number'
        self._x = float(value)
        if self._cache_on:
            self._cache(CACHE_POS)
    
    @property
    def y(self):
        """The vertical coordinate of the bottom.
        
        **Invariant**: Must be an int or float. It is equivalent to attribute `bottom`."""
        return self._y
    
    @y.setter
    def y(self,value):
        assert type(value) in [int, float], `value`+' is not a number'
        self._y = float(value)  
        if self._cache_on:
            self._cache(CACHE_POS)
    
    @property
    def width(self):
        """The horizontal width of this shape. Positive values go to the right.
        
        **Invariant**: Must be an int or float.""" 
        return self._width
    
    @width.setter
    def width(self,value):
        assert type(value) in [int, float], `value`+' is not a number'
        self._width = float(value)
        if self._cache_on:
            self._cache(CACHE_SIZE)
    
    @property
    def height(self):
        """The vertical height of this shape. Positive values go up.
        
        **Invariant**: Must be an int or float.""" 
        return self._height
    
    @height.setter
    def height(self,value):
        assert type(value) in [int, float], `value`+' is not a number'
        self._height = float(value)
        if self._cache_on:
            self._cache(CACHE_SIZE)
    
    @property
    def center_x(self):
        """The horizontal center of this shape.
        
        **Invariant**: Must be an int or float. It is equivalent to `x+width/2`""" 
        return self._x+self._width/2.0
    
    @center_x.setter
    def center_x(self,value):
        # Width remains fixed.
        self.x = value - (self._width/2.0)
    
    @property
    def center_y(self):
        """The vertical center of this shape.
        
        **Invariant**: Must be an int or float. It is equivalent to `y+height/2`""" 
        return self._y+self._height/2.0
    
    @center_y.setter
    def center_y(self,value):
        # Width remains fixed.
        self.y = value - (self._height/2.0)
    
    @property
    def left(self):
        """The horizontal coordinate of the left hand side.
        
        **Invariant**: Must be an int or float. It is equivalent to attribute `x`."""
        return self._x
    
    @left.setter
    def left(self,value):
        self.x = value
    
    @property
    def right(self):
        """The horizontal coordinate of the right hand side.
        
        **Invariant**: Must be an int or float. It is equivalent to `x+width`."""
        return self._x + self._width
    
    @right.setter
    def right(self,value):
        self.x = value - self._width
    
    @property
    def bottom(self):
        """The vertical coordinate of the bottom.
        
        **Invariant**: Must be an int or float. It is equivalent to attribute `y`."""
        return self._y
    
    @bottom.setter
    def bottom(self,value):
        self.y = value
    
    @property
    def top(self):
        """The vertical coordinate of the bottom.
        
        **Invariant**: Must be an int or float. It is equivalent to `y+height`."""
        return self._y + self._height
    
    @top.setter
    def top(self,value):
        self.y = value - self._height
    
    @property
    def fillcolor(self):
        """The object fill color.
        
        Used to color the backgrounds or, in the case of solid shapes, the shape
        interior.
        
        **Invariant**: Must be a 4-element list of float between 0 and 1. If you 
        assign it a RGB or HSV object from module `colormodel`, it will convert
        the color for your automatically."""
        return self._fillcolor.rgba
    
    @fillcolor.setter
    def fillcolor(self,value):
        assert _is_color(value), `value`+' is not a valid color'
        if type(value) in [tuple, list] and len(value) == 3:
            value = list(value)+[1.0]
        elif type(value) in [colormodel.RGB, colormodel.HSV]:
            value = value.glColor()
        
        self._fillcolor = Color(value[0],value[1],value[2],value[3])
        if self._cache_on:
            self._cache(CACHE_COLOR)
        
    @property
    def linecolor(self):
        """The object line color.
        
        Used to color the foreground, text, or, in the case of solid shapes, the
        shape border.
        
        **Invariant**: Must be a 4-element list of float between 0 and 1. If you 
        assign it a RGB or HSV object from module `colormodel`, it will convert
        the color for your automatically."""
        return self._linecolor.rgba
    
    @linecolor.setter
    def linecolor(self,value):
        assert _is_color(value), `value`+' is not a valid color'
        if type(value) in [tuple, list] and len(value) == 3:
            value = list(value)+[1.0]
        elif type(value) in [colormodel.RGB, colormodel.HSV]:
            value = value.glColor()
        
        self._linecolor = Color(value[0],value[1],value[2],value[3])
        if self._cache_on:
            self._cache(CACHE_COLOR)
    
    def __init__(self,**keywords):
        """**Constructor**: creates a new GObject to support drawing.
        
            :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide
        it with a list of keyword arguments that initialize various
        attributes.  For example, to initialize the x position and
        the fill color, use the constructor call
        
            GObject(x=2,fillcolor=colormodel.RED)
        
        You do not need to provide the keywords as a dictionary.
        The ** in the parameter `keywords` does that automatically.
        
        Any attribute of this class may be used as a keyword. The
        argument must satisfy the invariants of that attribute. See
        the list of attributes of this class for more information."""
        # Set the properties.
        # Set cache check to correct value
        self._cache_on = False
        
        # Have to initialize size first
        self.width  = keywords['width']  if  'width' in keywords else 0.0
        self.height = keywords['height'] if 'height' in keywords else 0.0
                
        # Now (relative) position
        if 'x' in keywords:
            self.x = keywords['x']
        elif 'left' in keywords:
            self.left = keywords['left']
        elif 'center_x' in keywords:
            self.center_x = keywords['center_x']
        elif 'right' in keywords:
            self.right = keywords['right']
        else:
            self._x = 0.0
        
        if 'y' in keywords:
            self.y = keywords['y']
        elif 'bottom' in keywords:
            self.bottom = keywords['bottom']
        elif 'center_y' in keywords:
            self.center_y = keywords['center_y']
        elif 'top' in keywords:
            self.top = keywords['top']
        else:
            self._y = 0.0
        
        self.fillcolor = keywords['fillcolor'] if 'fillcolor' in keywords else (1.0,1.0,1.0,1.0)
        self.linecolor = keywords['linecolor'] if 'linecolor' in keywords else (0,0,0,1)
    
    def contains(self,x,y):
        """Return: True if this shape contains the point (x,y), False otherwise.
        
            :param x: x coordinate of point to check
            **Precondition**: an int or float
            
            :param y: y coordinate of point to check
            **Precondition**: an int or float
        
        This method always returns `False` for a `GObject`."""
        return False
    
    def _cache(self,style=CACHE_ALL):
        """Helper method to cache data to speed drawing. This method should be  
        overridden for specific drawing instructions."""
        pass
    
    def draw(self,view):
        """Draw this shape in the provide view.
        
            :param view: view to draw to
            **Precondition**: an *instance of* `GView`
        
        Ideally view should be the one provided by `Game`."""
        # No drawing, but turn on the cache
        if not self._cache_on:
            self._cache()
            self._cache_on = True


class GLine(GObject):
    """Instances represent a sequence of line segments
    
    The line is defined by the `points` attribute which is an (even) sequence
    of alternating x and y values. When drawn in a `GView` object, the line
    starts from one x-y pair in `points` and goes to the next x-y pair.  If 
    `points` has length 2n, then the result is n-1 line segments.
    
    The object uses the attribute `linecolor` to determine the color of the
    line.  The attribute `fillcolor` is unused (even though it is inherited
    from `GObject`)."""
    
    # PROPERTIES 
    @property
    def x(self):
        """The horizontal coordinate of the left hand side.
        
        **Invariant**: Immutable float. It is equivalent to attribute `left`."""
        return self._x
    
    @property
    def y(self):
        """The vertical coordinate of the bottom
        
        **Invariant**: Immutable float. It is equivalent to attribute `bottom`."""
        return self._y
    
    @property
    def width(self):
        """The horizontal width of this shape. Positive values go to the right.
        
        **Invariant**: Immutable float.""" 
        return self._width
    
    @property
    def height(self):
        """The vertical height of this shape. Positive values go up.
        
        **Invariant**: Immutable float.""" 
        return self._height
    
    @property
    def center_x(self):
        """The horizontal center of this shape.
        
        **Invariant**: Immutable float. It is equivalent to `x+width/2`""" 
        return (self._x+self._width)/2.0
    
    @property
    def center_y(self):
        """The vertical center of this shape.
        
        **Invariant**: Immutable float. It is equivalent to `y+height/2`""" 
        return (self._y+self._height)/2.0
    
    @property
    def left(self):
        """The horizontal coordinate of the left hand side.
        
        **Invariant**: Immutable float. It is equivalent to attribute `x`."""
        return self._x
    
    @property
    def right(self):
        """The horizontal coordinate of the right hand side.
        
        **Invariant**: Immutable float. It is equivalent to `x+width`."""
        return self._x + self._width
    
    @property
    def bottom(self):
        """The vertical coordinate of the bottom.
        
        **Invariant**: Immutable float. It is equivalent to attribute `y`."""
        return self._y
        
    @property
    def top(self):
        """The vertical coordinate of the bottom.
        
        **Invariant**: Immutable float. It is equivalent to `y+height`."""
        return self._y + self._height
        
    @property
    def points(self):
        """The sequence of points that make up this line.
        
        **Invariant**: Must be a sequence (list or tuple) of int or float. 
        The length of this sequence must be even with length at least 4."""
        return self._points
    
    @points.setter
    def points(self,value):
        assert type(value) in [tuple,list], `value`+' is not a tuple or list'
        assert len(value) % 2 == 0 and len(value) > 2, 'length '+`len(value)`+' is not the correct size'
        assert reduce(_and, map(_is_num,value)), `value`+' is not a tuple of numbers'
        self._points = tuple(value)
        if self._cache_on:
            self._cache(CACHE_ALL)
    
    def __init__(self,**keywords):
        """**Constructor**: creates a new sequence of line segments.
        
            :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide
        it with a list of keyword arguments that initialize various
        attributes. For example, to create a line from (0,0) to
        (2,3), use the constructor call
        
            GLine(points=[0,0,2,3])
        
        This class supports the same keywords as `GObject`, though many of 
        them are unused, as the position and size attributes are now all 
        immutable.  Position and size are computed from the list of points.
        Therefore `point` and `linecolor` are the two primary keywords
        used by this constructor."""
        self._cache_on = False
        self.points = keywords['points'] if 'points' in keywords else ()
        self.fillcolor = keywords['fillcolor'] if 'fillcolor' in keywords else (1,1,1,1)
        self.linecolor = keywords['linecolor'] if 'linecolor' in keywords else (0,0,0,1)
    
    def _cache(self,style=CACHE_ALL):
        """Helper method to cache data to speed drawing. This method should be  
        overridden for specific drawing instructions."""
        mxx = None
        mxy = None
        mnx = None
        mny = None
        
        xpos = True
        for p in self.points:
            if xpos:
                if mxx is None or mxx < p:
                    mxx = p
                if mnx is None or mnx > p:
                    mnx = p
            else:
                if mxy is None or mxy < p:
                    mxy = p
                if mny is None or mny > p:
                    mny = p
            xpos = not xpos
        
        self._x = mnx
        self._y = mny
        self._width  = mxx-mnx
        self._height = mxy-mny
        self._lcache = Line(points=self.points,cap='round',joint='round',close=True)
    
    def contains(self,x,y):
        """Return: True if this shape contains the point (x,y), False otherwise.
        
            :param x: x coordinate of point to check
            **Precondition**: an int or float
            
            :param y: y coordinate of point to check
            **Precondition**: an int or float
        
        This method always returns `False` as a `GLine` has no interior."""
        return False
    
    def draw(self,view):
        """Draw this shape in the provide view.
        
            :param view: view to draw to
            **Precondition**: an *instance of* `GView`
        
        Ideally view should be the one provided by `Game`."""
        # Invoke the cache
        GObject.draw(self,view)
        view.draw(self._linecolor)
        view.draw(self._lcache)


class GTriangle(GLine):
    """Instances represent a solid triangle.
    
    The triangle is defined sequence of three point. Just as with the `GLine` class
    (which is the parent of this class), it has an attribute `point` which represents
    this points as an even-length sequence of ints or floats.
    
    The interior (fill) color of this rectangle is `fillcolor`, while `linecolor`
    is the color of the border."""
    
    @property
    def points(self):
        """The sequence of points that make up this triangle.
        
        **Invariant**: Must be a sequence (list or tuple) of int or float. 
        The length of this sequence must be 6 (for 3 points)."""
        return self._points
    
    @points.setter
    def points(self,value):
        assert type(value) in [tuple,list], `value`+' is not a tuple or list'
        assert len(value) == 6, 'length '+`len(value)`+' does not have 6 elements'
        assert reduce(lambda x, y: x and y, map(_is_num,value)), `value`+' is not a tuple of numbers'
        self._points = tuple(value)
        if self._cache_on:
            self._cache(CACHE_ALL)
    
    def __init__(self,**keywords):
        """**Constructor**: creates a new solid triangle.
        
            :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide it with a 
        list of keyword arguments that initialize various attributes. For 
        example, to create a red triangle with vertices (0,0), (2,3), and (0,4),
        use the constructor call
        
            GTriangle(points=[0,0,2,3,0,4],fillcolor=colormodel.RED)
        
        As with `GLine` the position and size attributes of this class are all
        immutable.  They are computed from the list of points."""
        GLine.__init__(self,**keywords)
    
    def _cache(self,style=CACHE_ALL):
        """Helper method to cache data to speed drawing. This method should be  
        overridden for specific drawing instructions."""
        GLine._cache(self)
        size = 3
        vertices = ()
        for x in range(3):
            vertices += self.points[2*x:2*x+2]+(0,0)
        self._mcache = Mesh(vertices=vertices, indices=range(size), mode='triangle_strip')
    
    def contains(self,x,y):
        """Return: True if this shape contains the point (x,y), False otherwise.
        
            :param x: x coordinate of point to check
            **Precondition**: an int or float
            
            :param y: y coordinate of point to check
            **Precondition**: an int or float
        
        This method uses a standard test for triangle inclusion."""
        return _in_triangle((x,y),self._points)
    
    def draw(self,view):
        """Draw this shape in the provide view.
        
            :param view: view to draw to
            **Precondition**: an *instance of* `GView`
        
        Ideally view should be the one provided by `Game`."""
        GObject.draw(self,view)
        view.draw(self._fillcolor)
        view.draw(self._mcache)
        view.draw(self._linecolor)
        view.draw(self._lcache)


class GPolygon(GLine):
    """Instances represent a solid polygon.  
    
    The polygon is a triangle fan from the attribute `centroid` to the points in the
    attribute `points` (inherited from `GLine`). If you wish to construct a convex 
    polygon, simply store the outside border in `point`, and assign `centroid` any
    point inside the polygon.  If you do not assign a `centroid`, one will be computed
    by averaging all of the points on the boundary.
    
    We use this approach to define polygons as it allows us to avoid complex 
    tesselation algorithms."""
    
    @property
    def centroid(self):
        """The base of the triangle fan representing this polygon.  
        
        In practice it should be an interior point in the shape, preferably the centroid.
        However, this is not enforced.
        
        **Invariant**: Must be a sequence (list or tuple) of int or float. 
        The length of this sequence must be 2 (to represent one point)."""
        return self._centroid

    @centroid.setter
    def centroid(self,value):
        assert type(value) in [tuple,list], `value`+' is not a tuple or list'
        assert len(value) == 2, `value`+' does not have 2 elements'
        assert reduce(lambda x, y: x and y, map(_is_num,value)), `value`+' is not a list of numbers'
        self._centroid = tuple(value)
        self._cache()
        
    def __init__(self,**keywords):
        """**Constructor**: creates a new solid polyon
        
            :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide it with a 
        list of keyword arguments that initialize various attributes. For 
        example, to create a hexagon, use the constructor call
        
            GPolygon(points=[0.87,0.5,0,1,-0.87,0.5,-0.87,-0.5,0,-1,0.87,-0.5])
        
        As with `GLine` the position and size attributes of this class are all
        immutable. They are computed from the list of points. If the shape is
        not convex, you must specify a `centroid` to act as the anchor for
        the triangle fan.  Otherwise, the centroid is computed automatically."""
        GLine.__init__(self,**keywords)

        if 'centroid' in keywords:
            self.centroid = keywords['centroid']
        else:
            xpos = 0.0
            ypos = 0.0
            for i in range(len(self.points)):
                if i % 2 == 0:
                    xpos += self.points[i]
                else:
                    ypos += self.points[i]
            size = float(len(self.points)/2)
            self.centroid = (xpos/size, ypos/size)
    
    def _cache(self,style=CACHE_ALL):
        """Helper method to cache data to speed drawing. This method should be  
        overridden for specific drawing instructions."""
        GLine._cache(self)
        size = len(self.points)/2
        vertices = self.centroid+(0,0)
        for x in range(size):
            vertices += self.points[2*x:2*x+2]+(0,0)
        vertices += self.points[0:2]+(0,0)
        self._mcache = Mesh(vertices=vertices, indices=range(size+2), mode='triangle_fan')
    
    def contains(self,x,y):
        """Return: True if this shape contains the point (x,y), False otherwise.
        
            :param x: x coordinate of point to check
            **Precondition**: an int or float
            
            :param y: y coordinate of point to check
            **Precondition**: an int or float
        
        This method cycles through each triangle in the triangle fan and
        tests each triangle for inclusion."""
        found = False
        for i in xrange(4,len(self._points),2):
            t = self.centroid+self.points[i-4:i]
            found = found or _in_triangle((x,y),t)
        
        return found
    
    def draw(self,view):
        """Draw this shape in the provide view.
        
            :param view: view to draw to
            **Precondition**: an *instance of* `GView`
        
        Ideally view should be the one provided by `Game`."""
        GObject.draw(self,view)
        view.draw(self._fillcolor)
        view.draw(self._mcache)
        view.draw(self._linecolor)
        view.draw(self._lcache)


class GRectangle(GObject):
    """Instances represent a solid rectangle.
    
    The attributes x and y refer to the bottom left corner of the rectangle. The 
    interior (fill) color of this rectangle is `fillcolor`, while `linecolor`
    is the color of the border.
    
    For more fine-grained rectangle placement, you should make use of the attributes 
    `center_x`, `center_y`, `right`, and `top`, all inherited from `GObject`.  
    See that class for more information."""
    
    
    def __init__(self,**keywords):
        """**Constructor**: creates a new solid rectangle
        
            :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide it with a 
        list of keyword arguments that initialize various attributes. For 
        example, to create a red square anchored at (0,0), use the constructor call
        
            GRectangle(x=0,y=0,width=10,height=10,fillcolor=colormodel.RED)
        
        This class supports the all same keywords as `GObject`."""
        GObject.__init__(self,**keywords)
        self._scache = None
        self._lcache = None
    
    def _cache(self,style=CACHE_ALL):
        """Helper method to cache data to speed drawing. This method should be  
        overridden for specific drawing instructions."""
        if self._scache is None:
            self._scache = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
            self._lcache = Rectangle(pos=(self.x-LINE_SIZE,self.y-LINE_SIZE),size=(self.width+2*LINE_SIZE,self.height+2*LINE_SIZE))        
        elif style == CACHE_POS:
            self._scache.pos=(self.x, self.y)
            self._lcache.pos=(self.x-LINE_SIZE, self.y-LINE_SIZE) 
        elif style == CACHE_SIZE:
            self._scache.size=(self.width, self.height)
            self._lcache.size=(self.width+2*LINE_SIZE, self.height+2*LINE_SIZE)
        else:
            self._scache = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
            self._lcache = Rectangle(pos=(self.x-LINE_SIZE,self.y-LINE_SIZE),size=(self.width+2*LINE_SIZE,self.height+2*LINE_SIZE))
    
    def contains(self,x,y):
        """Return: True if this shape contains the point (x,y), False otherwise.
        
            :param x: x coordinate of point to check
            **Precondition**: an int or float
            
            :param y: y coordinate of point to check
            **Precondition**: an int or float
        
        This method uses a standard test for rectangle inclusion."""
        return (self.left <= x and x <= self.right and self.bottom <= y and y <= self.top)
    
    def draw(self,view):
        """Draw this shape in the provide view.
        
            :param view: view to draw to
            **Precondition**: an *instance of* `GView`
        
        Ideally view should be the one provided by `Game`."""
        # Invoke the cache
        GObject.draw(self,view)
        view.draw(self._linecolor)
        view.draw(self._lcache)
        view.draw(self._fillcolor)
        view.draw(self._scache)


class GEllipse(GRectangle):
    """Instances represent a solid ellipse.
    
    The ellipse is the largest one that can be drawn inside of a rectangle whose 
    bottom left corner is at (x,y), with the given width and height.  The interior 
    (fill) color of this ellipse is `fillcolor`, while `linecolor` is the color 
    of the border.
    
    For more fine-grained rectangle placement, you should make use of the attributes 
    `center_x`, `center_y`, `right`, and `top`, all inherited from `GObject`.  
    See that class for more information."""
    
    def __init__(self,**keywords):
        """**Constructor**: creates a new solid ellipse
        
            :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide it with a 
        list of keyword arguments that initialize various attributes. For 
        example, to create a red circle anchored at (0,0), use the constructor call
        
            GEllipse(x=0,y=0,width=10,height=10,fillcolor=colormodel.RED)
        
        This class supports the all same keywords as `GObject`."""
        GRectangle.__init__(self,**keywords)
    
    def _cache(self,style=CACHE_ALL):
        """Helper method to cache data to speed drawing. This method should be  
        overridden for specific drawing instructions."""
        if self._scache is None:
            self._scache = Ellipse(pos=(self.x, self.y), size=(self.width, self.height))
            self._lcache = Ellipse(pos=(self.x-LINE_SIZE,self.y-LINE_SIZE),size=(self.width+2*LINE_SIZE,self.height+2*LINE_SIZE))
        if style == CACHE_POS:
            self._scache.pos=(self.x, self.y)
            self._lcache.pos=(self.x-LINE_SIZE, self.y-LINE_SIZE) 
        elif style == CACHE_SIZE:
            self._scache.size=(self.width, self.height)
            self._lcache.size=(self.width+2*LINE_SIZE, self.height+2*LINE_SIZE)
        else:
            self._scache = Ellipse(pos=(self.x, self.y), size=(self.width, self.height))
            self._lcache = Ellipse(pos=(self.x-LINE_SIZE,self.y-LINE_SIZE),size=(self.width+2*LINE_SIZE,self.height+2*LINE_SIZE))
    
    def contains(self,x,y):
        """Return: True if this shape contains the point (x,y), False otherwise.
        
            :param x: x coordinate of point to check
            **Precondition**: an int or float
            
            :param y: y coordinate of point to check
            **Precondition**: an int or float
        
        This method is better than simple rectangle inclusion.  It checks that
        the point is within the proper radius as well."""
        if not GRectangle.contains(self,x,y):
            return False
        
        cx = self.center_x
        cy = self.center_y
        rx = self.width/2.0
        ry = self.height/2.0
        
        dx = (x-cx)*(x-cx)/(rx*rx)
        dy = (y-cy)*(y-cy)/(ry*ry)
        
        return (dx+dy) <= 1.0


class GImage(GRectangle):
    """Instance represents a rectangular image.
    
    The image is given by a JPEG, PNG, or GIF file whose name is stored
    in the attribute `source`.  Image files should be stored in the
    **Images** directory so that Kivy can find them without the complete
    path name.
    
    In this graphics object, the `linecolor` and `fillcolor` attributes
    are ignored.  The image is displayed as a rectangle whose bottom
    left corner is defined by the attributes `x` and `y`. If the attributes
    `width` and `height` do not agree with the actual size of the image, 
    the image is scaled to fit.
    
    If the image supports transparency, then this object can be used to
    represent irregular shapes.  However, the `contains` method still
    treats this shape as a rectangle.
    """
    @property
    def source(self):
        """The source file for this image.
        
        **Invariant**. Must be a string refering to a valid file."""
        return self._source

    @source.setter
    def source(self,value):
        assert value is None or _is_image_file(value), `value`+' is not an image file'
        self._source = value
        self._cache()
        
    def __init__(self,**keywords):
        """**Constructor**: creates a new rectangle image
        
            :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide it with a 
        list of keyword arguments that initialize various attributes. For 
        example, load the image `beach-ball.png`, use the constructor
        
            GImage(x=0,y=0,width=10,height=10,source='beach-ball.png')
        
        This class supports the all same keywords as `GRectangle`, though
        the color keywords are ignored."""
        GRectangle.__init__(self,**keywords)
        if 'source' in keywords:
            value =  keywords['source']
            assert value is None or _is_image_file(value), `value`+' is not an image file'
            self._source = value
        else:
            self._source = None
        self._scache = None
    
    def _cache(self,style=CACHE_ALL):
        """Helper method to cache data to speed drawing. This method should be  
        overridden for specific drawing instructions."""
        if self._scache is None:
            self._scache = Rectangle(pos=(self.x, self.y), size=(self.width, self.height), source=self._source)        
        elif style == CACHE_POS:
            self._scache.pos=(self.x, self.y)
        elif style == CACHE_SIZE:
            self._scache.size=(self.width, self.height)
        elif style == CACHE_SOURCE:
            self._scache.source = self._source
        else:
            self._scache = Rectangle(pos=(self.x, self.y), size=(self.width, self.height), source=self._source)        
    
    def draw(self,view):
        """Draw this shape in the provide view.
        
            :param view: view to draw to
            **Precondition**: an *instance of* `GView`
        
        Ideally view should be the one provided by `Game`."""
        # Invoke the cache
        GObject.draw(self,view)
        view.draw(self._fillcolor)
        view.draw(self._scache)


class GLabel(GRectangle):
    """Instances represent an (uneditable) text label
    
    The attribute `text` defines the content of this image.  Uses of
    the escape character '\\n' will result in a label that spans multiple
    lines.  The label includes both the text, and a rectangular backdrop
    with bottom left corner at `pos` and width and height `size`.  The
    background color of this rectangle is `fillcolor`, while `linecolor`
    is the color of the text.
    
    The text itself is aligned within this rectangle according to the
    attributes `halign` and `valign`.  See the documentation of these
    attributes for how alignment works.  There are also attributes
    to change the point size, font style, and font name of the text.
    The `size` attribute of this label will grow to ensure that the
    text will fit in the rectangle, no matter the font or point size.
    
    To change the font, you need a .ttf (TrueType Font) file in the
    Fonts folder; refer to the font by filename, including the .ttf.
    If you give no name, it will use the default Kivy font.  The
    `bold` attribute only works for the default Kivy font; for other
    fonts you will need the .ttf file for the bold version of that
    font.  See `ComicSans.ttf` and `ComicSansBold.ttf` for an example."""
    
    @property
    def font_size(self):
        """Size of the text font in points.
        
        **Invariant**: A positive number (int or float)"""
        return self._label.font_size

    @font_size.setter
    def font_size(self,value):
        assert type(value) in (int,float), `value`+' is not a number'
        self._label.font_size = value
        self._label.texture_update()

    @property
    def font_name(self):
        """File name for the .ttf file to use as a font
        
        **Invariant**: string referring to a .ttf file in folder Fonts"""
        return self._label.font_name

    @font_name.setter
    def font_name(self,value):
        assert _is_font_file(value), `value`+' is not a font name'
        self._label.font_name = value
        self._label.texture_update()

    @property
    def bold(self):
        """Boolean indicating whether or not the text should be bold.
        
        Only works on the default Kivy font.  Does not work on custom
        .ttf files.  In that case, you need the bold version of the
        .ttf file.  See `ComicSans.ttf` and `ComicSansBold.ttf` for
        an example.
        
        **Invariant**: boolean"""
        return self._label.bold

    @bold.setter
    def bold(self,value):
        assert type(value) == bool, `value`+' is not a bool'
        self._label.bold = value
        self._label.texture_update()

    @property
    def text(self):
        """Text for this label.
        
        The text in the label is displayed as a single line, or broken
        up into multiple lines in the presence of the escape character
        '\\n'. The `size` attribute of this label grows to make sure
        that the entire text fits inside of the rectangle.
        
        **Invariant**: string"""
        return self._label.text
    
    @text.setter
    def text(self,value):
        assert type(value) == str, `value`+' is not a string'
        self._label.text = value
        self._label.texture_update()

    @property
    def halign(self):
        """Horizontal alignment for this label.
        
        The text is anchored inside of the label rectangle on either the
        left, the right or the center.  This means that as the size of
        the label increases, the text will still stay rooted at that
        anchor.
        
        **Invariant**: one of 'left', 'right', or 'center'"""
        return self._halign
    
    @halign.setter
    def halign(self,value):
        assert value in ('left','right','center'), `value`+' is not a valid horizontal alignment'
        self._halign = value
        self._label.halign = value
        self._cache(CACHE_POS)

    @property
    def valign(self):
        """Vertical alignment for this label.
        
        The text is anchored inside of the label rectangle at either the
        top, the bottom or the middle.  This means that as the size of
        the label increases, the text will still stay rooted at that
        anchor.
        
        **Invariant**: one of 'top', 'bottom', or 'middle'"""
        return self._valign
    
    @valign.setter
    def valign(self,value):
        assert value in ('top','middle','bottom'), `value`+' is not a valid vertical alignment'
        self._valign = value
        self._label.valign = value
        self._cache(CACHE_POS)

    def __init__(self,**keywords):
        """**Constructor**: creates a new text label.
        
            :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide
        it with a list of keyword arguments that initialize various
        attributes. For example, to create a label containing the
        word 'Hello', use the constructor call
        
            GLabel(text='Hello')
        
        This class supports the same keywords as `GObject`, as well
        as additional attributes for the text properties (e.g. font
        size and name)."""
        if not 'fillcolor' in keywords:
            keywords['fillcolor'] = [0.0,0.0,0.0,0.0]
        
        GRectangle.__init__(self,**keywords)
        self._label = Label(**keywords)
        self._label.size_hint = (None,None)
        
        if 'halign' in keywords:
            self._halign = keywords['halign']
        else:
            self._halign = 'left'
            self._label._halign = 'left'

        if 'valign' in keywords:
            self._valign = keywords['valign']
        else:
            self._valign = 'bottom'
            self._label._valign = 'bottom'
        
        self._label.bind(texture_size=self._callback)

    def _callback(self,instance=None,value=None):
        """Workaround to deal with parameter requirements for callbacks"""
        self._cache()
    
    def _cache(self,style=CACHE_ALL):
        """Helper method to cache data to speed drawing. This method should be  
        overridden for specific drawing instructions."""
        if style == CACHE_POS and not self._scache is None:
            self._label.pos=(self.x, self.y)
            self._scache.pos = (self.x, self.y)
            return
    
        self._label.size = self._label.texture_size
        self._label.pos = (self.x, self.y)
        self._label.color = self._linecolor.rgba
        
        # Resize the outside if necessary
        width  = max(self._width,self._label.width)
        height = max(self._height,self._label.height)
   
        # Reset to horizontal anchor position.
        if self._halign == 'left':
            self._width = width
        elif self._halign == 'center':
            cx = self.center_x
            self._width = width
            self._x = cx-(self._width/2.0)
        else:
            right = self.right
            self._width = width
            self._x = right-self._width

        # Reset to vertical anchor position.
        if self._valign == 'top':
            top = self.top
            self._height = height
            self._y = top - self._height
        elif self._valign == 'middle':
            cy = self.center_y
            self._height = height
            self._y = cy - (self._height/2.0)
        else:
            self._height = height
        
        # Internal Horizontal placement
        if self._halign == 'left':
            self._label.x = self.x
        elif self._halign == 'center':
            self._label.center_x = self.center_x
        else: # 'ightr'
            self._label.right = self.right
        
        # Internal Vertical placement
        if self._valign == 'top':
            self._label.top = self.top
        elif self._valign == 'middle':
            self._label.center_y = self.center_y
        else: # 'bottom'
            self._label.y = self.y
        
        self._scache = Rectangle(pos=(self.x, self.y), size=(self.width, self.height))
    
    def draw(self,view):
        """Draw this shape in the provide view.
        
            :param view: view to draw to
            **Precondition**: an *instance of* `GView`
        
        Ideally view should be the one provided by `Game`."""
        # Invoke the cache
        GObject.draw(self,view)
        view.draw(self._fillcolor)
        view.draw(self._scache)
        view.draw(self._label.canvas)


#### APPLICATION CLASSES ####

class GView(FloatLayout):
    """The view class for a `Game` application.
    
    You may need to access an instance of this class to draw `GObject` 
    instances.  However, you will never need to construct one.
    You should only use the one provided in the `view` attribute of
    `Game`. See class `Game` for more information."""
    
    @property
    def touch(self):
        """The current (x,y) coordinate of the mouse, if pressed.
        
        This method only returns coordinates if the mouse button is pressed.
        If the mouse button is not pressed it returns None. The origin (0,0)
        corresponds to the bottom left corner of the application window.
        
        There is currently no way to get the location of the mouse when
        the button is not preseed.  This a limitation of Kivy.
        
        **Invariant**: Either a GPoint or None (if there is no touch)."""
        if self._touch is None:
            return None
        
        return GPoint(self._touch.x,self._touch.y)
    
    def __init__(self):
        """**Initializer**: creates a new GView"""
        FloatLayout.__init__(self)
        self.bind(on_touch_down=self._capture_touch)
        self.bind(on_touch_move=self._capture_touch)
        self.bind(on_touch_up=self._release_touch)
        self._frame = InstructionGroup()
        self.canvas.add(self._frame)
        self._touch = None
    
    def _capture_touch(self,view,touch):
        """Helper method to respond (and grap) a mouse press"""
        self._touch = touch
        #self._touch.grab(self)
    
    def _release_touch(self,view,touch):
        """Helper method to respond (and release) a mouse release"""
        self._touch = None
    
    def draw(self,cmd):
        """Adds the giving drawing command to this canvas for drawing.
        
            :param cmd: The drawing command
            **Invariant**: cmd is a Kivy drawing instruction.
        """
        self._frame.add(cmd)
    
    def _redraw(self):
        """Helper called to refresh the screen each animation frame"""
        self.canvas.remove(self._frame)
        self._frame.clear()
        self._frame = InstructionGroup()
        self.canvas.add(self._frame)
        self._frame.add(Color(1,1,1))
        self._frame.add(Rectangle(pos=self.pos,size=self.size))


class GameApp(kivy.app.App):
    """Primary controller class for a simple game application."""
    
    @property
    def width(self):
        """The window width
        
        **Invariant**: Immutable float."""
        return self._wwidth
    
    @property
    def height(self):
        """The window height
        
        **Invariant**: Immutable float."""
        return self._wheight

    @property
    def fps(self):
        """Target animation FPS
        
        We cannot guarantee that the FPS is achievable.  Python is not super
        fast. We do try for 60 FPS, however.
        
        **Invariant**: Immutable float > 0."""
        return self._fps
    
    @property
    def view(self):
        """The Game view.
        
        Pass this attribute to the `draw` method of a `GObject` instance 
        to draw it.
        
        Invariant**: Immutable instance of GView."""
        return self._view
    
    def __init__(self,**keywords):
        """**Constructor**: creates, but does not start, a new game.
        
            :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide it with a 
        list of keyword arguments that initialize various attributes. The
        primary user defined attributes are the window width and height.
        For example, to create a game that fits inside of a 400x400
        window, the constructor
        
            Game(width=400,height=400)
        
        The game window will not show until you start the game.
        To start the game, use the method `run()`."""
        w = keywords['width']  if  'width' in keywords else 0.0
        h = keywords['height'] if 'height' in keywords else 0.0
        f = keywords['fps']    if 'fps'    in keywords else 60.0

        assert type(w) in [int, float], `w`+' is not a number'
        assert type(h) in [int, float], `h`+' is not a number'
        assert type(f) in [int, float], `f`+' is not a number'
        assert f > 0.0, `f`+' is not positive'
        self._wwidth = w
        self._wheight = h
        self._fps = f
        Config.set('graphics', 'width', str(self.width))
        Config.set('graphics', 'height', str(self.height))
        
        # Tell Kivy to build the application
        kivy.app.App.__init__(self,**keywords)
    
    def build(self):
        """Special Kivy method to initialize the graphics window"""
        self._view = GView()
        self._view.size_hint = (1,1)
        return self.view
    
    def _startup(self,dt):
        """Called to initialize.
        
        This is a callback-proxy for method init().  It handles
        important issues behind the scenes."""
        Clock.schedule_interval(self._refresh,1.0/self._fps)
        self.init()
    
    def _refresh(self,dt):
        """Called every animation frame.
        
            :param dt: time in seconds since last update
            **Precondition**: a number (int or float)
        
        This is a callback-proxy for method update().  It handles
        important issues behind the scenes."""
        self.view._redraw()
        self.update(dt)
        self.draw()
    
    def run(self):
        """Display the game window and start the game"""
        Clock.schedule_once(self._startup,-1)
        kivy.app.App.run(self)
    
    def stop(self):
        """Close the game window and exit Python.
        
        You should never need to call this"""
        kivy.app.App.stop(self)
        sys.exit(0)
    
    def init(self):
        """Initialize the game state.
        
        This method is distinct from the built-in initializer __init__.
        This method is called once the game is running.  You should use
        it to initialize any game specific attributes."""
        pass
    
    def update(self,dt):
        """Called every animation frame.
        
            :param dt: time in seconds since last update
            **Precondition**: a number (int or float)
        
        This method is called 60x a second to provide on-screen animation.
        Think of it as the body of the loop.  It is best to have fields
        that represent the current animation state so that you know where
        you are in the animation."""
        pass
    
    def draw(self):
        pass
