from django.conf.urls import url

from deedsearch.views import get_deed, index, search

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^(?:deed/(?P<county>[A-Z]{2})/(?P<book>[0-9]{4})/(?P<plan>[0-9]{4})/)?$', get_deed, name='get_deed'),
    url(r'^search/$', search, name='search'),
]
