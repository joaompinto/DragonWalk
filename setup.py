from distutils.core import setup
from glob import glob
from os.path import join
import py2exe
import os

origIsSystemDLL = py2exe.build_exe.isSystemDLL  # save the orginal before we edit it


def isSystemDLL(pathname):
    # checks if the freetype and ogg dll files are being included
    if os.path.basename(pathname).lower() in ("libfreetype-6.dll", "libogg-0.dll", "sdl_ttf.dll"):
        return 0
    return origIsSystemDLL(pathname)  # return the orginal function


py2exe.build_exe.isSystemDLL = isSystemDLL  # override the default function with this one

data_parts = ['backgrounds', 'blocks', 'objects']

setup(windows=['editor.py'],
      packages=[
          'dragonwalk',
          'dragonwalk.editor',
          'dragonwalk.gfx',
          'dragonwalk.player',
          'dragonwalk.yattag'],
      data_files=[(join('data', part), glob(join('data', part, '*'))) for part in data_parts] +
                 [('levels', glob(join('levels', '*')))]
)