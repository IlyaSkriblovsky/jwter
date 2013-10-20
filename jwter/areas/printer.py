# -*- coding: utf-8 -*-

import httplib
import StringIO
import urlparse
import multiprocessing
from itertools import izip

from django.conf import settings

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm, cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.utils import ImageReader

from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from PIL import Image


from jwter.areas.models import MapCache



class PrintException(Exception): pass

class MapFetchingException(PrintException): pass


CIRCLE_STEPS = 24
def gen_circle(x1, y1, x2, y2):
    import math

    points = []

    for step in xrange(CIRCLE_STEPS + 1):
        angle = 2 * math.pi * step / CIRCLE_STEPS
        points.append([
            (x1 + x2)/2 + math.cos(angle) * (x2 - x1)/2,
            (y1 + y2)/2 + math.sin(angle) * (y2 - y1)/2,
        ])

    return yandex_encode(points)


def yandex_encode(points):
    import struct
    import base64

    points = [ [ int(p[0]*1000000), int(p[1]*1000000) ] for p in points ]
    for i in reversed(xrange(1, len(points))):
        points[i] = [ points[i][0] - points[i-1][0], points[i][1] - points[i-1][1] ]

    ints = []
    for p in points:
        ints.append(p[0] & 0xffffffff)
        ints.append(p[1] & 0xffffffff)

    bytes = struct.pack('<{0}I'.format(len(ints)), *ints)

    return base64.b64encode(bytes).replace('+', '-').replace('/', '_')


def build_map_url(x, y, zoom, marks):
    if marks:
        marks = [ mark.split('|') for mark in marks.split(',') ]
    else:
        marks = []

    polygons_enc = [
        mark[1] for mark in marks if mark[0] == 'Polygon'
    ]

    circles_enc = [
        gen_circle(*(float(m) for m in mark[1:])) for mark in marks if mark[0] == 'Circle'
    ]


    marks_style = 'c:000000ff,f:00000010,w:3'

    polyline_arg = '~'.join('{0},{1}'.format(marks_style, enc) for enc in polygons_enc + circles_enc)

    url_domain = 'static-maps.yandex.ru'
    url_path = '/1.x/?l=map&ll={x},{y}&z={z}&size={w},{h}{pl}'.format(
        x = x,
        y = y,
        z = zoom,
        w = 650,
        h = 284,
        pl = '&pl=' + polyline_arg if polyline_arg else ''
    )
    return ''.join(('http://', url_domain, url_path))


def fetch_map(url):
    url_parts = urlparse.urlparse(url)

    try:
        http = httplib.HTTPConnection(url_parts.netloc)
        http.request('GET', '?'.join((url_parts.path, url_parts.query)))
        response = http.getresponse()
        if response.status == 200:
            return response.read()
        else:
            raise Exception("Invalid response from Yandex.Maps Static API: {0}".format(response.read()))
    finally:
        http.close()

    return None



ADJ_BRIGHTNESS = 1.0
ADJ_CONTRAST   = 3.0
def adjust_colors(map):
    from PIL.ImageEnhance import Brightness, Contrast
    return Contrast(Brightness(map).enhance(ADJ_BRIGHTNESS)).enhance(ADJ_CONTRAST).convert('L')



BLANK_WIDTH  = 146*mm
BLANK_HEIGHT =  94*mm


