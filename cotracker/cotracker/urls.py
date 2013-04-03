from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

from checkouts.views import (
    PilotList,
    PilotDetail,
    AirstripList,
    AirstripDetail,
)

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^emerald/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    url(
        regex=r'^pilots/$',
        view=PilotList.as_view(),
        name='pilot_list',
    ),
    url(
        regex=r'^pilots/(?P<username>\w+)/$',
        view=PilotDetail.as_view(),
        name='pilot_detail',
    ),
    url(
        regex=r'^airstrips/$',
        view=AirstripList.as_view(),
        name='airstrip_list',
    ),
    url(
        regex=r'^airstrips/(?P<ident>\w+)/$',
        view=AirstripDetail.as_view(),
        name='airstrip_detail',
    ),
)

if settings.SERVE_STATIC:
    urlpatterns += patterns('',
	url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT,})
    )

