import datetime

from django.test import TestCase

from checkouts import util
from checkouts.models import AircraftType, Checkout

import helper


class GetAircraftTypeNamesTests(TestCase):
    
    def test_empty(self):
	self.assertEqual(len(util.get_aircrafttype_names()), 0)
    
    def test_single(self):
	name = 'ACTypeName'
	AircraftType.objects.create(name=name)
	self.assertEqual(util.get_aircrafttype_names(), [name,])
    
    def test_multiple(self):
	names = ['Name1','Name2','Name3']
	for n in names:
	    AircraftType.objects.create(name=n)
	self.assertEqual(util.get_aircrafttype_names(), names)
    
    def test_multiple_sort(self):
	names = ['Name2','Name1','Name3']
	for n in names:
	    AircraftType.objects.create(name=n)
	
	# Ascending
	names.sort()
	self.assertEqual(util.get_aircrafttype_names(), names)
	# Descending
	names.reverse()
	self.assertEqual(util.get_aircrafttype_names("-name"), names)


class PilotCheckoutsGroupedByAirstripTests(TestCase):
    
    def test_empty(self):
	pilot = helper.create_pilot()
	self.assertEqual(len(util.pilot_checkouts_grouped_by_airstrip(pilot)), 0)
    
    def test_single_airstrip_single_aircrafttype(self):
	c = helper.create_checkout()
	
	expected = [{
	    'ident': c.airstrip.ident,
	    'name': c.airstrip.name,
	    'aircraft': [util.CHECKOUT_SUDAH,],
	}]
	
	by_airstrip = util.pilot_checkouts_grouped_by_airstrip(c.pilot)
	self.assertEqual(by_airstrip, expected)
    
    def test_single_airstrip_multiple_aircrafttype_single_checkout(self):
	actype1 = helper.create_aircrafttype('Name1')    
	actype2 = helper.create_aircrafttype('Name2')
	
	c = helper.create_checkout(aircraft_type=actype1)
	expected = [{
	    'ident': c.airstrip.ident,
	    'name': c.airstrip.name,
	    'aircraft': [util.CHECKOUT_SUDAH,util.CHECKOUT_BELUM],
	},]
	by_airstrip = util.pilot_checkouts_grouped_by_airstrip(c.pilot)
	self.assertEqual(by_airstrip, expected)
    
    def test_single_airstrip_multiple_aircrafttype_multiple_checkout(self):
	actype1 = helper.create_aircrafttype('Name1')    
	actype2 = helper.create_aircrafttype('Name2')
	
	c = helper.create_checkout(aircraft_type=actype1)
	helper.create_checkout(pilot=c.pilot, airstrip=c.airstrip, aircraft_type=actype2)
	
	expected = [{
	    'ident': c.airstrip.ident,
	    'name': c.airstrip.name,
	    'aircraft': [util.CHECKOUT_SUDAH,util.CHECKOUT_SUDAH],
	},]
	
	by_airstrip = util.pilot_checkouts_grouped_by_airstrip(c.pilot)
	self.assertEqual(by_airstrip, expected)
	
    def test_multiple_airstrip_single_aircrafttype_single_checkout(self):
	airstrip1 = helper.create_airstrip('ID1','Airstrip1')
	airstrip2 = helper.create_airstrip('ID2','Airstrip2')
	
	c = helper.create_checkout(airstrip=airstrip1)
	
	expected = [
	    {
		'ident': airstrip1.ident,
		'name': airstrip1.name,
		'aircraft': [util.CHECKOUT_SUDAH,],
	    },
	]
	
	by_airstrip = util.pilot_checkouts_grouped_by_airstrip(c.pilot)
	self.assertEqual(by_airstrip, expected)
	
    def test_multiple_airstrip_single_aircrafttype_multiple_checkout(self):
	airstrip1 = helper.create_airstrip('ID1','Airstrip1')
	airstrip2 = helper.create_airstrip('ID2','Airstrip2')
	
	c = helper.create_checkout(airstrip=airstrip1)
	helper.create_checkout(pilot=c.pilot, airstrip=airstrip2, aircraft_type=c.aircraft_type)
	
	expected = [
	    {
		'ident': airstrip1.ident,
		'name': airstrip1.name,
		'aircraft': [util.CHECKOUT_SUDAH,],
	    }, {
		'ident': airstrip2.ident,
		'name': airstrip2.name,
		'aircraft': [util.CHECKOUT_SUDAH,],
	    },
	]
	
	by_airstrip = util.pilot_checkouts_grouped_by_airstrip(c.pilot)
	self.assertEqual(by_airstrip, expected)
	
    def test_multiple_airstrip_multiple_aircrafttype(self):
	airstrip1 = helper.create_airstrip('ID1','Airstrip1')
	airstrip2 = helper.create_airstrip('ID2','Airstrip2')
	actype1 = helper.create_aircrafttype('AC1')
	actype2 = helper.create_aircrafttype('AC2')
	
	c = helper.create_checkout(airstrip=airstrip1, aircraft_type=actype1)
	helper.create_checkout(pilot=c.pilot, airstrip=airstrip1, aircraft_type=actype2)
	helper.create_checkout(pilot=c.pilot, airstrip=airstrip2, aircraft_type=actype1)
	helper.create_checkout(pilot=c.pilot, airstrip=airstrip2, aircraft_type=actype2)
	
	expected = [
	    {
		'ident': airstrip1.ident,
		'name': airstrip1.name,
		'aircraft': [util.CHECKOUT_SUDAH,util.CHECKOUT_SUDAH],
	    }, {
		'ident': airstrip2.ident,
		'name': airstrip2.name,
		'aircraft': [util.CHECKOUT_SUDAH,util.CHECKOUT_SUDAH],
	    },
	]
	
	by_airstrip = util.pilot_checkouts_grouped_by_airstrip(c.pilot)
	self.assertEqual(by_airstrip, expected)
	

