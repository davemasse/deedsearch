from django.conf.urls import patterns, include, url

urlpatterns = patterns('deedsearch.views',
    (r'^$', 'index', {}, 'index'),
)