def print_area_blank(c, x, y, area, map_image):
    c.saveState()
    c.translate(x, y)

    c.setFont('FreeSerifBold', 15)
    c.drawCentredString(BLANK_WIDTH / 2, BLANK_HEIGHT - 1*cm, u'Карта участка')


    address_y = BLANK_HEIGHT - 1.7*cm

    c.setFont('FreeSerifBold', 10)
    c.drawString(1*cm, address_y, u'Местонахождение')
    c.drawString(9.5*cm, address_y, u'Номер участка')

    c.setLineWidth(1)
    c.setDash([0, 2])
    c.setStrokeGray(0)
    c.setLineCap(1)
    c.line(4.2*cm, address_y, 9.3*cm, address_y)
    c.line(12.2*cm, address_y, BLANK_WIDTH - cm, address_y)


    style = getSampleStyleSheet()['BodyText']
    style.fontName = 'FreeSerifBold'
    style.fontSize = 7.5
    style.leading = 8
    style.alignment = TA_JUSTIFY
    p = Paragraph(u'Храни, пожалуйста, эту карту в чехле. Не пачкай ее, не делай на ней пометок и не сгибай. Всякий раз, когда прорабатывается участок, сообщай, пожалуйста, об этом брату, ведущему картотеку территории собрания.', style)
    p.wrap(BLANK_WIDTH - 2*cm, 3*cm)
    p.drawOn(c, 1*cm, 1.1*cm)


    c.setFont('FreeSerif', 8)
    c.drawString(1*cm, 0.7*cm, u'S-12-U   6/72')



    c.setFont('FreeSerif', 12)
    c.drawCentredString((12.25*cm+BLANK_WIDTH-cm)/2, address_y + 0.5*mm, unicode(area.number))

    c.setFont('FreeSerif', 12)

    font_size = 13
    while font_size >= 6:
        text = c.beginText()
        text.setTextOrigin(4.25*cm, address_y + 0.5*mm)
        text.setFont('FreeSerif', font_size)
        text.textOut(area.address)
        if text.getX() < 9.3*cm:
            break
        font_size -= 1

    c.drawText(text)


    c.drawImage(ImageReader(map_image), 1*cm, 2*cm, BLANK_WIDTH - 2*cm, BLANK_HEIGHT - 3.9*cm)

    c.restoreState()


def init_pdf():
    for font, filename in settings.PDF_FONTS.iteritems():
        pdfmetrics.registerFont(TTFont(font, filename))



def print_many_areas(areas):
    init_pdf()

    c = Canvas('1.pdf', pagesize = A4)

    x = (A4[0] - BLANK_WIDTH) / 2
    y = (A4[1] - 3*BLANK_HEIGHT) / 2


    map_urls = [ build_map_url(area.x, area.y, area.zoom, area.marks) for area in areas ]


    urls_to_fetch = []
    map_pngs = {}
    for url in map_urls:
        png = MapCache.get_map(url)
        if png:
            map_pngs[url] = png
        else:
            urls_to_fetch.append(url)


    if urls_to_fetch:
        fetched_pngs = multiprocessing.Pool(16).map(fetch_map, urls_to_fetch)
    else:
        fetched_pngs = []


    for url, png in izip(urls_to_fetch, fetched_pngs):
        if png is None:
            raise Exception("Cannot fetch {0}".format(url))
        map_pngs[url] = png

    map_images = {}
    for url, png in map_pngs.iteritems():
        map_images[url] = adjust_colors(Image.open(StringIO.StringIO(png)).convert('RGB'))


    # Saving PNG to MapCache only after creating Image from it to insure it is proper PNG
    for url, png in izip(urls_to_fetch, fetched_pngs):
        MapCache.save_map(url, png)


    for page_no in xrange((len(areas) + 2) / 3):
        page_set = areas[page_no*3 : (page_no+1)*3]

        c.setLineWidth(0.5)
        c.setStrokeGray(0.5)
        c.line(x, 0, x, A4[1])
        c.line(x + BLANK_WIDTH, 0, x + BLANK_WIDTH, A4[1])

        c.line(0, y + 3*BLANK_HEIGHT, A4[0], y + 3*BLANK_HEIGHT)

        print_area_blank(c, x, y + 2*BLANK_HEIGHT, areas[page_no*3 + 0], map_images[map_urls[page_no*3 + 0]])
        c.line(0, y + 2*BLANK_HEIGHT, A4[0], y + 2*BLANK_HEIGHT)

        if len(page_set) >= 2:
            print_area_blank(c, x, y + BLANK_HEIGHT, areas[page_no*3 + 1], map_images[map_urls[page_no*3 + 1]])
            c.line(0, y + BLANK_HEIGHT, A4[0], y + BLANK_HEIGHT)

        if len(page_set) >= 3:
            print_area_blank(c, x, y, areas[page_no*3 + 2], map_images[map_urls[page_no*3 + 2]])
            c.line(0, y, A4[0], y)

        c.showPage()


    return c.getpdfdata()
