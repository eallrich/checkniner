from django.conf.urls import include, url
from django.contrib import admin, auth
from django.shortcuts import redirect

from checkouts.views import (
    PilotList,
    PilotDetail,
    AirstripList,
    AirstripDetail,
    BaseList,
    BaseAttachedDetail,
    BaseUnattachedDetail,
    BaseEditAttached,
    FilterFormView,
    CheckoutEditFormView,
    WeightList,
    WeightEdit,
)

admin.autodiscover()

urlpatterns = [
    url(r'^login/$', auth.views.LoginView.as_view(template_name='checkouts/login.html'), name='login'),
    url(r'^logout/$', auth.views.logout_then_login, name='logout'),
    url(r'^password_change/$', auth.views.PasswordChangeView.as_view(template_name='checkouts/password_change_form.html'), name='password_change'),
    url(r'^password_change/done/$', auth.views.PasswordChangeDoneView.as_view(template_name='checkouts/password_change_done.html'), name='password_change_done'),
    url(r'^emerald/', admin.site.urls),
    # Checkouts app views
    url(
        regex=r'^$',
        # No 'home' view at this time, but we may want to add one later. For
        # now, provide a redirect to a popular view instead.
        view=lambda x: redirect('checkout_filter', permanent=False),
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
        regex=r'^bases/(?P<ident>\w+)/edit/$',
        view=BaseEditAttached.as_view(),
        name='base_edit',
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
    url(
        regex=r'^weights/$',
        view=WeightList.as_view(),
        name='weight_list',
    ),
    url(
        regex=r'^weights/(?P<pilot>\w+)/edit/$',
        view=WeightEdit.as_view(),
        name='weight_edit',
    ),
]

