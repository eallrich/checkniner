from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

from checkouts.views import (
    CheckoutsByPilotList,
    CheckoutsByPilotDetail,
    CheckoutsByAirstripList,
    CheckoutsByAirstripDetail,
)

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^emerald/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    url(
        regex=r'^pilots/$',
        view=CheckoutsByPilotList.as_view(),
        name='checkouts_by_pilot_list',
    ),
    url(
        regex=r'^pilots/(?P<username>\w+)/$',
        view=CheckoutsByPilotDetail.as_view(),
        name='checkouts_by_pilot_detail',
    ),
    url(
        regex=r'^airstrips/$',
        view=CheckoutsByAirstripList.as_view(),
        name='checkouts_by_airstrip_list',
    ),
    url(
        regex=r'^airstrips/(?P<ident>\w+)/$',
        view=CheckoutsByAirstripDetail.as_view(),
        name='checkouts_by_airstrip_detail',
    ),
)

if settings.SERVE_STATIC:
    urlpatterns += patterns('',
	url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT,})
    )

