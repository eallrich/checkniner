from django.conf.urls import patterns, url

from .views import (
    CheckoutsByPilotList,
    CheckoutsByPilotDetail,
    CheckoutsByAirstripList,
    CheckoutsByAirstripDetail,
)

urlpatterns = patterns('',
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
