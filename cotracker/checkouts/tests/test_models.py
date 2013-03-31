import datetime

from django.test import TestCase
from django.contrib.auth.models import Group, User

from checkouts.models import AircraftType, Airstrip, Checkout


def create_aircrafttype(name='FooBar1234'):
    o = AircraftType.objects.create(name=name)
    return (o, {'name': name,})


def create_airstrip(ident='ABCD', name='AlphaBravoCharlieDelta'):
    o = Airstrip.objects.create(ident=ident, name=name)
    return (o, {'ident': ident, 'name': name,})


def create_pilot(username='kimpilot', email='kim@ex.com', password='secret', first_name='Kim', last_name='Pilot'):
    pilot_group, _ = Group.objects.get_or_create(name='Pilots')
    pilot = User.objects.create_user(username, email, password)
    pilot.groups.add(pilot_group)
    pilot.first_name = first_name
    pilot.last_name = last_name
    
    attributes = {
	'username': username,
	'email': email,
	'password': password,
	'first_name': first_name,
	'last_name': last_name,
    }
    
    return (pilot, attributes)


class AircraftTypeTests(TestCase):
    
    def test_unicode(self):
	o, attributes = create_aircrafttype()
	self.assertEqual(o.__unicode__(), attributes['name'])


class AirstripTests(TestCase):
    
    def test_unicode(self):
	o, attributes = create_airstrip()
	self.assertEqual(
	    o.__unicode__(), 
	    "%s (%s)" % (attributes['ident'], attributes['name'])
	) 


class CheckoutTests(TestCase):
    
    def setUp(self):
	self.pilot, self.pilot_attr = create_pilot()
	self.aircrafttype, self.ac_attr = create_aircrafttype()
	self.airstrip, self.airstrip_attr = create_airstrip()
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

