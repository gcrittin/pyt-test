"""
stddraw.py

The stddraw module defines functions that allow the user to create a
drawing.  A drawing appears on the canvas.  The canvas appears
in the window.  As a convenience, the module also imports the
commonly used Color objects defined in the color module.
"""

import os
import sys
import time

import pygame
import pygame.font
import pygame.gfxdraw

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

if sys.hexversion < 0x03000000:
    import Tkinter
    import tkMessageBox
    import tkFileDialog
else:
    import tkinter as Tkinter
    import tkinter.messagebox as tkMessageBox
    import tkinter.filedialog as tkFileDialog

# -----------------------------------------------------------------------

# Define colors so clients need not import the color module.

from stdlib.color import WHITE
from stdlib.color import BLACK
from stdlib.color import RED
from stdlib.color import GREEN
from stdlib.color import BLUE
from stdlib.color import CYAN
from stdlib.color import MAGENTA
from stdlib.color import YELLOW
from stdlib.color import DARK_RED
from stdlib.color import DARK_GREEN
from stdlib.color import DARK_BLUE
from stdlib.color import ORANGE
from stdlib.color import PINK

# -----------------------------------------------------------------------

# Default Sizes and Values

_BORDER = 0.0
# _BORDER = 0.05
_DEFAULT_XMIN = 0.0
_DEFAULT_XMAX = 1.0
_DEFAULT_YMIN = 0.0
_DEFAULT_YMAX = 1.0
_DEFAULT_CANVAS_SIZE = 512
_DEFAULT_PEN_RADIUS = .005  # Maybe change this to 0.0 in the future.
_DEFAULT_PEN_COLOR = BLACK

_DEFAULT_FONT_FAMILY = 'Helvetica'
_DEFAULT_FONT_SIZE = 12

_xmin = None
_ymin = None
_xmax = None
_ymax = None

_fontFamily = _DEFAULT_FONT_FAMILY
_fontSize = _DEFAULT_FONT_SIZE

_canvasWidth = float(_DEFAULT_CANVAS_SIZE)
_canvasHeight = float(_DEFAULT_CANVAS_SIZE)
_pen_radius = None
_penColor = _DEFAULT_PEN_COLOR
_keysTyped = []

# Has the window been created?
_windowCreated = False

# -----------------------------------------------------------------------
# Begin added by Alan J. Broder
# -----------------------------------------------------------------------

# Keep track of mouse status

# Has the mouse been left-clicked since the last time we checked?
_mousePressed = False

# The position of the mouse as of the most recent mouse click
_mousePos = None


# -----------------------------------------------------------------------
# End added by Alan J. Broder
# -----------------------------------------------------------------------

# -----------------------------------------------------------------------

def _pygame_color(c):
    """
    Convert c, an object of type color.Color, to an equivalent object
    of type pygame.Color.  Return the result.
    """
    r = c.get_red()
    g = c.get_green()
    b = c.get_blue()
    return pygame.Color(r, g, b)


# -----------------------------------------------------------------------

# Private functions to scale and factor X and Y values.

def _scale_x(x):
    return _canvasWidth * (x - _xmin) / (_xmax - _xmin)


def _scale_y(y):
    return _canvasHeight * (_ymax - y) / (_ymax - _ymin)


def _factor_x(w):
    return w * _canvasWidth / abs(_xmax - _xmin)


def _factor_y(h):
    return h * _canvasHeight / abs(_ymax - _ymin)


# -----------------------------------------------------------------------
# Begin added by Alan J. Broder
# -----------------------------------------------------------------------

def _user_x(x):
    return _xmin + x * (_xmax - _xmin) / _canvasWidth


def _user_y(y):
    return _ymax - y * (_ymax - _ymin) / _canvasHeight


# -----------------------------------------------------------------------
# End added by Alan J. Broder
# -----------------------------------------------------------------------

# -----------------------------------------------------------------------

def set_canvas_size(w=_DEFAULT_CANVAS_SIZE, h=_DEFAULT_CANVAS_SIZE):
    """
    Set the size of the canvas to w pixels wide and h pixels high.
    Calling this function is optional. If you call it, you must do
    so before calling any drawing function.
    """
    global _background
    global _surface
    global _canvasWidth
    global _canvasHeight
    global _windowCreated

    if _windowCreated:
        raise Exception('The stddraw window already was created')

    if (w < 1) or (h < 1):
        raise Exception('width and height must be positive')

    _canvasWidth = w
    _canvasHeight = h
    _background = pygame.display.set_mode([w, h])
    pygame.display.set_caption('stddraw window (r-click to save)')
    _surface = pygame.Surface((w, h))
    _surface.fill(_pygame_color(WHITE))
    _windowCreated = True


