from io import BytesIO
import re
import requests
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

COUNTIES = {
    'BB': 'Belknap',
    'CB': 'Carroll',
    'EB': 'Cheshire',
    'OB': 'Coos',
    'GB': 'Grafton',
    'HB': 'Hillsborough',
    'RB': 'Rockingham',
    'SB': 'Strafford',
    'UB': 'Sullivan',
}
COUNTY_CHOICES = (
    ('BB', COUNTIES['BB']),
    ('CB', COUNTIES['CB']),
    ('EB', COUNTIES['EB']),
    ('OB', COUNTIES['OB']),
    ('GB', COUNTIES['GB']),
    ('HB', COUNTIES['HB']),
    ('RB', COUNTIES['RB']),
    ('SB', COUNTIES['SB']),
    ('UB', COUNTIES['UB']),
)
COUNTY_CHUNK_LENGTH = 264
COUNTY_INITIAL_LENGTH = 396
COUNTY_URL_SHORT = {
    'BB': 'be',
    'CB': 'ca',
    'EB': 'ch',
    'OB': 'co',
    'GB': 'gf',
    'HB': 'hi',
    'RB': 'ro',
    'SB': 'st',
    'UB': 'su',
}
INDEX = (
    ('GRANTOR', 'Grantor'),
    ('GRANTEE', 'Grantee'),
)


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
        request = self.get_page(1)

        if request.status_code == 404:
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
            'end': '',
        }
        url = 'http://www.nhdeeds.com/%(county_full)s/book/book%(book_hundred)ssp/book%(book)s/%(county)s%(book)s-%(plan)s-%(page)03d.tif' % data

        return requests.get(url)

    def get_pages(self, start=1, end=100):
        raw_images = []

        for i in range(start, end):
            request = self.get_page(i)

            if request.status_code == 404:
                break

            raw_images.append(request.content)

        if raw_images:
            # Create canvas in memory
            canvas_data = BytesIO()
            canvas = Canvas(canvas_data)

            # Iterate through URLs and add image data to PDF canvas
            for raw_img in raw_images:
                canvas.drawImage(ImageReader(BytesIO(raw_img)), 0, 0, 8.5 * inch, 11 * inch)
                canvas.showPage()

            canvas.save()

            return canvas_data

class DeedSearch(object):
    def search(self, county, index, first_name, last_name):
        payload = {
            'reqType': 'F',
            'surName': last_name.upper(),
            'gvnName': first_name.upper(),
            'indexChoice': index,
            'startDate': '0',
            'endDate': '20171231',
            'allnames': '1',
            'county': COUNTIES[county.upper()],
            'displayLines': '100',
        }
        data = {
            'county': COUNTIES[county.upper()].lower(),
            'county_url_short': COUNTY_URL_SHORT[county.upper()],
        }
        url = 'http://www.nhdeeds.com/%(county)s/%(county_url_short)sindxservlet/%(county_url_short)sindxServlet1' % data
        request = requests.post(url, data=payload)

        content = request.text
        # Remove leading info content
        output = re.sub(r'^.{%s}' % (COUNTY_INITIAL_LENGTH,), '', content)

        entries = []
        for line in list(chunkstring(output, COUNTY_CHUNK_LENGTH)):
            # Skip empty lines
            if not line.strip():
                continue

            matches = re.search(r'([0-9]{4})-([0-9]{4})', line)
            if not matches:
                continue

            entries.append({
                'book': matches.group(1),
                'plan': matches.group(2),
                'full_record': line.strip(),
            })

        return entries

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))
