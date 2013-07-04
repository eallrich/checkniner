"""View definitions for the Checkouts app"""
import logging

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render # Used for rendering 403 Forbidden
from django.views.generic import DetailView, ListView, TemplateView

from braces.views import LoginRequiredMixin

from .forms import FilterForm, CheckoutEditForm
from .models import AircraftType, Airstrip, Checkout
import util

logger = logging.getLogger(__name__)


class Home(LoginRequiredMixin, ListView):
    """List of latest checkouts"""
    queryset = Checkout.objects.all().order_by('-date')[:20]
    context_object_name = 'checkout_list'
    template_name = 'checkouts/home.html'

class PilotList(LoginRequiredMixin, ListView):
    """List of current pilots"""
    queryset = util.get_pilots()
    context_object_name = 'pilot_list'
    template_name = 'checkouts/pilot_list.html'
    

class PilotDetail(LoginRequiredMixin, DetailView):
    """All checkout information for a particular pilot"""
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
    """List of current airstrips"""
    queryset = Airstrip.objects.all().order_by('ident')
    context_object_name = 'airstrip_list'
    template_name = 'checkouts/airstrip_list.html'


class AirstripDetail(LoginRequiredMixin, DetailView):
    """All checkout information for a particular airstrip"""
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
    """List of airstrips which are bases"""
    queryset = util.get_bases().annotate(attached=Count('airstrip'))
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
    """List of airstrips which are attached to a given base"""
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
    """List of airstrips which are not attached to a given base"""
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


class FilterFormView(LoginRequiredMixin, TemplateView):
    """Provides an interface for filtering the set of checkout records
    
    Not limited to existing records: it's possible to query for 'which
    checkouts have not been completed?'
    """
    form_class = FilterForm
    template_name = 'checkouts/filter.html'
    
    def get(self, request, *args, **kwargs):
        """Renders a fresh filter form"""
        logger.debug("=> FilterFormView.get")
        context = {'form': self.form_class(),}
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        """If the filter is valid, renders the filtered checkout data"""
        logger.debug("=> FilterFormView.post")
        logger.debug(request.POST)
        form = self.form_class(request.POST)
        context = {'form': form}
        
        if not form.is_valid():
            logger.debug("Unable to validate form data")
        else:
            logger.debug(form.cleaned_data)
            status = form.cleaned_data['checkout_status']
            if status == util.CHECKOUT_SUDAH:
                context['checkouts'] = util.sudah_selesai(**form.cleaned_data)
            else:
                context['checkouts'] = util.belum_selesai(**form.cleaned_data)
            
            context['show_summary'] = True
            
        return self.render_to_response(context)