def set_xscale(min=_DEFAULT_XMIN, max=_DEFAULT_XMAX):
    """
    Set the x-scale of the canvas such that the minimum x value
    is min and the maximum x value is max.
    """
    global _xmin
    global _xmax
    min = float(min)
    max = float(max)
    if min >= max:
        raise Exception('min must be less than max')
    size = max - min
    _xmin = min - _BORDER * size
    _xmax = max + _BORDER * size


def set_yscale(min=_DEFAULT_YMIN, max=_DEFAULT_YMAX):
    """
    Set the y-scale of the canvas such that the minimum y value
    is min and the maximum y value is max.
    """
    global _ymin
    global _ymax
    min = float(min)
    max = float(max)
    if min >= max:
        raise Exception('min must be less than max')
    size = max - min
    _ymin = min - _BORDER * size
    _ymax = max + _BORDER * size


def set_pen_radius(r=_DEFAULT_PEN_RADIUS):
    """
    Set the pen radius to r, thus affecting the subsequent drawing
    of points and lines. If r is 0.0, then points will be drawn with
    the minimum possible radius and lines with the minimum possible
    width.
    """
    global _pen_radius
    r = float(r)
    if r < 0.0:
        raise Exception('Argument to setPenRadius() must be non-neg')
    _pen_radius = r * float(_DEFAULT_CANVAS_SIZE)


def set_pen_color(c=_DEFAULT_PEN_COLOR):
    """
    Set the pen color to c, where c is an object of class color.Color.
    c defaults to stddraw.BLACK.
    """
    global _penColor
    _penColor = c


def set_font_family(f=_DEFAULT_FONT_FAMILY):
    """
    Set the font family to f (e.g. 'Helvetica' or 'Courier').
    """
    global _fontFamily
    _fontFamily = f


def set_font_size(s=_DEFAULT_FONT_SIZE):
    """
    Set the font size to s (e.g. 12 or 16).
    """
    global _fontSize
    _fontSize = s


# -----------------------------------------------------------------------

def _make_sure_window_created():
    global _windowCreated
    if not _windowCreated:
        set_canvas_size()
        _windowCreated = True


# -----------------------------------------------------------------------

# Functions to draw shapes, text, and images on the background canvas.

def _pixel(x, y):
    """
    Draw on the background canvas a pixel at (x, y).
    """
    _make_sure_window_created()
    xs = _scale_x(x)
    xy = _scale_y(y)
    pygame.gfxdraw.pixel(
        _surface,
        int(round(xs)),
        int(round(xy)),
        _pygame_color(_penColor))


def point(x, y):
    """
    Draw on the background canvas a point at (x, y).
    """
    _make_sure_window_created()
    x = float(x)
    y = float(y)
    # If the radius is too small, then simply draw a pixel.
    if _pen_radius <= 1.0:
        _pixel(x, y)
    else:
        xs = _scale_x(x)
        ys = _scale_y(y)
        pygame.draw.ellipse(
            _surface,
            _pygame_color(_penColor),
            pygame.Rect(
                xs - _pen_radius,
                ys - _pen_radius,
                _pen_radius * 2.0,
                _pen_radius * 2.0),
            0)


def _thick_line(x0, y0, x1, y1, r):
    """
    Draw on the background canvas a line from (x0, y0) to (x1, y1).
    Draw the line with a pen whose radius is r.
    """
    xs0 = _scale_x(x0)
    ys0 = _scale_y(y0)
    xs1 = _scale_x(x1)
    ys1 = _scale_y(y1)
    if (abs(xs0 - xs1) < 1.0) and (abs(ys0 - ys1) < 1.0):
        filledCircle(x0, y0, r)
        return
    xMid = (x0 + x1) / 2
    yMid = (y0 + y1) / 2
    _thick_line(x0, y0, xMid, yMid, r)
    _thick_line(xMid, yMid, x1, y1, r)


