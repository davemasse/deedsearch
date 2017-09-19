from io import BytesIO
import re
import requests
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

COUNTIES = {
    'EB': 'Cheshire',
    'GB': 'Grafton',
    'HB': 'Hillsborough',
    'OB': 'Coos',
    'RB': 'Rockingham',
    'UB': 'Sullivan',
}
COUNTY_CHOICES = (
    ('EB', COUNTIES['EB']),
    ('GB', COUNTIES['GB']),
    ('HB', COUNTIES['HB']),
    ('OB', COUNTIES['OB']),
    ('RB', COUNTIES['RB']),
    ('UB', COUNTIES['UB']),
)
COUNTY_CHUNK_LENGTH = {
    'EB': 264,
    'GB': 264,
    'HB': 264,
    'OB': 528,
    'RB': 264,
    'UB': 264,
}
COUNTY_INITIAL_LENGTH = {
    'EB': 264,
    'GB': 264,
    'HB': 264,
    'OB': 396,
    'RB': 396,
    'UB': 264,
}
COUNTY_DATA_RANGES = {
    'EB': {
        'grantee': [2, 41],
        'grantor': [41, 64],
        'book': [64, 68],
        'plan': [69, 73],
        'type': [73, 83],
        'town': [83, 93],
        'date': [93, 101],
    },
    'GB': {
        'grantee': [2, 41],
        'grantor': [41, 64],
        'book': [64, 68],
        'plan': [69, 73],
        'type': [73, 83],
        'town': [83, 93],
        'date': [93, 101],
    },
    'HB': {
        'grantee': [2, 41],
        'grantor': [41, 64],
        'book': [64, 68],
        'plan': [69, 73],
        'type': [73, 83],
        'town': [83, 93],
        'date': [93, 101],
    },
    'OB': {
        'grantee': [2, 41],
        'grantor': [41, 64],
        'book': [64, 68],
        'plan': [69, 73],
        'type': [73, 83],
        'town': [83, 93],
        'date': [93, 101],
    },
    'RB': {
        'grantee': [2, 41],
        'grantor': [50, 73],
        'book': [73, 77],
        'plan': [78, 82],
        'type': [82, 92],
        'town': [92, 102],
        'date': [41, 49],
    },
    'UB': {
        'grantee': [2, 41],
        'grantor': [41, 64],
        'book': [64, 68],
        'plan': [69, 73],
        'type': [73, 83],
        'town': [83, 93],
        'date': [93, 101],
    },
}
COUNTY_URL_SHORT = {
    'EB': 'ch',
    'GB': 'gf',
    'HB': 'hi',
    'OB': 'co',
    'RB': 'ro',
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
            'startDate': '19000101',
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
        output = re.sub(r'^.{%s}' % (COUNTY_INITIAL_LENGTH[county],), '', content)

        entries = []
        for line in list(chunkstring(output, COUNTY_CHUNK_LENGTH[county])):
            # Skip empty lines
            if len(line.strip()) == 0:
                continue

            range = COUNTY_DATA_RANGES[county]
            entries.append({
                'book': line[range['book'][0]:range['book'][1]],
                'date': line[range['date'][0]:range['date'][1]],
                'grantee': line[range['grantee'][0]:range['grantee'][1]],
                'grantor': line[range['grantor'][0]:range['grantee'][1]],
                'plan': line[range['plan'][0]:range['plan'][1]],
                'town': line[range['town'][0]:range['town'][1]],
                'type': line[range['type'][0]:range['type'][1]],
            })

        for entry in entries:
            for key, value in entry.items() :
                entry[key] = value.strip()

        return entries

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))
