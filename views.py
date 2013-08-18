import StringIO
import io
import reportlab
import requests
from PIL import Image
from django.http import HttpResponse
from django.shortcuts import render
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .forms import COUNTIES, DeedForm

def index(request):
    raw_images = []

    if len(request.GET):
        form = DeedForm(request.GET)
        if form.is_valid():
            for i in range(1, 100):
                # Iterate URLs and check for existence of images (there's no API to get number of pages per document)
                data = {
                    'book': form.cleaned_data['book'],
                    'book_hundred': form.cleaned_data['book'][:2] + '00',
                    'county': form.cleaned_data['county'],
                    'county_full': COUNTIES[form.cleaned_data['county']],
                    'page': i,
                    'plan': form.cleaned_data['plan'],
                }
                url = 'http://www.nhdeeds.com/%(county_full)s/book/book%(book_hundred)ssp/book%(book)s/%(county)s%(book)s-%(plan)s-%(page)03d.tif' % data

                r = requests.get(url)

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
                    c.drawImage(ImageReader(StringIO.StringIO(raw_img)), 0, 0, 8.5 * inch, 11 * inch)#, 600, 800)
                    c.showPage()
                    c.save()

                # Output PDF data to browser
                response = HttpResponse(content_type='application/pdf')
                response.write(canvas_data.getvalue())
                return response
    else:
        form = DeedForm()

    return render(request, 'index.html', {
        'form': form,
    })
