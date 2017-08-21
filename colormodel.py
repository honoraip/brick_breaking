# colormodel.py
# Walker M. White (wmw2), Lillian Lee (LJL2), Steve Marschner (srm2)
# Feb 25, 2013
"""Class for RGB color objects, where the channel values are all ints in 0..255.

    In the docstrings below, we use David Gries' range notation: a..b,
    where a and b are integers and b >= a-1, represents the set of integers
    from a to b, inclusive.  If b == a-1, then a..b indicates the empty range
    that contains no integers.

    Don't confuse this range notation with python's range() function.  The Gries
    ".." range notation is useful in discussions and descriptions; Python's
    range() function is useful in lines of actual code.  a..b includes b;
    range(a,b) does NOT include b.

"""


class RGB(object):
    """An instance is a RGB color value."""

    # METHODS

    def __init__(self, r, g, b, a=255):
        """**Constructor**: creates a new RGB object (r,g,b,a).

            :param r: initial red value            :param g: initial green value
            :param b: initial blue value
            :param a: initial alpha value (default 255)

        The alpha channel is 255 by default, unless otherwise specified,
        so you can create RGB objects by specifying only three parameters.
        Thus, saying RGB(255, 255, 255) is a valid call.

        **Precondition**: r, g, b, a must all be in 0..255
        (using Gries range notation, explained in colormodel.py's docstring).
        """
        for value in (r,g,b,a):
            if type(value) != int:
                raise TypeError("value %s is not an int" % repr(value))
            if value < 0 or value > 255:
                raise ValueError("value %s is outside of range [0,255]" % repr(value))

        self.red = r
        self.green = g
        self.blue = b
        self.alpha = a

    def __eq__(self, other):
        """Returns: True if self and other are equivalent RGB colors. """
        return (type(other) == RGB and self.red == other.red and
                self.green == other.green and self.blue == other.blue and
                self.alpha == other.alpha)

    def __ne__(self, other):
        """Returns: True if self and other are not equivalent RGB colors. """
        return (type(other) != RGB or self.red != other.red or
                self.green != other.green or self.blue != other.blue or
                self.alpha != other.alpha)

    def __str__(self):
        """Returns: Readable string representation of this color. """
        from a3 import rgb_to_string # local to prevent circular import
        return rgb_to_string(self)

    def __repr__(self):
        """Returns: Unambiguous string representation of this color. """
        return "(red="+str(self.red)+",green="+str(self.green)+",blue="+str(self.blue)+")"

    def glColor(self):
        """Returns: 4-element list of the attributes scaled to be between 0 and 1,
        inclusive

        This is a conversion of this object's values into a format that can be
        used in openGL graphics"""
        return [self.red/255.0, self.green/255.0, self.blue/255.0, self.alpha/255.0]

    def turtleColor(self):
        """Returns: 3-element tuple of the attributes scaled to be between 0 and 1,
        inclusive

        This is a conversion of this object's values into a format that can be
        used in turtle graphics in CS1110 A4."""
        return (self.red/255.0, self.green/255.0, self.blue/255.0)


# Color Constants


# The color Carnelian, or Cornell Red

CARNELIAN = RGB(179, 27, 27)

#: The color white

WHITE = RGB(255, 255, 255)

#: The color light gray

LIGHT_GRAY = RGB(192, 192, 192)

#: The color gray

GRAY = RGB(128, 128, 128)

#: The color dark gray

DARK_GRAY = RGB(64, 64, 64)

#: The color black

BLACK = RGB(0, 0, 0)

#: The color red,

RED = RGB(255, 0, 0)

#: The color pink

PINK = RGB(255, 175, 175)

#: The color orange

ORANGE = RGB(255, 200, 0)

#: The color yellow

YELLOW = RGB(255, 255, 0)

#: The color green

GREEN = RGB(0, 255, 0)

#: The color magenta

MAGENTA = RGB(255, 0, 255)

#: The color cyan

CYAN = RGB(0, 255, 255)

#: The color blue

BLUE = RGB(0, 0, 255)