def line(x0, y0, x1, y1):
    """
    Draw on the background canvas a line from (x0, y0) to (x1, y1).
    """

    THICK_LINE_CUTOFF = 3  # pixels

    _make_sure_window_created()

    x0 = float(x0)
    y0 = float(y0)
    x1 = float(x1)
    y1 = float(y1)

    lineWidth = _pen_radius * 2.0
    if lineWidth == 0.0: lineWidth = 1.0
    if lineWidth < THICK_LINE_CUTOFF:
        x0s = _scale_x(x0)
        y0s = _scale_y(y0)
        x1s = _scale_x(x1)
        y1s = _scale_y(y1)
        pygame.draw.line(
            _surface,
            _pygame_color(_penColor),
            (x0s, y0s),
            (x1s, y1s),
            int(round(lineWidth)))
    else:
        _thick_line(x0, y0, x1, y1, _pen_radius / _DEFAULT_CANVAS_SIZE)


def circle(x, y, r):
    """
    Draw on the background canvas a circle of radius r centered on
    (x, y).
    """
    _make_sure_window_created()
    x = float(x)
    y = float(y)
    r = float(r)
    ws = _factor_x(2.0 * r)
    hs = _factor_y(2.0 * r)
    # If the radius is too small, then simply draw a pixel.
    if (ws <= 1.0) and (hs <= 1.0):
        _pixel(x, y)
    else:
        xs = _scale_x(x)
        ys = _scale_y(y)
        pygame.draw.ellipse(
            _surface,
            _pygame_color(_penColor),
            pygame.Rect(xs - ws / 2.0, ys - hs / 2.0, ws, hs),
            int(round(_pen_radius)))


def filledCircle(x, y, r):
    """
    Draw on the background canvas a filled circle of radius r
    centered on (x, y).
    """
    _make_sure_window_created()
    x = float(x)
    y = float(y)
    r = float(r)
    ws = _factor_x(2.0 * r)
    hs = _factor_y(2.0 * r)
    # If the radius is too small, then simply draw a pixel.
    if (ws <= 1.0) and (hs <= 1.0):
        _pixel(x, y)
    else:
        xs = _scale_x(x)
        ys = _scale_y(y)
        pygame.draw.ellipse(
            _surface,
            _pygame_color(_penColor),
            pygame.Rect(xs - ws / 2.0, ys - hs / 2.0, ws, hs),
            0)


def rectangle(x, y, w, h):
    """
    Draw on the background canvas a rectangle of width w and height h
    whose lower left point is (x, y).
    """
    global _surface
    _make_sure_window_created()
    x = float(x)
    y = float(y)
    w = float(w)
    h = float(h)
    ws = _factor_x(w)
    hs = _factor_y(h)
    # If the rectangle is too small, then simply draw a pixel.
    if (ws <= 1.0) and (hs <= 1.0):
        _pixel(x, y)
    else:
        xs = _scale_x(x)
        ys = _scale_y(y)
        pygame.draw.rect(
            _surface,
            _pygame_color(_penColor),
            pygame.Rect(xs, ys - hs, ws, hs),
            int(round(_pen_radius)))


def filledRectangle(x, y, w, h):
    """
    Draw on the background canvas a filled rectangle of width w and
    height h whose lower left point is (x, y).
    """
    global _surface
    _make_sure_window_created()
    x = float(x)
    y = float(y)
    w = float(w)
    h = float(h)
    ws = _factor_x(w)
    hs = _factor_y(h)
    # If the rectangle is too small, then simply draw a pixel.
    if (ws <= 1.0) and (hs <= 1.0):
        _pixel(x, y)
    else:
        xs = _scale_x(x)
        ys = _scale_y(y)
        pygame.draw.rect(
            _surface,
            _pygame_color(_penColor),
            pygame.Rect(xs, ys - hs, ws, hs),
            0)


def square(x, y, r):
    """
    Draw on the background canvas a square whose sides are of length
    2r, centered on (x, y).
    """
    _make_sure_window_created()
    rectangle(x - r, y - r, 2.0 * r, 2.0 * r)


def filledSquare(x, y, r):
    """
    Draw on the background canvas a filled square whose sides are of
    length 2r, centered on (x, y).
    """
    _make_sure_window_created()
    filledRectangle(x - r, y - r, 2.0 * r, 2.0 * r)


