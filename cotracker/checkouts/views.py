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
	
	pilot_checkouts = Checkout.objects.filter(pilot=self.object).select_related()
	
	grouped_checkouts = {}
	for c in pilot_checkouts:
	    if c.airstrip.ident not in grouped_checkouts:
		grouped_checkouts[c.airstrip.ident] = {
		    'airstrip_name': c.airstrip.name,
		    'aircraft': {},
		}
	    grouped_checkouts[c.airstrip.ident]['aircraft'][c.aircraft_type.name] = True
	
	checkout_data = []
	sorted_keys = grouped_checkouts.keys()
	sorted_keys.sort()
	for ident in sorted_keys:
	    name = grouped_checkouts[ident]['airstrip_name']
	    row_data = {
		'ident': ident, 
		'name': name,
		'aircraft': [],
	    }
	    for actype in context['aircrafttypes']:
		if actype in grouped_checkouts[ident]['aircraft']:
		    row_data['aircraft'].append(True)
		else:
		    row_data['aircraft'].append(False)
	    checkout_data.append(row_data)
	    
	context['checkout_data'] = checkout_data
	
	return context
