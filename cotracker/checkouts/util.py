from django.contrib.auth.models import User

from .models import AircraftType, Airstrip, Checkout


"""
Checkout States
---------------
+ Sudah: The pilot has been checked out at the airstrip in the aircraft type
+ Belum: The pilot has not been checked out at the airstrip in the aircraft
	 type, but another pilot has.
+ Unprecedented: No pilot has been checked out at the airstrip in the aircraft
		 type.

These states have corresponding names in the CSS file to make them easy to
style as necessary.
"""
CHECKOUT_SUDAH = "sudah"
CHECKOUT_SUDAH_LABEL = "Sudah Selesai"
CHECKOUT_BELUM = "belum"
CHECKOUT_BELUM_LABEL = "Belum Selesai"
CHECKOUT_UNPRECEDENTED = "unprecedented"


def choices_checkout_status():
    return [(CHECKOUT_SUDAH, CHECKOUT_SUDAH_LABEL), (CHECKOUT_BELUM, CHECKOUT_BELUM_LABEL)]


def get_pilots():
    return User.objects.filter(groups__name="Pilots").order_by('last_name','first_name')


def get_bases():
    return Airstrip.objects.filter(is_base=True).order_by('ident')


def get_aircrafttype_names(order="name"):
    """Populates a sorted list with the names of all known AircraftTypes"""
    aircrafttypes = AircraftType.objects.order_by(order)
    return [actype.name for actype in aircrafttypes]


def checkout_filter(pilot=None, airstrip=None, base=None):
    core_query = Checkout.objects.all()
    if pilot != None:
	core_query = core_query.filter(pilot=pilot)
    if airstrip != None:
	core_query = core_query.filter(airstrip=airstrip)
    if base != None:
	core_query = core_query.filter(airstrip__bases=base)
	
    checkouts = core_query.select_related(
		    'pilot', 'airstrip', 'aircraft_type'
		).order_by(
		    'pilot__last_name',
		    'pilot__first_name',
		    'airstrip__ident',
		    'aircraft_type__name'
		)
    actypes = get_aircrafttype_names()
    results = []
    for c in checkouts:
	if len(results) > 0:
	    r = results.pop()
	    if r['pilot_slug'] == c.pilot.username and r['airstrip_ident'] == c.airstrip.ident:
		r['actypes'][c.aircraft_type.name] = CHECKOUT_SUDAH
		results.append(r)
		continue
	    else:
		# Put the unmodified record back in the list before creating
		# the new record
		results.append(r)
		
	r = {
	    'pilot_name': c.get_pilot_name(),
	    'pilot_slug': c.pilot.username,
	    'airstrip_ident': c.airstrip.ident,
	    'airstrip_name': c.airstrip.name,
	    'actypes': {},
	}
	for actype in actypes:
	    if actype == c.aircraft_type.name:
		# Mark the entry for the current checkout aircraft during init
		r['actypes'][actype] = CHECKOUT_SUDAH
	    else:
		r['actypes'][actype] = CHECKOUT_BELUM
	
	results.append(r)
    return results


def checkouts_selesai(**kwargs):
    results = {
	'populate': {
	    'pilot': True,
	    'airstrip': True,
	},
	'aircraft_types': get_aircrafttype_names(),
	'results': checkout_filter(**kwargs),
    }
    
    return results


def pilot_checkouts_grouped_by_airstrip(pilot):
    """Organizes the pilot's checkouts by airstrips.
    
    Returns a list (sorted by airstrip ident) in which every airstrip at which
    the given pilot is checked out is a dictionary, with a key:value pair 
    indicating whether the pilot is checked out or not in each AircraftType."""
    
    results = {
	'populate': {
	    'pilot': False,
	    'airstrip': True,
	},
	'aircraft_types': get_aircrafttype_names(),
	'results': checkout_filter(pilot=pilot),
    }
    
    return results


def airstrip_checkouts_grouped_by_pilot(airstrip):
    """Organizes the airstrip's checkouts by pilot.
    
    Returns a list (sorted by pilot last name then first name) in which every
    pilot checked out at the given airstrip is a dictionary, with a key:value
    pair indicating whether the pilot is checked out or not in each 
    AircraftType.
    """
    
    results = {
	'populate': {
	    'pilot': True,
	    'airstrip': False,
	},
	'aircraft_types': get_aircrafttype_names(),
	'results': checkout_filter(airstrip=airstrip),
    }
    
    return results