def polygon(x, y):
    """
    Draw on the background canvas a polygon with coordinates
    (x[i], y[i]).
    """
    global _surface
    _make_sure_window_created()
    # Scale X and Y values.
    xScaled = []
    for xi in x:
        xScaled.append(_scale_x(float(xi)))
    yScaled = []
    for yi in y:
        yScaled.append(_scale_y(float(yi)))
    points = []
    for i in range(len(x)):
        points.append((xScaled[i], yScaled[i]))
    points.append((xScaled[0], yScaled[0]))
    pygame.draw.polygon(
        _surface,
        _pygame_color(_penColor),
        points,
        int(round(_pen_radius)))


def filledPolygon(x, y):
    """
    Draw on the background canvas a filled polygon with coordinates
    (x[i], y[i]).
    """
    global _surface
    _make_sure_window_created()
    # Scale X and Y values.
    xScaled = []
    for xi in x:
        xScaled.append(_scale_x(float(xi)))
    yScaled = []
    for yi in y:
        yScaled.append(_scale_y(float(yi)))
    points = []
    for i in range(len(x)):
        points.append((xScaled[i], yScaled[i]))
    points.append((xScaled[0], yScaled[0]))
    pygame.draw.polygon(_surface, _pygame_color(_penColor), points, 0)


def text(x, y, s):
    """
    Draw string s on the background canvas centered at (x, y).
    """
    _make_sure_window_created()
    x = float(x)
    y = float(y)
    xs = _scale_x(x)
    ys = _scale_y(y)
    font = pygame.font.SysFont(_fontFamily, _fontSize)
    text = font.render(s, 1, _pygame_color(_penColor))
    textpos = text.get_rect(center=(xs, ys))
    _surface.blit(text, textpos)


def picture(pic, x=None, y=None):
    """
    Draw pic on the background canvas centered at (x, y).  pic is an
    object of class picture.Picture. x and y default to the midpoint
    of the background canvas.
    """
    global _surface
    _make_sure_window_created()
    # By default, draw pic at the middle of the surface.
    if x is None:
        x = (_xmax + _xmin) / 2.0
    if y is None:
        y = (_ymax + _ymin) / 2.0
    x = float(x)
    y = float(y)
    xs = _scale_x(x)
    ys = _scale_y(y)
    ws = pic.width()
    hs = pic.height()
    picSurface = pic._surface  # violates encapsulation
    _surface.blit(picSurface, [xs - ws / 2.0, ys - hs / 2.0, ws, hs])


def clear(c=WHITE):
    """
    Clear the background canvas to color c, where c is an
    object of class color.Color. c defaults to stddraw.WHITE.
    """
    _make_sure_window_created()
    _surface.fill(_pygame_color(c))


def save(f):
    """
    Save the window canvas to file f.
    """
    _make_sure_window_created()

    # if sys.hexversion >= 0x03000000:
    #    # Hack because Pygame without full image support
    #    # can handle only .bmp files.
    #    bmpFileName = f + '.bmp'
    #    pygame.image.save(_surface, bmpFileName)
    #    os.system('convert ' + bmpFileName + ' ' + f)
    #    os.system('rm ' + bmpFileName)
    # else:
    #    pygame.image.save(_surface, f)

    pygame.image.save(_surface, f)


# -----------------------------------------------------------------------

def _show():
    """
    Copy the background canvas to the window canvas.
    """
    _background.blit(_surface, (0, 0))
    pygame.display.flip()
    _checkForEvents()


def _showAndWaitForever():
    """
    Copy the background canvas to the window canvas. Then wait
    forever, that is, until the user closes the stddraw window.
    """
    _make_sure_window_created()
    _show()
    QUANTUM = .1
    while True:
        time.sleep(QUANTUM)
        _checkForEvents()


def show(msec=float('inf')):
    """
    Copy the background canvas to the window canvas, and
    then wait for msec milliseconds. msec defaults to infinity.
    """
    if msec == float('inf'):
        _showAndWaitForever()

    _make_sure_window_created()
    _show()
    _checkForEvents()

    # Sleep for the required time, but check for events every
    # QUANTUM seconds.
    QUANTUM = .1
    sec = msec / 1000.0
    if sec < QUANTUM:
        time.sleep(sec)
        return
    secondsWaited = 0.0
    while secondsWaited < sec:
        time.sleep(QUANTUM)
        secondsWaited += QUANTUM
        _checkForEvents()


# -----------------------------------------------------------------------

