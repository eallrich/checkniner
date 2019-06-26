from django.contrib.auth.models import User
from django.test import TestCase

from checkouts import util
from checkouts.models import AircraftType

import checkouts.tests.helper as helper


class GetAircraftTypeNamesTests(TestCase):
    
    def test_empty(self):
        self.assertNotEqual(len(util.get_aircrafttype_names()), 0)
    
    def test_single(self):
        name = 'ACTypeName'
        AircraftType.objects.create(name=name)
        self.assertEqual(util.get_aircrafttype_names(), [name,])
    
    def test_default_sort_without_position(self):
        """Without sorted_position values, defaults to an alpha sort"""
        names = ['Name1', 'Name2', 'Name3']
        for n in names:
            AircraftType.objects.create(name=n)
        self.assertEqual(util.get_aircrafttype_names(), names)
    
    def test_specific_sort(self):
        names = ['Name2','Name1', 'Name3']
        for i, n in enumerate(names):
            AircraftType.objects.create(name=n, sorted_position=i)
        
        # Default
        self.assertEqual(util.get_aircrafttype_names(), names)
        
        # By name, ascending
        names.sort()
        self.assertEqual(util.get_aircrafttype_names("name"), names)
        # By name, descending
        names.reverse()
        self.assertEqual(util.get_aircrafttype_names("-name"), names)


class GetPilotAirstripPairsTests(TestCase):
    
    def test_empty(self):
        self.assertEqual(util.get_pilot_airstrip_pairs(), [])
    
    def test_single(self):
        pilot = helper.create_pilot()
        airstrip = helper.create_airstrip()
        
        expected = [(pilot.username, airstrip.ident)]
        self.assertEqual(util.get_pilot_airstrip_pairs(), expected)
    
    def test_multiple(self):
        pilot1 = helper.create_pilot('kim', 'Kim', 'Pilot1')
        pilot2 = helper.create_pilot('sam', 'Sam', 'Pilot2')
        airstrip1 = helper.create_airstrip('ID1', 'Airstrip1')
        airstrip2 = helper.create_airstrip('ID2', 'Airstrip2')
        
        expected = [
            (pilot1.username, airstrip1.ident),
            (pilot1.username, airstrip2.ident),
            (pilot2.username, airstrip1.ident),
            (pilot2.username, airstrip2.ident),
        ]
        self.assertEqual(util.get_pilot_airstrip_pairs(), expected)
        
        # Filter on Pilot
        expected = [
            (pilot1.username, airstrip1.ident),
            (pilot1.username, airstrip2.ident),
        ]
        self.assertEqual(util.get_pilot_airstrip_pairs(pilot=pilot1), expected)
        
        # Filter on Airstrip
        expected = [
            (pilot1.username, airstrip2.ident),
            (pilot2.username, airstrip2.ident),
        ]
        self.assertEqual(util.get_pilot_airstrip_pairs(airstrip=airstrip2), expected)
        
        # Filter on Base
        base1 = helper.create_airstrip('BASE', 'Base1', is_base=True)
        airstrip1.bases.add(base1)
        
        expected = [
            (pilot1.username, airstrip1.ident),
            (pilot2.username, airstrip1.ident),
        ]
        self.assertEqual(util.get_pilot_airstrip_pairs(base=base1), expected)


class GetPrecedentedCheckoutsTests(TestCase):
    
    def test_empty(self):
        self.assertEqual(util.get_precedented_checkouts(), {})
    
    def test_single_precedented(self):
        c = helper.create_checkout()
        
        expected = {
            c.airstrip.ident: {
                c.aircraft_type.name: True,
            },
        }
        
        self.assertEqual(util.get_precedented_checkouts(), expected)
    
    def test_single_unprecedented(self):
        pilot = helper.create_pilot()
        airstrip = helper.create_airstrip()
        aircraft = helper.create_aircrafttype()
        
        expected = {}
        
        self.assertEqual(util.get_precedented_checkouts(), expected)
    
    def test_multiple(self):
        pilot1 = helper.create_pilot('kim', 'Kim', 'Pilot1')
        pilot2 = helper.create_pilot('sam', 'Sam', 'Pilot2')
        actype1 = helper.create_aircrafttype('Name1')    
        actype2 = helper.create_aircrafttype('Name2')
        airstrip1 = helper.create_airstrip('ID1', 'Airstrip1')
        airstrip2 = helper.create_airstrip('ID2', 'Airstrip2')
        airstrip3 = helper.create_airstrip('ID3', 'Airstrip3')
            
        c1 = helper.create_checkout(pilot=pilot1, airstrip=airstrip1, aircraft_type=actype1)
        c2 = helper.create_checkout(pilot=pilot1, airstrip=airstrip1, aircraft_type=actype2)
        c3 = helper.create_checkout(pilot=pilot2, airstrip=airstrip2, aircraft_type=actype1)
        
        expected = {
            airstrip1.ident: {
                actype1.name: True,
                actype2.name: True,
            },
            airstrip2.ident: {
                actype1.name: True,
            },
        }
        
        self.assertEqual(util.get_precedented_checkouts(), expected)


