#!/usr/bin/python
from sketch import SketchFile
from PyQt4.QtCore import *
import sys

if len(sys.argv) != 2:
    print("Usage: %s <file>\n" % sys.argv[0] +
          "Reads the given scribble/sketch export file\n"
          "(usually named scribble_??.sketch) and\n"
          "transforms every page into an SVG file named\n"
          "scribble_??.sketch_page_?.svg.")
    sys.exit(1)

sketch = SketchFile(sys.argv[1])
print("Converting .sketch to svgs")
svgs = sketch.converttosvgdict()

for key, value in svgs.iteritems():
    file = QFile(sys.argv[1] + "_page_%03d.svg" % key)
    file.open(QIODevice.WriteOnly)
    file.write(value.buffer())
    file.close()