def _saveToFile():
    """
    Display a dialog box that asks the user for a file name.  Save the
    drawing to the specified file.  Display a confirmation dialog box
    if successful, and an error dialog box otherwise.  The dialog boxes
    are displayed using Tkinter, which (on some computers) is
    incompatible with Pygame. So the dialog boxes must be displayed
    from child processes.
    """
    import subprocess
    _make_sure_window_created()

    stddrawPath = os.path.realpath(__file__)

    childProcess = subprocess.Popen(
        [sys.executable, stddrawPath, 'getFileName'],
        stdout=subprocess.PIPE)
    so, se = childProcess.communicate()
    fileName = so.strip()

    if sys.hexversion >= 0x03000000:
        fileName = fileName.decode('utf-8')

    if fileName == '':
        return

    if not fileName.endswith(('.jpg', '.png')):
        childProcess = subprocess.Popen(
            [sys.executable, stddrawPath, 'reportFileSaveError',
             'File name must end with ".jpg" or ".png".'])
        return

    try:
        save(fileName)
        childProcess = subprocess.Popen(
            [sys.executable, stddrawPath, 'confirmFileSave'])
    except (pygame.error) as e:
        childProcess = subprocess.Popen(
            [sys.executable, stddrawPath, 'reportFileSaveError', str(e)])


def _checkForEvents():
    """
    Check if any new event has occured (such as a key typed or button
    pressed).  If a key has been typed, then put that key in a queue.
    """
    global _surface
    global _keysTyped

    # -------------------------------------------------------------------
    # Begin added by Alan J. Broder
    # -------------------------------------------------------------------
    global _mousePos
    global _mousePressed
    # -------------------------------------------------------------------
    # End added by Alan J. Broder
    # -------------------------------------------------------------------

    _make_sure_window_created()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            _keysTyped = [event.unicode] + _keysTyped
        elif (event.type == pygame.MOUSEBUTTONUP) and \
                (event.button == 3):
            _saveToFile()

        # ---------------------------------------------------------------
        # Begin added by Alan J. Broder
        # ---------------------------------------------------------------
        # Every time the mouse button is pressed, remember
        # the mouse position as of that press.
        elif (event.type == pygame.MOUSEBUTTONDOWN) and \
                (event.button == 1):
            _mousePressed = True
            _mousePos = event.pos
            # ---------------------------------------------------------------
        # End added by Alan J. Broder
        # ---------------------------------------------------------------


# -----------------------------------------------------------------------

# Functions for retrieving keys

def hasNextKeyTyped():
    """
    Return True if the queue of keys the user typed is not empty.
    Otherwise return False.
    """
    global _keysTyped
    return _keysTyped != []


def nextKeyTyped():
    """
    Remove the first key from the queue of keys that the the user typed,
    and return that key.
    """
    global _keysTyped
    return _keysTyped.pop()


# -----------------------------------------------------------------------
# Begin added by Alan J. Broder
# -----------------------------------------------------------------------

# Functions for dealing with mouse clicks 

def mousePressed():
    """
    Return True if the mouse has been left-clicked since the 
    last time mousePressed was called, and False otherwise.
    """
    global _mousePressed
    if _mousePressed:
        _mousePressed = False
        return True
    return False


def mouseX():
    """
    Return the x coordinate in user space of the location at
    which the mouse was most recently left-clicked. If a left-click
    hasn't happened yet, raise an exception, since mouseX() shouldn't
    be called until mousePressed() returns True.
    """
    global _mousePos
    if _mousePos:
        return _user_x(_mousePos[0])
    raise Exception(
        "Can't determine mouse position if a click hasn't happened")


def mouseY():
    """
    Return the y coordinate in user space of the location at
    which the mouse was most recently left-clicked. If a left-click
    hasn't happened yet, raise an exception, since mouseY() shouldn't
    be called until mousePressed() returns True.
    """
    global _mousePos
    if _mousePos:
        return _user_y(_mousePos[1])
    raise Exception(
        "Can't determine mouse position if a click hasn't happened")


# -----------------------------------------------------------------------
# End added by Alan J. Broder
# -----------------------------------------------------------------------

# -----------------------------------------------------------------------

# Initialize the x scale, the y scale, and the pen radius.

set_xscale()
set_yscale()
set_pen_radius()
pygame.font.init()


# -----------------------------------------------------------------------

# Functions for displaying Tkinter dialog boxes in child processes.