class CheckoutEditFormView(LoginRequiredMixin, TemplateView):
    """Provides an interface for adding and removing checkouts"""
    form_class = CheckoutEditForm
    template_name = 'checkouts/edit.html'
    
    def forbidden(self, request, message="Sorry, you can't do that."):
        """Shortcut for rendering an 'access denied' page"""
        template = 'checkouts/forbidden.html'
        context = {
            'reason': message,
        }
        return render(request, template, context, status=403)
    
    def get(self, request, *args, **kwargs):
        """Renders a fresh form instance"""
        logger.debug("=> CheckoutEditFormView.get")
        
        # Security Check
        # --------------
        # This would be unusual, but just in case: make sure that the request
        # is from a superuser or a pilot (normal users may not edit checkouts).
        if not request.user.is_superuser and not request.user.is_pilot:
            username = request.user.username
            logger.warn("Forbidden: '%s' is neither a pilot nor a superuser" % username)
            message = 'Only pilots may edit checkouts.'
            return self.forbidden(request, message)
        
        # Help out a pilot by pre-selecting their name
        if request.user.is_pilot:
            form = self.form_class(initial={'pilot': request.user})
        else:
            form = self.form_class()
        
        # Pilots may only edit their own checkouts if they are not a superuser
        if not request.user.is_superuser:
            form['pilot'].field.queryset = User.objects.filter(pk=request.user.id)
        
        return self.render_to_response({'form': form})
    
    def post(self, request, *args, **kwargs):
        """Given a valid form, performs the requested add/remove action and
        then renders the same view again."""
        logger.debug("=> CheckoutEditFormView.post")
        
        # Security Check
        # --------------
        # This would be unusual, but just in case: make sure that the request
        # is from a superuser or a pilot (normal users may not edit checkouts).
        if not request.user.is_superuser and not request.user.is_pilot:
            username = request.user.username
            logger.warn("Forbidden: '%s' is neither a pilot nor a superuser" % username)
            message = 'Only pilots may edit checkouts.'
            return self.forbidden(request, message)
        
        # Note that we're not doing anything with the submitted data until
        # _after_ the user has been verified as someone who can access this
        # view.
        logger.debug(request.POST)
        form = self.form_class(request.POST)
        context = {'form': form}
        
        if not form.is_valid():
            logger.debug("Unable to validate form data: %s" % form.errors)
            messages.add_message(
                        request, 
                        messages.ERROR, 
                        "Sorry, please check below for any error messages.")
        else:
            logger.debug(form.cleaned_data)
            pilot = form.cleaned_data['pilot']
            airstrip = form.cleaned_data['airstrip']
            aircraft_types = form.cleaned_data['aircraft_type']
            action = request.POST['action']
            
            # Security Check
            # --------------
            # This would be unusual, but just in case: if the user is not a
            # superuser, they may only edit their own checkouts
            if pilot != request.user and not request.user.is_superuser:
                username = request.user.username
                logger.warn("Forbidden: '%s' may not edit for '%s'" % (username, pilot.username))
                message = 'Pilots may only edit their own checkouts.'
                return self.forbidden(request, message)
            
            if action == u'Remove Checkout':
                checkouts = Checkout.objects.filter(
                                pilot=pilot, 
                                airstrip=airstrip, 
                                aircraft_type__in=aircraft_types)
                
                for c in checkouts:
                    logger.info("Deleting '%s'" % c)
                    # We'll be pretending that all of the requested checkouts
                    # were deleted, even if they never existed, so we need to
                    # keep track of which ones haven't really been deleted.
                    # Then we'll use those remaining 'checkouts' to construct
                    # 'delete successful' messages for the user.
                    aircraft_types = aircraft_types.exclude(name=c.aircraft_type)
                    c.delete()
                    messages.add_message(request, messages.SUCCESS, "Deleted '%s'" % c)
                
                # Now that all the checkouts which actually existed have been
                # deleted, we'll build 'delete successful' messages for each
                # of the remainders.
                if len(aircraft_types) > 0:
                    for ac_type in aircraft_types:
                        c = "%s is checked out at %s in a %s" % (pilot, airstrip, ac_type)
                        logger.info("Pretending to delete non-existent checkout '%s'" % c)
                        messages.add_message(request, messages.SUCCESS, "Deleted '%s'" % c)
                
            else:
                for ac_type in aircraft_types:
                    existing = Checkout.objects.filter(
                                    pilot=pilot, 
                                    airstrip=airstrip, 
                                    aircraft_type=ac_type)
                    
                    # Don't allow a duplicate checkout to be created. Unlike
                    # the 'delete checkout' version, here we'll actually tell
                    # the user that we found a duplicate (although it's still
                    # styled as a 'success' message).
                    if existing.exists():
                        c = existing[0]
                        logger.debug("Prevented duplicate '%s'" % c)
                        messages.add_message(
                                    request, 
                                    messages.SUCCESS, 
                                    "Already exists: '%s'" % c)
                    else:
                        c = Checkout(pilot=pilot, airstrip=airstrip, aircraft_type=ac_type)
                        logger.info("Adding '%s'" % c)
                        c.save()
                        messages.add_message(request, messages.SUCCESS, "Added '%s'" % c)
        
        return self.render_to_response(context)
