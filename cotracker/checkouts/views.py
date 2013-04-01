from django.contrib.auth.models import User
from django.db.models import Count
from django.views.generic import DetailView, ListView

from .models import AircraftType, Airstrip, Checkout
import util

class CheckoutsByPilotList(ListView):
    queryset = User.objects.filter(groups__name='Pilots').order_by('last_name','first_name')
    context_object_name = 'pilot_list'
    template_name = 'checkouts/checkouts_by_pilot_list.html'
    
    def get_queryset(self):
	"""Attaches the number of checkouts for each pilot to the
	returned queryset."""
	queryset = super(CheckoutsByPilotList, self).get_queryset()
	return queryset.annotate(checkouts=Count('checkout'))
	

class CheckoutsByPilotDetail(DetailView):
    model = User
    context_object_name = 'pilot'
    template_name = 'checkouts/checkouts_by_pilot_detail.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
	context = super(CheckoutsByPilotDetail, self).get_context_data(**kwargs)
	
	context['aircrafttypes'] = util.get_aircrafttype_names()
	context['checkouts_by_airstrip'] = util.pilot_checkouts_grouped_by_airstrip(self.object)
	
	return context