class CheckoutFilterTests(TestCase):   
 
    def test_empty(self):
        self.assertEqual(util.checkout_filter(), [])
    
    def test_single_checkout(self):
        c = helper.create_checkout()
        
        expected = [{
            'pilot_name': c.pilot.full_name,
            'pilot_slug': c.pilot.username,
            'airstrip_ident': c.airstrip.ident,
            'airstrip_name': c.airstrip.name,
            'actypes': {
                c.aircraft_type.name: util.CHECKOUT_SUDAH,
            },
        },]
        
        self.assertEqual(util.checkout_filter(), expected)
    
    def test_multiple_aircrafttypes(self):
        actype1 = helper.create_aircrafttype('Name1')    
        actype2 = helper.create_aircrafttype('Name2')
        
        c = helper.create_checkout(aircraft_type=actype1)
        
        expected = [{
            'pilot_name': c.pilot.full_name,
            'pilot_slug': c.pilot.username,
            'airstrip_ident': c.airstrip.ident,
            'airstrip_name': c.airstrip.name,
            'actypes': {
                actype1.name: util.CHECKOUT_SUDAH,
                actype2.name: util.CHECKOUT_BELUM,
            },
        },]
        
        self.assertEqual(util.checkout_filter(), expected)
        
        # Testing what happens when limiting to a particular aircraft type
        expected[0]['actypes'].pop(actype2.name)
        self.assertEqual(util.checkout_filter(aircraft_type=actype1), expected)
        
        helper.create_checkout(aircraft_type=actype2, pilot=c.pilot, airstrip=c.airstrip)
        expected[0]['actypes'][actype2.name] = util.CHECKOUT_SUDAH
        
        self.assertEqual(util.checkout_filter(), expected)
    
    def test_multiple_airstrips(self):
        airstrip1 = helper.create_airstrip('ID1', 'Airstrip1')
        airstrip2 = helper.create_airstrip('ID2', 'Airstrip2')
        
        c = helper.create_checkout(airstrip=airstrip1)
        
        expected = [{
            'pilot_name': c.pilot.full_name,
            'pilot_slug': c.pilot.username,
            'airstrip_ident': airstrip1.ident,
            'airstrip_name': airstrip1.name,
            'actypes': {
                c.aircraft_type.name: util.CHECKOUT_SUDAH,
            },
        },]
        
        self.assertEqual(util.checkout_filter(), expected)
        
        helper.create_checkout(airstrip=airstrip2, pilot=c.pilot, aircraft_type=c.aircraft_type)
        r = {
            'pilot_name': c.pilot.full_name,
            'pilot_slug': c.pilot.username,
            'airstrip_ident': airstrip2.ident,
            'airstrip_name': airstrip2.name,
            'actypes': {
                c.aircraft_type.name: util.CHECKOUT_SUDAH,
            },
        }
        expected.append(r)
        
        self.assertEqual(util.checkout_filter(), expected)
    
    def test_filtering_by_base(self):
        base1 = helper.create_airstrip('BASE', 'Base1', is_base=True)
        airstrip1 = helper.create_airstrip('ID1', 'Airstrip1')
        airstrip1.bases.add(base1)
        airstrip2 = helper.create_airstrip('ID2', 'Airstrip2')
        
        c = helper.create_checkout(airstrip=airstrip1)
        _ = helper.create_checkout(airstrip=airstrip2, pilot=c.pilot, aircraft_type=c.aircraft_type)
        
        expected = [{
            'pilot_name': c.pilot.full_name,
            'pilot_slug': c.pilot.username,
            'airstrip_ident': airstrip1.ident,
            'airstrip_name': airstrip1.name,
            'actypes': {
                c.aircraft_type.name: util.CHECKOUT_SUDAH,
            },
        },]
        
        self.assertEqual(util.checkout_filter(base=base1), expected)
    
    def test_multiple_pilots(self):
        pilot1 = helper.create_pilot('kim', 'Kim', 'Pilot1')
        pilot2 = helper.create_pilot('sam', 'Sam', 'Pilot2')
            
        c1 = helper.create_checkout(pilot=pilot1)
        
        expected = [{
            'pilot_name': pilot1.full_name,
            'pilot_slug': c1.pilot.username,
            'airstrip_ident': c1.airstrip.ident,
            'airstrip_name': c1.airstrip.name,
            'actypes': {
                c1.aircraft_type.name: util.CHECKOUT_SUDAH,
            },
        },]
        
        self.assertEqual(util.checkout_filter(), expected)
        
        c2 = helper.create_checkout(pilot=pilot2, airstrip=c1.airstrip, aircraft_type=c1.aircraft_type)
        r = {
            'pilot_name': pilot2.full_name,
            'pilot_slug': c2.pilot.username,
            'airstrip_ident': c2.airstrip.ident,
            'airstrip_name': c2.airstrip.name,
            'actypes': {
                c2.aircraft_type.name: util.CHECKOUT_SUDAH,
            },
        }
        expected.append(r)
        
        self.assertEqual(util.checkout_filter(), expected)
    
    def test_multiple_all(self):
        pilot1 = helper.create_pilot('kim', 'Kim', 'Pilot1')
        pilot2 = helper.create_pilot('sam', 'Sam', 'Pilot2')
        actype1 = helper.create_aircrafttype('Name1')    
        actype2 = helper.create_aircrafttype('Name2')
        airstrip1 = helper.create_airstrip('ID1', 'Airstrip1')
        airstrip2 = helper.create_airstrip('ID2', 'Airstrip2')
            
        c1 = helper.create_checkout(pilot=pilot1, airstrip=airstrip1, aircraft_type=actype1)
        c2 = helper.create_checkout(pilot=pilot1, airstrip=airstrip1, aircraft_type=actype2)
        c3 = helper.create_checkout(pilot=pilot1, airstrip=airstrip2, aircraft_type=actype1)
        c3 = helper.create_checkout(pilot=pilot1, airstrip=airstrip2, aircraft_type=actype2)
        c4 = helper.create_checkout(pilot=pilot2, airstrip=airstrip1, aircraft_type=actype1)
        c5 = helper.create_checkout(pilot=pilot2, airstrip=airstrip1, aircraft_type=actype2)
        c6 = helper.create_checkout(pilot=pilot2, airstrip=airstrip2, aircraft_type=actype1)
        c7 = helper.create_checkout(pilot=pilot2, airstrip=airstrip2, aircraft_type=actype2)
        
        expected = [{
            'pilot_name': pilot1.full_name,
            'pilot_slug': pilot1.username,
            'airstrip_ident': airstrip1.ident,
            'airstrip_name': airstrip1.name,
            'actypes': {
                actype1.name: util.CHECKOUT_SUDAH,
                actype2.name: util.CHECKOUT_SUDAH,
            },
        }, {
            'pilot_name': pilot1.full_name,
            'pilot_slug': pilot1.username,
            'airstrip_ident': airstrip2.ident,
            'airstrip_name': airstrip2.name,
            'actypes': {
                actype1.name: util.CHECKOUT_SUDAH,
                actype2.name: util.CHECKOUT_SUDAH,
            },
        }, {
            'pilot_name': pilot2.full_name,
            'pilot_slug': pilot2.username,
            'airstrip_ident': airstrip1.ident,
            'airstrip_name': airstrip1.name,
            'actypes': {
                actype1.name: util.CHECKOUT_SUDAH,
                actype2.name: util.CHECKOUT_SUDAH,
            },
        }, {
            'pilot_name': pilot2.full_name,
            'pilot_slug': pilot2.username,
            'airstrip_ident': airstrip2.ident,
            'airstrip_name': airstrip2.name,
            'actypes': {
                actype1.name: util.CHECKOUT_SUDAH,
                actype2.name: util.CHECKOUT_SUDAH,
            },
        },]
        
        self.assertEqual(util.checkout_filter(), expected)
        
        # Since we already have all these objects created, let's test the
        # filtering feature!
        self.assertEqual(util.checkout_filter(pilot=pilot1), expected[:2])
        self.assertEqual(util.checkout_filter(pilot=pilot2), expected[2:])
        t = [r for i, r in enumerate(expected) if i in (0,2)]
        self.assertEqual(util.checkout_filter(airstrip=airstrip1), t)
        t = [r for i, r in enumerate(expected) if i in (1,3)]
        self.assertEqual(util.checkout_filter(airstrip=airstrip2), t)
        
        c1.delete()
        expected = expected[1:]
        for e in expected:
           e['actypes'].pop(actype2.name)
        self.assertEqual(util.checkout_filter(aircraft_type=actype1), expected)
        
        
