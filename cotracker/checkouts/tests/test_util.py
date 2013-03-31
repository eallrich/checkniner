from django.test import TestCase

from checkouts import util
from checkouts.models import AircraftType


class UtilTests(TestCase):
    
    def test_get_aircrafttype_names_empty(self):
	self.assertEqual(len(util.get_aircrafttype_names()), 0)
    
    def test_get_aircrafttype_names_single(self):
	name = 'ACTypeName'
	AircraftType.objects.create(name=name)
	self.assertEqual(util.get_aircrafttype_names(), [name,])
    
    def test_get_aircrafttype_names_multi(self):
	names = ['Name1','Name2','Name3']
	for n in names:
	    AircraftType.objects.create(name=n)
	self.assertEqual(util.get_aircrafttype_names(), names)
    
    def test_get_aircrafttype_names_sort(self):
	names = ['Name2','Name1','Name3']
	for n in names:
	    AircraftType.objects.create(name=n)
	
	# Ascending
	names.sort()
	self.assertEqual(util.get_aircrafttype_names(), names)
	# Descending
	names.reverse()
	self.assertEqual(util.get_aircrafttype_names("-name"), names)
