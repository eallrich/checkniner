from django.contrib.auth.models import User
from django.test import TestCase

from checkouts.models import (Checkout, user_full_name, user_is_pilot)

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
        
        self.checkout = Checkout.objects.create(
            pilot = self.pilot,
            aircraft_type = self.aircrafttype,
            airstrip = self.airstrip,
        )
    
    def test_unicode(self):
        expected = '%s is checked out at %s in a %s' % (self.pilot.full_name, self.airstrip, self.aircrafttype) 
        self.assertEqual(self.checkout.__unicode__(), expected)
    

class ModelFunctionTests(TestCase):
    
    def test_user_full_name(self):
        user = helper.create_pilot()
        expected = '%s, %s' % (user.last_name, user.first_name)
        self.assertEqual(user_full_name(user), expected)
        
        user.first_name = ''
        expected = user.username
        self.assertEqual(user_full_name(user), expected)
        
        user.first_name = 'Foo'
        user.last_name = ''
        self.assertEqual(user_full_name(user), expected)
        
        user.first_name = ''
        self.assertEqual(user_full_name(user), expected)
    
    def test_user_is_pilot(self):
        pilot_user = helper.create_pilot('pilot','Pilot','User')
        self.assertTrue(user_is_pilot(pilot_user))
        
        normal_user = User.objects.create_user(
                        'username',
                        'normal@example.com',
                        'secret',
                        first_name='Normal',
                        last_name='User')
        self.assertFalse(user_is_pilot(normal_user))


class VerifyPatchedUserModelTests(TestCase):
    
    def setUp(self):
        self.user = helper.create_pilot()
    
    def test_full_name(self):
        expected = '%s, %s' % (self.user.last_name, self.user.first_name)
        self.assertEqual(self.user.full_name, expected) 
    
    def test_is_pilot(self):
        self.assertTrue(self.user.is_pilot)
    
    def test_unicode(self):
        expected = '%s, %s' % (self.user.last_name, self.user.first_name)
        self.assertEqual(self.user.__unicode__(), expected)
