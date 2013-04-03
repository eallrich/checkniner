from django.contrib.auth.models import User
from django.db.models import Count
from django.views.generic import DetailView, ListView

from .models import AircraftType, Airstrip, Checkout
import util

class CheckoutsByPilotList(ListView):
    queryset = User.objects.filter(groups__name='Pilots').order_by('last_name','first_name')
    context_object_name = 'pilot_list'
    template_name = 'checkouts/checkouts_by_pilot_list.html'
    

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


class CheckoutsByAirstripList(ListView):
    queryset = Airstrip.objects.all().order_by('ident')
    context_object_name = 'airstrip_list'
    template_name = 'checkouts/checkouts_by_airstrip_list.html'


class CheckoutsByAirstripDetail(DetailView):
    model = Airstrip
    context_object_name = 'airstrip'
    template_name = 'checkouts/checkouts_by_airstrip_detail.html'
    slug_field = 'ident'
    slug_url_kwarg = 'ident'
    
    def get_context_data(self, **kwargs):
	context = super(CheckoutsByAirstripDetail, self).get_context_data(**kwargs)
	
	context['aircrafttypes'] = util.get_aircrafttype_names()
	example = [{
	    'pilot_name': 'Brown, Mike',
	    'pilot_username': 'mbrown',
	    'aircraft': ['sudah','belum','sudah'],
	}, {
	    'pilot_name': 'Janse, Kees',
	    'pilot_username': 'kjanse',
	    'aircraft': ['sudah','belum','belum'],
	}, {
	    'pilot_name': 'Lynne, Kevin',
	    'pilot_username': 'klynne',
	    'aircraft': ['sudah','belum','belum'],
	}]
	
	context['checkouts_by_pilot'] = example
	
	return context
