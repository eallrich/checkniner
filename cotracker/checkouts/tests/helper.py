from django.contrib.auth.models import Group, User

from checkouts.models import AircraftType, Airstrip

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
