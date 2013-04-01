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
	pilot, _ = helper.create_pilot()
	self.assertEqual(len(util.pilot_checkouts_grouped_by_airstrip(pilot)), 0)
    
    def test_single_airstrip_single_aircrafttype(self):
	pilot, _ = helper.create_pilot()
	airstrip, _ = helper.create_airstrip()
	actype, _ = helper.create_aircrafttype()
	Checkout.objects.create(
	    pilot=pilot,
	    airstrip=airstrip,
	    aircraft_type=actype,
	    date=datetime.datetime.now(),
	)
	
	expected = [{
	    'ident': airstrip.ident,
	    'name': airstrip.name,
	    'aircraft': [True,],
	},]
	
	by_airstrip = util.pilot_checkouts_grouped_by_airstrip(pilot)
	self.assertEqual(by_airstrip, expected)
    
    def test_single_airstrip_multiple_aircrafttype(self):
	pilot, _ = helper.create_pilot()
	airstrip, _ = helper.create_airstrip()
	actype1, _ = helper.create_aircrafttype('Name1')    
	actype2, _ = helper.create_aircrafttype('Name2')
	Checkout.objects.create(
	    pilot=pilot,
	    airstrip=airstrip,
	    aircraft_type=actype1,
	    date=datetime.datetime.now(),
	)
	Checkout.objects.create(
	    pilot=pilot,
	    airstrip=airstrip,
	    aircraft_type=actype2,
	    date=datetime.datetime.now(),
	)
	
	expected = [{
	    'ident': airstrip.ident,
	    'name': airstrip.name,
	    'aircraft': [True,True],
	},]
	
	by_airstrip = util.pilot_checkouts_grouped_by_airstrip(pilot)
	self.assertEqual(by_airstrip, expected)
	
    def test_multiple_airstrip_single_aircrafttype(self):
	pilot, _ = helper.create_pilot()
	airstrip1, _ = helper.create_airstrip('ID1','Airstrip1')
	airstrip2, _ = helper.create_airstrip('ID2','Airstrip2')
	actype, _ = helper.create_aircrafttype()    
	Checkout.objects.create(
	    pilot=pilot,
	    airstrip=airstrip1,
	    aircraft_type=actype,
	    date=datetime.datetime.now(),
	)
	Checkout.objects.create(
	    pilot=pilot,
	    airstrip=airstrip2,
	    aircraft_type=actype,
	    date=datetime.datetime.now(),
	)
	
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
	
	by_airstrip = util.pilot_checkouts_grouped_by_airstrip(pilot)
	self.assertEqual(by_airstrip, expected)
	
    def test_multiple_airstrip_multiple_aircrafttype(self):
	pilot, _ = helper.create_pilot()
	airstrip1, _ = helper.create_airstrip('ID1','Airstrip1')
	airstrip2, _ = helper.create_airstrip('ID2','Airstrip2')
	actype1, _ = helper.create_aircrafttype('AC1')
	actype2, _ = helper.create_aircrafttype('AC2')
	Checkout.objects.create(
	    pilot=pilot,
	    airstrip=airstrip1,
	    aircraft_type=actype1,
	    date=datetime.datetime.now(),
	)
	Checkout.objects.create(
	    pilot=pilot,
	    airstrip=airstrip1,
	    aircraft_type=actype2,
	    date=datetime.datetime.now(),
	)
	Checkout.objects.create(
	    pilot=pilot,
	    airstrip=airstrip2,
	    aircraft_type=actype1,
	    date=datetime.datetime.now(),
	)
	Checkout.objects.create(
	    pilot=pilot,
	    airstrip=airstrip2,
	    aircraft_type=actype2,
	    date=datetime.datetime.now(),
	)
	
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
	
	by_airstrip = util.pilot_checkouts_grouped_by_airstrip(pilot)
	self.assertEqual(by_airstrip, expected)
	