class PilotCheckoutsGroupedByAirstripTests(TestCase):
    
    def setUp(self):
        # Template for expected results
        self.expected = {
            'populate': {
                'pilot': False,
                'airstrip': True,
            },
            'aircraft_types': [],
            'results': [],
        }
    
    def test_empty(self):
        pilot = helper.create_pilot()
        self.assertEqual(util.pilot_checkouts_grouped_by_airstrip(pilot), self.expected)
    
    def test_multiple_pilots(self):
        pilot1 = helper.create_pilot('kim', 'Kim', 'Pilot1')
        pilot2 = helper.create_pilot('sam', 'Sam', 'Pilot2')
        
        c1 = helper.create_checkout(pilot=pilot1)
        c2 = helper.create_checkout(pilot=pilot2, airstrip=c1.airstrip, aircraft_type=c1.aircraft_type)
        
        results = [{
            'pilot_name': pilot1.full_name,
            'pilot_slug': pilot1.username,
            'airstrip_ident': c1.airstrip.ident,
            'airstrip_name': c1.airstrip.name,
            'actypes': {
                c1.aircraft_type.name: util.CHECKOUT_SUDAH,
            },
        },]
        
        self.expected['aircraft_types'] = [c1.aircraft_type.name,]
        self.expected['results'] = results
        
        self.assertEqual(util.pilot_checkouts_grouped_by_airstrip(pilot1), self.expected)
    

