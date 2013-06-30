from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from checkouts.views import (
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
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'checkouts/login.html',}),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^emerald/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    url(
        regex=r'^pilots/$',
        view=login_required(PilotList.as_view()),
        name='pilot_list',
    ),
    url(
        regex=r'^pilots/(?P<username>\w+)/$',
        view=login_required(PilotDetail.as_view()),
        name='pilot_detail',
    ),
    url(
        regex=r'^airstrips/$',
        view=login_required(AirstripList.as_view()),
        name='airstrip_list',
    ),
    url(
        regex=r'^airstrips/(?P<ident>\w+)/$',
        view=login_required(AirstripDetail.as_view()),
        name='airstrip_detail',
    ),
    url(
        regex=r'^bases/$',
        view=login_required(BaseList.as_view()),
        name='base_list',
    ),
    url(
        regex=r'^bases/(?P<ident>\w+)/attached/$',
        view=login_required(BaseAttachedDetail.as_view()),
        name='base_attached_detail',
    ),
    url(
        regex=r'^bases/(?P<ident>\w+)/unattached/$',
        view=login_required(BaseUnattachedDetail.as_view()),
        name='base_unattached_detail',
    ),
    url(
	regex=r'^checkouts/$',
	view=login_required(FilterFormView.as_view()),
	name='checkout_filter',
    ),
    url(
	regex=r'^checkouts/edit/$',
	view=login_required(CheckoutEditFormView.as_view()),
	name='checkout_edit',
    ),
)

if settings.SERVE_STATIC:
    urlpatterns += patterns('',
	url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT,})
    )

