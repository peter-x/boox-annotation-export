#!/usr/bin/python
import sys
import os.path
import gzip
import zipfile
import re
import uuid
from PyQt4.QtCore import *
from sketch import SketchFile

def writeEpub(svgdict, filename, title):
    epub = zipfile.ZipFile(filename, 'w', compression=zipfile.ZIP_DEFLATED)

    #needs to start at offset 38 but every reader i tried was still ok with this
    epub.writestr("mimetype", "application/epub+zip")

    epub.writestr("META-INF/container.xml", '''<container version="1.0"
    xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
    <rootfile full-path="OEBPS/Content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
    </container>''');
    
    contentopf = '''
    <package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookID" version="2.0" >
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
        <dc:title>%(title)s</dc:title> 
        <dc:creator opf:role="aut">sketch2epub</dc:creator>
        <dc:language>en-US</dc:language> 
        <dc:rights>Restricted</dc:rights> 
        <dc:publisher>sketch2epub</dc:publisher> 
        <dc:identifier id="BookID" opf:scheme="UUID">%(uuid)s</dc:identifier>
    </metadata>
    <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />
    %(manifest)s
    </manifest>
    <spine toc="ncx">
    %(spine)s
    </spine>
    </package>'''
    
    toc = '''<?xml version="1.0" encoding="UTF-8"?>
    <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    
    <head>
    <meta name="dtb:uid" content="%(uuid)s"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle><text>%(title)s</text></docTitle>
    <navMap>
    <navPoint id="title" playOrder="1">
    <navLabel><text>%(title)s</text></navLabel>
    <content src="index.html"/>
    </navPoint>
    </navMap>
    </ncx>'''

    manifest = ""
    spine = ""

    indexhtml = '<?xml version="1.0" encoding="UTF-8"?>'
    indexhtml += '<html xmlns="http://www.w3.org/1999/html" xmlns:epub="http://www.idpf.org/2007/ops">'
    indexhtml += '<head><title>%s</title></head><body>'

    manifest += '<item id="file_1" href="index.html" media-type="application/xhtml+xml"/>\n'
    for key,svg in svgdict.iteritems():
        manifest +='<item id="svg_%s" href="images/%s.svg" media-type="image/svg+xml" />\n' % (key, key)
        epub.writestr('OEBPS/images/%s.svg' % key, svg)


    for key in sorted(svgdict.iterkeys()):
        indexhtml += '<p>'
        indexhtml += '<object data="images/%s.svg" width="100%%" height="100%%" type="image/svg+xml"></object>' % key
        indexhtml += '</p>\n'
        

    indexhtml += "</body></html>"
    
    spine += '<itemref idref="file_1" />'

    bookuuid = str(uuid.uuid1())
    epub.writestr('OEBPS/index.html', indexhtml)
    epub.writestr('OEBPS/toc.ncx', toc % {
        'title': title,
        'uuid' : bookuuid,
    })

    epub.writestr('OEBPS/Content.opf', contentopf % {
        'manifest': manifest,
        'spine': spine,
        'title': title,
        'uuid': bookuuid,
        })

    epub.close()

def removevectoreffect(svgdict):
    # this probalby cleans up svg 1.2 -> 1.1
    # this is highly stupid and does no real conversion
    newdict = {}
    
    vectoreffectregexp = re.compile('vector-effect=".*?"')
    versionregexp = re.compile('version="1.2"')
    for key,svg in svgdict.iteritems():
        data = str(QString(svg.data()))
        cleaned = vectoreffectregexp.sub('', data)
        cleaned2 = versionregexp.sub('version="1.1"', cleaned)
        newdict[key] = cleaned2
    return newdict

if len(sys.argv) != 2:
    print("Usage: %s <file>\n" % sys.argv[0] +
          "Reads the given scribble/sketch export file\n"
          "(usually named scribble_??.sketch) and\n"
          "transforms into an epub\n")
    sys.exit(1)

sketch = SketchFile(sys.argv[1])
print("Converting .sketch to svgs")
svgs = sketch.converttosvgdict()
print("converting svg into different format")
cleaneddictversion = removevectoreffect(svgs)
print("writing epub")
exportfile = sys.argv[1] + ".epub"
writeEpub(cleaneddictversion, exportfile, sys.argv[1])