class AirstripCheckoutsGroupedByPilotTests(TestCase):
    
    def test_empty(self):
	airstrip = helper.create_airstrip()
	self.assertEqual(len(util.airstrip_checkouts_grouped_by_pilot(airstrip)), 0)
    
    def test_single_pilot_single_aircrafttype(self):
	c = helper.create_checkout()
	
	expected = [{
	    'pilot_name': c.get_pilot_name(),
	    'pilot_username': c.pilot.username,
	    'aircraft': [util.CHECKOUT_SUDAH,],
	}]
	
	by_pilot = util.airstrip_checkouts_grouped_by_pilot(c.airstrip)
	self.assertEqual(by_pilot, expected)
    
    def test_single_pilot_multiple_aircrafttype_single_checkout(self):
	actype1 = helper.create_aircrafttype('Name1')    
	actype2 = helper.create_aircrafttype('Name2')
	
	c = helper.create_checkout(aircraft_type=actype1)
	expected = [{
	    'pilot_name': c.get_pilot_name(),
	    'pilot_username': c.pilot.username,
	    'aircraft': [util.CHECKOUT_SUDAH,util.CHECKOUT_BELUM],
	},]
	by_pilot = util.airstrip_checkouts_grouped_by_pilot(c.airstrip)
	self.assertEqual(by_pilot, expected)
    
    def test_single_pilot_multiple_aircrafttype_multiple_checkout(self):
	actype1 = helper.create_aircrafttype('Name1')    
	actype2 = helper.create_aircrafttype('Name2')
	
	c = helper.create_checkout(aircraft_type=actype1)
	helper.create_checkout(pilot=c.pilot, airstrip=c.airstrip, aircraft_type=actype2)
	
	expected = [{
	    'pilot_name': c.get_pilot_name(),
	    'pilot_username': c.pilot.username,
	    'aircraft': [util.CHECKOUT_SUDAH,util.CHECKOUT_SUDAH],
	},]
	
	by_pilot = util.airstrip_checkouts_grouped_by_pilot(c.airstrip)
	self.assertEqual(by_pilot, expected)
	
    def test_multiple_pilot_single_aircrafttype_single_checkout(self):
	pilot1 = helper.create_pilot('kim','Kim','Pilot1')
	pilot2 = helper.create_pilot('sam','Sam','Pilot2')
	
	c = helper.create_checkout(pilot=pilot1)
	
	expected = [
	    {
		'pilot_name': c.get_pilot_name(),
		'pilot_username': c.pilot.username,
		'aircraft': [util.CHECKOUT_SUDAH,],
	    },
	]
	
	by_pilot = util.airstrip_checkouts_grouped_by_pilot(c.airstrip)
	self.assertEqual(by_pilot, expected)
	
    def test_multiple_airstrip_single_aircrafttype_multiple_checkout(self):
	pilot1 = helper.create_pilot('kim','Kim','Pilot1')
	pilot2 = helper.create_pilot('sam','Sam','Pilot2')
	
	c1 = helper.create_checkout(pilot=pilot1)
	c2 = helper.create_checkout(pilot=pilot2, airstrip=c1.airstrip, aircraft_type=c1.aircraft_type)
	
	expected = [
	    {
		'pilot_name': c1.get_pilot_name(),
		'pilot_username': c1.pilot.username,
		'aircraft': [util.CHECKOUT_SUDAH,],
	    }, {
		'pilot_name': c2.get_pilot_name(),
		'pilot_username': c2.pilot.username,
		'aircraft': [util.CHECKOUT_SUDAH,],
	    },
	]
	
	by_pilot = util.airstrip_checkouts_grouped_by_pilot(c1.airstrip)
	self.assertEqual(by_pilot, expected)
	
    def test_multiple_pilot_multiple_aircrafttype(self):
	pilot1 = helper.create_pilot('kim','Kim','Pilot1')
	pilot2 = helper.create_pilot('sam','Sam','Pilot2')
	actype1 = helper.create_aircrafttype('AC1')
	actype2 = helper.create_aircrafttype('AC2')
	
	c1 = helper.create_checkout(pilot=pilot1, aircraft_type=actype1)
	c2 = helper.create_checkout(pilot=pilot1, airstrip=c1.airstrip, aircraft_type=actype2)
	c3 = helper.create_checkout(pilot=pilot2, airstrip=c1.airstrip, aircraft_type=actype1)
	c4 = helper.create_checkout(pilot=pilot2, airstrip=c1.airstrip, aircraft_type=actype2)
	
	expected = [
	    {
		'pilot_name': c1.get_pilot_name(),
		'pilot_username': c1.pilot.username,
		'aircraft': [util.CHECKOUT_SUDAH,util.CHECKOUT_SUDAH],
	    }, {
		'pilot_name': c3.get_pilot_name(),
		'pilot_username': c3.pilot.username,
		'aircraft': [util.CHECKOUT_SUDAH,util.CHECKOUT_SUDAH],
	    },
	]
	
	by_pilot = util.airstrip_checkouts_grouped_by_pilot(c1.airstrip)
	self.assertEqual(by_pilot, expected)
	