class AirstripCheckoutsGroupedByPilotTests(TestCase):
    
    def setUp(self):
        # Template for expected results
        self.expected = {
            'populate': {
                'pilot': True,
                'airstrip': False,
            },
            'aircraft_types': [],
            'results': [],
        }
    
    def test_empty(self):
        airstrip = helper.create_airstrip()
        self.assertEqual(util.airstrip_checkouts_grouped_by_pilot(airstrip), self.expected)
    
    def test_multiple_pilots(self):
        airstrip1 = helper.create_airstrip('ID1', 'Airstrip1')
        airstrip2 = helper.create_airstrip('ID2', 'Airstrip2')
        
        c1 = helper.create_checkout(airstrip=airstrip1)
        c2 = helper.create_checkout(airstrip=airstrip2, pilot=c1.pilot, aircraft_type=c1.aircraft_type)
        
        results = [{
            'pilot_name': c1.pilot.full_name,
            'pilot_slug': c1.pilot.username,
            'airstrip_ident': airstrip1.ident,
            'airstrip_name': airstrip1.name,
            'actypes': {
                c1.aircraft_type.name: util.CHECKOUT_SUDAH,
            },
        },]
        
        self.expected['aircraft_types'] = [c1.aircraft_type.name,]
        self.expected['results'] = results
        
        self.assertEqual(util.airstrip_checkouts_grouped_by_pilot(airstrip1), self.expected)
        

class CheckoutsSelesaiTests(TestCase):
    
    def setUp(self):
        # Template for expected results
        self.expected = {
            'populate': {
                'pilot': True,
                'airstrip': True,
            },
            'aircraft_types': [],
            'results': [],
        }
    
    def test_empty(self):
        self.assertEqual(util.sudah_selesai(), self.expected)
    
    def test_with_checkouts(self):
        c = helper.create_checkout()
        
        results = [{
            'pilot_name': c.pilot.full_name,
            'pilot_slug': c.pilot.username,
            'airstrip_ident': c.airstrip.ident,
            'airstrip_name': c.airstrip.name,
            'actypes': {
                c.aircraft_type.name: util.CHECKOUT_SUDAH,
            },
        },]
        
        self.expected['aircraft_types'] = [c.aircraft_type.name,]
        self.expected['results'] = results
        
        self.assertEqual(util.sudah_selesai(), self.expected)
        