def _getFileName():
    """
    Display a dialog box that asks the user for a file name.
    """
    root = Tkinter.Tk()
    root.withdraw()
    reply = tkFileDialog.asksaveasfilename(initialdir='.')
    sys.stdout.write(reply)
    sys.stdout.flush()
    sys.exit()


def _confirmFileSave():
    """
    Display a dialog box that confirms a file save operation.
    """
    root = Tkinter.Tk()
    root.withdraw()
    tkMessageBox.showinfo(title='File Save Confirmation',
                          message='The drawing was saved to the file.')
    sys.exit()


def _reportFileSaveError(msg):
    """
    Display a dialog box that reports a msg.  msg is a string which
    describes an error in a file save operation.
    """
    root = Tkinter.Tk()
    root.withdraw()
    tkMessageBox.showerror(title='File Save Error', message=msg)
    sys.exit()


# -----------------------------------------------------------------------

def _regressionTest():
    """
    Perform regression testing.
    """

    clear()

    set_pen_radius(.5)
    set_pen_color(ORANGE)
    point(0.5, 0.5)
    show(0.0)

    set_pen_radius(.25)
    set_pen_color(BLUE)
    point(0.5, 0.5)
    show(0.0)

    set_pen_radius(.02)
    set_pen_color(RED)
    point(0.25, 0.25)
    show(0.0)

    set_pen_radius(.01)
    set_pen_color(GREEN)
    point(0.25, 0.25)
    show(0.0)

    set_pen_radius(0)
    set_pen_color(BLACK)
    point(0.25, 0.25)
    show(0.0)

    set_pen_radius(.1)
    set_pen_color(RED)
    point(0.75, 0.75)
    show(0.0)

    set_pen_radius(0)
    set_pen_color(CYAN)
    for i in range(0, 100):
        point(i / 512.0, .5)
        point(.5, i / 512.0)
    show(0.0)

    set_pen_radius(0)
    set_pen_color(MAGENTA)
    line(.1, .1, .3, .3)
    line(.1, .2, .3, .2)
    line(.2, .1, .2, .3)
    show(0.0)

    set_pen_radius(.05)
    set_pen_color(MAGENTA)
    line(.7, .5, .8, .9)
    show(0.0)

    set_pen_radius(.01)
    set_pen_color(YELLOW)
    circle(.75, .25, .2)
    show(0.0)

    set_pen_radius(.01)
    set_pen_color(YELLOW)
    filledCircle(.75, .25, .1)
    show(0.0)

    set_pen_radius(.01)
    set_pen_color(PINK)
    rectangle(.25, .75, .1, .2)
    show(0.0)

    set_pen_radius(.01)
    set_pen_color(PINK)
    filledRectangle(.25, .75, .05, .1)
    show(0.0)

    set_pen_radius(.01)
    set_pen_color(DARK_RED)
    square(.5, .5, .1)
    show(0.0)

    set_pen_radius(.01)
    set_pen_color(DARK_RED)
    filledSquare(.5, .5, .05)
    show(0.0)

    set_pen_radius(.01)
    set_pen_color(DARK_BLUE)
    polygon([.4, .5, .6], [.7, .8, .7])
    show(0.0)

    set_pen_radius(.01)
    set_pen_color(DARK_GREEN)
    set_font_size(24)
    text(.2, .4, 'hello, world')
    show(0.0)

    # import picture as p
    # pic = p.Picture('saveIcon.png')
    # picture(pic, .5, .85)
    # show(0.0)

    # Test handling of mouse and keyboard events.
    set_pen_color(BLACK)
    import stdio
    stdio.writeln('Left click with the mouse or type a key')
    while True:
        if mousePressed():
            filledCircle(mouseX(), mouseY(), .02)
        if hasNextKeyTyped():
            stdio.write(nextKeyTyped())
        show(0.0)

    # Never get here.
    show()


# -----------------------------------------------------------------------

def _main():
    """
    Dispatch to a function that does regression testing, or to a
    dialog-box-handling function.
    """
    import sys
    if len(sys.argv) == 1:
        _regressionTest()
    elif sys.argv[1] == 'getFileName':
        _getFileName()
    elif sys.argv[1] == 'confirmFileSave':
        _confirmFileSave()
    elif sys.argv[1] == 'reportFileSaveError':
        _reportFileSaveError(sys.argv[2])


if __name__ == '__main__':
    _main()
