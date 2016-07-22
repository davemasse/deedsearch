import StringIO
import io
import reportlab
import requests
from PIL import Image
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .forms import COUNTIES

class Deed(object):
    book = ''
    county = ''
    plan = ''

    def __init__(self, county, book, plan):
        self.book = book
        self.county = county
        self.plan = plan

        return

    def is_valid(self):
        r = self.get_page(1)

        if r.status_code == 404:
            ret = False
        else:
            ret = True

        return ret

    def get_page(self, page_number=1):
        # Iterate URLs and check for existence of images (there's no API to get number of pages per document)
        data = {
            'book': self.book,
            'book_hundred': self.book[:2] + '00',
            'county': self.county,
            'county_full': COUNTIES[self.county.upper()].lower(),
            'page': page_number,
            'plan': self.plan,
        }
        url = 'http://www.nhdeeds.com/%(county_full)s/book/book%(book_hundred)ssp/book%(book)s/%(county)s%(book)s-%(plan)s-%(page)03d.tif' % data

        return requests.get(url)

    def get_pages(self, start=1, end=100):
        raw_images = []

        for i in range(start, end):
            r = self.get_page(i)
            
            if r.status_code == 404:
                break

            raw_images.append(r.content)

        if len(raw_images):
            # Create canvas in memory
            canvas_data = io.BytesIO()
            c = canvas.Canvas(canvas_data)

            # Iterate through URLs and add image data to PDF canvas
            for raw_img in raw_images:
                img = Image.open(StringIO.StringIO(raw_img))
                c.drawImage(ImageReader(StringIO.StringIO(raw_img)), 0, 0, 8.5 * inch, 11 * inch)
                c.showPage()
                c.save()

            return canvas_data
