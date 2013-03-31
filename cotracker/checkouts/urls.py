from django.conf.urls import patterns, url

from .views import (
    CheckoutsByPilotList,
    CheckoutsByPilotDetail,
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
)
