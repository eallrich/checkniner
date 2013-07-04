from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

from checkouts.views import (
    Home,
    PilotList,
    PilotDetail,
    AirstripList,
    AirstripDetail,
    BaseList,
    BaseAttachedDetail,
    BaseUnattachedDetail,
    FilterFormView,
    CheckoutEditFormView,
)

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'checkouts/login.html',}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^emerald/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    url(
        regex=r'^$',
        view=Home.as_view(),
        name='home',
    ),
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
    url(
        regex=r'^bases/$',
        view=BaseList.as_view(),
        name='base_list',
    ),
    url(
        regex=r'^bases/(?P<ident>\w+)/attached/$',
        view=BaseAttachedDetail.as_view(),
        name='base_attached_detail',
    ),
    url(
        regex=r'^bases/(?P<ident>\w+)/unattached/$',
        view=BaseUnattachedDetail.as_view(),
        name='base_unattached_detail',
    ),
    url(
        regex=r'^checkouts/$',
        view=FilterFormView.as_view(),
        name='checkout_filter',
    ),
    url(
        regex=r'^checkouts/edit/$',
        view=CheckoutEditFormView.as_view(),
        name='checkout_edit',
    ),
)

if settings.SERVE_STATIC:
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT,})
    )

