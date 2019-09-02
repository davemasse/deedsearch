import datetime
import re
import requests
from io import BytesIO
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

COUNTIES = {
    'BB': 'Belknap',
    'CB': 'Carroll',
    'HB': 'Hillsborough',
    'RB': 'Rockingham',
    'SB': 'Strafford',
}
COUNTY_CHOICES = (
    ('BB', COUNTIES['BB']),
    ('CB', COUNTIES['CB']),
    ('HB', COUNTIES['HB']),
    ('RB', COUNTIES['RB']),
    ('SB', COUNTIES['SB']),
)
COUNTY_CHUNK_LENGTH = 264
COUNTY_INITIAL_LENGTH = 396
COUNTY_URL_SHORT = {
    'BB': 'be',
    'CB': 'ca',
    'HB': 'hi',
    'RB': 'ro',
    'SB': 'st',
}
INDEX = (
    ('GRANTOR', 'Grantor'),
    ('GRANTEE', 'Grantee'),
    ('UGRANTOR', 'Unverified Grantor'),
    ('UGRANTEE', 'Unverified Grantee'),
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
        request = requests.get(url)

        if request.status_code != 200:
            url = 'http://test.nhdeeds.com/nh%(county_full)s/CCSimulacrum.WebSite/images/doc_%(book)s-%(plan)s-%(page)03d.tif' % data
            request = requests.get(url)

        return request

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
            'endDate': datetime.datetime.now().strftime('%Y%m%d'),
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

        if request.status_code != 200:
            # Some counties are starting to use a new search URL
            url = 'http://test.nhdeeds.com/nh%(county)s/CCSimulacrum.WebSite/indexsearch/search' % data
            request = requests.post(url, data=payload)

        content = request.text
        # Remove leading info content
        output = re.sub(r'^.{%s}' % (COUNTY_INITIAL_LENGTH,), '', content)

        entries = []
        # Data is returned in a long stream and needs to be broken down for processing
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

# Borrowed from https://stackoverflow.com/a/18854817
def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))
