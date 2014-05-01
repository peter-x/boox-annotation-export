Boox Annotation Export
======================

Tools that can be used to export annotations from Onyx Boox devices.

`sketchfile_to_svg.py`: Python script that transforms .sketch
files to SVG graphics. Needed libraries: PyQt4 and sqlite3 for Python.

`sketchfile_to_epub.py`: Python script that transforms .sketch
files to Epub with embedded SVG graphics. Needed libraries: PyQt4 and sqlite3 for Python.
Notice that there are some problems with this implementation:
- some epub reader can not render the svg.
- Epub guesses the number of pages by the amount of text in it. As we don't have text the pagenumbers might not be useful.