class CheckoutsBelumSelesaiTests(TestCase):
    
    def setUp(self):
        # Template for expected results
        self.expected = {
            'populate': {
                'pilot': True,
                'airstrip': True,
            },
            'aircraft_types': [],
            'results': [],
        }
    
    def test_empty(self):
        self.assertEqual(util.belum_selesai(), self.expected)
    
    def test_exclude_fully_selesai(self):
        """If all AircraftTypes for a Pilot/Airstrip pair have a Sudah Selesai
        status, that Pilot/Airstrip pair should be removed from the results."""
        c = helper.create_checkout()
        
        self.expected['aircraft_types'] = util.get_aircrafttype_names()
        
        self.assertEqual(util.belum_selesai(), self.expected)
        
    def test_with_data(self):
        pilot1 = helper.create_pilot('kim', 'Kim', 'Pilot1')
        pilot2 = helper.create_pilot('sam', 'Sam', 'Pilot2')
        actype1 = helper.create_aircrafttype('Name1')
        actype2 = helper.create_aircrafttype('Name2')
        airstrip1 = helper.create_airstrip('ID1', 'Airstrip1')
        airstrip2 = helper.create_airstrip('ID2', 'Airstrip2')
        airstrip3 = helper.create_airstrip('ID3', 'Airstrip3')
        
        c1 = helper.create_checkout(pilot=pilot1, airstrip=airstrip1, aircraft_type=actype1)
        c2 = helper.create_checkout(pilot=pilot1, airstrip=airstrip1, aircraft_type=actype2)
        c3 = helper.create_checkout(pilot=pilot2, airstrip=airstrip2, aircraft_type=actype1)
        
        results = [{
            'pilot_name': pilot1.full_name,
            'pilot_slug': pilot1.username,
            'airstrip_ident': airstrip2.ident,
            'airstrip_name': airstrip2.name,
            'actypes': {
                actype1.name: util.CHECKOUT_BELUM,
                actype2.name: util.CHECKOUT_UNPRECEDENTED,
            },
        }, {
            'pilot_name': pilot2.full_name,
            'pilot_slug': pilot2.username,
            'airstrip_ident': airstrip1.ident,
            'airstrip_name': airstrip1.name,
            'actypes': {
                actype1.name: util.CHECKOUT_BELUM,
                actype2.name: util.CHECKOUT_BELUM,
            },
        }, {
            'pilot_name': pilot2.full_name,
            'pilot_slug': pilot2.username,
            'airstrip_ident': airstrip2.ident,
            'airstrip_name': airstrip2.name,
            'actypes': {
                actype1.name: util.CHECKOUT_SUDAH,
                actype2.name: util.CHECKOUT_UNPRECEDENTED,
            },
        },]
        
        self.expected['aircraft_types'] = util.get_aircrafttype_names()
        self.expected['results'] = results
        
        self.assertEqual(util.belum_selesai(), self.expected)
        
        # Since we already have all these objects created, let's test the
        # 'belum selesai' filtering feature!
        self.expected['results'] = results[:1]
        self.assertEqual(util.belum_selesai(pilot=pilot1), self.expected)
        self.expected['results'] = results[1:]
        self.assertEqual(util.belum_selesai(pilot=pilot2), self.expected)
        self.expected['results'] = [results[1],]
        self.assertEqual(util.belum_selesai(airstrip=airstrip1), self.expected)
        self.expected['results'] = [r for i, r in enumerate(results) if i in (0,2)]
        self.assertEqual(util.belum_selesai(airstrip=airstrip2), self.expected)
        
        self.expected['results'] = results[:2]
        for r in self.expected['results']:
            r['actypes'].pop(actype2.name)
        self.expected['aircraft_types'] = [actype1.name,]
        self.assertEqual(util.belum_selesai(aircraft_type=actype1), self.expected)


class ChoicesTests(TestCase):
    
    def test_choices_checkout_status(self):
        expected = [(util.CHECKOUT_SUDAH, util.CHECKOUT_SUDAH_LABEL), (util.CHECKOUT_BELUM, util.CHECKOUT_BELUM_LABEL)]
        self.assertEqual(util.choices_checkout_status(), expected)


class QueryTests(TestCase):
    
    def test_get_pilots(self):
        self.assertEqual(len(util.get_pilots()), 0)
        
        pilot1 = helper.create_pilot('kim', 'Kim', 'Pilot1')
        pilot2 = helper.create_pilot('sam', 'Sam', 'Pilot2')
        pilot3 = helper.create_pilot('ada', 'Ada', 'Pilot0')
        
        expected = [pilot3, pilot1, pilot2]
        query = util.get_pilots()
        
        self.assertEqual([o for o in query], expected)
        
        user1 = User.objects.create_user('user', 'User', 'Non-Pilot')
        
        query = util.get_pilots()
        self.assertEqual([o for o in query], expected)
    
    def test_get_bases(self):
        self.assertEqual(len(util.get_bases()), 0)
        
        base1 = helper.create_airstrip('SCND', 'Second', is_base=True)
        base2 = helper.create_airstrip('FRST', 'First', is_base=True)
        base3 = helper.create_airstrip('THRD', 'Third', is_base=True)
        
        expected = [base2, base1, base3]
        query = util.get_bases()
        
        self.assertEqual([o for o in query], expected)
        
        airstrip1 = helper.create_airstrip('FRTH', 'Fourth', is_base=False)
        
        query = util.get_bases()
        self.assertEqual([o for o in query], expected)
