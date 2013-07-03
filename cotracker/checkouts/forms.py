from django import forms

from .models import AircraftType, Airstrip
import util


class BaseModelChoiceField(forms.ModelChoiceField):
    """Airstrips are generally represented as an 'Ident (Name)' string, but for
    the Filter form only the Name component should be shown.
    """
    def label_from_instance(self, airstrip):
	return airstrip.name


class FilterForm(forms.Form):
    pilot = forms.ModelChoiceField(
	queryset=util.get_pilots(), 
	empty_label="All", 
	required=False,
    )
    
    airstrip = forms.ModelChoiceField(
	queryset=Airstrip.objects.all().order_by('ident'),
	empty_label="All",
	required=False,
    )
    
    base = BaseModelChoiceField(
	queryset=util.get_bases().order_by('name'),
	empty_label="All",
	required=False,
    )
    
    aircraft_type = forms.ModelChoiceField(
	queryset=AircraftType.objects.all().order_by('name'),
	empty_label="All",
	required=False,
	widget=forms.RadioSelect,
    )
    
    checkout_status = forms.ChoiceField(
	choices=util.choices_checkout_status(),
	initial=util.CHECKOUT_SUDAH,
	widget=forms.RadioSelect,
    )


class CheckoutEditForm(forms.Form):
    pilot = forms.ModelChoiceField(
	# We're defaulting to the full list, but it may be trimmed down to the
	# request's authenticated user in the view
	queryset=util.get_pilots(), 
	empty_label=None,
    )
    
    airstrip = forms.ModelChoiceField(
	queryset=Airstrip.objects.all().order_by('ident'),
	empty_label=None,
    )
    
    aircraft_type = forms.ModelMultipleChoiceField(
	queryset=AircraftType.objects.all().order_by('name'),
	widget=forms.CheckboxSelectMultiple,
    )
