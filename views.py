import StringIO
import reportlab
import requests
from PIL import Image
from django.http import HttpResponse
from django.shortcuts import render
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .forms import COUNTIES, DeedForm

def index(request):
    urls = []

    if len(request.GET):
        form = DeedForm(request.GET)
        if form.is_valid():
            for i in range(1, 100):
                data = {
                    'book': form.cleaned_data['book'],
                    'book_hundred': form.cleaned_data['book'][:2] + '00',
                    'county': form.cleaned_data['county'],
                    'county_full': COUNTIES[form.cleaned_data['county']],
                    'page': i,
                    'plan': form.cleaned_data['plan'],
                }
                url = 'http://www.nhdeeds.com/%(county_full)s/book/book%(book_hundred)ssp/book%(book)s/%(county)s%(book)s-%(plan)s-%(page)03d.tif' % data
                return HttpResponse(url)

                r = requests.get(url)

                if r.status_code == 404:
                    break

                urls.append(url)

            if len(urls):
                c = canvas.Canvas('ex.pdf')

                for url in urls:
                    raw_img = requests.get(url).content
                    print StringIO.StringIO(raw_img)
                    img = Image.open(StringIO.StringIO(raw_img))
                    c.drawImage(ImageReader(StringIO.StringIO(raw_img)), 0, 0, 600, 800)
                    c.showPage()
                    c.save()

                response = HttpResponse(content_type='application/pdf')
                #response['Content-Disposition'] = 'attachment; filename="%s%s.pdf"' % (form.cleaned_data.get('book'), form.cleaned_data.get('plan'),)
                response.write(open('ex.pdf').read())
                return response
    else:
        form = DeedForm()

    return render(request, 'index.html', {
        'form': form,
        'urls': urls,
    })
