from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import Group, User

from checkouts.models import AircraftType, Airstrip, Checkout


class AircraftTypeTests(TestCase):
    
    def test_unicode(self):
	name = 'FooBar1234'
	o = AircraftType.objects.create(name=name)
	self.assertEqual(o.__unicode__(), name)


class AirstripTests(TestCase):
    
    def test_unicode(self):
	ident, name = ('ABCD', 'AlphaBravoCharlieDelta')
	o = Airstrip.objects.create(ident=ident, name=name)
	self.assertEqual(o.__unicode__(), "%s (%s)" % (ident, name)) 


class CheckoutTests(TestCase):
    
    def setUp(self):
	# Properties
	self.group_name = 'Pilots'
	
	self.pilot_username = 'kimpilot'
	self.pilot_email = 'kimpilot@example.com'
	self.pilot_password = 'super password'
	self.pilot_first_name = 'Kim'
	self.pilot_last_name = 'Pilot'
	
	self.aircrafttype_name = 'FooBar1234'
	self.airstrip_ident = 'ABCD'
	self.airstrip_name = 'AlphaBravoCharlieDelta'
	
	# Objects
	group = Group.objects.create(name=self.group_name)
	
	self.pilot = User.objects.create_user(
	    self.pilot_username, 
	    self.pilot_email, 
	    self.pilot_password
	)
	self.pilot.groups.add(group)
	self.pilot.first_name = self.pilot_first_name
	self.pilot.last_name = self.pilot.last_name
	
	self.aircraft_type = AircraftType.objects.create(name=self.aircrafttype_name)
	
	self.airstrip = Airstrip.objects.create(
	    ident=self.airstrip_ident,
	    name=self.airstrip_name
	)
	
	self.checkout = Checkout.objects.create(
	    pilot = self.pilot,
	    aircraft_type = self.aircraft_type,
	    airstrip = self.airstrip,
	    date = datetime.now(),
	)
	
	# We'll reuse the date during testing. Since the tests will (very)
	# likely complete on the same day they were started, this shouldn't
	# cause problems.
	self.date = self.checkout.date
    
    def test_unicode(self):
	expected = '%s was checked out at %s in a %s on %s' % (self.checkout.get_pilot_name(), self.airstrip, self.aircraft_type, self.date) 
	self.assertEqual(self.checkout.__unicode__(), expected)
    
    def test_get_pilot_name(self):
	expected = '%s, %s' % (self.pilot.last_name, self.pilot.first_name)
	self.assertEqual(self.checkout.get_pilot_name(), expected)

