from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^emerald/', include(admin.site.urls)),
    url(r'^checkouts/', include('checkouts.urls')),
)

if settings.SERVE_STATIC:
    urlpatterns += patterns('',
	url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT,})
    )

