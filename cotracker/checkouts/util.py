from django.contrib.auth.models import User, Group

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


def get_pilot_airstrip_pairs(pilot=None, airstrip=None, base=None):
    """Populates a sorted list of Pilot/Airstrip tuples"""
    pilots = get_pilots()
    if pilot is not None:
	# Limiting to the requested object and maintaining iterability
	pilots = [pilots.get(pk=pilot.pk),]
    airstrips = Airstrip.objects.all().order_by('ident')
    if airstrip is not None:
	# Limiting to the requested object and maintaining iterability
	airstrips = [airstrips.get(pk=airstrip.pk),]
    elif base is not None:
	airstrips = airstrips.filter(bases=base)
    
    pairs = []
    for p in pilots:
	for a in airstrips:
	    pairs.append((p.username, a.ident))
    
    return pairs


def get_precedented_checkouts():
    """Provides a two-tier dictionary summarizing whether each
    airstrip has an existing checkout entry for each aircraft.
    
    precedented = {
	'airstrip_ident': {
	    'actype': True,
	},
    }
    """
    precedented = {}
    
    actypes = AircraftType.objects.all()
    for actype in actypes:
	checkouts = Checkout.objects.filter(aircraft_type=actype).select_related('airstrip')
	airstrips = []
	for c in checkouts:
	    if c.airstrip not in airstrips:
		airstrips.append(c.airstrip)
	for a in airstrips:
	    if a.ident not in precedented:
		precedented[a.ident] = {}
	    precedented[a.ident][actype.name] = True
    
    return precedented


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
	    'pilot_name': c.pilot.full_name,
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


def checkouts_belum_selesai(**kwargs):
    results = {
	'populate': {
	    'pilot': True,
	    'airstrip': True,
	},
	#'aircraft_types': get_aircrafttype_names(),
	#'results': checkout_filter(**kwargs),
    }
    
    original_checkouts = checkout_filter(**kwargs)
    actypes = get_aircrafttype_names()
    results['aircraft_types'] = actypes
    pilots_v_airstrips = get_pilot_airstrip_pairs(**kwargs)
    next_pair_index = 0
    
    belum_selesai_checkouts = []
    for c in original_checkouts:
	current_pair = (c['pilot_slug'], c['airstrip_ident'])
	expected_pair = pilots_v_airstrips[next_pair_index]
	while current_pair != expected_pair:
	    # Need to insert the missing pair
	    pilot_slug, airstrip_ident = expected_pair
	    pilot = User.objects.get(username=pilot_slug)
	    airstrip = Airstrip.objects.get(ident=airstrip_ident)
	    new_result = {
		'pilot_name': pilot.full_name,
		'pilot_slug': pilot_slug,
		'airstrip_ident': airstrip_ident,
		'airstrip_name': airstrip.name,
		'actypes': {},
	    }
	    for actype in actypes:
		new_result['actypes'][actype] = CHECKOUT_BELUM
	    
	    belum_selesai_checkouts.append(new_result)
	    
	    # Still missing a Pilot/Airstrip pair?
	    next_pair_index += 1
	    expected_pair = pilots_v_airstrips[next_pair_index]
	
	belum_selesai_checkouts.append(c)
	# Prepare for the next check
	next_pair_index += 1
    
    if next_pair_index != len(pilots_v_airstrips):
	# Still some missing pairs
	for i in range(next_pair_index,len(pilots_v_airstrips)):
	    expected_pair = pilots_v_airstrips[i]
	    pilot_slug, airstrip_ident = expected_pair
	    pilot = User.objects.get(username=pilot_slug)
	    airstrip = Airstrip.objects.get(ident=airstrip_ident)
	    new_result = {
		'pilot_name': pilot.full_name,
		'pilot_slug': pilot_slug,
		'airstrip_ident': airstrip_ident,
		'airstrip_name': airstrip.name,
		'actypes': {},
	    }
	    for actype in actypes:
		new_result['actypes'][actype] = CHECKOUT_BELUM
	    
	    belum_selesai_checkouts.append(new_result)
    
    precedented = get_precedented_checkouts()
    checkouts = []
    for c in belum_selesai_checkouts:
	ident = c['airstrip_ident']
	incomplete = False
	for ac,status in c['actypes'].items():
	    if status == CHECKOUT_BELUM:
		incomplete = True
		# A Belum should be changed to Unprecedented when no pilot has
		# been checked out at the given location in the given AircraftType
		if ident not in precedented or ac not in precedented[ident]:
		    c['actypes'][ac] = CHECKOUT_UNPRECEDENTED
	
	# Only save entries with BELUM or UNPRECEDENTED statuses
	if incomplete:
	    checkouts.append(c)
    
    results['results'] = checkouts
    return results


def pilot_checkouts_grouped_by_airstrip(pilot):
    """Organizes the pilot's checkouts by airstrips."""
    results = checkouts_selesai(pilot=pilot)
    results['populate']['pilot'] = False
    return results


def airstrip_checkouts_grouped_by_pilot(airstrip):
    """Organizes the airstrip's checkouts by pilot."""
    results = checkouts_selesai(airstrip=airstrip)
    results['populate']['airstrip'] = False
    return results
