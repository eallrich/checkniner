import datetime

from django.test import TestCase

from checkouts.models import Checkout

import helper


class AircraftTypeTests(TestCase):
    
    def test_unicode(self):
	o, attributes = helper.create_aircrafttype(object_only=False)
	self.assertEqual(o.__unicode__(), attributes['name'])


class AirstripTests(TestCase):
    
    def test_unicode(self):
	o, attributes = helper.create_airstrip(object_only=False)
	self.assertEqual(
	    o.__unicode__(), 
	    "%s (%s)" % (attributes['ident'], attributes['name'])
	) 


class CheckoutTests(TestCase):
    
    def setUp(self):
	self.pilot = helper.create_pilot()
	self.aircrafttype = helper.create_aircrafttype()
	self.airstrip = helper.create_airstrip()
	self.date = datetime.date(2013,03,31)
	
	self.checkout = Checkout.objects.create(
	    pilot = self.pilot,
	    aircraft_type = self.aircrafttype,
	    airstrip = self.airstrip,
	    date = self.date,
	)
    
    def test_unicode(self):
	expected = '%s was checked out at %s in a %s on %s' % (self.checkout.get_pilot_name(), self.airstrip, self.aircrafttype, self.date) 
	self.assertEqual(self.checkout.__unicode__(), expected)
    
    def test_get_pilot_name(self):
	expected = '%s, %s' % (self.pilot.last_name, self.pilot.first_name)
	self.assertEqual(self.checkout.get_pilot_name(), expected)

