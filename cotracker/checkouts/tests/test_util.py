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
	    'aircraft': [True,],
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
	    'aircraft': [True,False],
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
	    'aircraft': [True,True],
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
		'aircraft': [True,],
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
		'aircraft': [True,],
	    }, {
		'ident': airstrip2.ident,
		'name': airstrip2.name,
		'aircraft': [True,],
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
		'aircraft': [True,True],
	    }, {
		'ident': airstrip2.ident,
		'name': airstrip2.name,
		'aircraft': [True,True],
	    },
	]
	
	by_airstrip = util.pilot_checkouts_grouped_by_airstrip(c.pilot)
	self.assertEqual(by_airstrip, expected)
	
