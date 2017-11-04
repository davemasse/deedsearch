from urllib.parse import urlencode

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

from .forms import DeedForm, DeedSearchForm
from .utils import Deed, DeedSearch


def index(request):
    if request.GET:
        form = DeedForm(request.GET)
        if form.is_valid():
            return redirect(reverse('get_deed', kwargs=form.cleaned_data))
    else:
        form = DeedForm()

    return render(request, 'deedsearch/index.html', {
        'form': form,
    })

def get_deed(request, county, book, plan):
    deed_args = {
        'county': county,
        'book': book,
        'plan': plan
    }

    form = DeedForm(deed_args)
    if form.is_valid():
        deed = Deed(county=form.cleaned_data.get('county'), book=form.cleaned_data.get('book'), plan=form.cleaned_data.get('plan'))

        canvas_data = deed.get_pages()
        # Output PDF data to browser
        response = HttpResponse(content_type='application/pdf')
        response.write(canvas_data.getvalue())
        return response

    return HttpResponseRedirect('%s?%s' % (reverse('index'), urlencode(deed_args)))

def search(request):
    searched = True

    if request.POST:
        form = DeedSearchForm(request.POST)

        if form.is_valid():
            deed_search = DeedSearch()
            entries = deed_search.search(county=form.cleaned_data.get('county'), index=form.cleaned_data.get('index'), first_name=form.cleaned_data.get('first_name'), last_name=form.cleaned_data.get('last_name'))
    else:
        entries = []
        form = DeedSearchForm()
        searched = False

    return render(request, 'deedsearch/search.html', {
        'entries': entries,
        'form': form,
        'searched': searched,
    })
