#!/usr/bin/python
import gi
gi.require_version('Rsvg', '2.0')
from gi.repository import Rsvg
import cairo

INPUTFILE = 'data/sources/Box.svg'

if __name__ == '__main__':
    # create the cairo context
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 128, 128)
    context = cairo.Context(surface)

    # use rsvg to render the cairo context
    handle = Rsvg.Handle()
    svg = handle.new_from_file(INPUTFILE)
    svg.render_cairo(context)
    surface.write_to_png('svg.png')