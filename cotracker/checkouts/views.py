import pprint
import sys

from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render
from django.views.generic import DetailView, ListView, View

from .forms import FilterForm
from .models import AircraftType, Airstrip, Checkout
import util

class PilotList(ListView):
    queryset = User.objects.filter(groups__name='Pilots').order_by('last_name','first_name')
    context_object_name = 'pilot_list'
    template_name = 'checkouts/pilot_list.html'
    

class PilotDetail(DetailView):
    model = User
    context_object_name = 'pilot'
    template_name = 'checkouts/pilot_detail.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
	context = super(PilotDetail, self).get_context_data(**kwargs)
	
	context['aircrafttypes'] = util.get_aircrafttype_names()
	context['checkouts_by_airstrip'] = util.pilot_checkouts_grouped_by_airstrip(self.object)
	
	return context


class AirstripList(ListView):
    queryset = Airstrip.objects.all().order_by('ident')
    context_object_name = 'airstrip_list'
    template_name = 'checkouts/airstrip_list.html'


class AirstripDetail(DetailView):
    model = Airstrip
    context_object_name = 'airstrip'
    template_name = 'checkouts/airstrip_detail.html'
    slug_field = 'ident'
    slug_url_kwarg = 'ident'
    
    def get_context_data(self, **kwargs):
	context = super(AirstripDetail, self).get_context_data(**kwargs)
	
	context['aircrafttypes'] = util.get_aircrafttype_names()
	
	context['checkouts_by_pilot'] = util.airstrip_checkouts_grouped_by_pilot(self.object)
	
	return context


class BaseList(ListView):
    queryset = Airstrip.objects.filter(is_base=True).order_by('name').annotate(attached=Count('airstrip'))
    template_name = 'checkouts/base_list.html'
    
    def get_context_data(self, **kwargs):
	context = super(BaseList, self).get_context_data(**kwargs)
	
	bases = self.object_list
	base_list = []
	for base in bases:
	    unattached = base.unattached_airstrips().count()
	    base_list.append((base, base.attached, unattached))
	
	context['base_list'] = base_list
	
	return context


class BaseAttachedDetail(DetailView):
    model = Airstrip
    context_object_name = 'base'
    template_name = 'checkouts/base_detail.html'
    slug_field = 'ident'
    slug_url_kwarg = 'ident'
    
    def get_context_data(self, **kwargs):
	context = super(BaseAttachedDetail, self).get_context_data(**kwargs)
	context['attached_state'] = "attached"
	context['airstrips'] = self.object.attached_airstrips()
	
	return context


class BaseUnattachedDetail(DetailView):
    model = Airstrip
    context_object_name = 'base'
    template_name = 'checkouts/base_detail.html'
    slug_field = 'ident'
    slug_url_kwarg = 'ident'
    
    def get_context_data(self, **kwargs):
	context = super(BaseUnattachedDetail, self).get_context_data(**kwargs)
	context['attached_state'] = "unattached"
	context['airstrips'] = self.object.unattached_airstrips()
	
	return context


class FilterFormView(View):
    form_class = FilterForm
    template_name = 'checkouts/filter.html'
    
    def get(self, request, *args, **kwargs):
	form = self.form_class()
	return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
	pprint.pprint(request.POST, stream=sys.stderr)
	form = self.form_class(request.POST)
	return render(request, self.template_name, {'form': form})
