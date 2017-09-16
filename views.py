from urllib.parse import urlencode

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

from .forms import COUNTIES, DeedForm
from .utils import Deed

def index(request):
    if len(request.GET):
        form = DeedForm(request.GET)
        if form.is_valid():
            return redirect(reverse('get_deed', kwargs=form.cleaned_data))
    else:
        form = DeedForm()

    return render(request, 'index.html', {
        'form': form,
    })

def get_deed(request, county, book, plan):
    deed_args = {
        'county': county,
        'book': book,
        'plan': plan
    }
    form = DeedForm(deed_args)
    form.is_valid()
    if form.is_valid():
        deed = Deed(county=form.cleaned_data.get('county'), book=form.cleaned_data.get('book'), plan=form.cleaned_data.get('plan'))

        canvas_data = deed.get_pages()
        # Output PDF data to browser
        response = HttpResponse(content_type='application/pdf')
        response.write(canvas_data.getvalue())
        return response

    return HttpResponseRedirect('%s?%s' % (reverse('index'), urlencode(deed_args)))
