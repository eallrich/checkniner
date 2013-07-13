"""Utility functions for test cases"""

import datetime

from django.contrib.auth.models import Group, User

from checkouts.models import AircraftType, Airstrip, Checkout

def create_aircrafttype(name='FooBar1234', object_only=True):
    """Returns a new AircraftType with the given name.
    
    To also receive a dictionary of the properties set on the model, use
    object_only=False.
    """
    o = AircraftType.objects.create(name=name)
    
    if object_only:
        return o
    return (o, {'name': name,})


def create_airstrip(ident='ABCD', name='AlphaBravoCharlieDelta', is_base=False, object_only=True):
    """Returns a new Airstrip with the given ident and name.
    
    To also receive a dictionary of the properties set on the model, use
    object_only=False.
    """
    o = Airstrip.objects.create(ident=ident, name=name, is_base=is_base)
    
    if object_only:
        return o
    return (o, {'ident': ident, 'name': name,})


def create_pilot(username='kimpilot', first_name='Kim', last_name='Pilot', email='kim@example.com', password='secret'):
    """Returns a new Pilot (User) with the given properties."""
    pilot_group, _ = Group.objects.get_or_create(name='Pilots')
    pilot = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
    pilot.groups.add(pilot_group)
    
    return pilot


def create_flight_scheduler(username='samscheduler', first_name='Sam', last_name='Scheduler', email='sam@example.com', password='secret'):
    """Returns a new Flight Scheduler (User) with the given properties."""
    flightsched_group, _ = Group.objects.get_or_create(name='Flight Schedulers')
    scheduler = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
    scheduler.groups.add(flightsched_group)
    
    return scheduler


def create_checkout(**kwargs):
    """Returns a new Checkout model instance with relationships to the given
    model instances.
    
    To create an instance attached to one or more particular related model
    instances, pass the related instances as keyword arguments. If an
    argument is not set, a default instance will be created and used.
    
    Possible keyword args:
        pilot
        airstrip
        aircraft_type
        date
    """
    if 'pilot' not in kwargs:
        kwargs['pilot'] = create_pilot()
    if 'airstrip' not in kwargs:
        kwargs['airstrip'] = create_airstrip()
    if 'aircraft_type' not in kwargs:
        kwargs['aircraft_type'] = create_aircrafttype()
    if 'date' not in kwargs:
        kwargs['date'] = datetime.datetime.now()
    
    return Checkout.objects.create(**kwargs)
    
