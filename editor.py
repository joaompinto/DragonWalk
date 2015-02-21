#!/usr/bin/python
import sys
from os.path import exists, join
from dragonwalk.editor.window import TopWindow
from dragonwalk.editor.cmdline import command_line_parser
from dragonwalk.player import Level

def main():
    (options, args) = command_line_parser().parse_args()

    if len(args) < 1:
        filename = join('levels', 'simple.xml')
        must_load = False
    else:
        filename = args[0]
        must_load = False

    if not filename.endswith('.xml'):
        print "Filename must end with .xml"
        sys.exit(2)

    if options.new_file:
        if exists(filename):
            print "Can not create file %s, it already exists!" % filename
            sys.exit(3)
    else:
        must_load = True
        if not exists(filename):
            print "Could not find file %s" % filename
            sys.exit(4)

    editor = TopWindow(filename)
    if must_load:
        level = Level.load(editor.window, filename)
        editor.update_editor_from_level(level)
    editor.run_event_loop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print 'User requested interrupt'
        sys.exit(1)
