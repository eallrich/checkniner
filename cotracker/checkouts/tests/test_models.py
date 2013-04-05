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
    
    def test_attached_airstrips(self):
	base1 = helper.create_airstrip('B1', is_base=True)
	# Single base, no airstrips
	self.assertEqual(base1.attached_airstrips().count(), 0)
	
	airstrip1 = helper.create_airstrip('A1')
	airstrip2 = helper.create_airstrip('A2')
	# Single base, multiple airstrips
	self.assertEqual(base1.attached_airstrips().count(), 0)
	
	airstrip1.bases.add(base1)
	# Single airstrip attached
	self.assertEqual(base1.attached_airstrips().count(), 1)
	
	airstrip2.bases.add(base1)
	# Multiple airstrips attached
	self.assertEqual(base1.attached_airstrips().count(), 2)
	
	base2 = helper.create_airstrip('B2', is_base=True)
	# Multiple bases, no attached airstrips
	self.assertEqual(base2.attached_airstrips().count(), 0)
	
	airstrip1.bases.add(base2)
	# Multiple attached bases on airstrip
	self.assertEqual(base1.attached_airstrips().count(), 2)
	self.assertEqual(base2.attached_airstrips().count(), 1)

    def test_unattached_airstrips(self):
	base1 = helper.create_airstrip('B1', is_base=True)
	# Single base, no airstrips
	self.assertEqual(base1.unattached_airstrips().count(), 0)
	
	airstrip1 = helper.create_airstrip('A1')
	airstrip2 = helper.create_airstrip('A2')
	# Single base, multiple airstrips
	self.assertEqual(base1.unattached_airstrips().count(), 2)
	
	airstrip1.bases.add(base1)
	# Single airstrip attached
	self.assertEqual(base1.unattached_airstrips().count(), 1)
	
	airstrip2.bases.add(base1)
	# Multiple airstrips attached
	self.assertEqual(base1.unattached_airstrips().count(), 0)
	
	base2 = helper.create_airstrip('B2', is_base=True)
	# Multiple bases, no attached airstrips
	self.assertEqual(base2.unattached_airstrips().count(), 3)
	
	airstrip1.bases.add(base2)
	# Multiple attached bases on airstrip
	self.assertEqual(base1.unattached_airstrips().count(), 1)
	self.assertEqual(base2.unattached_airstrips().count(), 2)


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

