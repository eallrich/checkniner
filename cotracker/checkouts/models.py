from django.db import models
from django.contrib.auth.models import User

from model_utils.models import TimeStampedModel


class Airstrip(TimeStampedModel):
    ident = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=255)
    is_base = models.BooleanField()
    bases = models.ManyToManyField('self', symmetrical=False, limit_choices_to={'is_base': True}, blank=True, null=True)

    def __unicode__(self):
        return "%s (%s)" % (self.ident, self.name)
    
    def attached_airstrips(self):
	"""Retrieves the set of Airstrips which reference this instance as a
	base
	"""
	return Airstrip.objects.filter(bases=self).order_by('ident')
    
    def unattached_airstrips(self):
	"""Retrieves the set of Airstrips which do not reference this instance
	as a base
	"""
	# Note that the 'self' instance is specifically removed from the list
	return Airstrip.objects.exclude(pk=self.pk).exclude(bases=self).order_by('ident')


class AircraftType(TimeStampedModel):
    name = models.CharField(max_length=10)

    def __unicode__(self):
        return self.name


class Checkout(TimeStampedModel):
    pilot = models.ForeignKey(User, limit_choices_to={'groups__name': 'Pilots'})
    airstrip = models.ForeignKey(Airstrip)
    aircraft_type = models.ForeignKey(AircraftType)
    date = models.DateField('Checked out on')

    def get_pilot_name(self):
        return '%s, %s' % (self.pilot.last_name, self.pilot.first_name)
    get_pilot_name.short_description = 'Pilot'
    get_pilot_name.admin_order_field = 'pilot'

    def __unicode__(self):
        return '%s was checked out at %s in a %s on %s' % (self.get_pilot_name(), self.airstrip, self.aircraft_type, self.date)
