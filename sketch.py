import sqlite3
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSvg import *


pen_colors = {100: 0xff, 101: 0x20, 102: 0x10, 103: 0x00}
point_sizes = {200: 1, 201: 2, 202: 4, 203: 6, 204: 8}
class SketchFile:
    def __init__(self, dbfile):
        self.dbfile = dbfile

    def converttosvgdict(self):
        if not self.dbfile:
            raise ValueError
        
        bufferdict = {}

        conn = sqlite3.connect(self.dbfile)
        cur = conn.cursor()
        cur.execute('select * from sketch')
        for (row_id, page_id, data, background_id) in cur:
            # TODO use background_id?
            g = QSvgGenerator()
            number = int(page_id)
                
            curbuffer = QBuffer()
            g.setOutputDevice(curbuffer)

            s = QDataStream(QByteArray.fromRawData(data))
                
            # TODO use orientation and bk_color
            orientation = s.readInt16()
            bk_color = QColor()
            s >> bk_color
            content_area = QRect()
            s >> content_area
                
            g.setViewBox(content_area)

            num_strokes = s.readInt16()
            p = QPainter()
            p.begin(g)
            for i in range(num_strokes):
                # TODO transform: rotate (and area?)
                color = s.readInt16()
                shape = s.readInt16()
                zoom = s.readFloat() / 60.0
                layer = s.readInt16()
                num_points = s.readInt16()
                area = QRect()
                s >> area

                # the SDK uses QBrush and then fills each pixel individually
                pen = QPen(QColor(pen_colors[color],
                                  pen_colors[color],
                                  pen_colors[color]))
                pen.setWidth(point_sizes[shape] / zoom)
                
                p.setPen(pen)

                num_points_real = s.readInt32()
                coords = []
                for i in range(num_points_real):
                    x = s.readInt16() / zoom
                    y = s.readInt16() / zoom
                    pressure = s.readInt16()
                    coords += [(x, y)]

                if len(coords) == 1 or (len(coords) == 2 and coords[0] == coords[1]):
                    p.drawPoint(coords[0][0], coords[0][1])
                else:
                    poly = QPolygon()
                    for (x, y) in coords:
                        poly.append(QPoint(x, y))
                    p.drawPolyline(poly)
            p.end()

            bufferdict[number] =  curbuffer
        return bufferdict
