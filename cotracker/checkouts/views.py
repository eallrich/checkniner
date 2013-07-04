import logging

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render
from django.views.generic import DetailView, ListView, View

from braces.views import LoginRequiredMixin

from .forms import FilterForm, CheckoutEditForm
from .models import AircraftType, Airstrip, Checkout
import util

logger = logging.getLogger(__name__)

class PilotList(LoginRequiredMixin, ListView):
    queryset = User.objects.filter(groups__name='Pilots').order_by('last_name','first_name')
    context_object_name = 'pilot_list'
    template_name = 'checkouts/pilot_list.html'
    

class PilotDetail(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = 'pilot'
    template_name = 'checkouts/pilot_detail.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
	context = super(PilotDetail, self).get_context_data(**kwargs)
	
	context['checkouts'] = util.pilot_checkouts_grouped_by_airstrip(self.object)
	
	return context


class AirstripList(LoginRequiredMixin, ListView):
    queryset = Airstrip.objects.all().order_by('ident')
    context_object_name = 'airstrip_list'
    template_name = 'checkouts/airstrip_list.html'


class AirstripDetail(LoginRequiredMixin, DetailView):
    model = Airstrip
    context_object_name = 'airstrip'
    template_name = 'checkouts/airstrip_detail.html'
    slug_field = 'ident'
    slug_url_kwarg = 'ident'
    
    def get_context_data(self, **kwargs):
	context = super(AirstripDetail, self).get_context_data(**kwargs)
	
	context['checkouts'] = util.airstrip_checkouts_grouped_by_pilot(self.object)
	
	return context


class BaseList(LoginRequiredMixin, ListView):
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


class BaseAttachedDetail(LoginRequiredMixin, DetailView):
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


class BaseUnattachedDetail(LoginRequiredMixin, DetailView):
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


class FilterFormView(LoginRequiredMixin, View):
    form_class = FilterForm
    template_name = 'checkouts/filter.html'
    
    def get(self, request, *args, **kwargs):
	logger.debug("=> FilterFormView.get")
	form = self.form_class()
	return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
	logger.debug("=> FilterFormView.post")
	logger.debug(request.POST)
	form = self.form_class(request.POST)
	context = {'form': form}
	
	if form.is_valid():
	    logger.debug(form.cleaned_data)
	    pilot = form.cleaned_data['pilot']
	    airstrip = form.cleaned_data['airstrip']
	    base = form.cleaned_data['base']
	    status = form.cleaned_data['checkout_status']
	    if status == util.CHECKOUT_SUDAH:
		context['checkouts'] = util.checkouts_selesai(pilot=pilot, airstrip=airstrip, base=base)
	    else:
		context['checkouts'] = util.checkouts_belum_selesai(pilot=pilot, airstrip=airstrip, base=base)
	    context['show_summary'] = True
	else:
	    logger.debug("Unable to validate form data")
	    
	return render(request, self.template_name, context)


class CheckoutEditFormView(LoginRequiredMixin, View):
    form_class = CheckoutEditForm
    template_name = 'checkouts/edit.html'
    
    def get(self, request, *args, **kwargs):
	logger.debug("=> CheckoutEditFormView.get")
	
	# Security Check
	# --------------
	# This would be unusual, but just in case: make sure that the request
	# is from a superuser or a pilot (normal users may not edit checkouts).
	if not request.user.is_superuser and not request.user.is_pilot():
	    logger.warn("Forbidden: '%s' is neither a pilot nor a superuser" % request.user.username)
	    context = {
		'reason': "Only pilots may edit checkouts.",
	    }
	    return render(request, 'checkouts/forbidden.html', context, status=403)
	
	init_data = {}
	if request.user.is_pilot():
	    init_data['pilot'] = request.user
	
	form = self.form_class(initial=init_data)
	
	if not request.user.is_superuser:
	    form['pilot'].field.queryset = User.objects.filter(pk=request.user.id)
	
	return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
	logger.debug("=> CheckoutEditFormView.post")
	
	# Security Check
	# --------------
	# This would be unusual, but just in case: make sure that the request
	# is from a superuser or a pilot (normal users may not edit checkouts).
	if not request.user.is_superuser and not request.user.is_pilot():
	    username = request.user.username
	    logger.warn("Forbidden: '%s' is neither a pilot nor a superuser" % username)
	    context = {
		'reason': "Only pilots may edit checkouts.",
	    }
	    return render(request, 'checkouts/forbidden.html', context, status=403)
	
	logger.debug(request.POST)
	form = self.form_class(request.POST)
	context = {'form': form}
	
	if form.is_valid():
	    logger.debug(form.cleaned_data)
	    pilot = form.cleaned_data['pilot']
	    
	    # Security Check
	    # --------------
	    # This would be unusual, but just in case: if the user is not a
	    # superuser, they may only edit their own checkouts
	    if pilot != request.user and not request.user.is_superuser:
		username = request.user.username
		logger.warn("Forbidden: '%s' is not a superuser and may only edit their own checkouts" % username)
		context = {
		    'reason': "Pilots may only edit their own checkouts.",
		}
		return render(request, 'checkouts/forbidden.html', context, status=403)
	    
	    airstrip = form.cleaned_data['airstrip']
	    aircraft_types = form.cleaned_data['aircraft_type']
	    
	    delete_checkouts = False
	    if request.POST['action'] == u'Remove Checkout':
		delete_checkouts = True
	    
	    if delete_checkouts:
		checkouts = Checkout.objects.filter(pilot=pilot, airstrip=airstrip, aircraft_type__in=aircraft_types)
		for c in checkouts:
		    logger.info("Deleting '%s'" % c)
		    aircraft_types = aircraft_types.exclude(name=c.aircraft_type)
		    c.delete()
		    messages.add_message(request, messages.SUCCESS, "Deleted '%s'" % c)
		if len(aircraft_types) > 0:
		    for ac_type in aircraft_types:
			logger.info("Pretending to delete non-existent checkout '%s is checked out at %s in a %s'" % (pilot, airstrip, ac_type))
			messages.add_message(request, messages.SUCCESS, "Deleted '%s is checked out at %s in a %s'" % (pilot, airstrip, ac_type))
	    else:
		for ac_type in aircraft_types:
		    existing = Checkout.objects.filter(pilot=pilot, airstrip=airstrip, aircraft_type=ac_type)
		    if existing.exists():
			logger.debug("Prevented duplicate '%s'" % existing[0])
			messages.add_message(request, messages.SUCCESS, "Already exists: '%s'" % existing[0])
		    else:
			c = Checkout(pilot=pilot, airstrip=airstrip, aircraft_type=ac_type)
			logger.info("Adding '%s'" % c)
			c.save()
			messages.add_message(request, messages.SUCCESS, "Added '%s'" % c)
	else:
	    logger.debug("Unable to validate form data: %s" % form.errors)
	    messages.add_message(request, messages.ERROR, "Unable to complete your request - please check the error message(s) below.")
	
	return render(request, self.template_name, context)
